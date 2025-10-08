#! /usr/bin/env python3

"""
Process launching and querying
"""

#===============================================================================
# Imports
#===============================================================================

import itertools
import ipaddress
import logging
import os
import subprocess
import random
import sys
from typing import Any, Dict, Iterator, List, NamedTuple, Optional, Set, Tuple

import ctypes
import socket
import struct

from .platform import is_windows, windows_only
from .version import Version
from .warnings import warn

if is_windows():
    # Pywin32
    from winreg import EnumKey as _EnumKey
    from winreg import OpenKey as _OpenKey, CloseKey as _CloseKey
    from winreg import QueryValueEx as _QueryValueEx
    from winreg import HKEY_LOCAL_MACHINE as _HKLM, KEY_READ as _KEY_READ
    from winreg import KEY_WOW64_32KEY as _KEY32, KEY_WOW64_64KEY as _KEY64
    from winreg import REG_SZ as _REG_SZ

    import win32con
    import win32com.client
else:
    win32com = object()
    win32con = object()

#===============================================================================
# Pywin32, socket, related window constants, structures
#===============================================================================


_AF_INET = 2
_AF_INET6 = int(socket.AF_INET6)
_UBYTE = ctypes.c_ubyte
_DWORD = ctypes.c_ulong
_ERROR_NO_MORE_ITEMS = 259
_MIB_TCP_STATE_LISTEN = 2
_NULL = ""
_TCP_TABLE_BASIC_ALL = 2
_TCP_TABLE_OWNER_PID_LISTENER = 3


# pylint: disable=too-few-public-methods, missing-class-docstring, invalid-name
# pylint: disable=missing-function-docstring


class AddressPortPid(NamedTuple):
    address: str
    port: int
    pid: int

    @classmethod
    def from_row(cls, row):

        return cls(row.local_address, row.local_port, row.dwOwningPid)

class AddressPortPidApp(NamedTuple):
    address: str
    port: int
    pid: int
    appname: str


class MIB_TCPROW_LH(ctypes.Structure):
    _fields_ = [('dwState', _DWORD),
                ('dwLocalAddr', _DWORD),
                ('dwLocalPort', _DWORD),
                ('dwRemoteAddr', _DWORD),
                ('dwRemotePort', _DWORD)]


class MIB_TCPROW_OWNER_PID(ctypes.Structure):
    _fields_ = [('dwState', _DWORD),
                ('dwLocalAddr', _DWORD),
                ('dwLocalPort', _DWORD),
                ('dwRemoteAddr', _DWORD),
                ('dwRemotePort', _DWORD),
                ('dwOwningPid', _DWORD)]

    @property
    def local_address(self) -> str:
        return socket.inet_ntoa(struct.pack('L', self.dwLocalAddr))

    @property
    def local_port(self) -> int:
        return socket.ntohs(self.dwLocalPort)


class MIB_TCP6ROW_OWNER_PID(ctypes.Structure):
    _fields_ = [('ucLocalAddr', _UBYTE * 16),
                ('dwLocalScopeId', _DWORD),
                ('dwLocalPort', _DWORD),
                ('ucRemoteAddr', _UBYTE * 16),
                ('dwRemoteScopeId', _DWORD),
                ('dwRemotePort', _DWORD),
                ('dwState', _DWORD),
                ('dwOwningPid', _DWORD)]

    @property
    def local_address(self) -> str:
        return str(ipaddress.ip_address(bytes(self.ucLocalAddr)))

    @property
    def local_port(self) -> int:
        return socket.ntohs(self.dwLocalPort)


# pylint: enable=missing-function-docstring
# pylint: enable=too-few-public-methods, missing-class-docstring, invalid-name



#===============================================================================
# Logging
#===============================================================================

_LOG = logging.getLogger(__name__)


#===============================================================================
# WMI Query
#===============================================================================

def _wmi():
    if not hasattr(_wmi, '_cache'):
        obj = win32com.client.GetObject('winmgmts:')
        t_i = obj._oleobj_.GetTypeInfo().GetContainingTypeLib()[0].GetTypeComp() # pylint: disable=protected-access
        flags = (t_i.Bind('wbemFlagReturnImmediately')[1].value |
                 t_i.Bind('wbemFlagForwardOnly')[1].value)
        _wmi._cache = (obj, flags)            # pylint: disable=protected-access

    return _wmi._cache                        # pylint: disable=protected-access

def _query(*props: str, where: Optional[str] = None, kind: type = tuple):

    fields = ', '.join(props)

    query = f"SELECT {fields} FROM Win32_Process"
    if where:
        query += " WHERE " + where
    _LOG.debug("WMI.query: %s", query)

    wmi, flags = _wmi()
    result = wmi.ExecQuery(query, iFlags=flags)

    return [kind(getattr(row, prop) for prop in props) for row in result]


#===============================================================================
# Find processes
#===============================================================================

@windows_only
def process_pids(*names: str) -> List[Tuple[str, int]]:

    """
    Return the process id's of any process with the given executable names.

    Application names may include the ``%`` wildcard.  For example,
    the following query might find both ``SkypeApp.exe`` and
    ``SkypeBackgroundHost.exe``::

        process_ids('skype%.exe')

    Since applications may terminate and can be started at any time,
    the returned value is obsolete immediately upon being returned.

    Parameters:
        *names (str): application filename patterns, without any path.

    Returns:
        List[tuple]: A list of process name & process id pairs
    """

    if len(names) == 1 and isinstance(names[0], (tuple, list)):
        names = names[0]

    where = None
    if names:
        where = " OR ".join(f"Name LIKE {name!r}" for name in names)

    return _query('Name', 'ProcessId', where=where)

@windows_only
def is_running(app_name: str) -> bool:

    """
    Determine if there is an ``app`` process in the list of running processes.

    Application names may include the ``%`` wildcard.  For example,
    the following query might find both ``SkypeApp.exe`` and
    ``SkypeBackgroundHost.exe``::

        is_running('skype%.exe')

    Since applications may terminate and can be started at any time,
    the returned value is obsolete immediately upon being returned.

    Parameters:
        app (str): application filename, without any path.

    Returns:
        bool: `True` if a process can be found, `False` otherwise.
    """

    return len(_query('ProcessId', where=f'Name LIKE {app_name!r}')) > 0


#===============================================================================
# Localhost IP Addresses
#===============================================================================

def host_addresses(host: str) -> Set[str]:
    """
    Convert a host name into one or more IP address (ie, IPv4 & IPv6)
    """

    return {addr[4][0] for addr in socket.getaddrinfo(host, 0)} # type: ignore


def is_local_host(host: str) -> bool:
    """
    Does the given hostname represent the local host?

    Returns True if the given 'host' is a public IP address of the host,
    a loopback address, an IPADDR_ANY-type address, or a symbolic name
    that represents any of these.
    """

    if host in {'', '::1', '127.0.0.1', '::', '0.0.0.0'}:
        return True

    addrs = host_addresses(host)
    if any(ipaddress.ip_address(addr).is_loopback for addr in addrs):
        return True

    if {'::', '0.0.0.0'} & addrs:
        return True

    localhost_addrs = host_addresses(socket.getfqdn())
    if localhost_addrs & addrs:
        return True

    return False


def host_filter(host: str):
    """
    Return a filter function to filter an iterable of ``AddressPortPid`` or
    ``AddressPortPidApp`` listeners against the given host
    """

    addrs = host_addresses(host)
    any_ipv4 = '0.0.0.0' in addrs
    any_ipv6 = '::' in addrs
    ip_versions = {ipaddress.ip_address(addr).version for addr in addrs}
    host_ipv4 = 4 in ip_versions
    host_ipv6 = 6 in ip_versions

    def filter_func(listener):
        if listener.address in addrs:
            return True
        if listener.address == '0.0.0.0' and host_ipv4:
            return True
        if listener.address == '::' and host_ipv6:
            return True

        ipaddr = ipaddress.ip_address(listener.address)
        if ipaddr.version == 4 and any_ipv4:
            return True
        if ipaddr.version == 6 and any_ipv6:
            return True

        return False

    return filter_func


#===============================================================================
# Listening Ports
#===============================================================================

@windows_only
def tcp_ports_in_use() -> Set[int]:
    """
    Find all TCP ports in use

    Returns:
        Set[int]: Set of all ports in use by the TCP protocol
    """

    ip_api = ctypes.windll.iphlpapi

    dw_size = _DWORD(0)
    b_order = 0        # Unordered

    # Get TcpTable dwSize value
    ip_api.GetExtendedTcpTable(_NULL, ctypes.byref(dw_size), b_order,
                               _AF_INET, _TCP_TABLE_BASIC_ALL, 0)

    # Divide the size of buffer by the size of each row to get the
    # approximate number of rows in the table.  If the header is large,
    # or there is a lot of padding, we might end up allocating an extra
    # row or two, but it is OK to have extra.
    max_rows = dw_size.value // ctypes.sizeof(MIB_TCPROW_LH)

    # pylint: disable=too-few-public-methods, missing-class-docstring, invalid-name, attribute-defined-outside-init

    class MIB_TCPTABLE(ctypes.Structure):
        _fields_ = [('dwNumEntries', _DWORD),
                    ('table', MIB_TCPROW_LH * max_rows)]

    tcp_table = MIB_TCPTABLE()
    tcp_table.dwNumEntries = 0

    # pylint: enable=too-few-public-methods, missing-class-docstring, invalid-name, attribute-defined-outside-init

    error = ip_api.GetExtendedTcpTable(ctypes.byref(tcp_table),
                                       ctypes.byref(dw_size), b_order, _AF_INET,
                                       _TCP_TABLE_BASIC_ALL, 0)

    if error:
        ports = set()
        _LOG.warning("Error getting TCP Table: %s", error)

    else:
        ports = set(socket.ntohs(row.dwLocalPort)
                    for row in tcp_table.table[:tcp_table.dwNumEntries])

    return ports

@windows_only
def unused_tcp_port(ports: Optional[range] = None) -> int:
    """
    Find an available TCP ports in the specified range.  If no range is
    given, the dynamic/private range (0xC000--0xFFFF) is used.

    Returns:
        int: an available TCP port
    """

    if ports is None:
        ports = range(49192, 65536)

    valid_range = range(1024, 65536)
    if not ports or ports[0] not in valid_range or ports[-1] not in valid_range:
        raise ValueError("Invalid range")

    used_ports = tcp_ports_in_use()

    # Try ports sequentially
    port_iter = iter(ports)
    if len(ports) > 100:
        # Unless we have a large range, in which case try a few randomly first
        port_iter = itertools.chain(random.sample(ports, 20), port_iter)

    for port in port_iter:
        if port not in used_ports:
            return port

    raise ValueError("No unused TCP port found")


def _listener_ports_by_pid(pid: Tuple[int, ...],
                           family: int,
                           row_class: type) -> List[AddressPortPid]:
    # Loosely based on:
    #   "Using the WIN32 IPHelper API (Python Recipe)"
    #   http://code.activestate.com/recipes/392572/

    ip_api = ctypes.windll.iphlpapi

    dw_size = _DWORD(0)
    b_order = 0        # Unordered

    # Get TcpTable dwSize value
    ip_api.GetExtendedTcpTable(_NULL, ctypes.byref(dw_size), b_order,
                               family, _TCP_TABLE_OWNER_PID_LISTENER, 0)

    # Divide the size of buffer by the size of each row to get the
    # approximate number of rows in the table.  If the header is large,
    # or there is a lot of padding, we might end up allocating an extra
    # row or two, but it is OK to have extra.
    max_rows = dw_size.value // ctypes.sizeof(row_class)

    # pylint: disable=too-few-public-methods, missing-class-docstring, invalid-name, attribute-defined-outside-init

    class MIB_TCPTABLE_OWNER_PID(ctypes.Structure):
        _fields_ = [('dwNumEntries', _DWORD),
                    ('table', row_class * max_rows)] # type: ignore

    tcp_table = MIB_TCPTABLE_OWNER_PID()
    tcp_table.dwNumEntries = 0

    # pylint: enable=too-few-public-methods, missing-class-docstring, invalid-name, attribute-defined-outside-init

    error = ip_api.GetExtendedTcpTable(ctypes.byref(tcp_table),
                                       ctypes.byref(dw_size), b_order, family,
                                       _TCP_TABLE_OWNER_PID_LISTENER, 0)

    if error:
        ports = []
        _LOG.warning("Error getting TCP Table: %s", error)

    else:
        ports = [AddressPortPid.from_row(row)
                 for row in tcp_table.table[:tcp_table.dwNumEntries]
                 if (row.dwState == _MIB_TCP_STATE_LISTEN and
                     row.dwOwningPid in pid)]

    return ports

@windows_only
def listener_ports_by_pid(*pid: int) -> List[AddressPortPid]:
    """
    Find all listener ports opened by processes with the given PIDs.

    Since applications may terminate and can be started at any time,
    as well as open and close ports at any time,
    the returned value is obsolete immediately upon being returned.

    Parameters:
        *pid (int): Process ids

    Returns:
        List[tuple]: a list of (addr, port, pid) tuples
    """

    ports = _listener_ports_by_pid(pid, _AF_INET, MIB_TCPROW_OWNER_PID)
    ports += _listener_ports_by_pid(pid, _AF_INET6, MIB_TCP6ROW_OWNER_PID)

    return ports

@windows_only
def listener_ports_by_name(*names: str) -> List[AddressPortPidApp]:

    """
    Find all listener ports opened by processes with the given executable name.

    Application names may include the ``%`` wildcard.  For example,
    the following query might find both listener ports opened by both
    ``SkypeApp.exe`` and ``SkypeBackgroundHost.exe``::

        listener_ports_by_name('skype%.exe')

    Since applications may terminate and can be started at any time,
    as well as open and close ports at any time,
    the returned value is obsolete immediately upon being returned.

    Parameters:
        *names (str): application filename patterns, without any path.

    Returns:
        List[tuple]: a list of (addr, port, pid, name) tuples
    """

    name_by_pid = {pid: name for name, pid in process_pids(*names)}

    ports = [AddressPortPidApp(addr, port, pid, name_by_pid[pid])
             for addr, port, pid in listener_ports_by_pid(*name_by_pid.keys())]

    return ports


#===============================================================================
# Launch processes
#===============================================================================

def _subkeys(key) -> Iterator[str]:

    i = 0
    while True:
        try:
            yield _EnumKey(key, i) # pylint: disable=possibly-used-before-assignment
            i += 1
        except OSError as ex:
            if ex.winerror == _ERROR_NO_MORE_ITEMS: # type: ignore
                break
            raise


def _app_path(app_name: str) -> Tuple[Dict[str, str],Dict[str, str]]:
    # pylint: disable=possibly-used-before-assignment

    app_paths = []

    company_names = ['Manitoba HVDC Research Centre Inc',
                     'Manitoba Hydro International']

    for access in (_KEY32, _KEY64): # pylint: disable=too-many-nested-blocks
        paths = {}
        for company_name in company_names:
            keyname = rf'SOFTWARE\{company_name}\{app_name}'

            try:
                key = _OpenKey(_HKLM, keyname, 0, access | _KEY_READ)
                for ver in _subkeys(key):
                    subkey = _OpenKey(key, ver)
                    try:
                        app_path = _QueryValueEx(subkey, 'AppPath')
                        if app_path[1] == _REG_SZ:
                            paths[ver] = app_path[0]
                    except FileNotFoundError:
                        pass
                    _CloseKey(subkey)
                _CloseKey(key)
            except FileNotFoundError:
                pass
        app_paths.append(paths)

    return app_paths[0], app_paths[1]


def _exe_path(app_name: str) -> Tuple[Dict[str, str],Dict[str, str]]:

    exe_paths = []

    for app_paths in _app_path(app_name):
        paths = {}

        for version, path in app_paths.items():
            exe = os.path.join(path, app_name + '.exe')
            if os.path.isfile(exe):
                paths[version] = exe
            else:
                for ver in ('Alpha', 'Beta', 'Free', version):
                    exe = os.path.join(path, app_name + ver + '.exe')
                    if os.path.isfile(exe):
                        paths[version] = exe
                        break

        exe_paths.append(paths)

    return exe_paths[0], exe_paths[1]

@windows_only
def versions(app_name: str) -> List[Tuple[str, bool]]:
    """
    Find the installed versions of an MHI application.

    Returns:
        List[Tuple]: List of tuples of version and bit-size
    """

    versions32, versions64 = _exe_path(app_name)

    versions_all = [(version, True) for version in versions64]
    for version in versions32:
        versions_all.append((version, False))

    return versions_all

@windows_only
def find_exe(app_name: str,     # pylint: disable=too-many-arguments,too-many-positional-arguments
             version: Optional[str] = None, x64: Optional[bool] = None,
             minimum: Optional[str] = None, maximum: Optional[str] = None,
             allow_alpha: bool = False, allow_beta: bool = False
             ) -> Optional[str]:
    """
    Find an MHI application executable.

    If no ``version`` is specified, the highest version available is used,
    with Alpha and Beta versions being considered the highest and second
    highest respectively.
    If no ``x64`` flag is given, a 32-bit or 64-bit version may be returned,
    with preference given to 64-bit versions.

    Parameters:
        app (str): name of the application (without any extension)
        version (str): application version such as '5.0.1' or '5.1 (Beta)'
        x64 (bool): ``True`` for 64-bit version, ``False`` for 32-bit version
        minimum (str): The lowest allowable version, such as '5.0'
        maximum (str): The highest allowable version, such as '5.0.9'

    Returns:
        str: the path to the executable

    .. versionadded:: 2.1
        ``minimum``, ``maximum``, ``allow_alpha`` & ``allow_beta`` parameters.
    .. versionchanged:: 2.4.5
        ``allow_alpha``, ``allow_beta`` parameters are no longer supported.
    .. versionchanged:: 3.0.3
        ``allow_beta`` parameter is once again supported.
    """

    if allow_alpha:
        warn("allow_alpha is no longer supported and will be removed",
             DeprecationWarning)

    versions32, versions64 = _exe_path(app_name)


    # Select the 32 or 64 bit dictionaries, or merge the two dictionaries
    if x64 is not None:
        all_versions = versions64 if x64 else versions32
    else:
        all_versions = dict(versions32, **versions64)

    # If an explicit version is given, select it.
    if version is not None:
        return all_versions.get(version, None)

    # Filter out any non-standard versions (Alpha, Free, ...)
    filtered = {Version(ver): exe_path for ver, exe_path in all_versions.items()
                if Version.valid(ver)}

    # Filter out beta versions, if not allowed
    if not allow_beta:
        filtered = {ver: exe_path for ver, exe_path in filtered.items()
                    if not ver.beta}

    # Filter any versions outside minimum/maximum limits
    if minimum:
        limit = Version(minimum)
        filtered = {ver: exe_path for ver, exe_path in filtered.items()
                    if ver >= limit}

    if maximum:
        limit = Version(maximum)
        filtered = {ver: exe_path for ver, exe_path in filtered.items()
                    if ver <= limit}

    # Select the highest surviving version
    best_version = max(filtered, default=None)

    if best_version is None:
        return None

    return filtered[best_version]

@windows_only
def launch(*args: str, options: Optional[Dict[str, Any]] = None, **kwargs):

    """
    Launch an application process.

    All ``{keyword}`` format codes in the list of ``args`` strings are
    replaced by the value in the corresponding ``options`` dictionary and/or
    ``kwargs`` key-value argument pairs.

    For example::

        launch("C:\\{dir}\\{name}.exe", "/silent:{silent}", "/title:{title!r}",
               dir="temp", name="app", silent=True, title="Hello world")

    will launch ``C:\\temp\\app.exe`` passing the arguments ``/silent:True``
    and ``/title:'Hello world'``


    Parameters:
        *args (str): the application and the arguments for the application
        options: values which may be substituted in the application arguments
        **kwargs: additional substitution values

    Returns:
        The subprocess handle

    .. table:: Special keyword arguments

        =================== ============================================
        Keyword=Value              Effect
        =================== ============================================
        ``minimize=True``   process started with ``SW_SHOWMINNOACTIVE``
        ``minimize=False``  process started with ``SW_SHOWNOACTIVATE``
        ``debug=True``             process is not started, command line printed
        =================== ============================================
    """

    if not args:
        raise ValueError("An application must be specified")

    if len(args) == 1 and isinstance(args[0], (tuple, list)):
        args = args[0]

    options = dict(options, **kwargs) if options else kwargs
    launch_args = [arg.format(**options) for arg in args]

    if options.get('debug', False):
        print("Awaiting manual launch in debugger", file=sys.stderr)
        print("    args:", " ".join(launch_args[1:]), file=sys.stderr)
        proc = None
    else:
        proc = _launch(launch_args, options)

    return proc

def _launch(args: List[str], options: Dict[str, Any]):

    _LOG.info("Launching %s", args[0])
    _LOG.info("    Args: %s", args[1:])

    # Ensure application crashes don't result in an Error Dialog
    # that needs to be dismissed manually
    ctypes.windll.kernel32.SetErrorMode(win32con.SEM_NOGPFAULTERRORBOX)

    # Start Up Info for the child process
    sui = subprocess.STARTUPINFO()
    minimize = options.get('minimize', None)
    minimize = options.get('launch-minimized', minimize) # Backwards compat
    if minimize is not None:
        if minimize:
            sui.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            sui.wShowWindow = win32con.SW_SHOWMINNOACTIVE

    # Launch the subprocess
    proc = subprocess.Popen(args, close_fds=True, startupinfo=sui) # pylint: disable=consider-using-with
    _LOG.debug("Process ID = %d", proc.pid)

    return proc


#===============================================================================
# Process Report
#===============================================================================

@windows_only
def report(installed=True, minimums=False, running=True, file=sys.stdout):
    """
    Report known, installed MHI products
    """

    fmt = "    {0:<8} = {1}"

    # Show executables for known apps, but it is ok if they aren't installed.
    if installed:
        print("Installed executables", file=file)
        for app in ('PSCAD', 'Enerplot'):
            exe = find_exe(app)
            print(fmt.format(app, exe), file=file)
        print(file=file)

        # Installed executables w/ enforced minimums
        if minimums:
            print("Installed executables (minimum versions)", file=file)
            for app, minimum in {'PSCAD': '5.0', 'Enerplot': '1.1'}.items():
                exe = find_exe(app, minimum=minimum)
                print(fmt.format(app, exe), file=file)
            print(file=file)

    if running:
        print("Running", file=file)
        fmt = "    {0:<39} {1:<5} {2:<5} {3}"
        print(fmt.format("Address", "Port", "PID", "Executable"), file=file)
        for app_name in ('PSCAD%', 'Enerplot%'):
            for data in listener_ports_by_name(app_name):
                print(fmt.format(*data), file=file)
        print(file=file)


#===============================================================================
# CLI Utility
#===============================================================================

if __name__ == '__main__':
    report()
