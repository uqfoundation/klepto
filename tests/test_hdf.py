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
    try: os.remove('memo.hdf5')
    except: pass
    try: os.remove('xxxx.hdf5')
    except: pass
    try: os.remove('memo.h5')
    except: pass
    try: os.remove('xxxx.h5')
    except: pass
    try: pox.rmtree('memoq')
    except: pass
    try: pox.rmtree('memor')
    except: pass
    try: pox.rmtree('memos')
    except: pass
    try: pox.rmtree('memot')
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
      hdf_archive('memo.hdf5',init,serialized=True,meta=False),
      hdf_archive('memo.h5',init,serialized=False,meta=False),
      hdf_archive('xxxx.hdf5',init,serialized=True,meta=True),
      hdf_archive('xxxx.h5',init,serialized=False,meta=True),
#     hdfdir_archive('memoq',init,serialized=False,meta=False),
      hdfdir_archive('memor',init,serialized=True,meta=False),
#     hdfdir_archive('memos',init,serialized=False,meta=True),
      hdfdir_archive('memot',init,serialized=True,meta=True),
      #FIXME: hdfdir_archive fails with serialized=False in python 3.x
    ]
    maps = [
      None,
      keymap(typed=False, flat=True, sentinel=NOSENTINEL),
      keymap(typed=False, flat=False, sentinel=NOSENTINEL),
      keymap(typed=True, flat=False, sentinel=NOSENTINEL),
      hashmap(typed=False, flat=True, sentinel=NOSENTINEL),
      hashmap(typed=False, flat=False, sentinel=NOSENTINEL),
      hashmap(typed=True, flat=True, sentinel=NOSENTINEL),
      hashmap(typed=True, flat=False, sentinel=NOSENTINEL),
      stringmap(typed=False, flat=True, sentinel=NOSENTINEL),
      stringmap(typed=False, flat=False, sentinel=NOSENTINEL),
      stringmap(typed=True, flat=True, sentinel=NOSENTINEL),
      stringmap(typed=True, flat=False, sentinel=NOSENTINEL),
      picklemap(typed=False, flat=True, sentinel=NOSENTINEL),
      picklemap(typed=False, flat=False, sentinel=NOSENTINEL),
      picklemap(typed=True, flat=True, sentinel=NOSENTINEL),
      picklemap(typed=True, flat=False, sentinel=NOSENTINEL),
    ]

    for mapper in maps:
       #print (mapper)
        func = [_test_cache(cache, mapper) for cache in archives]
        _cleanup()

        for f in func:
           #print (f.info())
            assert f.info().hit + f.info().miss + f.info().load == N


if __name__ == '__main__':
    try:
        import h5py
        test_combinations()
    except ImportError:
        print("to test hdf, install h5py")
