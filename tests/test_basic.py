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
    return


if __name__ == '__main__':

    from klepto.archives import *
    from klepto.keymaps import keymap, hashmap, stringmap, picklemap
    from klepto.keymaps import SENTINEL, NOSENTINEL
    seed(1234) # random seed

    #XXX: archive/cache should allow scalar and list, also dict (as new table) ?
    dicts = [
      {},
      {'a':1},
      {'a':[1,2]},
      {'a':{'x':3}},
    ]
    init = dicts[0]

    na = null_archive
    da = dict_archive
    fa = file_archive
    db = sql_archive
    dr = dir_archive
    caches = [
      cache(archive=na(), **init),
      cache(archive=da(), **init),
      cache(archive=fa(filename=None,serialized=True), **init),
      cache(archive=fa(filename=None,serialized=False), **init),
      cache(archive=fa(filename='xxxx.pkl',serialized=True), **init),
      cache(archive=fa(filename='xxxx.py',serialized=False), **init),
     #cache(archive=dr(dirname='imemo',serialized=False), **init),
     #cache(archive=dr(dirname='pmemo',serialized=True), **init),
     #cache(archive=dr(dirname='jmemo',serialized=True,fast=True), **init),
     #cache(archive=dr(dirname='zmemo',serialized=True,compression=1), **init),
     #cache(archive=dr(dirname='mmemo',serialized=True,memmode='r+'), **init),
     #cache(archive=db(database=None,table=None), **init), 
     #cache(archive=db(database='memo.db',table=None), **init), 
     #cache(archive=db(database=None,table='memo'), **init), 
    ]
    #FIXME: even 'safe' archives throw Error when cache.load, cache.dump fails
    #       (often demonstrated in sql_archive, as it barfs on tuple & dict)

    #XXX: when running a single map, there should be 3 possible results:
    #     1) flat=False may produce unhashable keys: all misses
    #     2) typed=False doesn't distinguish float & int: more hits & loads
    #     3) typed=True distingushes float & int: less hits & loads
    #XXX: due to the seed, each of the 3 cases should yield the same results
    maps = [
      None,
      keymap(typed=False, flat=True, sentinel=NOSENTINEL),
      keymap(typed=False, flat=False, sentinel=NOSENTINEL),
      keymap(typed=True, flat=True, sentinel=NOSENTINEL),
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
        func = [_test_cache(cache, mapper) for cache in caches]
        _cleanup()

        for f in func:
           #print (f.info())
            assert f.info().hit + f.info().miss + f.info().load == N


# EOF
