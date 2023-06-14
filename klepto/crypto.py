#!/usr/bin/env python
#
# Author: Mike McKerns (mmckerns @caltech and @uqfoundation)
# Copyright (c) 2013-2016 California Institute of Technology.
# Copyright (c) 2016-2023 The Uncertainty Quantification Foundation.
# License: 3-clause BSD.  The full license text is available at:
#  - https://github.com/uqfoundation/klepto/blob/master/LICENSE

import os
import sys
import hashlib
import pkgutil
import encodings as codecs
__hash = hash

def algorithms():
    """return a tuple of available hash algorithms"""
    try:
        algs =  hashlib.algorithms
    except:
        algs = ('md5', 'sha1', 'sha224', 'sha256', 'sha384', 'sha512')
    return (None,) + algs

def hash(object, algorithm=None):
    if algorithm is None:
        return __hash(object)
    return hashlib.new(algorithm, repr(object).encode()).hexdigest()
hash.algorithms = algorithms
hash.__doc__ = \
"""cryptographic hashing

    algorithm: one of %s
    The default is algorithm=None, which uses python's 'hash'.""" % repr(algorithms())


def encodings():
    """return a tuple of available encodings and string-like types"""
    try:
        algs = set([modname for importer, modname, ispkg in pkgutil.walk_packages(path=[os.path.dirname(codecs.__file__)], prefix='')])
    except:
        algs = set()
    algs = algs.union(set(codecs.aliases.aliases.values()))
    try: #FIXME: essentially, a poor alias for python 3.x
        eval('unicode') #XXX: i.e. only allow unicode and bytes in python 2.x
        utype = ('unicode','bytes')
    except NameError:
        utype = tuple()
        if 'tactis' in algs:
            algs.remove('tactis')
        pop = [t for t in algs if t.endswith('_codec')]
        [algs.remove(t) for t in pop] #FIXME: giving up here for 3.x...
        # (any '*_codec' throws 'str' does not support the buffer interface)
    stype = ('str','repr')
    return (None,) + tuple(algs) + stype + utype
    

def string(object, encoding=None, strict=True):
    """encode an object (as a string)

    strict: bool or None, for 'strictness' of the encoding
    encoding: one of the available string encodings or string-like types

    For encodings, such as 'utf-8', strict=True will raise an exception in
    the case of an encoding error, strict=None will ignore malformed data,
    and strict=False will replace malformed data with a suitable marker
    such as '?' or '\ufffd'.  For string-like types, strict=True restricts
    the type casting to the list of types in klepto.crypto.encodings().

    The default is encoding=None, which uses python's 'str'."""
    if encoding is None:
        return str(object)
    try:
        if strict and encoding not in encodings():
            raise NameError
        try: #FIXME: 'bytes' not quite right for python3.x
            return eval("%s(object)" % encoding) #XXX: safer is %s(repr(object))
        except TypeError: # special case for bytes: object is a string
            return eval("%s(object, 'utf_8')" % encoding)
    except:
        if strict: strict = 'strict'
        elif strict is None: strict = 'ignore'
        else: strict = 'replace'
        return repr(object).encode(encoding, strict)

string.encodings = encodings


def serializers(): #FIXME: could be much smarter
    """return a tuple of string names of serializers"""
    serializers = (None, 'pickle', 'json', 'dill')
    from importlib import util as imp
    if imp.find_spec('cloudpickle'):
        serializers += ('cloudpickle',)
    if imp.find_spec('jsonpickle'):
        serializers += ('jsonpickle',)
    return serializers


def pickle(object, serializer=None, **kwds):
    """pickle an object (to a string)

    serializer: name of pickler module with a 'dumps' method
    The default is serializer=None, which uses python's 'repr'.

    NOTE: any 'bad' kwds will cause all kwds to be ignored."""
    if serializer is None:
        return repr(object) #XXX: better hex(id(object)) ?
    if not isinstance(serializer, type(os)): # if module, don't try to import it
        if not isinstance(serializer, str):
            raise TypeError("'%s' is not a module" % repr(serializer))
        try: # is a string
            serializer = __import__(serializer)
        except:
            raise NameError("name '%s' is not defined" % serializer)
    # now serializer is a module, work with it
    try:
        return serializer.dumps(object, **kwds)
    except TypeError:
        return serializer.dumps(object) #XXX: better alternative behavior?
pickle.serializers = serializers


# EOF
