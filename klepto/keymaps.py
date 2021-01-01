#!/usr/bin/env python
#
# Author: Mike McKerns (mmckerns @caltech and @uqfoundation)
# Copyright (c) 2013-2016 California Institute of Technology.
# Copyright (c) 2016-2021 The Uncertainty Quantification Foundation.
# License: 3-clause BSD.  The full license text is available at:
#  - https://github.com/uqfoundation/klepto/blob/master/LICENSE
"""
custom 'keymaps' for generating dictionary keys from function input signatures
"""

__all__ = ['SENTINEL','NOSENTINEL','keymap','hashmap','stringmap','picklemap']

class _Sentinel(object):
    """build a sentinel object for the SENTINEL singleton"""
    def __repr__(self):
        return "<SENTINEL>"
class _NoSentinel(object):
    """build a sentinel object for the NOSENTINEL singleton"""
    def __repr__(self):
        return "<NOSENTINEL>"

SENTINEL = _Sentinel()
NOSENTINEL = _NoSentinel()
# SENTINEL = object()
# NOSENTINEL = (SENTINEL,)  #XXX: use to indicate "don't use a sentinel" ?

from copy import copy
from klepto.crypto import hash, string, pickle

def __chain__(x, y):
    "chain two keymaps: calls 'x' then 'y' on object to produce y(x(object))"
    if x is None:
        x,y = y,x
    if y is None:
        f = lambda z: x(z)
    else:
        f = lambda z: y(x(z))
    if y is None: msg = ""
    else: msg = "calls %s then %s" % (x,y)
    f.__doc__ = msg
    f.__inner__ = x
    f.__outer__ = y
    return f


class keymap(object):
    """tool for converting a function's input signature to an unique key

    This keymap does not serialize objects, but does do some formatting.
    Since the keys are stored as raw objects, there is no information loss,
    and thus it is easy to recover the original input signature.  However,
    to use an object as a key, the object must be hashable.
    """
    def __init__(self, typed=False, flat=True, sentinel=NOSENTINEL, **kwds):
        '''initialize the key builder

        typed: if True, include type information in the key
        flat: if True, flatten the key to a sequence; if False, use (args, kwds)
        sentinel: marker for separating args and kwds in flattened keys

        This keymap stores function args and kwds as (args, kwds) if flat=False,
        or a flattened ``(*args, zip(**kwds))`` if flat=True.  If typed, then
        include a tuple of type information (args, kwds, argstypes, kwdstypes)
        in the generated key.  If a sentinel is given, the sentinel will be
        added to a flattened key to indicate the boundary between args, keys,
        argstypes, and kwdstypes. 
        '''
        self.typed = typed
        self.flat = flat
        self.sentinel = sentinel
       #self.__chain__ = __chain__(self, None)
        self.__inner__ = None
        self.__outer__ = None
       #self.__type__ = None #XXX: stuff breaks if this exists
        self.__stub__ = ''

        # some rare kwds that allow keymap customization
        try:
            self._fasttypes = (int,str,bytes,frozenset,type(None))
        except NameError:
            self._fasttypes = (int,str,frozenset,type(None))
        self._fasttypes = kwds.pop('fasttypes', set(self._fasttypes))
        self._sorted = kwds.pop('sorted', sorted)
        self._tuple = kwds.pop('tuple', tuple)
        self._type = kwds.pop('type', type)
        self._len = kwds.pop('len', len)

        # the rest of the kwds are for customizaton of the encoder
        self._config = kwds.copy()
        return

    def __get_outer(self):
        "get 'outer' keymap"
        return self.__outer__

    def __get_inner(self):
        "get 'nested' keymap, if one exists"
       #if self.__chain__.__outer__:
       #    return self.__chain__.__inner__
       #return None
        return self.__inner__

    def __chain(self, map):
        "create a 'nested' keymap"
        raise NotImplementedError("Combine keymaps with '+'")

    def __repr__(self):
        msg = "%s(" % self.__class__.__name__
        if self.typed != False:
            msg += 'typed=%s, ' % self.typed
        if self.flat != True:
            msg += 'flat=%s, ' % self.flat
        if self.sentinel != NOSENTINEL:
            msg += 'sentinel=%s, ' % self.sentinel
        if self.__stub__ != '' and self.__type__ is not None:
            msg += "%s='%s', " % (self.__stub__, self.__type__)
       #msg += 'inner=%s)' % bool(self.inner)
        if msg: msg = msg.rstrip().rstrip(',')
        if bool(self.inner):
            msg += ')*'
        else:
            msg += ')'
        return msg

    def __get_sentinel(self):
        if self._mark:
            return self._mark[0]
        return NOSENTINEL #XXX: or None?
    def __sentinel(self, mark):
        if mark != NOSENTINEL:
            self._mark = (mark,)
        else: self._mark = None

    def __call__(self, *args, **kwds):
        'generate a key from optionally typed positional and keyword arguments'
        if self.flat:
            return self.encode(*args, **kwds)
        return self.encrypt(*args, **kwds)

    def encrypt(self, *args, **kwds):
        """use a non-flat scheme for generating a key"""
        key = (args, kwds) #XXX: pickles larger, but is simpler to unpack
        if self.typed:
            sorted_items = self._sorted(list(kwds.items()))
            key += (self._tuple(self._type(v) for v in args), \
                    self._tuple(self._type(v) for (k,v) in sorted_items))
        # __chain__
        if self.outer:
            return self.inner(key)
        return key

    def encode(self, *args, **kwds):
        """use a flattened scheme for generating a key"""
        key = args
        if kwds:
            sorted_items = self._sorted(list(kwds.items()))
            if self._mark: key += self._mark
            for item in sorted_items:
                key += item
        if self.typed: #XXX: 'mark' between each part, so easy to split
            if self._mark: key += self._mark
            key += self._tuple(self._type(v) for v in args)
            if kwds:
                if self._mark: key += self._mark
                key += self._tuple(self._type(v) for (k,v) in sorted_items)
        elif self._len(key) == 1 and self._type(key[0]) in self._fasttypes:
            key = key[0]
        # __chain__
        if self.outer:
            return self.inner(key)
        return key

    def decrypt(self, key):
        """recover the stored value directly from a generated (non-flat) key"""
        raise NotImplementedError("Key decryption is not implemented")

    def decode(self, key):
        """recover the stored value directly from a generated (flattened) key"""
        raise NotImplementedError("Key decoding is not implemented")

    def dumps(self, obj, **kwds):
        """a more pickle-like interface for encoding a key"""
        return self.encode(obj, **kwds)

    def loads(self, key):
        """a more pickle-like interface for decoding a key"""
        return self.decode(key)

    def __add__(self, other):
        """concatenate two keymaps, to produce a new keymap"""
        if not isinstance(other, keymap):
            raise TypeError("can't concatenate '%s' and '%s' objects" % (self.__class__.__name__, other.__class__.__name__))
        k = copy(other)
       #k.__chain__ = __chain__(self, k)
        k.__inner__ = copy(self)  #XXX: or just... self ?
        k.__outer__ = copy(other) #XXX: or just... other ?
        return k

    # interface
    sentinel = property(__get_sentinel, __sentinel)
    inner = property(__get_inner, __chain)
    outer = property(__get_outer, __chain)
    pass


class hashmap(keymap):
    """tool for converting a function's input signature to an unique key

    This keymap generates a hash for the given object.  Not all objects are
    hashable, and generating a hash incurrs some information loss.  Hashing
    is fast, however there is not a method to recover the input signature
    from a hash.
    """ #XXX: algorithm as first argument? easier to build, but less standard
    def __init__(self, typed=False, flat=True, sentinel=NOSENTINEL, **kwds):
        '''initialize the key builder

        typed: if True, include type information in the key
        flat: if True, flatten the key to a sequence; if False, use (args, kwds)
        sentinel: marker for separating args and kwds in flattened keys
        algorithm: string name of hashing algorithm [default: use python's hash]

        This keymap stores function args and kwds as (args, kwds) if flat=False,
        or a flattened ``(*args, zip(**kwds))`` if flat=True.  If typed, then
        include a tuple of type information (args, kwds, argstypes, kwdstypes)
        in the generated key.  If a sentinel is given, the sentinel will be
        added to a flattened key to indicate the boundary between args, keys,
        argstypes, and kwdstypes.

        Use kelpto.crypto.algorithms() to get the names of available hashing
        algorithms.
        '''
        self.__type__ = kwds.pop('algorithm', None)
        keymap.__init__(self, typed=typed, flat=flat, sentinel=sentinel, **kwds)
        self.__stub__ = 'algorithm' #XXX: unnecessary if unified kwd
        return
    def encode(self, *args, **kwds):
        """use a flattened scheme for generating a key"""
        return hash(keymap.encode(self, *args, **kwds), algorithm=self.__type__, **self._config)
    def encrypt(self, *args, **kwds):
        """use a non-flat scheme for generating a key"""
        return hash(keymap.encrypt(self, *args, **kwds), algorithm=self.__type__, **self._config)

class stringmap(keymap):
    """tool for converting a function's input signature to an unique key

    This keymap serializes objects by converting __repr__ to a string.
    Converting to a string is slower than hashing, however will produce a
    key in all cases.  Some forms of archival storage, like a database,
    may require string keys.  There is not a method to recover the input
    signature from a string key that works in all cases, however this is
    possible for any object where __repr__ effectively mimics __init__.
    """ #XXX: encoding as first argument? easier to build, but less standard
    def __init__(self, typed=False, flat=True, sentinel=NOSENTINEL, **kwds):
        '''initialize the key builder

        typed: if True, include type information in the key
        flat: if True, flatten the key to a sequence; if False, use (args, kwds)
        sentinel: marker for separating args and kwds in flattened keys
        encoding: string name of string encoding [default: use python's str]

        This keymap stores function args and kwds as (args, kwds) if flat=False,
        or a flattened ``(*args, zip(**kwds))`` if flat=True.  If typed, then
        include a tuple of type information (args, kwds, argstypes, kwdstypes)
        in the generated key.  If a sentinel is given, the sentinel will be
        added to a flattened key to indicate the boundary between args, keys,
        argstypes, and kwdstypes.

        Use kelpto.crypto.encodings() to get the names of available string
        encodings.
        '''
        self.__type__ = kwds.pop('encoding', None)
        keymap.__init__(self, typed=typed, flat=flat, sentinel=sentinel, **kwds)
        self.__stub__ = 'encoding' #XXX: unnecessary if unified kwd
        return
    def encode(self, *args, **kwds):
        """use a flattened scheme for generating a key"""
        return string(keymap.encode(self, *args, **kwds), encoding=self.__type__, **self._config)
    def encrypt(self, *args, **kwds):
        """use a non-flat scheme for generating a key"""
        return string(keymap.encrypt(self, *args, **kwds), encoding=self.__type__, **self._config)

class picklemap(keymap):
    """tool for converting a function's input signature to an unique key

    This keymap serializes objects by pickling the object.  Serializing an
    object with pickle is relatively slower, however will reliably produce a
    unique key for all picklable objects.  Also, pickling is a reversible
    operation, where the original input signature can be recovered from the
    generated key.
    """ #XXX: serializer as first argument? easier to build, but less standard
    def __init__(self, typed=False, flat=True, sentinel=NOSENTINEL, **kwds):
        '''initialize the key builder

        typed: if True, include type information in the key
        flat: if True, flatten the key to a sequence; if False, use (args, kwds)
        sentinel: marker for separating args and kwds in flattened keys
        serializer: string name of pickler [default: use python's repr]

        This keymap stores function args and kwds as (args, kwds) if flat=False,
        or a flattened ``(*args, zip(**kwds))`` if flat=True.  If typed, then
        include a tuple of type information (args, kwds, argstypes, kwdstypes)
        in the generated key.  If a sentinel is given, the sentinel will be
        added to a flattened key to indicate the boundary between args, keys,
        argstypes, and kwdstypes.

        Use kelpto.crypto.serializers() to get the names of available picklers.
        NOTE: the serializer kwd expects a <module> object, and not a <str>.
        '''
        kwds['byref'] = kwds.get('byref',True) #XXX: for dill
        self.__type__ = kwds.pop('serializer', None)
        #XXX: better not convert __type__ to string, so don't __import__ ?
        if not isinstance(self.__type__, (str, type(None))):
            self.__type__ = self.__type__.__name__
        keymap.__init__(self, typed=typed, flat=flat, sentinel=sentinel, **kwds)
        self.__stub__ = 'serializer' #XXX: unnecessary if unified kwd
        return
    def encode(self, *args, **kwds):
        """use a flattened scheme for generating a key"""
        return pickle(keymap.encode(self, *args, **kwds), serializer=self.__type__, **self._config) # separator=(',',':') for json
    def encrypt(self, *args, **kwds):
        """use a non-flat scheme for generating a key"""
        return pickle(keymap.encrypt(self, *args, **kwds), serializer=self.__type__, **self._config) # separator=(',',':') for json


# EOF
