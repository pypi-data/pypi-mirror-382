"""
Warns Control
"""

import inspect
import warnings

class FuzzyMatchWarning(Warning):
    """
    Warning message for fuzzy matching
    """

def warn(msg, category=UserWarning):
    """
    Show warning message focused on first frame not inside the
    mhi.* package space
    """

    frame = inspect.currentframe()
    traceback = inspect.getouterframes(frame)
    level = 1
    f_info = None

    for level, f_info in enumerate(traceback, 1):
        pkg = f_info.frame.f_globals.get('__package__', '')
        if not pkg or not pkg.startswith("mhi."):
            break
    del traceback
    del f_info
    del frame

    warnings.warn(msg, category, stacklevel=level)
