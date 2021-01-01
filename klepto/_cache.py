#!/usr/bin/env python
#
# code inspired by Raymond Hettinger's LFU and LRU cache decorators
# on http://code.activestate.com/recipes/498245-lru-and-lfu-cache-decorators
# and subsequent forks as well as the version available in python3.3
#
# Author: Mike McKerns (mmckerns @caltech and @uqfoundation)
# Copyright (c) 2013-2016 California Institute of Technology.
# Copyright (c) 2016-2021 The Uncertainty Quantification Foundation.
# License: 3-clause BSD.  The full license text is available at:
#  - https://github.com/uqfoundation/klepto/blob/master/LICENSE
"""
a selection of caching decorators
"""
from functools import update_wrapper, partial
from klepto.archives import cache as archive_dict
from klepto.keymaps import hashmap
from klepto.tools import CacheInfo
from klepto.rounding import deep_round, simple_round
from ._inspect import _keygen

__all__ = ['no_cache','inf_cache','lfu_cache',\
           'lru_cache','mru_cache','rr_cache']

class Counter(dict):
    'Mapping where default values are zero'
    def __missing__(self, key):
        return 0

#XXX: what about caches that expire due to time, calls, etc...
#XXX: check the impact of not serializing by default, and hashmap by default

class no_cache(object):
    """empty (NO) cache decorator.

    Unlike other cache decorators, this decorator does not cache.  It is a
    dummy that collects statistics and conforms to the caching interface.  This
    decorator takes an integer tolerance 'tol', equal to the number of decimal
    places to which it will round off floats, and a bool 'deep' for whether the
    rounding on inputs will be 'shallow' or 'deep'.  Note that rounding is not
    applied to the calculation of new results, but rather as a simple form of
    cache interpolation.  For example, with tol=0 and a cached value for f(3.0),
    f(3.1) will lookup f(3.0) in the cache while f(3.6) will store a new value;
    however if tol=1, both f(3.1) and f(3.6) will store new values.

    maxsize = maximum cache size [fixed at maxsize=0]
    cache = storage hashmap (default is {})
    keymap = cache key encoder (default is keymaps.hashmap(flat=True))
    ignore = function argument names and indicies to 'ignore' (default is None)
    tol = integer tolerance for rounding (default is None)
    deep = boolean for rounding depth (default is False, i.e. 'shallow')
    purge = boolean for purge cache to archive at maxsize (fixed at True)

    If *keymap* is given, it will replace the hashing algorithm for generating
    cache keys.  Several hashing algorithms are available in 'keymaps'. The
    default keymap requires arguments to the cached function to be hashable.

    If the keymap retains type information, then arguments of different types
    will be cached separately.  For example, f(3.0) and f(3) will be treated
    as distinct calls with distinct results.  Cache typing has a memory penalty,
    and may also be ignored by some 'keymaps'.  Here, the keymap is only used
    to look up keys in an associated archive.

    If *ignore* is given, the keymap will ignore the arguments with the names
    and/or positional indicies provided. For example, if ignore=(0,), then
    the key generated for f(1,2) will be identical to that of f(3,2) or f(4,2).
    If ignore=('y',), then the key generated for f(x=3,y=4) will be identical
    to that of f(x=3,y=0) or f(x=3,y=10). If ignore=('*','**'), all varargs
    and varkwds will be 'ignored'.  Ignored arguments never trigger a
    recalculation (they only trigger cache lookups), and thus are 'ignored'.
    When caching class methods, it may be useful to ignore=('self',).

    View cache statistics (hit, miss, load, maxsize, size) with f.info().
    Clear the cache and statistics with f.clear().  Replace the cache archive
    with f.archive(obj).  Load from the archive with f.load(), and dump from
    the cache to the archive with f.dump().
    """
    def __init__(self, maxsize=0, cache=None, keymap=None, ignore=None, tol=None, deep=False, purge=True):
       #if maxsize is not 0: raise ValueError('maxsize cannot be set')
        maxsize = 0 #XXX: allow maxsize to be given but ignored ?
        purge = True #XXX: allow purge to be given but ignored ?
        if cache is None: cache = archive_dict()
        elif type(cache) is dict: cache = archive_dict(cache)

        if keymap is None: keymap = hashmap(flat=True)
        if ignore is None: ignore = tuple()

        if deep: rounded = deep_round
        else: rounded = simple_round
       #else: rounded = shallow_round #FIXME: slow

        @rounded(tol)
        def rounded_args(*args, **kwds):
            return (args, kwds)

        # set state
        self.__state__ = {
            'maxsize': maxsize,
            'cache': cache,
            'keymap': keymap,
            'ignore': ignore,
            'roundargs': rounded_args,
            'tol': tol,
            'deep': deep,
            'purge': purge,
        }
        return

    def __call__(self, user_function):
       #cache = dict()                  # mapping of args to results
        stats = [0, 0, 0]               # make statistics updateable non-locally
        HIT, MISS, LOAD = 0, 1, 2       # names for the stats fields
        _len = len                      # localize the global len() function
       #lock = RLock()                  # linkedlist updates aren't threadsafe
        maxsize = self.__state__['maxsize']
        cache = self.__state__['cache']
        keymap = self.__state__['keymap']
        ignore = self.__state__['ignore']
        rounded_args = self.__state__['roundargs']

        def wrapper(*args, **kwds):
            _args, _kwds = rounded_args(*args, **kwds)
            _args, _kwds = _keygen(user_function, ignore, *_args, **_kwds)
            key = keymap(*_args, **_kwds)

            # look in archive
            if cache.archived():
                cache.load(key)
            try:
                result = cache[key]
                cache.clear()
                stats[LOAD] += 1
            except KeyError:
                # if not found, then compute
                result = user_function(*args, **kwds)
                cache[key] = result
                stats[MISS] += 1

            # purge cache
            if _len(cache) > maxsize:
                #XXX: better: if cache is cache.archive ?
                if cache.archived():
                    cache.dump()
                cache.clear() 
            return result

        def archive(obj):
            """Replace the cache archive"""
            if isinstance(obj, archive_dict): cache.archive = obj.archive
            else: cache.archive = obj

        def key(*args, **kwds):
            """Get the cache key for the given *args,**kwds"""
            _args, _kwds = rounded_args(*args, **kwds)
            _args, _kwds = _keygen(user_function, ignore, *_args, **_kwds)
            return keymap(*_args, **_kwds)

        def lookup(*args, **kwds):
            """Get the stored value for the given *args,**kwds"""
            _args, _kwds = rounded_args(*args, **kwds)
            _args, _kwds = _keygen(user_function, ignore, *_args, **_kwds)
            return cache[keymap(*_args, **_kwds)]

        def __get_cache():
            """Get the cache"""
            return cache

        def __get_mask():
            """Get the (ignore) mask"""
            return ignore

        def __get_keymap():
            """Get the keymap"""
            return keymap

        def clear(keepstats=False):
            """Clear the cache and statistics"""
            if not keepstats: stats[:] = [0, 0, 0]

        def info():
            """Report cache statistics"""
            return CacheInfo(stats[HIT], stats[MISS], stats[LOAD], maxsize, len(cache))

        # interface
        wrapper.__wrapped__ = user_function
        #XXX: better is handle to key_function=keygen(ignore)(user_function) ?
        wrapper.info = info
        wrapper.clear = clear
        wrapper.load = cache.load
        wrapper.dump = cache.dump
        wrapper.archive = archive
        wrapper.archived = cache.archived
        wrapper.key = key
        wrapper.lookup = lookup
        wrapper.__cache__ = __get_cache
        wrapper.__mask__ = __get_mask
        wrapper.__map__ = __get_keymap
       #wrapper._queue = None  #XXX
        return update_wrapper(wrapper, user_function)

    def __get__(self, obj, objtype):
        """support instance methods"""
        return partial(self.__call__, obj)

    def __reduce__(self):
        cache = self.__state__['cache']
        keymap = self.__state__['keymap']
        ignore = self.__state__['ignore']
        tol = self.__state__['tol']
        deep = self.__state__['deep']
        return (self.__class__, (0, cache, keymap, ignore, tol, deep, True))


class inf_cache(object):
    """infinitely-growing (INF) cache decorator.

    This decorator memoizes a function's return value each time it is called.
    If called later with the same arguments, the cached value is returned, and
    not re-evaluated.  This cache will grow without bound.  To avoid memory
    issues, it is suggested to frequently dump and clear the cache.  This
    decorator takes an integer tolerance 'tol', equal to the number of decimal
    places to which it will round off floats, and a bool 'deep' for whether the
    rounding on inputs will be 'shallow' or 'deep'.  Note that rounding is not
    applied to the calculation of new results, but rather as a simple form of
    cache interpolation.  For example, with tol=0 and a cached value for f(3.0),
    f(3.1) will lookup f(3.0) in the cache while f(3.6) will store a new value;
    however if tol=1, both f(3.1) and f(3.6) will store new values.

    maxsize = maximum cache size [fixed at maxsize=None]
    cache = storage hashmap (default is {})
    keymap = cache key encoder (default is keymaps.hashmap(flat=True))
    ignore = function argument names and indicies to 'ignore' (default is None)
    tol = integer tolerance for rounding (default is None)
    deep = boolean for rounding depth (default is False, i.e. 'shallow')
    purge = boolean for purge cache to archive at maxsize (fixed at False)

    If *keymap* is given, it will replace the hashing algorithm for generating
    cache keys.  Several hashing algorithms are available in 'keymaps'. The
    default keymap requires arguments to the cached function to be hashable.

    If the keymap retains type information, then arguments of different types
    will be cached separately.  For example, f(3.0) and f(3) will be treated
    as distinct calls with distinct results.  Cache typing has a memory penalty,
    and may also be ignored by some 'keymaps'.

    If *ignore* is given, the keymap will ignore the arguments with the names
    and/or positional indicies provided. For example, if ignore=(0,), then
    the key generated for f(1,2) will be identical to that of f(3,2) or f(4,2).
    If ignore=('y',), then the key generated for f(x=3,y=4) will be identical
    to that of f(x=3,y=0) or f(x=3,y=10). If ignore=('*','**'), all varargs
    and varkwds will be 'ignored'.  Ignored arguments never trigger a
    recalculation (they only trigger cache lookups), and thus are 'ignored'.
    When caching class methods, it may be useful to ignore=('self',).

    View cache statistics (hit, miss, load, maxsize, size) with f.info().
    Clear the cache and statistics with f.clear().  Replace the cache archive
    with f.archive(obj).  Load from the archive with f.load(), and dump from
    the cache to the archive with f.dump().
    """
    def __init__(self, maxsize=None, cache=None, keymap=None, ignore=None, tol=None, deep=False, purge=False):
       #if maxsize is not None: raise ValueError('maxsize cannot be set')
        maxsize = None #XXX: allow maxsize to be given but ignored ?
        purge = False #XXX: allow purge to be given but ignored ?
        if cache is None: cache = archive_dict()
        elif type(cache) is dict: cache = archive_dict(cache)

        if keymap is None: keymap = hashmap(flat=True)
        if ignore is None: ignore = tuple()

        if deep: rounded = deep_round
        else: rounded = simple_round
       #else: rounded = shallow_round #FIXME: slow

        @rounded(tol)
        def rounded_args(*args, **kwds):
            return (args, kwds)

        # set state
        self.__state__ = {
            'maxsize': maxsize,
            'cache': cache,
            'keymap': keymap,
            'ignore': ignore,
            'roundargs': rounded_args,
            'tol': tol,
            'deep': deep,
            'purge': purge,
        }
        return

    def __call__(self, user_function):
       #cache = dict()                  # mapping of args to results
        stats = [0, 0, 0]               # make statistics updateable non-locally
        HIT, MISS, LOAD = 0, 1, 2       # names for the stats fields
       #_len = len                      # localize the global len() function
       #lock = RLock()                  # linkedlist updates aren't threadsafe
        maxsize = self.__state__['maxsize']
        cache = self.__state__['cache']
        keymap = self.__state__['keymap']
        ignore = self.__state__['ignore']
        rounded_args = self.__state__['roundargs']

        def wrapper(*args, **kwds):
            _args, _kwds = rounded_args(*args, **kwds)
            _args, _kwds = _keygen(user_function, ignore, *_args, **_kwds)
            key = keymap(*_args, **_kwds)

            try:
                # get cache entry
                result = cache[key]
                stats[HIT] += 1
            except KeyError:
                # if not in cache, look in archive
                if cache.archived():
                    cache.load(key)
                try:
                    result = cache[key]
                    stats[LOAD] += 1
                except KeyError:
                    # if not found, then compute
                    result = user_function(*args, **kwds)
                    cache[key] = result
                    stats[MISS] += 1
            return result

        def archive(obj):
            """Replace the cache archive"""
            if isinstance(obj, archive_dict): cache.archive = obj.archive
            else: cache.archive = obj

        def key(*args, **kwds):
            """Get the cache key for the given *args,**kwds"""
            _args, _kwds = rounded_args(*args, **kwds)
            _args, _kwds = _keygen(user_function, ignore, *_args, **_kwds)
            return keymap(*_args, **_kwds)

        def lookup(*args, **kwds):
            """Get the stored value for the given *args,**kwds"""
            _args, _kwds = rounded_args(*args, **kwds)
            _args, _kwds = _keygen(user_function, ignore, *_args, **_kwds)
            return cache[keymap(*_args, **_kwds)]

        def __get_cache():
            """Get the cache"""
            return cache

        def __get_mask():
            """Get the (ignore) mask"""
            return ignore

        def __get_keymap():
            """Get the keymap"""
            return keymap

        def clear(keepstats=False):
            """Clear the cache and statistics"""
            cache.clear()
            if not keepstats: stats[:] = [0, 0, 0]

        def info():
            """Report cache statistics"""
            return CacheInfo(stats[HIT], stats[MISS], stats[LOAD], maxsize, len(cache))

        # interface
        wrapper.__wrapped__ = user_function
        #XXX: better is handle to key_function=keygen(ignore)(user_function) ?
        wrapper.info = info
        wrapper.clear = clear
        wrapper.load = cache.load
        wrapper.dump = cache.dump
        wrapper.archive = archive
        wrapper.archived = cache.archived
        wrapper.key = key
        wrapper.lookup = lookup
        wrapper.__cache__ = __get_cache
        wrapper.__mask__ = __get_mask
        wrapper.__map__ = __get_keymap
       #wrapper._queue = None  #XXX
        return update_wrapper(wrapper, user_function)

    def __get__(self, obj, objtype):
        """support instance methods"""
        return partial(self.__call__, obj)

    def __reduce__(self):
        cache = self.__state__['cache']
        keymap = self.__state__['keymap']
        ignore = self.__state__['ignore']
        tol = self.__state__['tol']
        deep = self.__state__['deep']
        return (self.__class__, (None, cache, keymap, ignore, tol, deep, False))


class lfu_cache(object):
    """least-frequenty-used (LFU) cache decorator.

    This decorator memoizes a function's return value each time it is called.
    If called later with the same arguments, the cached value is returned, and
    not re-evaluated.  To avoid memory issues, a maximum cache size is imposed.
    For caches with an archive, the full cache dumps to archive upon reaching
    maxsize. For caches without an archive, the LFU algorithm manages the cache.
    Caches with an archive will use the latter behavior when 'purge' is False.
    This decorator takes an integer tolerance 'tol', equal to the number of
    decimal places to which it will round off floats, and a bool 'deep' for
    whether the rounding on inputs will be 'shallow' or 'deep'.  Note that
    rounding is not applied to the calculation of new results, but rather as a
    simple form of cache interpolation.  For example, with tol=0 and a cached
    value for f(3.0), f(3.1) will lookup f(3.0) in the cache while f(3.6) will
    store a new value; however if tol=1, both f(3.1) and f(3.6) will store
    new values.

    maxsize = maximum cache size
    cache = storage hashmap (default is {})
    keymap = cache key encoder (default is keymaps.hashmap(flat=True))
    ignore = function argument names and indicies to 'ignore' (default is None)
    tol = integer tolerance for rounding (default is None)
    deep = boolean for rounding depth (default is False, i.e. 'shallow')
    purge = boolean for purge cache to archive at maxsize (default is False)

    If *maxsize* is None, this cache will grow without bound.

    If *keymap* is given, it will replace the hashing algorithm for generating
    cache keys.  Several hashing algorithms are available in 'keymaps'. The
    default keymap requires arguments to the cached function to be hashable.

    If the keymap retains type information, then arguments of different types
    will be cached separately.  For example, f(3.0) and f(3) will be treated
    as distinct calls with distinct results.  Cache typing has a memory penalty,
    and may also be ignored by some 'keymaps'.

    If *ignore* is given, the keymap will ignore the arguments with the names
    and/or positional indicies provided. For example, if ignore=(0,), then
    the key generated for f(1,2) will be identical to that of f(3,2) or f(4,2).
    If ignore=('y',), then the key generated for f(x=3,y=4) will be identical
    to that of f(x=3,y=0) or f(x=3,y=10). If ignore=('*','**'), all varargs
    and varkwds will be 'ignored'.  Ignored arguments never trigger a
    recalculation (they only trigger cache lookups), and thus are 'ignored'.
    When caching class methods, it may be useful to ignore=('self',).

    View cache statistics (hit, miss, load, maxsize, size) with f.info().
    Clear the cache and statistics with f.clear().  Replace the cache archive
    with f.archive(obj).  Load from the archive with f.load(), and dump from
    the cache to the archive with f.dump().

    See: http://en.wikipedia.org/wiki/Cache_algorithms#Least_Frequently_Used
    """
    def __new__(cls, *args, **kwds):
        maxsize = kwds.get('maxsize', -1)
        if maxsize == 0:
            return no_cache(*args, **kwds)
        if maxsize is None:
            return inf_cache(*args, **kwds)
        return object.__new__(cls)

    def __init__(self, maxsize=100, cache=None, keymap=None, ignore=None, tol=None, deep=False, purge=False):
        if maxsize is None or maxsize == 0:
            return
        if cache is None: cache = archive_dict()
        elif type(cache) is dict: cache = archive_dict(cache)

        if keymap is None: keymap = hashmap(flat=True)
        if ignore is None: ignore = tuple()

        if deep: rounded = deep_round
        else: rounded = simple_round
       #else: rounded = shallow_round #FIXME: slow

        @rounded(tol)
        def rounded_args(*args, **kwds):
            return (args, kwds)

        # set state
        self.__state__ = {
            'maxsize': maxsize,
            'cache': cache,
            'keymap': keymap,
            'ignore': ignore,
            'roundargs': rounded_args,
            'tol': tol,
            'deep': deep,
            'purge': purge,
        }
        return

    def __call__(self, user_function):
        from heapq import nsmallest
        from operator import itemgetter
       #cache = dict()                  # mapping of args to results
        use_count = Counter()           # times each key has been accessed
        stats = [0, 0, 0]               # make statistics updateable non-locally
        HIT, MISS, LOAD = 0, 1, 2       # names for the stats fields
        _len = len                      # localize the global len() function
       #lock = RLock()                  # linkedlist updates aren't threadsafe
        maxsize = self.__state__['maxsize']
        cache = self.__state__['cache']
        keymap = self.__state__['keymap']
        ignore = self.__state__['ignore']
        rounded_args = self.__state__['roundargs']
        purge = self.__state__['purge']

        def wrapper(*args, **kwds):
            _args, _kwds = rounded_args(*args, **kwds)
            _args, _kwds = _keygen(user_function, ignore, *_args, **_kwds)
            key = keymap(*_args, **_kwds)

            try:
                # get cache entry
                result = cache[key]
                use_count[key] += 1
                stats[HIT] += 1
            except KeyError:
                # if not in cache, look in archive
                if cache.archived():
                    cache.load(key)
                try:
                    result = cache[key]
                    use_count[key] += 1
                    stats[LOAD] += 1
                except KeyError:
                    # if not found, then compute
                    result = user_function(*args, **kwds)
                    cache[key] = result
                    use_count[key] += 1
                    stats[MISS] += 1

                # purge cache
                if _len(cache) > maxsize:
                    #XXX: better: if cache is cache.archive ?
                    if cache.archived() and purge:
                        cache.dump()
                        cache.clear() 
                        use_count.clear()
                    else: # purge least frequent cache entries
                        for k, _ in nsmallest(max(2, maxsize // 10),
                                              iter(use_count.items()),
                                              key=itemgetter(1)):
                            if cache.archived(): cache.dump(k)
                            try: del cache[k]
                            except KeyError: pass #FIXME: possible less purged
                            use_count.pop(k, None)
            return result

        def archive(obj):
            """Replace the cache archive"""
            if isinstance(obj, archive_dict): cache.archive = obj.archive
            else: cache.archive = obj

        def key(*args, **kwds):
            """Get the cache key for the given *args,**kwds"""
            _args, _kwds = rounded_args(*args, **kwds)
            _args, _kwds = _keygen(user_function, ignore, *_args, **_kwds)
            return keymap(*_args, **_kwds)

        def lookup(*args, **kwds):
            """Get the stored value for the given *args,**kwds"""
            _args, _kwds = rounded_args(*args, **kwds)
            _args, _kwds = _keygen(user_function, ignore, *_args, **_kwds)
            return cache[keymap(*_args, **_kwds)]

        def __get_cache():
            """Get the cache"""
            return cache

        def __get_mask():
            """Get the (ignore) mask"""
            return ignore

        def __get_keymap():
            """Get the keymap"""
            return keymap

        def clear(keepstats=False):
            """Clear the cache and statistics"""
            cache.clear()
            use_count.clear()
            if not keepstats: stats[:] = [0, 0, 0]

        def info():
            """Report cache statistics"""
            return CacheInfo(stats[HIT], stats[MISS], stats[LOAD], maxsize, len(cache))

        # interface
        wrapper.__wrapped__ = user_function
        #XXX: better is handle to key_function=keygen(ignore)(user_function) ?
        wrapper.info = info
        wrapper.clear = clear
        wrapper.load = cache.load
        wrapper.dump = cache.dump
        wrapper.archive = archive
        wrapper.archived = cache.archived
        wrapper.key = key
        wrapper.lookup = lookup
        wrapper.__cache__ = __get_cache
        wrapper.__mask__ = __get_mask
        wrapper.__map__ = __get_keymap
       #wrapper._queue = use_count #XXX
        return update_wrapper(wrapper, user_function)

    def __get__(self, obj, objtype):
        """support instance methods"""
        return partial(self.__call__, obj)

    def __reduce__(self):
        maxsize = self.__state__['maxsize']
        cache = self.__state__['cache']
        keymap = self.__state__['keymap']
        ignore = self.__state__['ignore']
        tol = self.__state__['tol']
        deep = self.__state__['deep']
        purge = self.__state__['purge']
        return (self.__class__, (maxsize, cache, keymap, ignore, tol, deep, purge))


class lru_cache(object):
    """least-recently-used (LRU) cache decorator.

    This decorator memoizes a function's return value each time it is called.
    If called later with the same arguments, the cached value is returned, and
    not re-evaluated.  To avoid memory issues, a maximum cache size is imposed.
    For caches with an archive, the full cache dumps to archive upon reaching
    maxsize. For caches without an archive, the LRU algorithm manages the cache.
    Caches with an archive will use the latter behavior when 'purge' is False.
    This decorator takes an integer tolerance 'tol', equal to the number of
    decimal places to which it will round off floats, and a bool 'deep' for
    whether the rounding on inputs will be 'shallow' or 'deep'.  Note that
    rounding is not applied to the calculation of new results, but rather as a
    simple form of cache interpolation.  For example, with tol=0 and a cached
    value for f(3.0), f(3.1) will lookup f(3.0) in the cache while f(3.6) will
    store a new value; however if tol=1, both f(3.1) and f(3.6) will store
    new values.

    maxsize = maximum cache size
    cache = storage hashmap (default is {})
    keymap = cache key encoder (default is keymaps.hashmap(flat=True))
    ignore = function argument names and indicies to 'ignore' (default is None)
    tol = integer tolerance for rounding (default is None)
    deep = boolean for rounding depth (default is False, i.e. 'shallow')
    purge = boolean for purge cache to archive at maxsize (default is False)

    If *maxsize* is None, this cache will grow without bound.

    If *keymap* is given, it will replace the hashing algorithm for generating
    cache keys.  Several hashing algorithms are available in 'keymaps'. The
    default keymap requires arguments to the cached function to be hashable.

    If the keymap retains type information, then arguments of different types
    will be cached separately.  For example, f(3.0) and f(3) will be treated
    as distinct calls with distinct results.  Cache typing has a memory penalty,
    and may also be ignored by some 'keymaps'.

    If *ignore* is given, the keymap will ignore the arguments with the names
    and/or positional indicies provided. For example, if ignore=(0,), then
    the key generated for f(1,2) will be identical to that of f(3,2) or f(4,2).
    If ignore=('y',), then the key generated for f(x=3,y=4) will be identical
    to that of f(x=3,y=0) or f(x=3,y=10). If ignore=('*','**'), all varargs
    and varkwds will be 'ignored'.  Ignored arguments never trigger a
    recalculation (they only trigger cache lookups), and thus are 'ignored'.
    When caching class methods, it may be useful to ignore=('self',).

    View cache statistics (hit, miss, load, maxsize, size) with f.info().
    Clear the cache and statistics with f.clear().  Replace the cache archive
    with f.archive(obj).  Load from the archive with f.load(), and dump from
    the cache to the archive with f.dump().

    See: http://en.wikipedia.org/wiki/Cache_algorithms#Least_Recently_Used
    """
    def __new__(cls, *args, **kwds):
        maxsize = kwds.get('maxsize', -1)
        if maxsize == 0:
            return no_cache(*args, **kwds)
        if maxsize is None:
            return inf_cache(*args, **kwds)
        return object.__new__(cls)

    def __init__(self, maxsize=100, cache=None, keymap=None, ignore=None, tol=None, deep=False, purge=False):
        if maxsize is None or maxsize == 0:
            return
        if cache is None: cache = archive_dict()
        elif type(cache) is dict: cache = archive_dict(cache)

        if keymap is None: keymap = hashmap(flat=True)
        if ignore is None: ignore = tuple()

        if deep: rounded = deep_round
        else: rounded = simple_round
       #else: rounded = shallow_round #FIXME: slow

        @rounded(tol)
        def rounded_args(*args, **kwds):
            return (args, kwds)

        # set state
        self.__state__ = {
            'maxsize': maxsize,
            'cache': cache,
            'keymap': keymap,
            'ignore': ignore,
            'roundargs': rounded_args,
            'tol': tol,
            'deep': deep,
            'purge': purge,
        }
        return

    def __call__(self, user_function):
        from collections import deque
        try:
            from itertools import filterfalse
        except ImportError:
            from itertools import ifilterfalse as filterfalse
       #cache = dict()                  # mapping of args to results
        queue = deque()                 # order that keys have been used
        refcount = Counter()            # times each key is in the queue
        sentinel = object()             # marker for looping around the queue
        stats = [0, 0, 0]               # make statistics updateable non-locally
        HIT, MISS, LOAD = 0, 1, 2       # names for the stats fields
        _len = len                      # localize the global len() function
       #lock = RLock()                  # linkedlist updates aren't threadsafe
        maxsize = self.__state__['maxsize']
        cache = self.__state__['cache']
        keymap = self.__state__['keymap']
        ignore = self.__state__['ignore']
        rounded_args = self.__state__['roundargs']
        purge = self.__state__['purge']
        maxqueue = maxsize * 10 #XXX: settable? confirm this works as expected

        # lookup optimizations (ugly but fast)
        queue_append, queue_popleft = queue.append, queue.popleft
        queue_appendleft, queue_pop = queue.appendleft, queue.pop

        def wrapper(*args, **kwds):
            _args, _kwds = rounded_args(*args, **kwds)
            _args, _kwds = _keygen(user_function, ignore, *_args, **_kwds)
            key = keymap(*_args, **_kwds)

            try:
                # get cache entry
                result = cache[key]
                # record recent use of this key
                queue_append(key)
                refcount[key] += 1
                stats[HIT] += 1
            except KeyError:
                # if not in cache, look in archive
                if cache.archived():
                    cache.load(key)
                try:
                    result = cache[key]
                    # record recent use of this key
                    queue_append(key)
                    refcount[key] += 1
                    stats[LOAD] += 1
                except KeyError:
                    # if not found, then compute
                    result = user_function(*args, **kwds)
                    cache[key] = result
                    # record recent use of this key
                    queue_append(key)
                    refcount[key] += 1
                    stats[MISS] += 1

                # purge cache
                if _len(cache) > maxsize:
                    #XXX: better: if cache is cache.archive ?
                    if cache.archived() and purge:
                        cache.dump()
                        cache.clear() 
                        queue.clear()
                        refcount.clear()
                    else: # purge least recently used cache entry
                        key = queue_popleft()
                        refcount[key] -= 1
                        while refcount[key]:
                            key = queue_popleft()
                            refcount[key] -= 1
                        if cache.archived(): cache.dump(key)
                        try: del cache[key]
                        except KeyError: pass #FIXME: possible none purged
                        refcount.pop(key, None)

            # periodically compact the queue by eliminating duplicate keys
            # while preserving order of most recent access
            if _len(queue) > maxqueue:
                refcount.clear()
                queue_appendleft(sentinel)
                for key in filterfalse(refcount.__contains__,
                                        iter(queue_pop, sentinel)):
                    queue_appendleft(key)
                    refcount[key] = 1
            return result

        def archive(obj):
            """Replace the cache archive"""
            if isinstance(obj, archive_dict): cache.archive = obj.archive
            else: cache.archive = obj

        def key(*args, **kwds):
            """Get the cache key for the given *args,**kwds"""
            _args, _kwds = rounded_args(*args, **kwds)
            _args, _kwds = _keygen(user_function, ignore, *_args, **_kwds)
            return keymap(*_args, **_kwds)

        def lookup(*args, **kwds):
            """Get the stored value for the given *args,**kwds"""
            _args, _kwds = rounded_args(*args, **kwds)
            _args, _kwds = _keygen(user_function, ignore, *_args, **_kwds)
            return cache[keymap(*_args, **_kwds)]

        def __get_cache():
            """Get the cache"""
            return cache

        def __get_mask():
            """Get the (ignore) mask"""
            return ignore

        def __get_keymap():
            """Get the keymap"""
            return keymap

        def clear(keepstats=False):
            """Clear the cache and statistics"""
            cache.clear()
            queue.clear()
            refcount.clear()
            if not keepstats: stats[:] = [0, 0, 0]

        def info():
            """Report cache statistics"""
            return CacheInfo(stats[HIT], stats[MISS], stats[LOAD], maxsize, len(cache))

        # interface
        wrapper.__wrapped__ = user_function
        #XXX: better is handle to key_function=keygen(ignore)(user_function) ?
        wrapper.info = info
        wrapper.clear = clear
        wrapper.load = cache.load
        wrapper.dump = cache.dump
        wrapper.archive = archive
        wrapper.archived = cache.archived
        wrapper.key = key
        wrapper.lookup = lookup
        wrapper.__cache__ = __get_cache
        wrapper.__mask__ = __get_mask
        wrapper.__map__ = __get_keymap
       #wrapper._queue = queue #XXX
        return update_wrapper(wrapper, user_function)

    def __get__(self, obj, objtype):
        """support instance methods"""
        return partial(self.__call__, obj)

    def __reduce__(self):
        maxsize = self.__state__['maxsize']
        cache = self.__state__['cache']
        keymap = self.__state__['keymap']
        ignore = self.__state__['ignore']
        tol = self.__state__['tol']
        deep = self.__state__['deep']
        purge = self.__state__['purge']
        return (self.__class__, (maxsize, cache, keymap, ignore, tol, deep, purge))


class mru_cache(object):
    """most-recently-used (MRU) cache decorator.

    This decorator memoizes a function's return value each time it is called.
    If called later with the same arguments, the cached value is returned, and
    not re-evaluated.  To avoid memory issues, a maximum cache size is imposed.
    For caches with an archive, the full cache dumps to archive upon reaching
    maxsize. For caches without an archive, the MRU algorithm manages the cache.
    Caches with an archive will use the latter behavior when 'purge' is False.
    This decorator takes an integer tolerance 'tol', equal to the number of
    decimal places to which it will round off floats, and a bool 'deep' for
    whether the rounding on inputs will be 'shallow' or 'deep'.  Note that
    rounding is not applied to the calculation of new results, but rather as a
    simple form of cache interpolation.  For example, with tol=0 and a cached
    value for f(3.0), f(3.1) will lookup f(3.0) in the cache while f(3.6) will
    store a new value; however if tol=1, both f(3.1) and f(3.6) will store
    new values.

    maxsize = maximum cache size
    cache = storage hashmap (default is {})
    keymap = cache key encoder (default is keymaps.hashmap(flat=True))
    ignore = function argument names and indicies to 'ignore' (default is None)
    tol = integer tolerance for rounding (default is None)
    deep = boolean for rounding depth (default is False, i.e. 'shallow')
    purge = boolean for purge cache to archive at maxsize (default is False)

    If *maxsize* is None, this cache will grow without bound.

    If *keymap* is given, it will replace the hashing algorithm for generating
    cache keys.  Several hashing algorithms are available in 'keymaps'. The
    default keymap requires arguments to the cached function to be hashable.

    If the keymap retains type information, then arguments of different types
    will be cached separately.  For example, f(3.0) and f(3) will be treated
    as distinct calls with distinct results.  Cache typing has a memory penalty,
    and may also be ignored by some 'keymaps'.

    If *ignore* is given, the keymap will ignore the arguments with the names
    and/or positional indicies provided. For example, if ignore=(0,), then
    the key generated for f(1,2) will be identical to that of f(3,2) or f(4,2).
    If ignore=('y',), then the key generated for f(x=3,y=4) will be identical
    to that of f(x=3,y=0) or f(x=3,y=10). If ignore=('*','**'), all varargs
    and varkwds will be 'ignored'.  Ignored arguments never trigger a
    recalculation (they only trigger cache lookups), and thus are 'ignored'.
    When caching class methods, it may be useful to ignore=('self',).

    View cache statistics (hit, miss, load, maxsize, size) with f.info().
    Clear the cache and statistics with f.clear().  Replace the cache archive
    with f.archive(obj).  Load from the archive with f.load(), and dump from
    the cache to the archive with f.dump().

    See: http://en.wikipedia.org/wiki/Cache_algorithms#Most_Recently_Used
    """
    def __new__(cls, *args, **kwds):
        maxsize = kwds.get('maxsize', -1)
        if maxsize == 0:
            return no_cache(*args, **kwds)
        if maxsize is None:
            return inf_cache(*args, **kwds)
        return object.__new__(cls)

    def __init__(self, maxsize=100, cache=None, keymap=None, ignore=None, tol=None, deep=False, purge=False):
        if maxsize is None or maxsize == 0:
            return
        if cache is None: cache = archive_dict()
        elif type(cache) is dict: cache = archive_dict(cache)

        if keymap is None: keymap = hashmap(flat=True)
        if ignore is None: ignore = tuple()

        if deep: rounded = deep_round
        else: rounded = simple_round
       #else: rounded = shallow_round #FIXME: slow

        @rounded(tol)
        def rounded_args(*args, **kwds):
            return (args, kwds)

        # set state
        self.__state__ = {
            'maxsize': maxsize,
            'cache': cache,
            'keymap': keymap,
            'ignore': ignore,
            'roundargs': rounded_args,
            'tol': tol,
            'deep': deep,
            'purge': purge,
        }
        return

    def __call__(self, user_function):
        from collections import deque
       #cache = dict()                  # mapping of args to results
        queue = deque()                 # order that keys have been used
        stats = [0, 0, 0]               # make statistics updateable non-locally
        HIT, MISS, LOAD = 0, 1, 2       # names for the stats fields
        _len = len                      # localize the global len() function
       #lock = RLock()                  # linkedlist updates aren't threadsafe
        maxsize = self.__state__['maxsize']
        cache = self.__state__['cache']
        keymap = self.__state__['keymap']
        ignore = self.__state__['ignore']
        rounded_args = self.__state__['roundargs']
        purge = self.__state__['purge']

        # lookup optimizations (ugly but fast)
        queue_append, queue_popleft = queue.append, queue.popleft
        queue_appendleft, queue_pop = queue.appendleft, queue.pop

        def wrapper(*args, **kwds):
            _args, _kwds = rounded_args(*args, **kwds)
            _args, _kwds = _keygen(user_function, ignore, *_args, **_kwds)
            key = keymap(*_args, **_kwds)

            try:
                # get cache entry
                result = cache[key]
                try: queue.remove(key)
                except ValueError: pass
                stats[HIT] += 1
            except KeyError:
                # if not in cache, look in archive
                if cache.archived():
                    cache.load(key)
                try:
                    result = cache[key]
                    stats[LOAD] += 1
                except KeyError:
                    # if not found, then compute
                    result = user_function(*args, **kwds)
                    cache[key] = result
                    stats[MISS] += 1

                # purge cache
                if _len(cache) > maxsize:
                    #XXX: better: if cache is cache.archive ?
                    if cache.archived() and purge:
                        cache.dump()
                        cache.clear() 
                        queue.clear()
                    else: # purge most recently used cache entry
                        k = queue_pop()
                        if cache.archived(): cache.dump(k)
                        try: del cache[k]
                        except KeyError: pass #FIXME: possible none purged

            # record recent use of this key
            queue_append(key)
            return result

        def archive(obj):
            """Replace the cache archive"""
            if isinstance(obj, archive_dict): cache.archive = obj.archive
            else: cache.archive = obj

        def key(*args, **kwds):
            """Get the cache key for the given *args,**kwds"""
            _args, _kwds = rounded_args(*args, **kwds)
            _args, _kwds = _keygen(user_function, ignore, *_args, **_kwds)
            return keymap(*_args, **_kwds)

        def lookup(*args, **kwds):
            """Get the stored value for the given *args,**kwds"""
            _args, _kwds = rounded_args(*args, **kwds)
            _args, _kwds = _keygen(user_function, ignore, *_args, **_kwds)
            return cache[keymap(*_args, **_kwds)]

        def __get_cache():
            """Get the cache"""
            return cache

        def __get_mask():
            """Get the (ignore) mask"""
            return ignore

        def __get_keymap():
            """Get the keymap"""
            return keymap

        def clear(keepstats=False):
            """Clear the cache and statistics"""
            cache.clear()
            queue.clear()
            if not keepstats: stats[:] = [0, 0, 0]

        def info():
            """Report cache statistics"""
            return CacheInfo(stats[HIT], stats[MISS], stats[LOAD], maxsize, len(cache))

        # interface
        wrapper.__wrapped__ = user_function
        #XXX: better is handle to key_function=keygen(ignore)(user_function) ?
        wrapper.info = info
        wrapper.clear = clear
        wrapper.load = cache.load
        wrapper.dump = cache.dump
        wrapper.archive = archive
        wrapper.archived = cache.archived
        wrapper.key = key
        wrapper.lookup = lookup
        wrapper.__cache__ = __get_cache
        wrapper.__mask__ = __get_mask
        wrapper.__map__ = __get_keymap
       #wrapper._queue = queue #XXX
        return update_wrapper(wrapper, user_function)

    def __get__(self, obj, objtype):
        """support instance methods"""
        return partial(self.__call__, obj)

    def __reduce__(self):
        maxsize = self.__state__['maxsize']
        cache = self.__state__['cache']
        keymap = self.__state__['keymap']
        ignore = self.__state__['ignore']
        tol = self.__state__['tol']
        deep = self.__state__['deep']
        purge = self.__state__['purge']
        return (self.__class__, (maxsize, cache, keymap, ignore, tol, deep, purge))


class rr_cache(object):
    """random-replacement (RR) cache decorator.

    This decorator memoizes a function's return value each time it is called.
    If called later with the same arguments, the cached value is returned, and
    not re-evaluated.  To avoid memory issues, a maximum cache size is imposed.
    For caches with an archive, the full cache dumps to archive upon reaching
    maxsize. For caches without an archive, the RR algorithm manages the cache.
    Caches with an archive will use the latter behavior when 'purge' is False.
    This decorator takes an integer tolerance 'tol', equal to the number of
    decimal places to which it will round off floats, and a bool 'deep' for
    whether the rounding on inputs will be 'shallow' or 'deep'.  Note that
    rounding is not applied to the calculation of new results, but rather as a
    simple form of cache interpolation.  For example, with tol=0 and a cached
    value for f(3.0), f(3.1) will lookup f(3.0) in the cache while f(3.6) will
    store a new value; however if tol=1, both f(3.1) and f(3.6) will store
    new values.

    maxsize = maximum cache size
    cache = storage hashmap (default is {})
    keymap = cache key encoder (default is keymaps.hashmap(flat=True))
    ignore = function argument names and indicies to 'ignore' (default is None)
    tol = integer tolerance for rounding (default is None)
    deep = boolean for rounding depth (default is False, i.e. 'shallow')
    purge = boolean for purge cache to archive at maxsize (default is False)

    If *maxsize* is None, this cache will grow without bound.

    If *keymap* is given, it will replace the hashing algorithm for generating
    cache keys.  Several hashing algorithms are available in 'keymaps'. The
    default keymap requires arguments to the cached function to be hashable.

    If the keymap retains type information, then arguments of different types
    will be cached separately.  For example, f(3.0) and f(3) will be treated
    as distinct calls with distinct results.  Cache typing has a memory penalty,
    and may also be ignored by some 'keymaps'.

    If *ignore* is given, the keymap will ignore the arguments with the names
    and/or positional indicies provided. For example, if ignore=(0,), then
    the key generated for f(1,2) will be identical to that of f(3,2) or f(4,2).
    If ignore=('y',), then the key generated for f(x=3,y=4) will be identical
    to that of f(x=3,y=0) or f(x=3,y=10). If ignore=('*','**'), all varargs
    and varkwds will be 'ignored'.  Ignored arguments never trigger a
    recalculation (they only trigger cache lookups), and thus are 'ignored'.
    When caching class methods, it may be useful to ignore=('self',).

    View cache statistics (hit, miss, load, maxsize, size) with f.info().
    Clear the cache and statistics with f.clear().  Replace the cache archive
    with f.archive(obj).  Load from the archive with f.load(), and dump from
    the cache to the archive with f.dump().

    http://en.wikipedia.org/wiki/Cache_algorithms#Random_Replacement
    """
    def __new__(cls, *args, **kwds):
        maxsize = kwds.get('maxsize', -1)
        if maxsize == 0:
            return no_cache(*args, **kwds)
        if maxsize is None:
            return inf_cache(*args, **kwds)
        return object.__new__(cls)

    def __init__(self, maxsize=100, cache=None, keymap=None, ignore=None, tol=None, deep=False, purge=False):
        if maxsize is None or maxsize == 0:
            return
        if cache is None: cache = archive_dict()
        elif type(cache) is dict: cache = archive_dict(cache)

        if keymap is None: keymap = hashmap(flat=True)
        if ignore is None: ignore = tuple()

        if deep: rounded = deep_round
        else: rounded = simple_round
       #else: rounded = shallow_round #FIXME: slow

        @rounded(tol)
        def rounded_args(*args, **kwds):
            return (args, kwds)

        # set state
        self.__state__ = {
            'maxsize': maxsize,
            'cache': cache,
            'keymap': keymap,
            'ignore': ignore,
            'roundargs': rounded_args,
            'tol': tol,
            'deep': deep,
            'purge': purge,
        }
        return

    def __call__(self, user_function):
       #cache = dict()                  # mapping of args to results
        stats = [0, 0, 0]               # make statistics updateable non-locally
        HIT, MISS, LOAD = 0, 1, 2       # names for the stats fields
        _len = len                      # localize the global len() function
       #lock = RLock()                  # linkedlist updates aren't threadsafe
        maxsize = self.__state__['maxsize']
        cache = self.__state__['cache']
        keymap = self.__state__['keymap']
        ignore = self.__state__['ignore']
        rounded_args = self.__state__['roundargs']
        purge = self.__state__['purge']

        def wrapper(*args, **kwds):
            from random import choice #XXX: biased?
            _args, _kwds = rounded_args(*args, **kwds)
            _args, _kwds = _keygen(user_function, ignore, *_args, **_kwds)
            key = keymap(*_args, **_kwds)

            try:
                # get cache entry
                result = cache[key]
                stats[HIT] += 1
            except KeyError:
                # if not in cache, look in archive
                if cache.archived():
                    cache.load(key)
                try:
                    result = cache[key]
                    stats[LOAD] += 1
                except KeyError:
                    # if not found, then compute
                    result = user_function(*args, **kwds)
                    cache[key] = result
                    stats[MISS] += 1

                # purge cache
                if _len(cache) > maxsize:
                    #XXX: better: if cache is cache.archive ?
                    if cache.archived() and purge:
                        cache.dump()
                        cache.clear() 
                    else: # purge random cache entry
                        key = choice(list(cache.keys()))
                        if cache.archived(): cache.dump(key)
                        try: del cache[key]
                        except KeyError: pass #FIXME: possible none purged
            return result

        def archive(obj):
            """Replace the cache archive"""
            if isinstance(obj, archive_dict): cache.archive = obj.archive
            else: cache.archive = obj

        def key(*args, **kwds):
            """Get the cache key for the given *args,**kwds"""
            _args, _kwds = rounded_args(*args, **kwds)
            _args, _kwds = _keygen(user_function, ignore, *_args, **_kwds)
            return keymap(*_args, **_kwds)

        def lookup(*args, **kwds):
            """Get the stored value for the given *args,**kwds"""
            _args, _kwds = rounded_args(*args, **kwds)
            _args, _kwds = _keygen(user_function, ignore, *_args, **_kwds)
            return cache[keymap(*_args, **_kwds)]

        def __get_cache():
            """Get the cache"""
            return cache

        def __get_mask():
            """Get the (ignore) mask"""
            return ignore

        def __get_keymap():
            """Get the keymap"""
            return keymap

        def clear(keepstats=False):
            """Clear the cache and statistics"""
            cache.clear()
            if not keepstats: stats[:] = [0, 0, 0]

        def info():
            """Report cache statistics"""
            return CacheInfo(stats[HIT], stats[MISS], stats[LOAD], maxsize, len(cache))

        # interface
        wrapper.__wrapped__ = user_function
        #XXX: better is handle to key_function=keygen(ignore)(user_function) ?
        wrapper.info = info
        wrapper.clear = clear
        wrapper.load = cache.load
        wrapper.dump = cache.dump
        wrapper.archive = archive
        wrapper.archived = cache.archived
        wrapper.key = key
        wrapper.lookup = lookup
        wrapper.__cache__ = __get_cache
        wrapper.__mask__ = __get_mask
        wrapper.__map__ = __get_keymap
       #wrapper._queue = None  #XXX
        return update_wrapper(wrapper, user_function)

    def __get__(self, obj, objtype):
        """support instance methods"""
        return partial(self.__call__, obj)

    def __reduce__(self):
        maxsize = self.__state__['maxsize']
        cache = self.__state__['cache']
        keymap = self.__state__['keymap']
        ignore = self.__state__['ignore']
        tol = self.__state__['tol']
        deep = self.__state__['deep']
        purge = self.__state__['purge']
        return (self.__class__, (maxsize, cache, keymap, ignore, tol, deep, purge))


if __name__ == '__main__':
    import dill

   #@no_cache(10, tol=0)
   #@inf_cache(10, tol=0)
   #@lfu_cache(10, tol=0)
   #@lru_cache(10, tol=0)
   #@mru_cache(10, tol=0)
    @rr_cache(10, tol=0)
    def squared(x):
        return x**2

    res = squared(10)

    assert res == dill.loads(dill.dumps(squared))(10)


# EOF
