#!/usr/bin/env python
#
# Author: Mike McKerns (mmckerns @caltech and @uqfoundation)
# Copyright (c) 2013-2016 California Institute of Technology.
# Copyright (c) 2016-2023 The Uncertainty Quantification Foundation.
# License: 3-clause BSD.  The full license text is available at:
#  - https://github.com/uqfoundation/klepto/blob/master/LICENSE

from klepto.keymaps import hashmap
from klepto import lru_cache as memoize
from klepto import inf_cache
from klepto import keygen

hasher = hashmap(algorithm='md5')

class Adder(object):
    """A simple class with a memoized method"""

    @memoize(keymap=hasher, ignore=('self','**'))
    def __call__(self, x, *args, **kwds):
        debug = kwds.get('debug', False)
        if debug:
            print ('debug:', x, args, kwds)
        return sum((x,)+args)
    add = __call__


def test_adder():
    add = Adder()
    assert add(2,0) == 2
    assert add(2,0,z=4) == 2          # cached (ignore z)
    assert add(2,0,debug=False) == 2  # cached (ignore debug)
    assert add(1,2,debug=False) == 3
    assert add(1,2,debug=True) == 3   # cached (ignore debug)
    assert add(4) == 4
    assert add(x=4) == 4              # cached

    plus = Adder()
    assert plus(4,debug=True) == 4    # cached (ignore debug)
    assert plus(2,0,3) == 5
    assert plus(2,0,4) == 6

    info = add.__call__.info()
    assert info.hit == 5
    assert info.miss == 5
    cache = add.__call__.__cache__()
    assert sorted(cache.values()) == [2,3,4,5,6]

    # careful... remember we have self as first argument
    key = add.__call__.key(add,2,0)
    assert cache[key] == add.__call__.__wrapped__(add,2,0)
    assert cache[key] == add.__call__.lookup(add,2,0)


######################################################
def test_memoize():
    @memoize(keymap=hasher, ignore=('self','**'))
    def _add(x, *args, **kwds):
        debug = kwds.get('debug', False)
        if debug:
            print ('debug:', x, args, kwds)
        return sum((x,)+args)

    _add(2,0)
    _add(2,0,z=4)
    _add(2,0,debug=False)
    _add(1,2,debug=False)
    _add(1,2,debug=True)
    _add(4)
    _add(x=4)
    _add(4,debug=True)
    _add(2,0,3)
    _add(2,0,4)

    _cache =  _add.__cache__()
    _func = _add.__wrapped__

    # do a lookup
    assert _add.lookup(2,0) == _func(2,0)

    # generate the key, and do a look-up
    key = _add.key(2,0)
    assert _cache[key] == _func(2,0)

    # look-up the key again, doing a little more work...
    lookup = keygen('self','**')(_func)
    lookup.register(hasher)
    key = lookup(2,0)
    assert _cache[key] == _func(2,0)

    # since we have the 'key lookup', let's play with lookup a bit
    assert lookup.valid()
    assert lookup.call() == _func(2,0)


######################################################
# more of the same...
class Foo(object):
  @keygen('self')
  def bar(self, x,y):
    return x+y

class _Foo(object):
  @inf_cache(ignore='self')
  def bar(self, x,y):
    return x+y

def test_foo():
    fu = Foo()
    assert fu.bar(1,2) == ('x', 1, 'y', 2)
    assert Foo.bar(fu,1,2) == ('x', 1, 'y', 2)

    _fu = _Foo()
    _fu.bar(1,2)
    _fu.bar(2,2)
    _fu.bar(2,3)
    _fu.bar(1,2)
    assert len(_fu.bar.__cache__()) == 3
    assert _fu.bar.__cache__()[_fu.bar.key(_fu,1,2)] == 3
    assert _fu.bar.lookup(_fu,1,2) == 3


if __name__ == '__main__':
    test_adder()
    test_memoize()
    test_foo()
