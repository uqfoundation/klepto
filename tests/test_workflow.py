from klepto import lru_cache as memoize
from klepto.keymaps import hashmap
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

info = Adder.__call__.info()
assert info.hit == 5
assert info.miss == 5
cache = Adder.__call__.__cache__()
assert sorted(cache.values()) == [2,3,4,5,6]

#FIXME: apparently, doesn't work for class methods (Error: multiple 'self')
#key = Adder.__call__.key(2,0)
#assert cache[key] == Adder.__call__.__wrapped__(2,0)

######################################################

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

# generate the key, and do a look-up
key = _add.key(2,0)
assert _cache[key] == _func(2,0)

# look-up the key another way...
from klepto import keygen
lookup = keygen('self','**')(_func)
lookup.register(hasher)
key = lookup(2,0)
assert _cache[key] == _func(2,0)

# play with lookup a bit
assert lookup.valid()
assert lookup.call() == _func(2,0)


# EOF

