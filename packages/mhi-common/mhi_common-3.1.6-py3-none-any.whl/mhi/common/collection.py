"""
General purpose utilities
"""

#===============================================================================
# Imports
#===============================================================================

from __future__ import annotations

import itertools
from collections.abc import Hashable
from functools import wraps
from sys import getrefcount
from threading import Thread
from time import sleep
from typing import ClassVar, Dict, Generic, Optional, TypeVar
from weakref import WeakSet


#===============================================================================
# Generic Types
#===============================================================================

KT = TypeVar('KT', bound=Hashable)
VT = TypeVar('VT')


#===============================================================================
# Indexable Dictionary
#===============================================================================

class IndexableDict(Dict[KT, VT]):

    """
    An ordered dictionary, where values can be retrieved by index as well
    as by key, as long as the key is not an int::

        >>> idict = IndexableDict([('foo', 10), ('bar', 30), ('baz', 20)])
        >>> idict['foo'] == idict[0] == idict[-3] == 10
        True
        >>> idict['bar'] == idict[1] == idict[-2] == 30
        True
        >>> idict['baz'] == idict[2] == idict[-1] == 20
        True
    """

    def __getitem__(self, key):
        """
        If `key` is an integer, retrieve the value at that index.
        Otherwise, retrieve the value with the given `key`
        """

        if isinstance(key, int):
            num = len(self)
            if key < -num or key >= num:
                raise IndexError()
            idx = key if key >= 0 else num + key
            return next(itertools.islice(self.values(), idx, idx + 1))

        return super().__getitem__(key)


#===============================================================================
# Lingering Cache
#===============================================================================

class LingeringCache(Generic[KT, VT]):
    """
    A cache of items that evaporates if references are not externally held.

    The items must have a hashable key.

    ``None`` can never be stored in the cache.  Similarly, other immortal
    objects should never be cached.

    - ``cache[key] = obj`` will stores an object in the cache.
    - ``cache[key]`` will retrieve the object, or raise a ``KeyError`` if it has
      expired.
    - ``cache.get(key)`` returns ``None`` if the object has been
      forgotten.
    - ``del cache[key]`` will cause the object to be forgotten, but won't raise
      an exception if it is already lost.
    - ``cache.clear()`` forgets everything.

    No other dictionary methods are implemented.
    """

    _AGE_INTERVAL: ClassVar[float] = 5
    _AGE_LIMIT: ClassVar[float] = 15
    _CACHES: ClassVar[WeakSet[LingeringCache]] = WeakSet()
    _THREAD: ClassVar[Optional[Thread]] = None

    _cache: Dict[KT, _CacheItem]


    @classmethod
    def _start_aging(cls) -> None:
        cls._THREAD = Thread(target=cls._age_all_caches, name='LingeringCache',
                             daemon=True)
        cls._THREAD.start()


    @classmethod
    def _age_all_caches(cls) -> None:
        while True:
            cache = None
            age_inc = cls._AGE_INTERVAL
            sleep(age_inc)
            for cache in cls._CACHES:
                cache._age_cache(age_inc)     # pylint: disable=protected-access


    def __init__(self, age_limit: float = _AGE_LIMIT):

        if self._THREAD is None:
            self._start_aging()

        self._cache = {}
        self._age_limit = age_limit
        self._CACHES.add(self)


    def __setitem__(self, key: KT, value: VT):

        if value is None:
            raise ValueError("None cannot be cached")

        self._cache[key] = _CacheItem(value)


    def __getitem__(self, key: KT) -> VT:

        ci = self._cache[key]
        ci.age = 0

        return ci.item


    def __delitem__(self, key: KT):

        self._cache.pop(key, None)


    def get(self, key: KT) -> Optional[VT]:
        """
        Fetch an item from the cache.

        If it not longer exists, None is returned.
        """

        ci = self._cache.get(key)
        if ci is not None:
            ci.age = 0
            return ci.item

        return None


    def _age_cache(self, age_inc):

        cache = self._cache
        age_limit = self._age_limit

        for key, ci in list(cache.items()):
            if ci.in_use:
                ci.age = 0
            else:
                ci.age += age_inc
                if ci.age > age_limit:
                    del cache[key]


    def clear(self) -> None:
        """
        Forget all values in the cache
        """

        self._cache.clear()


    def __repr__(self):
        keys = ', '.join(f'{key}={ci.age}' for key, ci in self._cache.items())
        return f'LingeringCache[{keys}]'


#-------------------------------------------------------------------------------
# Cache item (with age)
#-------------------------------------------------------------------------------

class _CacheItem(Generic[VT]):          # pylint: disable=too-few-public-methods
    """
    The cached item, along with the age of the item
    """

    __slots__ = 'item', 'age'

    # An object not referenced anywhere but this cache will have a reference
    # count of 2: 1 for this class, and 1 temporary reference passed to the
    # sys.getrefcount(obj) call.  Exceeding this value indicates a strong
    # reference to it exists elsewhere.
    _IN_USE_THRESHOLD = 2


    def __init__(self, item: VT):
        self.item = item
        self.age = 0


    @property
    def in_use(self) -> bool:
        """
        Are there external, strong references to this item?
        """

        refs = getrefcount(self.item)
        return refs > self._IN_USE_THRESHOLD


#-------------------------------------------------------------------------------
# Method decorator
#-------------------------------------------------------------------------------

def lingering_cache(method):
    """
    Decorator for a method which creates a caching version of the method.

    The method must take one argument besides `self`, which is the `key`
    for the item, and looks up the item in the function's cache.
    If not found, the function is called as normal and the returned value
    is stored in the cache.

    The cached items evaporate over time if external references to the
    returned values are not kept.
    """

    @wraps(method)
    def wrapper(self, key, _cache_name=f'_{method.__name__}_cache'):

        cache = getattr(self, _cache_name, None)
        if cache is None:
            cache = LingeringCache()
            setattr(self, _cache_name, cache)

        item = cache.get(key)
        if item is None:
            item = method(self, key)
            if item is not None:
                cache[key] = item

        return item

    return wrapper
