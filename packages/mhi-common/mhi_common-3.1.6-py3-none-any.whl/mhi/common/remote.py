#! /usr/bin/env python3
"""
Remote method invocation from Python scripts to MHI application entities.
"""
# pylint: disable=too-many-lines

from __future__ import annotations

import importlib
import io
import pickle
import queue
import socket
import threading
import time

from functools import wraps
from typing import (Any, DefaultDict, Dict, List, Optional, Sequence, Union,
                    Tuple, Type, TypeVar, cast, TYPE_CHECKING)
from weakref import WeakValueDictionary


from .cache import cached_property, TimedCachedProperty
from .collection import LingeringCache
from .platform import is_windows
from .version import Version
from .warnings import warn

if TYPE_CHECKING:
    from .server import Server


#===============================================================================
# Exceptions
#===============================================================================

class RemoteException(Exception):
    """Indication of an API error communicating with remote objects"""

    def __init__(self, message, *args):
        if args:
            message = message % args
        super().__init__(message)


class NoSuchRemoteMethodError(RemoteException):
    """The Remote Method does not exists"""


#===============================================================================
# Remotable
#===============================================================================

class Remotable:
    """
    Base class for Remote Method Invocation (RMI) enabled objects
    """

    _identity: Dict[str, Any]
    _context: Context


    def __init__(self, *, _ctx: Optional[Context] = None,
                 _ident: Optional[Dict[str, Any]] = None):

        if _ctx is None or _ident is None:
            raise RemoteException("Attempt to instantiate a Proxy object")

        self._context = _ctx
        self._identity = _ident


    def _post_init(self):

        pass


    def _pid(self):

        cls = self.__class__
        module = getattr(self, '_MODULE', cls.__module__)
        return module, cls.__name__, self._identity


    def __repr__(self):

        identity = ", ".join(f"{key}={val!r}"
                             for key, val in self._identity.items())
        return f"{self.__class__.__name__}({identity})"


    def __eq__(self, other):

        return self._pid() == other._pid()


    def __ne__(self, other):

        return self._pid() != other._pid()


    def _rmi(self, method_name: str, *args, **kwargs):

        return self._context.call(self, method_name, *args, **kwargs)


    def _rmi_getprop(self, attr_name: str) -> Any:

        return self._context.get_prop(self, attr_name)


    def _rmi_setprop(self, attr_name: str, value: Any):

        return self._context.set_prop(self, attr_name, value)


    def _clear_cache(self):

        # Clear any WeakValueDictionaries, LingeringCaches and delete any
        # cached_properties.
        cls = type(self)
        for key, val in list(self.__dict__.items()):
            if isinstance(val,
                          (WeakValueDictionary, LingeringCache)):
                val.clear()
            elif isinstance(cls.__dict__.get(key),
                            (cached_property, TimedCachedProperty)):
                delattr(self, key)


    def _forget(self):

        self._clear_cache()

        return self._context.forget(self)


    @cached_property
    def _hash(self):

        keys = tuple(sorted(self._identity.keys()))
        values = tuple(self._identity[key] for key in keys) # pylint: disable=unsubscriptable-object
        return hash((keys, values))


    def __hash__(self):

        return self._hash


    @property
    def main(self) -> Application:
        """
        A reference to the :class:`.Application` object that returned this
        ``Remotable`` object.
        """

        return self._context._main            # pylint: disable=protected-access


#===============================================================================
# Remote Method Invocation
#===============================================================================

class rmi_property(property):                   # pylint: disable=invalid-name
    """
    A property which is stored in a remote object

    Apply this decorator to a property of a :class:`.Remotable` object causes
    the property access attempts to be forwarded to the remote application
    object.

    Remote properties may never be deleted.
    """


    def _fget(self) -> Any:
        """Undocumented"""


    def __init__(self, fget=None,           # pylint: disable=too-many-arguments,too-many-positional-arguments
                 fset=None, doc=None, name=None,
                 requires=None):            # pylint: disable=redefined-outer-name

        if fget is True:
            fget = rmi_property._fget
        super().__init__(fget=fget, fset=fset, fdel=None, doc=doc)
        if doc is not None:
            self.__doc__ = doc
        if not name:
            if fget and hasattr(fget, '__name__'):
                name = fget.__name__

        self._key = name
        self._required_version = Version(requires) if requires else None


    def __set_name__(self, owner, name):
        if self._key and self._key != name:
            raise AttributeError(f"@rmi_property name: {name} vs {self._key}")
        self._key = name


    def __get__(self, instance, owner):
        if instance is None:
            return self
        if not self.fget:
            raise AttributeError(f"can't get attribute {self._key}")
        if self._required_version:
            instance.main.requires(self._required_version, self._key)

        return instance._context.get_prop(instance, self._key)


    def __set__(self, instance, value):
        if not self.fset:
            raise AttributeError(f"can't set attribute {self._key}")
        if instance is not None:
            if self._required_version:
                instance.main.requires(self._required_version, self._key)

            instance._context.set_prop(instance, self._key, value)


    def __delete__(self, instance):
        raise AttributeError(f"can't delete attribute {self._key}")


    def __repr__(self):
        return f"RemoteProperty({self._key!r})"


    def __call__(self, fget):
        return rmi_property(fget, self.fset, fget.__doc__, fget.__name__)


#===============================================================================
# Remote Method Invocation
#===============================================================================

def rmi(_method=None, *, fallback=False):
    """
    Remote Method Invocation

    Applying this decorator to a method of a :class:`.Remotable` object causes
    the method invocation to be forwarded to the remote application object.

    If the remote application object's method does not exist and ``fallback``
    is ``True``, then the body of the decorated method is used as an client-side
    (and likely slower) implementation of the remote method.  Otherwise,
    the body of the decorated method is ignored.
    """

    def decorator(method):

        if isinstance(method, property):
            if fallback:
                raise ValueError("Fallback not valid for @rmi @property members.")
            return rmi_property(_method.fget, _method.fset, _method.fdel,
                                _method.__doc__)

        @wraps(method)
        def wrapper(self, *args, **kwargs):
            try:
                return self._context.call(self, # pylint: disable=protected-access
                                          method.__name__, *args, **kwargs)
            except NoSuchRemoteMethodError:
                if fallback is False:
                    raise
            return method(self, *args, **kwargs)

        return wrapper

    if callable(_method) or isinstance(_method, property):
        return decorator(_method)
    return decorator


#===============================================================================
# Application
#===============================================================================

class Application(Remotable):

    """
    A Remote Application object.

    This object represents the running application.  It implements the
    "context manager" protocol, allowing a Python script to automatically
    close the communication channel when the application object goes out of
    scope.
    """

    #-----------------------------------------------------------------------
    # Context Manager
    #-----------------------------------------------------------------------

    def __enter__(self):
        """
        Context Manager protocol

        Called when the application is used in a `with ...` statement.
        """

        return self


    def __exit__(self, exc_type, exc_value, traceback):
        """
        Context manager protocol

        When execution escapes the `with ...` statement, the connection
        to the application is closed.
        """

        if self.is_alive():
            self.close_connection()


    #-----------------------------------------------------------------------
    # Initialization
    #-----------------------------------------------------------------------

    def _initialize(self):
        pass


    #-----------------------------------------------------------------------
    #
    #-----------------------------------------------------------------------

    def _clear_cache(self):
        """
        Forget all cached remote application objects

        Note: This does not destroy any references held in script variables.
        delete or nullify variables to ensure complete amnesia.
        """

        super()._clear_cache()
        self._context._clear_cache()          # pylint: disable=protected-access


    #-----------------------------------------------------------------------
    # _generic command
    #-----------------------------------------------------------------------

    @rmi
    def _generic_cmd(self, cmd_id: int, lparam: int = 0, post: bool = False):
        """
        Execute a generic 'WM_COMMAND' command.

        Parameters:
            cmd_id (int): a 'word' parameter for the WM_COMMAND
            lparam (int): a 'long' parameter for the command (defaults to 0)
            post (bool): if True, uses PostMessage(), otherwise SendMessage()
        """

    #-----------------------------------------------------------------------
    # Common application functions
    #-----------------------------------------------------------------------

    @rmi_property(True, True)
    def silence(self) -> bool:                      # type: ignore[empty-body]
        """
        When set to `True`, silence all popup dialogs, using the dialog's
        "default" action.
        """


    def is_alive(self) -> bool:
        """
        Tests whether the application process is still running, and the
        communication socket to the application is still open.

        Returns:
            bool: ``True`` is the application communication channel is open,
            ``False`` otherwise.
        """

        return self._context.is_alive()


    def quit(self) -> None:
        """
        Terminate the remote application.

        Note: The local side of the socket connection to the remote
        application may not be closed.  The client is responsible
        for explicitly closing the connection::

            application.quit()
            application.close_connection()

        or by using a context manager::

            with ... as application:
                # interact with the application
                #
                # application.close_connection() is automatically called
                # when the `with` statement block exits.
        """

        self._clear_cache()

        self._rmi('quit')

        self._context.close()


    def close_connection(self) -> None:
        """
        Terminate connection to remote application.

        Note: The remote application will not be terminated.
        The "silence all dialog and message boxes" flag is cleared.
        """

        if self.is_alive():
            self.silence = False

        self._clear_cache()

        if self.is_alive():
            self._context.close()


    #-----------------------------------------------------------------------
    # Version Attribute
    #-----------------------------------------------------------------------

    @property
    def version(self) -> str:
        """Application Version"""

        raise NotImplementedError()


    #-----------------------------------------------------------------------
    # Requires
    #-----------------------------------------------------------------------

    def minimum_version(self, version: Union[str, Version]) -> bool:
        """
        Test if the remote application version is the given version or later.

        Parameters:
            version (str): The version number to test against.

        Returns:
            bool: ``True`` if the remote application version is greater than
                or equal to ``version``, ``False`` otherwise.
        """

        if not hasattr(self, '_version'):
            app_ver: Union[str, Version] = self.version
            if app_ver not in ('Alpha', 'Beta'):
                app_ver = Version(self.version)
            self._version = app_ver # pylint: disable=attribute-defined-outside-init

        if self._version in {'Alpha', 'Beta'}:
            return True

        if not isinstance(version, Version):
            version = Version(version)

        return self._version >= version


    def requires(self, version: str, msg: str = "Feature") -> None:
        """
        Verify the remote application is the given version or later.

        A ``NotImplementedError`` is raised if the remote application version
        is less than the required version.

        Parameters:
            version (str): The required version number.
        """

        if not self.minimum_version(version):
            msg = f"{msg} requires application version >= {version}"
            raise NotImplementedError(msg)


    #-----------------------------------------------------------------------
    # Embedded
    #-----------------------------------------------------------------------

    @property
    def is_embedded(self) -> bool:
        """Return whether an internal Python environment is being used"""

        return Context._EMBEDDED_SERVER is not None # pylint: disable=protected-access


    #-----------------------------------------------------------------------
    # Server Address
    #-----------------------------------------------------------------------

    def server_address(self) -> Tuple[str, int]:
        """
        Return the host/port address for the application server, which
        may be used to open additional connections to the application.

        .. versionadded:: 2.4.5
        """

        if self.is_embedded:
            return Context.server_address()

        # pylint: disable=protected-access
        return self._context._sock.getpeername()[:2]    # type: ignore[attr-defined]


    #-----------------------------------------------------------------------
    # Secondary Connection
    #-----------------------------------------------------------------------

    def secondary_connection(self, timeout=5) -> Application:
        """
        Open a secondary connection to the application server
        """

        # pylint: disable=protected-access
        host, port = self.server_address()
        app = Context._connect(host, port, timeout)
        app._initialize()
        return app


    #-----------------------------------------------------------------------
    # Map function and property
    #-----------------------------------------------------------------------

    def map_call(self, items: Sequence[Remotable], method: str, *args, **kwargs):
        """
        Call the same RMI method on a list of components, without using
        a round-trip to the server for each component.

        .. versionadded:: 2.4.5
        """

        # pylint: disable=protected-access
        return self._context._map_call(items, method, args, kwargs)


    def map_property(self, items: Sequence[Remotable], name: str):
        """
        Fetch the same RMI property from a list of components, without using
        a round-trip to the server for each component.

        .. versionadded:: 2.4.5
        """

        # pylint: disable=protected-access
        return self._context._map_getprop(items, name)


#===============================================================================
# requires decorator
#===============================================================================

def requires(version: str):
    """
    Requires a specific application version

    Ensures the appropriate remote application version before attempting to
    invoke the function.
    """

    required_version = Version(version)

    def decorator(method):
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            self.main.requires(required_version, method.__name__)
            return method(self, *args, **kwargs)
        return wrapper
    return decorator


#===============================================================================
# deprecated decorator
#===============================================================================

def deprecated(message="This method is deprecated"):
    """
    Flag a method as deprecated
    """

    def decorator(method):
        @wraps(method)
        def wrapper(*args, **kwargs):
            warn(message, DeprecationWarning)
            return method(*args, **kwargs)

        return wrapper

    return decorator if isinstance(message, str) else deprecated()(message)


#===============================================================================
# Context
#===============================================================================

# Flag Remotable for Generics
_Remotable = TypeVar('_Remotable', bound=Remotable)

class Context:                    # pylint: disable=too-many-instance-attributes
    """
    A Remote Context object

    This class is responsible for communications between the Python script
    and the remote application objects.

    Calls to :class:`.rmi` methods and access to :class:`.rmi_properties`
    are pickled, and sent over a communication channel.  The results of
    these operations are received from the communication channel, depickled,
    and returned to the caller.  Any exception generated by the remote
    operation is also transfered over the communication channel and raised
    locally.
    """

    _SIZE_OF_LENGTH = 4
    _EMBEDDED_SERVER: Optional[Server] = None
    _EMBEDDED_APPLICATION: Optional[Application] = None

    _call_cache: Dict[str, NoSuchRemoteMethodError]
    _proxy_cache: DefaultDict[Type[Remotable],
                              WeakValueDictionary[frozenset, Remotable]]


    #-----------------------------------------------------------------------
    # Embedded server address
    #-----------------------------------------------------------------------

    @classmethod
    def server_address(cls) -> Tuple[str, int]:
        """
        Return the first host/port address for the application server, which
        may be used to open additional connections to the application.

        .. versionadded:: 2.4.5

        .. versionchanged:: 3.0.2
            Returns the first address, if listening on more than one address.
            Multiple addresses are possible when both IPv4 and IPv6 are
            supported.
        """

        addresses = cls.server_addresses()

        if len(addresses) == 0:
            raise IndexError("No server address")

        return addresses[0]


    @classmethod
    def server_addresses(cls) -> List[Tuple[str, int]]:
        """
        Return the host/port addresses for the application server, which
        may be used to open additional connections to the application.

        .. versionadded:: 3.0.2
        """

        if cls._EMBEDDED_SERVER is None:
            raise ValueError("Not embedded")

        server = cls._EMBEDDED_SERVER._server # pylint: disable=protected-access
        if not server._running:               # pylint: disable=protected-access
            return []

        return server._addresses              # pylint: disable=protected-access


    #-----------------------------------------------------------------------
    # Factory & Constructor
    #-----------------------------------------------------------------------

    @classmethod
    def _application(cls, connect, launch, process_name=None) -> Application:

        app = None

        # Embedded?
        if cls._EMBEDDED_SERVER:
            app = cls._EMBEDDED_APPLICATION
            if app is None:
                app = cls._embedded()

        else:
            # Already running?

            from . import process      # pylint: disable=import-outside-toplevel

            if process_name and process.is_running(process_name):
                try:
                    app = connect()
                except ConnectionRefusedError:
                    pass

        # Connection to a running application succeeded?
        if app is not None:
            app.silence = True
            return app

        # No, try launching it
        return launch()


    @classmethod
    def _embedded(cls) -> Application:
        cls._EMBEDDED_APPLICATION = QueueContext(cls._EMBEDDED_SERVER)._main # pylint: disable=protected-access
        assert cls._EMBEDDED_APPLICATION is not None
        return cls._EMBEDDED_APPLICATION


    @classmethod
    def _connect(cls, host, port, timeout=5) -> Application: # pylint: disable=too-many-locals

        addr_infos = socket.getaddrinfo(host, port)
        if not addr_infos:
            raise OSError("getaddrinfo returns an empty list")

        exception: Optional[ConnectionRefusedError] = None

        for attempt in range(timeout):

            if attempt > 0:
                time.sleep(1)

            for af, socktype, proto, _, sa in addr_infos:
                sock = socket.socket(af, socktype, proto)

                if hasattr(socket, 'SIO_LOOPBACK_FAST_PATH'):
                    try:
                        sock.ioctl(socket.SIO_LOOPBACK_FAST_PATH, True)
                    except OSError as exc:
                        if is_windows():
                            WSAEOPNOTSUPP = 10045  # pylint: disable=invalid-name
                            if exc.winerror != WSAEOPNOTSUPP: # type: ignore
                                raise

                try:
                    sock.connect(sa)
                except ConnectionRefusedError as err:
                    exception = err
                else:
                    context = SocketContext(sock)
                    return context._main      # pylint: disable=protected-access

                sock.close()

        assert exception is not None
        raise exception


    def __init__(self):
        super().__init__()

        self.retries = 0
        self.retry_pause = None

        self._proxy_cache = DefaultDict(WeakValueDictionary)
        self._call_cache = {}

        self._pickler = Context._Pickler()
        self._unpickler = Context._Unpickler(self)

        self._thread = threading.Thread(target=self._reader, daemon=True,
                                        name='RxClient')
        self._thread.start()
        self._response = queue.Queue()

        self._main = self._getprop("SERVER", "_main")


    #-----------------------------------------------------------------------
    # RxClient
    #-----------------------------------------------------------------------

    def _reader(self):
        try:
            while self.is_alive():
                result = self._read()
                if type(result) == tuple and len(result) == 2:  # pylint: disable=unidiomatic-typecheck
                    channel, msg = result
                else:
                    channel, msg = None, result

                if channel:
                    self._broadcast(channel, msg)
                else:
                    self._response.put(msg)

                # Clear reference so LingeringCache counts "real" references
                result = None
                channel = None
                msg = None

        except OSError as ioerr:
            self._response.put(ioerr)
        except EOFError:
            pass # Can't forward EOF over connection
        finally:
            self._thread = None


    def _broadcast(self, channel, msg):
        self._main._broadcast(channel, msg)   # pylint: disable=protected-access


    #-----------------------------------------------------------------------
    # Cache
    #-----------------------------------------------------------------------

    def lookup(self, cls: Type[_Remotable], **identity) -> Optional[_Remotable]:
        """
        Retrieve a Remote Proxy object, if it can be found in the cache
        """

        cache = self._proxy_cache[cls]
        key = frozenset(identity.items())
        return cast(_Remotable, cache.get(key))


    def forget(self, obj: Remotable):
        """
        Remove a Remote Proxy object from the cache
        """

        cls = type(obj)
        cache = self._proxy_cache[cls]
        key = frozenset(obj._identity.items()) # pylint: disable=protected-access
        cache.pop(key, None)


    def _clear_cache(self):

        self._proxy_cache.clear()
        self._call_cache.clear()


    #-----------------------------------------------------------------------
    # Close & Closed check
    #-----------------------------------------------------------------------

    def is_alive(self) -> bool:
        """Is a connection to the server still active?"""
        raise NotImplementedError()


    def close(self) -> None:
        """Close communication"""
        raise NotImplementedError()


    #-----------------------------------------------------------------------
    # RMI Calls & Property Set/Get
    #-----------------------------------------------------------------------

    def call(self, rcvr: Remotable, method_name: str, *args, **kwargs):
        """
        Make a remote call to the application method

        If the application returns an exception object,
        the exception is raised here.

        The :py:obj:`mhi.common.remote.rmi` decorator is more convenient.

        .. versionadded:: 2.5.0
        """

        # If the method didn't exist before for this executable's context,
        # it still won't exists.  Skip the round trip to the server.
        key = f"{rcvr.__class__.__name__}.{method_name}"
        result = self._call_cache.get(key)
        if result is not None:
            raise result

        result = self._call(rcvr, method_name, *args, **kwargs)
        if isinstance(result, Exception):

            # Backwards compatibility:
            # promote mhi.any.package.RemoteException('Unknown method ...')
            if (result.__class__.__name__ == 'RemoteException' and
                result.args[0][:15] == 'Unknown method '):

                result = NoSuchRemoteMethodError(result.args[0])

            # Cache NoSuchRemoteMethodError
            if isinstance(result, NoSuchRemoteMethodError):
                self._call_cache[key] = result

            exception = result
            raise exception

        return result


    def _call(self, rcvr, method_name, *args, **kwargs):
        msg = ("_call", rcvr, method_name, args, kwargs)
        return self._rmi(msg)


    def get_prop(self, rcvr: Remotable, attr_name: str) -> Any:
        """
        Fetch a remote property

        If the application returns an exception object,
        the exception is raised here.

        The :py:obj:`mhi.common.remote.rmi_property` decorator is more
        convenient.

        .. versionadded:: 2.5.0
        """

        result = self._getprop(rcvr, attr_name)
        if isinstance(result, Exception):
            raise result
        return result


    def _getprop(self, rcvr, attr_name):
        msg = ("_getprop", rcvr, attr_name)
        return self._rmi(msg)


    def set_prop(self, rcvr: Remotable, attr_name: str, value: Any):
        """
        Set a remote property

        If the application returns an exception object,
        the exception is raised here.

        The :py:obj:`mhi.common.remote.rmi_property` decorator is more
        convenient.

        .. versionadded:: 2.5.0
        """

        exception = self._setprop(rcvr, attr_name, value)
        if isinstance(exception, Exception):
            raise exception


    def _setprop(self, rcvr, attr_name, value):
        msg = ("_setprop", rcvr, attr_name, value)
        return self._rmi(msg)


    def _map_call(self, rcvrs, method_name, args, kwargs):
        msg = ("_map_call", rcvrs, method_name, args, kwargs)
        return self._rmi(msg)


    def _map_getprop(self, rcvrs, attr_name):
        msg = ("_map_getprop", rcvrs, attr_name)
        return self._rmi(msg)


    #-----------------------------------------------------------------------
    # Write command to the remote server, and read the response
    #-----------------------------------------------------------------------

    def _rmi(self, msg):
        for _ in range(self.retries):
            response = self._do_rmi(msg)
            if not isinstance(response, SystemError):
                return response
            if str(response) != 'Could not queue task':
                return response

            if callable(self.retry_pause):
                self.retry_pause()              # pylint: disable=not-callable

        return self._do_rmi(msg)


    def _do_rmi(self, msg):
        if not self.is_alive():
            raise OSError("Connection has been closed")

        self._write(msg)
        return self._response.get()


    def _write(self, obj):
        buf = self._pickler.dumps(obj)
        self._tx_message(buf)


    def _read(self):
        buf = self._rx_message()
        return self._unpickler.loads(buf)


    def _tx_message(self, msg):
        raise NotImplementedError("Method must be overridden")


    def _rx_message(self):
        raise NotImplementedError("Method must be overridden")


    #===========================================================================
    # Pickler
    #===========================================================================

    class _Pickler(pickle.Pickler):

        def __init__(self):
            file = io.BytesIO()
            super().__init__(file, protocol=4)
            self._file = file
            self.fast = True

        def persistent_id(self, obj): # pylint: disable=missing-function-docstring
            if isinstance(obj, Remotable):
                return obj._pid()             # pylint: disable=protected-access
            return None

        def dumps(self, obj):       # pylint: disable=missing-function-docstring
            self._file.seek(0)
            self.dump(obj)
            self._file.truncate()
            res = self._file.getvalue()
            return res


    #===========================================================================
    # Unpickler
    #===========================================================================

    class _Unpickler(pickle.Unpickler):

        def __init__(self, context):
            file = io.BytesIO()
            super().__init__(file)
            self._file = file
            self._context = context


        def persistent_load(self, pid): # pylint: disable=missing-function-docstring

            if isinstance(pid, tuple):
                module_name, class_name, identity = pid
                module = importlib.import_module(module_name)
                cls = getattr(module, class_name)

                ctx = self._context
                cache = ctx._proxy_cache[cls] # pylint: disable=protected-access

                key = frozenset(identity.items())
                obj = cache.get(key)
                if obj is not None:
                    return obj

                obj = cls(_ctx=ctx, _ident=identity)
                obj._post_init()              # pylint: disable=protected-access

                cache[key] = obj
                return obj

            raise pickle.UnpicklingError(f"Unsupported PID: {pid!r}")


        def loads(self, data):      # pylint: disable=missing-function-docstring
            self._file.seek(0)
            self._file.write(data)
            self._file.truncate()

            self._file.seek(0)
            return self.load()


#===============================================================================
# Socket Context
#===============================================================================

class SocketContext(Context):

    """
    A context object with the communication channel implemented as a TCP/IP
    socket.
    """

    _SIZE_OF_LENGTH = 4


    def __init__(self, sock):
        self._sock = sock

        # Disable Nagling
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        self._rx_len = 4096
        self._rx_view = memoryview(bytearray(self._rx_len))

        super().__init__()


    #-----------------------------------------------------------------------
    # Close & Closed check
    #-----------------------------------------------------------------------

    def is_alive(self) -> bool:
        return self._sock is not None


    def close(self) -> None:
        self._clear_cache()
        try:
            if self._sock is None:
                raise OSError("Connection was already closed")
            self._sock.close()
        finally:
            self._sock = None


    #-----------------------------------------------------------------------
    # Send/Receive
    #-----------------------------------------------------------------------

    def _tx_message(self, msg):
        len_buf = len(msg).to_bytes(self._SIZE_OF_LENGTH, 'big')
        self._sock.sendall(len_buf)
        self._sock.sendall(msg)


    def _rx_message(self):
        msg = self._read_buffer(self._SIZE_OF_LENGTH)
        length = int.from_bytes(msg, 'big')
        msg = self._read_buffer(length)
        return msg


    def _read_buffer(self, length):

        if length > self._rx_len:
            view = memoryview(bytearray(length))
        else:
            view = self._rx_view

        index = 0
        while index < length:
            size = self._sock.recv_into(view[index:length], 0,
                                        socket.MSG_WAITALL)
            if size <= 0:
                raise EOFError("Connection closed by remote")
            index += size

        return view[:index]


#===============================================================================
# Queue Context
#===============================================================================

class QueueContext(Context):

    """
    A context object with the communication channel implemented with a Queue
    """

    def __init__(self, server):
        self._server = server
        self._queue = queue.Queue()
        super().__init__()

    #-----------------------------------------------------------------------
    # Close & Closed check
    #-----------------------------------------------------------------------

    def is_alive(self) -> bool:
        return True


    def close(self) -> None:
        self._clear_cache()


    #-----------------------------------------------------------------------
    # Send/Receive
    #-----------------------------------------------------------------------

    def _tx_message(self, msg):
        self._server._post(msg, self)         # pylint: disable=protected-access


    def _rx_message(self):
        msg = self._queue.get()
        return msg


    def reply(self, reply):
        """Accept a message reply, for client"""
        self._queue.put(reply)
