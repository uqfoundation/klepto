from klepto.safe import lru_cache as memoized
from random import choice, seed

def _test_cache(cache, keymap=None, maxsize=50, rangelimit=10, tries=100):

    @memoized(maxsize=maxsize, cache=cache, keymap=keymap)
    def f(x, y):
        return 3*x+y

    domain = list(range(rangelimit))
    domain += [float(i) for i in domain]
    for i in range(tries):
        r = f(choice(domain), choice(domain))

    f.dump()
    return f


if __name__ == '__main__':

    from klepto.archives import *
    from klepto.keymaps import keymap, hashmap, stringmap, picklemap
    from klepto.keymaps import SENTINEL, NOSENTINEL
    seed(1234) # random seed

    #XXX: archive/cache should allow scalar and list, also dict (as new table) ?
    init = {}
    #init = {'a':1}
    #init = {'a':[1,2]}
    #init = {'a':{'x':3}}

    ad = archive_dict
    na = null_archive
    fa = file_archive
    db = db_archive
    caches = [
      ad(archive=na(), **init),
      ad(archive=ad(), **init),
      ad(archive=fa(filename=None,serialized=True), **init),
      ad(archive=fa(filename=None,serialized=False), **init),
      ad(archive=fa(filename='xxxx.pkl',serialized=True), **init),
      ad(archive=fa(filename='xxxx.py',serialized=False), **init),
      ad(archive=db(database=None,table=None), **init), 
      ad(archive=db(database='memo.db',table=None), **init), 
      ad(archive=db(database=None,table='memo'), **init), 
    ]

    mapper = None
    #mapper = keymap(typed=False, flat=True, sentinel=NOSENTINEL) 
    #mapper = hashmap(typed=False, flat=True, sentinel=NOSENTINEL)
    #mapper = stringmap(typed=False, flat=True, sentinel=NOSENTINEL)
    #mapper = picklemap(typed=False, flat=True, sentinel=NOSENTINEL)
    #XXX: hashmap gives different results... that's bad, right ?
    #XXX: should have option to serialize value (as well as key) ?

    func = [_test_cache(cache, mapper) for cache in caches]

    for f in func:
        print (f.info())

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


# EOF
