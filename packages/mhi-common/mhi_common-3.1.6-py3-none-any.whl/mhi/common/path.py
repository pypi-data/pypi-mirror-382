#! /usr/bin/env python3
"""
Conversion between pathnames with and without expanded %ENVIRONMENT_VARIABLES%.
"""

import os
from pathlib import Path, PurePath
from typing import Dict, List, Optional, Sequence, Union

from .platform import is_windows, windows_only

if is_windows():
    import winreg

#===============================================================================
# When run from IDLE, if the HOME environment is not set, Tkinter is setting it
# to %HOMEDRIVE%%HOMEPATH% ... which can be wrong under Windows.
#    https://bugs.python.org/issue27263
# Attempt to detect and restore to correct default
#===============================================================================

if os.name == 'nt':
    import sys
    if 'idlelib' in sys.modules:
        if os.getenv('HOME') == os.getenv('HOMEDRIVE', '') + os.getenv('HOMEPATH', ''):
            try:
                os.environ['HOME'] = os.getenv('USERPROFILE', '')
            except KeyError:
                del os.environ['HOME']


#===============================================================================
# Expand Path
#===============================================================================

def expand_path(path: Union[str, PurePath], abspath: bool = False,
                folder: Optional[Union[str, PurePath]] = None) -> str:
    """
    Expand ``path``, by replacing a `~` or `~user` prefix, as well as
    expanding any `$var`, `${var}` and `%var%` patterns in the path.

    Parameters:
        path (str): The path to be expanded.
        abspath (bool): If `True`, convert resulting path to an absolute path.
        folder (str): If provided, the path to the filename is resolved
            relative to this folder.

    Returns:
        str: The expanded ``path``, optionally forced to an absolute path.
    """

    if folder:
        path = os.path.join(folder, path)

    path = os.path.normpath(os.path.expanduser(os.path.expandvars(path)))
    if abspath:
        path = os.path.abspath(path)

    return path

def expand_paths(paths: Sequence[Union[str, PurePath]], abspath: bool = False,
                 folder: Optional[Union[str, PurePath]] = None) -> List[str]:
    """
    Expand ``paths``, by replacing a `~` or `~user` prefix, as well as
    expanding any `$var`, `${var}` and `%var%` patterns in the paths.

    Parameters:
        path (List[str]): A list of paths to be expanded.
        abspath (bool): If `True`, convert resulting paths to absolute paths.
        folder (str): If provided, the paths to the filenames are resolved
            relative to this folder.

    Returns:
        List[str]: A list of expanded ``paths``, optionally forced to
        absolute paths.
    """

    return [expand_path(path, abspath, folder) for path in paths]


#===============================================================================
# Contract Path
#===============================================================================

def contract_path(path: str, *,             # pylint: disable=too-many-branches
                  keys: Optional[List[str]] = None,
                  reverse_map: Optional[Dict[str, str]] = None) -> str:
    """contract_path(path)

    Look for and replace any substring of the path that matches a value
    found in an environment variable with that environment variable:
    `${key}` or `%key%`.  Additionally, replace a path starting with
    the user's home path with `~`.

    Parameters:
        path (str): The path to be shortened by replacing parts with
           environment variables.

    Returns:
        str: The contracted ``path``.
    """

    keys = keys or []
    reverse_map = reverse_map or {}

    if len(keys) == 0:
        for key, val in os.environ.items():
            if ';' in val:
                continue
            if os.name == 'nt':
                key = f"%{key}%"
            else:
                key = f"${{{key}}}"

            if len(key) < len(val) or key == '%HOME%':
                if val not in reverse_map  or  len(key) < len(reverse_map[val]):
                    reverse_map[val] = key

        keys.extend(sorted(reverse_map.keys(), key=len, reverse=True))

    for text in keys:
        path = path.replace(text, reverse_map[text])

    if path in {"${HOME}", "%HOME%", "${USERPROFILE}", "%USERPROFILE%"}:
        path = "~"
    elif path.startswith("%HOME%\\"):
        path = os.path.join("~", path[7:])
    elif path.startswith("${HOME}/"):
        path = os.path.join("~", path[8:])
    elif path.startswith("%USERPROFILE%\\"):
        path = os.path.join("~", path[14:])
    elif path.startswith("${USERPROFILE}/"):
        path = os.path.join("~", path[15:])

    return os.path.normpath(path)

def contract_paths(paths):
    """
    Look for and replace any substring of the paths that matches a value
    found in an environment variable with that environment variable:
    `${key}` or `%key%`.  Additionally, replace paths starting with
    the user's home path with `~`.

    Parameters:
        paths (List[str]): The paths to be shortened by replacing parts with
           environment variables.

    Returns:
        List[str]: A list of contracted ``paths``.
    """

    return [contract_path(path) for path in paths]


#===============================================================================
# Shell Folders
#===============================================================================

@windows_only
def shell_folder(name: str) -> Path:
    """
    Return the path to a special Windows Shell Folder

    Parameters:
        name (str): The shell folder name

    Returns:
        str: The path, read from the Windows registry
    """

    # pylint: disable=possibly-used-before-assignment

    folders = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"
    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, folders) as key:
        try:
            value, value_type = winreg.QueryValueEx(key, name)
        except WindowsError:
            raise KeyError(f"No such Shell Folder {name!r}") from None

    if value_type == winreg.REG_EXPAND_SZ:
        value = os.path.expandvars(value)
    elif value_type != winreg.REG_SZ:
        raise ValueError(f"Shell Folder {name!r} is not a string")

    return Path(value)
