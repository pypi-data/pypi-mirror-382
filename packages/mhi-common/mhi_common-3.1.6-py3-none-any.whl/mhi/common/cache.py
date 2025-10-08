"""
Caching
"""

#===============================================================================
# Imports
#===============================================================================

from __future__ import annotations

import sys
from functools import update_wrapper
from time import monotonic
from typing import (overload, cast, Any, Callable, Dict, Generic, Optional,
                    Tuple, Type, TypeVar, Union)

#===============================================================================
# Exports
#===============================================================================

__all__ = ['cached_property', 'timed_cached_property', 'TimedCachedProperty',]


#===============================================================================
# Cached Property (prior to Python 3.8)
#===============================================================================

if sys.version_info >= (3, 8):
    from functools import cached_property
else:
    _NOT_FOUND = object()

    class cached_property: # pylint: disable=invalid-name,too-few-public-methods
        """Adapted from Python 3.8 & 3.12, for use in Python 3.7"""

        def __init__(self, func):

            self.func = func
            self.attrname = None
            update_wrapper(self, func)


        def __set_name__(self, owner, name):

            if self.attrname is None:
                self.attrname = name
            elif name != self.attrname:
                raise TypeError(
                    "Cannot assign the same cached_property to two different names "
                    f"({self.attrname!r} and {name!r})."
                )


        def __get__(self, instance, owner=None):

            if instance is None:
                return self
            if self.attrname is None:
                raise TypeError(
                    "Cannot use cached_property instance without calling __set_name__ on it.")

            try:
                cache = instance.__dict__
            except AttributeError:  # not all objects have __dict__ (e.g. class defines slots)
                msg = (
                    f"No '__dict__' attribute on {type(instance).__name__!r} "
                    f"instance to cache {self.attrname!r} property."
                )
                raise TypeError(msg) from None

            val = cache.get(self.attrname, _NOT_FOUND)
            if val is _NOT_FOUND:
                val = self.func(instance)
                try:
                    cache[self.attrname] = val
                except TypeError:
                    msg = (
                        f"The '__dict__' attribute on {type(instance).__name__!r} instance "
                        f"does not support item assignment for caching {self.attrname!r} property."
                    )
                    raise TypeError(msg) from None

            return val


#===============================================================================
# Timed Cached Property
#===============================================================================

_NO_ENTRY = None, None

Value = TypeVar('Value')

class TimedCachedProperty(Generic[Value]):
    """
    A cached property which will be "recomputed" when requested if the given
    period of time has elapsed since it was last cached.
    """

    _fget: Callable[[Any], Value]
    _fset: Optional[Callable[[Any, Value], Optional[Value]]]
    _name: str
    _life_sec: float

    def __init__(self,
                 prop_or_fget,
                 life_sec: float,
                 fset: Optional[Callable[[Any, Value], Optional[Value]]] = None):

        fget: Callable[[Any], Value]

        if isinstance(prop_or_fget, property):
            fget = cast(Callable[[Any], Value], prop_or_fget.fget)
            fset = fset or prop_or_fget.fset
            doc = prop_or_fget.__doc__
            assert fget is not None
            name = getattr(prop_or_fget, '__name__', fget.__name__)
        elif callable(prop_or_fget):
            fget = prop_or_fget
            doc = prop_or_fget.__doc__
            name = prop_or_fget.__name__
        else:
            raise ValueError("Expected property or setter function")

        if life_sec > 3600:
            interval = f'{life_sec/3600:.1f} hours'
        elif life_sec > 60:
            interval = f'{life_sec/60:.1f} minutes'
        else:
            interval = f'{life_sec:.1f} seconds'

        doc = doc + '\n\n' if doc else ''
        doc += ("When this property is retrieved, it will be cached for\n"
                f"{interval}, and if retrieved again within that time the\n"
                "cached value will be returned.")

        self._fget = fget
        self._fset = fset
        self._life_sec = life_sec
        self._name = f'_{name}_cache'
        self.__doc__ = doc

    def __set_name__(self, owner, name):
        self._name = f'_{name}_cache'

    @property
    def name(self):
        """Name of property which is cached"""
        return self._name[1:-6]

    def _cache(self, instance) -> Tuple[Dict[str, Any], str]:

        key = self._name

        try:
            return instance.__dict__, key
        except AttributeError:  # not all objects have __dict__ (e.g. class defines slots)
            msg = (
                f"No '__dict__' attribute on {type(instance).__name__!r} "
                f"instance to store {self.name!r} property."
            )
            raise TypeError(msg) from None

    def __delete__(self, instance):

        cache, key = self._cache(instance)
        cache.pop(key, None)

    @overload
    def __get__(self,
                instance: None,
                owner: Type[Any]
                ) -> TimedCachedProperty[Value]:
        """Called when an attribute is accessed via class not an instance"""

    @overload
    def __get__(self, instance, owner: Type[Any]) -> Value:
        """Called when an attribute is accessed on an instance variable"""

    def __get__(self,
                instance,
                owner: Type[Any]
                ) -> Union[Value, TimedCachedProperty[Value]]:
        if instance is None:
            return self

        cache, key = self._cache(instance)

        now = monotonic()
        val, expiry = cache.get(key, _NO_ENTRY)
        if expiry is None or now > expiry:
            val = self._fget(instance)
            cache[key] = (val, now + self._life_sec)
        return val

    def __set__(self, instance, value: Value):

        cache, key = self._cache(instance)
        fset = self._fset
        if fset is None:
            raise AttributeError(f"property {self.name!r} of "
                                 f"{instance.__class__.__name__} object "
                                 "has no setter")

        new_value = fset(instance, value)
        if new_value is not None:
            now = monotonic()
            cache[key] = (new_value, now + self._life_sec)
        else:
            cache.pop(key, None)

    def setter(self,
               fset: Callable[[Any, Value], Optional[Value]]):
        """
        Allow the property to be settable
        """

        return self.__class__(self._fget, self._life_sec, fset)


def timed_cached_property(secs: float):
    """
    A cached property which will be "recomputed" when requested if the given
    period of time has elapsed since it was last cached.
    """

    def decorator(func):
        return TimedCachedProperty(func, secs)

    return decorator
