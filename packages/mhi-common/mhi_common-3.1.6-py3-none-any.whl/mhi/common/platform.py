"""
Windows platform dependnecy utilities. This module is used to limit execution
of some functions/methods to Windows only. Usage:

@windows_only
def this_func_only_runs_on_windows(foo, bar): ...
 """

# ==============================================================================
# Imports
# ==============================================================================
import sys

from functools import wraps
from typing import cast, Any, Callable, TypeVar


F = TypeVar('F', bound=Callable[..., Any])


# ------------------------------------------------------------------------------
# Check OS type
# ------------------------------------------------------------------------------
def is_windows() -> bool:
    """
    Returns true is OS is Windows.
    """

    return sys.platform == 'win32'


# ------------------------------------------------------------------------------
# Decorator to limit execution to Windows only
# ------------------------------------------------------------------------------
def windows_only(function: F) -> F:  # pylint: disable=missing-function-docstring

    @wraps(function)
    def wrapper(*args, **kwargs):

        if not is_windows():
            raise ValueError(f'"{function.__qualname__}" can only be used on '
                             'Windows.')

        return function(*args, **kwargs)

    return cast(F, wrapper)
