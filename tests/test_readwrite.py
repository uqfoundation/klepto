#!/usr/bin/env python
#
# Author: Mike McKerns (mmckerns @caltech and @uqfoundation)
# Copyright (c) 2013-2016 California Institute of Technology.
# Copyright (c) 2016-2021 The Uncertainty Quantification Foundation.
# License: 3-clause BSD.  The full license text is available at:
#  - https://github.com/uqfoundation/klepto/blob/master/LICENSE

from klepto.archives import dir_archive
from pox import rmtree

def test_foo():
    # start fresh
    rmtree('foo', ignore_errors=True)

    d = dir_archive('foo', cached=False)
    key = '1234TESTMETESTMETESTME1234'
    d._mkdir(key)
    #XXX: repeat mkdir does nothing, should it clear?  I think not.
    _dir = d._mkdir(key)
    assert d._getdir(key) == _dir
    d._rmdir(key)

    # with _pickle
    x = [1,2,3,4,5]
    d._fast = True
    d[key] = x
    assert d[key] == x
    d._rmdir(key)

    # with dill
    d._fast = False
    d[key] = x
    assert d[key] == x
    d._rmdir(key)

    # with import
    d._serialized = False
    d[key] = x
    assert d[key] == x
    d._rmdir(key)
    d._serialized = True

    try: 
        import numpy as np
        y = np.array(x)

        # with _pickle
        d._fast = True
        d[key] = y
        assert all(d[key] == y)
        d._rmdir(key)

        # with dill
        d._fast = False
        d[key] = y
        assert all(d[key] == y)
        d._rmdir(key)

        # with import
        d._serialized = False
        d[key] = y
        assert all(d[key] == y)
        d._rmdir(key)
        d._serialized = True

    except ImportError:
        pass

    # clean up
    rmtree('foo')

# check archiving basic stuff
def check_basic(archive):
    d = archive
    d['a'] = 1
    d['b'] = '1'
    d['c'] = min
    squared = lambda x:x**2
    d['d'] = squared
    d['e'] = None
    assert d['a'] == 1
    assert d['b'] == '1'
    assert d['c'] == min
    assert d['d'](2) == squared(2)
    assert d['e'] == None
    return

# check archiving numpy stuff
def check_numpy(archive):
    try:
        import numpy as np
    except ImportError:
        return
    d = archive
    x = np.array([1,2,3,4,5])
    y = np.arange(1000)
    t = np.dtype([('int',np.int),('float32',np.float32)])
    d['a'] = x
    d['b'] = y
    d['c'] = np.inf
    d['d'] = np.ptp
    d['e'] = t
    assert all(d['a'] == x)
    assert all(d['b'] == y)
    assert d['c'] == np.inf
    assert d['d'](x) == np.ptp(x)
    assert d['e'] == t
    return

# FIXME: add tests for classes and class instances as values
# FIXME: add tests for non-string keys (e.g. d[1234] = 'hello')

def test_archive():
    # try some of the different __init__
    archive = dir_archive(cached=False)
    check_basic(archive)
    check_numpy(archive)
    #rmtree('memo')

    archive = dir_archive(cached=False,fast=True)
    check_basic(archive)
    check_numpy(archive)
    #rmtree('memo')

    archive = dir_archive(cached=False,compression=3)
    check_basic(archive)
    check_numpy(archive)
    #rmtree('memo')

    archive = dir_archive(cached=False,memmode='r+')
    check_basic(archive)
    check_numpy(archive)
    #rmtree('memo')

    archive = dir_archive(cached=False,serialized=False)
    check_basic(archive)
    #check_numpy(archive) #FIXME: see issue #53 
    rmtree('memo')


if __name__ == '__main__':
    test_foo()
    test_archive()
