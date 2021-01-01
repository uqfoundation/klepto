#!/usr/bin/env python
#
# Author: Mike McKerns (mmckerns @caltech and @uqfoundation)
# Copyright (c) 2013-2016 California Institute of Technology.
# Copyright (c) 2016-2021 The Uncertainty Quantification Foundation.
# License: 3-clause BSD.  The full license text is available at:
#  - https://github.com/uqfoundation/klepto/blob/master/LICENSE

from klepto.safe import lru_cache as memoized
from random import choice, seed

N = 100

def _test_cache(cache, keymap=None, maxsize=50, rangelimit=10, tries=N):

    @memoized(maxsize=maxsize, cache=cache, keymap=keymap)
    def f(x, y):
        return 3*x+y

    domain = list(range(rangelimit))
    domain += [float(i) for i in domain]
    for i in range(tries):
        r = f(choice(domain), choice(domain))

    f.dump()
    return f


def _cleanup():
    import os
    import pox
    try: os.remove('memo.pkl')
    except: pass
    try: os.remove('xxxx.pkl')
    except: pass
    try: os.remove('memo.py')
    except: pass
    try: os.remove('memo.pyc')
    except: pass
    try: os.remove('memo.pyo')
    except: pass
    try: os.remove('memo.pyd')
    except: pass
    try: os.remove('xxxx.py')
    except: pass
    try: os.remove('xxxx.pyc')
    except: pass
    try: os.remove('xxxx.pyo')
    except: pass
    try: os.remove('xxxx.pyd')
    except: pass
    try: os.remove('memo.db')
    except: pass
    try: pox.rmtree('memoi')
    except: pass
    try: pox.rmtree('memoj')
    except: pass
    try: pox.rmtree('memom')
    except: pass
    try: pox.rmtree('memop')
    except: pass
    try: pox.rmtree('memoz')
    except: pass
    try: pox.rmtree('memo')
    except: pass
    return


from klepto.archives import *
from klepto.keymaps import keymap, hashmap, stringmap, picklemap
from klepto.keymaps import SENTINEL, NOSENTINEL

def test_combinations():
    seed(1234) # random seed

    #XXX: archive/cache should allow scalar and list, also dict (as new table) ?
    dicts = [
      {},
      {'a':1},
      {'a':[1,2]},
      {'a':{'x':3}},
    ]
    init = dicts[0]

    archives = [
      null_archive(None,init),
      dict_archive(None,init),
      file_archive(None,init,serialized=True),
      file_archive(None,init,serialized=False),
      file_archive('xxxx.pkl',init,serialized=True),
      file_archive('xxxx.py',init,serialized=False),
      dir_archive('memoi',init,serialized=False),
      dir_archive('memop',init,serialized=True),
      dir_archive('memoj',init,serialized=True,fast=True),
      dir_archive('memoz',init,serialized=True,compression=1),
      dir_archive('memom',init,serialized=True,memmode='r+'),
     #sqltable_archive(None,init),
     #sqltable_archive('sqlite:///memo.db',init),
     #sqltable_archive('memo',init),
     #sql_archive(None,init),
     #sql_archive('sqlite:///memo.db',init),
     #sql_archive('memo',init),
    ]
    #FIXME: even 'safe' archives throw Error when cache.load, cache.dump fails
    #       (often demonstrated in sqltable_archive, as barfs on tuple & dict)

    #XXX: when running a single map, there should be 3 possible results:
    #     1) flat=False may produce unhashable keys: all misses
    #     2) typed=False doesn't distinguish float & int: more hits & loads
    #     3) typed=True distingushes float & int: less hits & loads
    #XXX: due to the seed, each of the 3 cases should yield the same results
    maps = [
      None,
      keymap(typed=False, flat=True, sentinel=NOSENTINEL),
      keymap(typed=False, flat=False, sentinel=NOSENTINEL),
#FIXME: keymap of (typed=True,flat=True) fails w/ dir_archive on Windows b/c
#     keymap(typed=True, flat=True, sentinel=NOSENTINEL), # bad directory name?
      keymap(typed=True, flat=False, sentinel=NOSENTINEL),
     #keymap(typed=False, flat=True, sentinel=SENTINEL),
     #keymap(typed=False, flat=False, sentinel=SENTINEL),
     #keymap(typed=True, flat=True, sentinel=SENTINEL),
     #keymap(typed=True, flat=False, sentinel=SENTINEL),
      hashmap(typed=False, flat=True, sentinel=NOSENTINEL),
      hashmap(typed=False, flat=False, sentinel=NOSENTINEL),
      hashmap(typed=True, flat=True, sentinel=NOSENTINEL),
      hashmap(typed=True, flat=False, sentinel=NOSENTINEL),
     #hashmap(typed=False, flat=True, sentinel=SENTINEL),
     #hashmap(typed=False, flat=False, sentinel=SENTINEL),
     #hashmap(typed=True, flat=True, sentinel=SENTINEL),
     #hashmap(typed=True, flat=False, sentinel=SENTINEL),
      stringmap(typed=False, flat=True, sentinel=NOSENTINEL),
      stringmap(typed=False, flat=False, sentinel=NOSENTINEL),
      stringmap(typed=True, flat=True, sentinel=NOSENTINEL),
      stringmap(typed=True, flat=False, sentinel=NOSENTINEL),
     #stringmap(typed=False, flat=True, sentinel=SENTINEL),
     #stringmap(typed=False, flat=False, sentinel=SENTINEL),
     #stringmap(typed=True, flat=True, sentinel=SENTINEL),
     #stringmap(typed=True, flat=False, sentinel=SENTINEL),
      picklemap(typed=False, flat=True, sentinel=NOSENTINEL),
      picklemap(typed=False, flat=False, sentinel=NOSENTINEL),
      picklemap(typed=True, flat=True, sentinel=NOSENTINEL),
      picklemap(typed=True, flat=False, sentinel=NOSENTINEL),
     #picklemap(typed=False, flat=True, sentinel=SENTINEL),
     #picklemap(typed=False, flat=False, sentinel=SENTINEL),
     #picklemap(typed=True, flat=True, sentinel=SENTINEL),
     #picklemap(typed=True, flat=False, sentinel=SENTINEL),
    ]
    #XXX: should have option to serialize value (as well as key) ?

    for mapper in maps:
       #print (mapper)
        func = [_test_cache(cache, mapper) for cache in archives]
        _cleanup()

        for f in func:
           #print (f.info())
            assert f.info().hit + f.info().miss + f.info().load == N


if __name__ == '__main__':
    test_combinations()
