"""
The `mhi.common` library is a package of common functions, which facilitate
the automation of various MHI applications from Python scripts.

This package is not intended to be used directly.  It will be used
internally by the application specific packages.
"""

#===============================================================================
# Script Version Identifiers
#===============================================================================

_VERSION = (3, 1, 6)

_TYPE = 'f0'

VERSION = '.'.join(map(str, _VERSION))
VERSION_HEX = int.from_bytes((*_VERSION, int(_TYPE, 16)), byteorder='big')

__all__ = [] # type: ignore

def version_msg():
    """
    Common Library Version Message
    """

    return (f"MHI Common Library v{VERSION}\n"
            "(c) Manitoba Hydro International Ltd.")
