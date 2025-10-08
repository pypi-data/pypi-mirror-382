#!/usr/bin/env python3
#===============================================================================
# MHRC Automation Library - Embedded Script Wrapper
#===============================================================================

"""
MHRC Automation Library - Embedded Script Wrapper

This module is used to start a user script from inside the application.
The user script may be terminated by the main application, such as by a
[Stop] button in the UI.

*** For internal application use only ***
"""

#===============================================================================
# Imports
#===============================================================================

import importlib
import pkgutil
import sys
import threading
import traceback

from ctypes import c_long, py_object, pythonapi
from linecache import clearcache

from .remote import Context


#===============================================================================
# External Script Base
#===============================================================================

class _ExternalScript(threading.Thread):
    """
    A thread object used to run external scripts.
    """

    __slots__ = ('_tid', '_result')

    def __init__(self):
        """
        Constructor
        """
        super().__init__()

        self._tid = 0
        self._result = None

    def result(self):
        """
        Script result, which could be an Exception
        """
        return self._result

    def run(self):
        """
        Identify the thread this runs on, and run the external script
        """
        self._tid = threading.get_ident()
        result = self._run()
        if result is not None:
            app = Context._embedded()         # pylint: disable=protected-access
            pickler = app._context._pickler   # pylint: disable=protected-access
            result = pickler.dumps(result)
        self._result = result


    def _run(self):
        # Re-allow once-only warnings
        globals().pop('__warningregistry__', None)

        try:
            return self._main()
        except BaseException as e:                # pylint: disable=broad-except
            # Report reason for failure, but don't mention our wrapper
            #
            #     File "C:\...\mhi\...\common\_script.py", line 93, in _main
            #       exec(script, module_globals)
            #
            # in the stack trace.
            etype, value, stack = sys.exc_info()
            traceback.print_exception(etype, value, stack.tb_next.tb_next)
            return e

        finally:
            # Ensure any memorized file/line information is forgotten.
            clearcache()

    def _main(self):
        raise ValueError("_main was not overridden")

    def _async_raise(self, exctype=KeyboardInterrupt):
        res = pythonapi.PyThreadState_SetAsyncExc(c_long(self._tid),
                                                  py_object(exctype))
        if res == 0:
            raise ValueError("Invalid thread id")
        if res != 1:
            pythonapi.PyThreadState_SetAsyncExc(c_long(self._tid), None)
            raise SystemError("PyThreadState_SetAsyncExc failed")

    def killScript(self, exctype=KeyboardInterrupt): # pylint: disable=invalid-name
        """
        Interrupt the User Script by injecting an exception into the
        thread
        """

        self._async_raise(exctype)


#===============================================================================
# UserScript
#===============================================================================

class _UserScript(_ExternalScript):
    """
    A user script.
    """

    __slots__ = ('_application', '_script', '_file',)

    def __init__(self, application, script, file="<string>"):
        """
        Constructor

        Parameters:
            application (str): application object name
            script (str): Script to execute
            file (str): Name of the script file
        """
        super().__init__()

        self._application = application
        self._script = script
        self._file = file

    def _main(self):
        child_globals = {
            '__name__': '__main__',
            '__file__': self._file,
            '__package__': None,
            self._application: Context._embedded(), # pylint: disable=protected-access
            }

        code = compile(self._script, self._file, 'exec')
        exec(code, child_globals)                    # pylint: disable=exec-used


#===============================================================================
# User Script Call
#===============================================================================

class _UserScriptCall(_ExternalScript):
    """
    Call a callable object from a external script
    """

    __slots__ = ('_name', '_msg', )

    def __init__(self, name: str, msg: bytes):

        super().__init__()

        self._name = name
        self._msg = msg

    def _main(self):

        if self._name.count(':') != 1:
            raise ValueError(f"Invalid call identifier {self._name!r}."
                             " - must have exactly 1 colon")

        # Attempt to reload the module (but won't reload transitive imports)
        mod_name = self._name[:self._name.index(':')]
        mod = sys.modules.get(mod_name)
        if mod:
            mod = importlib.reload(mod)
            # Re-allow once-only warnings
            mod.__dict__.pop('__warningregistry__', None)

        app = Context._embedded()             # pylint: disable=protected-access
        unpickler = app._context._unpickler   # pylint: disable=protected-access
        args = unpickler.loads(self._msg)

        user_script_function = pkgutil.resolve_name(self._name)
        return user_script_function(*args)
