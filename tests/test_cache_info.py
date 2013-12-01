"""
test speed and effectiveness of a selection of cache algorithms
"""

from klepto.archives import file_archive
from random import choice, seed

def _test_hits(algorithm, maxsize=20, keymap=None,
               rangelimit=5, tries=1000, archived=False):

    @algorithm(maxsize=maxsize, keymap=keymap)
    def f(x, y):
        return 3*x+y

    if archived:
        f.archive(file_archive('cache.pkl'))

    domain = list(range(rangelimit))
    domain += [float(i) for i in domain]
    for i in range(tries):
        r = f(choice(domain), choice(domain))

    f.dump()
    return f.info()


if __name__ == '__main__':

    import sys
    PY32 = ( hex(sys.hexversion) >= '0x30200f0' )
    from klepto import *
   #from klepto.safe import *
    seed(1234) # random seed

    caches = [rr_cache,mru_cache,lru_cache,lfu_cache,inf_cache,no_cache]

   #print ("WITHOUT ARCHIVE")
    results = [_test_hits(cache, maxsize=100,
                          rangelimit=20, tries=100) for cache in caches]
    x = results[0]
    if PY32:
        assert (x.hit, x.miss, x.load, x.maxsize, x.size) == (16,84,0,100,84)
    else:
        assert (x.hit, x.miss, x.load, x.maxsize, x.size) == (13,87,0,100,87)
    x = results[1]
    if PY32:
        assert (x.hit, x.miss, x.load, x.maxsize, x.size) == (12,88,0,100,88)
    else:
        assert (x.hit, x.miss, x.load, x.maxsize, x.size) == (13,87,0,100,87)
    x = results[2]
    if PY32:
        assert (x.hit, x.miss, x.load, x.maxsize, x.size) == (11,89,0,100,89)
    else:
        assert (x.hit, x.miss, x.load, x.maxsize, x.size) == (10,90,0,100,90)
    x = results[3]
    if PY32:
        assert (x.hit, x.miss, x.load, x.maxsize, x.size) == (11,89,0,100,89)
    else:
        assert (x.hit, x.miss, x.load, x.maxsize, x.size) == (8,92,0,100,92)
    x = results[4]
    if PY32:
        assert (x.hit, x.miss, x.load, x.maxsize, x.size) == (11,89,0,None,89)
    else:
        assert (x.hit, x.miss, x.load, x.maxsize, x.size) == (9,91,0,None,91)
    x = results[5]
    assert (x.hit, x.miss, x.load, x.maxsize, x.size) == (0,100,0,0,0)
   #for cache in caches:
   #    msg = cache.__name__ + ":"
   #    msg += "%s" % str(_test_hits(cache, maxsize=100, 
   #                                 rangelimit=20, tries=100))
   #    print (msg)

   #print ("\nWITH ARCHIVE")
    results = [_test_hits(cache, maxsize=100, rangelimit=20,
                          tries=100, archived=True) for cache in caches]
    x = results[0]
    if PY32:
        assert (x.hit, x.miss, x.load, x.maxsize, x.size) == (12,88,0,100,88)
    else:
        assert (x.hit, x.miss, x.load, x.maxsize, x.size) == (11,89,0,100,89)
    x = results[1]
    if PY32:
        assert (x.hit, x.miss, x.load, x.maxsize, x.size) == (8,68,24,100,92)
    else:
        assert (x.hit, x.miss, x.load, x.maxsize, x.size) == (12,70,18,100,88)
    x = results[2]
    if PY32:
        assert (x.hit, x.miss, x.load, x.maxsize, x.size) == (11,58,31,100,89)
    else:
        assert (x.hit, x.miss, x.load, x.maxsize, x.size) == (9,54,37,100,91)
    x = results[3]
    if PY32:
        assert (x.hit, x.miss, x.load, x.maxsize, x.size) == (11,36,53,100,89)
    else:
        assert (x.hit, x.miss, x.load, x.maxsize, x.size) == (11,42,47,100,89)
    x = results[4]
    if PY32:
        assert (x.hit, x.miss, x.load, x.maxsize, x.size) == (5,37,58,None,95)
    else:
        assert (x.hit, x.miss, x.load, x.maxsize, x.size) == (11,31,58,None,89)
    x = results[5]
    if PY32:
        assert (x.hit, x.miss, x.load, x.maxsize, x.size) == (0,18,82,0,0)
    else:
        assert (x.hit, x.miss, x.load, x.maxsize, x.size) == (0,22,78,0,0)
   #for cache in caches:
   #    msg = cache.__name__ + ":"
   #    msg += "%s" % str(_test_hits(cache, maxsize=100,
   #                                 rangelimit=20, tries=100, archived=True))
   #    print (msg)

    import os 
    os.remove('cache.pkl')


# EOF
