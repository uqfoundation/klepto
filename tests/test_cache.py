#!/usr/bin/env python
#
# Author: Mike McKerns (mmckerns @caltech and @uqfoundation)
# Copyright (c) 2013-2016 California Institute of Technology.
# Copyright (c) 2016-2021 The Uncertainty Quantification Foundation.
# License: 3-clause BSD.  The full license text is available at:
#  - https://github.com/uqfoundation/klepto/blob/master/LICENSE
"""
The decorator should produce the behavior as displayed in the following:

>>> s = Spam()
>>> s.eggs()
new: (), {}
42
>>> s.eggs()
42
>>> s.eggs(1)
new: (1,), {}
64
>>> s.eggs(1)
64
>>> s.eggs(1, bar='spam')
new: (1,), {'bar': 'spam'}
78
>>> s2 = Spam()
>>> s2.eggs(1, bar='spam')
78
"""

from klepto.safe import inf_cache as memoized
#from klepto import inf_cache as memoized
from klepto.keymaps import picklemap
dumps = picklemap(flat=False, serializer='dill')

class Spam(object):
    """A simple class with a memoized method"""

    @memoized(keymap=dumps, ignore='self')
    def eggs(self, *args, **kwds):
       #print ('new:', args, kwds)
        from random import random
        return int(100 * random())

def test_classmethod():
    s = Spam()
    assert s.eggs() == s.eggs()
    assert s.eggs(1) == s.eggs(1)
    s2 = Spam() 
    assert s.eggs(1, bar='spam') == s2.eggs(1, bar='spam')
    assert s.eggs.info().hit  == 3
    assert s.eggs.info().miss == 3
    assert s.eggs.info().load == 0

#print ('=' * 30)


# here caching saves time in a recursive function...
@memoized(keymap=dumps)
def fibonacci(n):
    "Return the nth fibonacci number."
   #print ('calculating %s' % n)
    if n in (0, 1):
        return n
    return fibonacci(n-1) + fibonacci(n-2)

def test_recursive():
    fibonacci(7)
    fibonacci(9)
    fibonacci(3)
    assert fibonacci.info().hit  == 9
    assert fibonacci.info().miss == 10
    assert fibonacci.info().load == 0

#print ('=' * 30)

def test_basic():
    try:
        from numpy import sum, asarray
        @memoized(keymap=dumps, tol=3)
        def add(*args):
           #print ('new:', args)
            return sum(args)

        assert add(1,2,3.0001)  == 6.0000999999999998
        assert add(1,2,3.00012) == 6.0000999999999998
        assert add(1,2,3.0234)  == 6.0234000000000005
        assert add(1,2,3.023)   == 6.0234000000000005
        assert add.info().hit  == 2
        assert add.info().miss == 2
        assert add.info().load == 0

        def cost(x,y):
           #print ('new: %s or %s' % (str(x), str(y)))
            x = asarray(x)
            y = asarray(y)
            return sum(x**2 - y**2)

        cost1 = memoized(keymap=dumps, tol=1)(cost)
        cost0 = memoized(keymap=dumps, tol=0)(cost)
        costD = memoized(keymap=dumps, tol=0, deep=True)(cost)

       #print ("rounding to one decimals...")
        cost1([1,2,3.1234], 3.9876)# == -32.94723372
        cost1([1,2,3.1234], 3.9876)# == -32.94723372
        cost1([1,2,3.1234], 3.6789)# == -25.84728807
        cost1([1,2,3.4321], 3.6789)# == -23.82360522
        assert cost1.info().hit  == 1
        assert cost1.info().miss == 3
        assert cost1.info().load == 0

       #print ("\nrerun the above with rounding to zero decimals...")
        cost0([1,2,3.1234], 3.9876)# == -32.94723372
        cost0([1,2,3.1234], 3.9876)# == -32.94723372
        cost0([1,2,3.1234], 3.6789)# == -32.94723372
        cost0([1,2,3.4321], 3.6789)# == -23.82360522
        assert cost0.info().hit  == 2
        assert cost0.info().miss == 2
        assert cost0.info().load == 0

       #print ("\nrerun again with deep rounding to zero decimals...")
        costD([1,2,3.1234], 3.9876)# == -32.94723372
        costD([1,2,3.1234], 3.9876)# == -32.94723372
        costD([1,2,3.1234], 3.6789)# == -32.94723372
        costD([1,2,3.4321], 3.6789)# == -32.94723372
        assert costD.info().hit  == 3
        assert costD.info().miss == 1
        assert costD.info().load == 0
       #print ("")
    except ImportError:
        pass


import sys
import dill
from klepto.archives import cache, sql_archive, dict_archive

def test_memoized():
    @memoized(cache=sql_archive())
    def add(x,y):
        return x+y
    add(1,2)
    add(1,2)
    add(1,3)
    #print ("sql_cache = %s" % add.__cache__())
    _key4 = '((), '+str({'y':3, 'x':1})+')'
    _key3 = '((), '+str({'y':2, 'x':1})+')'
    key4_ = '((), '+str({'x':1, 'y':3})+')'
    key3_ = '((), '+str({'x':1, 'y':2})+')'
    assert add.__cache__() == {_key4: 4, _key3: 3} or {key4_: 4, key3_: 3}

    @memoized(cache=dict_archive(cached=False)) # use archive backend 'direcly'
    def add(x,y):
        return x+y
    add(1,2)
    add(1,2)
    add(1,3)
    #print ("dict_cache = %s" % add.__cache__())
    assert add.__cache__() == {_key4: 4, _key3: 3} or {key4_: 4, key3_: 3}

    @memoized(cache=dict())
    def add(x,y):
        return x+y
    add(1,2)
    add(1,2)
    add(1,3)
    #print ("dict_cache = %s" % add.__cache__())
    assert add.__cache__() == {_key4: 4, _key3: 3} or {key4_: 4, key3_: 3}

    @memoized(cache=add.__cache__())
    def add(x,y):
        return x+y
    add(1,2)
    add(2,2)
    #print ("re_dict_cache = %s" % add.__cache__())
    _key2 = '((), '+str({'y':2, 'x':2})+')'
    key2_ = '((), '+str({'x':2, 'y':2})+')'
    assert add.__cache__() == {_key4: 4, _key3: 3, _key2: 4} or {key4_: 4, key3_: 3, key2_: 4}

    @memoized(keymap=dumps)
    def add(x,y):
        return x+y
    add(1,2)
    add(1,2)
    add(1,3)
    #print ("pickle_dict_cache = %s" % add.__cache__())
    _pkey4 = dill.dumps(eval(_key4))
    _pkey3 = dill.dumps(eval(_key3))
    pkey4_ = dill.dumps(eval(key4_))
    pkey3_ = dill.dumps(eval(key3_))
    assert add.__cache__() == {_pkey4: 4, _pkey3: 3} or {pkey4_: 4, pkey3_: 3}

from klepto import lru_cache

def test_lru():
    @lru_cache(maxsize=3, cache=dict_archive('test'), purge=True)
    def identity(x):
        return x

    identity(1)
    identity(2)
    identity(3)
    ic = identity.__cache__()
    assert len(ic.keys()) == 3
    assert len(ic.archive.keys()) == 0
    identity(4)
    assert len(ic.keys()) == 0
    assert len(ic.archive.keys()) == 4
    identity(5)
    assert len(ic.keys()) == 1
    assert len(ic.archive.keys()) == 4

    @lru_cache(maxsize=3, cache=dict_archive('test'), purge=False)
    def inverse(x):
        return -x

    inverse(1)
    inverse(2)
    inverse(3)
    ic = inverse.__cache__()
    assert len(ic.keys()) == 3
    assert len(ic.archive.keys()) == 0
    inverse(4)
    assert len(ic.keys()) == 3
    assert len(ic.archive.keys()) == 1
    inverse(5)
    assert len(ic.keys()) == 3
    assert len(ic.archive.keys()) == 2

    @lru_cache(maxsize=3, cache=dict_archive('test', cached=False))
    def foo(x):
        return x

    foo(1)
    foo(2)
    foo(3)
    ic = foo.__cache__()
    assert len(ic.keys()) == 3
    assert len(ic.archive.keys()) == 3
    foo(4)
    assert len(ic.keys()) == 3
    assert len(ic.archive.keys()) == 3
    foo(5)
    assert len(ic.keys()) == 3
    assert len(ic.archive.keys()) == 3

    #XXX: should it be 'correct' expected behavior to ignore purge?
    @lru_cache(maxsize=3, cache=None, purge=True)
    def bar(x):
        return -x

    bar(1)
    bar(2)
    bar(3)
    ic = bar.__cache__()
    assert len(ic.keys()) == 3
    assert len(ic.archive.keys()) == 0
    bar(4)
    assert len(ic.keys()) == 3
    assert len(ic.archive.keys()) == 0
    bar(5)
    assert len(ic.keys()) == 3
    assert len(ic.archive.keys()) == 0


if __name__ == '__main__':
    test_classmethod()
    test_recursive()
    test_basic()
    test_memoized()
    test_lru()
