#!/usr/bin/env python
#
# Author: Mike McKerns (mmckerns @caltech and @uqfoundation)
# Copyright (c) 2013-2016 California Institute of Technology.
# Copyright (c) 2016-2023 The Uncertainty Quantification Foundation.
# License: 3-clause BSD.  The full license text is available at:
#  - https://github.com/uqfoundation/klepto/blob/master/LICENSE
"""
test speed and effectiveness of a selection of cache algorithms
"""

from klepto.archives import file_archive
from random import choice, seed

def _test_hits(algorithm, maxsize=20, keymap=None,
               rangelimit=5, tries=1000, archived=False):

    @algorithm(maxsize=maxsize, keymap=keymap, purge=True)
    def f(x, y):
        return 3*x+y

    if archived:
        f.archive(file_archive('cache.pkl',cached=False))

    domain = list(range(rangelimit))
    domain += [float(i) for i in domain]
    for i in range(tries):
        r = f(choice(domain), choice(domain))

    f.dump()
   #print(f.info())
    return f.info()


import os 
import sys
from klepto import *
#from klepto.safe import *

def test_info():
    seed(1234) # random seed

    caches = [rr_cache,mru_cache,lru_cache,lfu_cache,inf_cache,no_cache]

    # clean-up
    if os.path.exists('cache.pkl'): os.remove('cache.pkl')

   #print ("WITHOUT ARCHIVE")
    results = [_test_hits(cache, maxsize=100,
                          rangelimit=20, tries=100) for cache in caches]
    x = results[0]
    assert (x.hit, x.miss, x.load, x.maxsize, x.size) == (16,84,0,100,84)
    x = results[1]
    assert (x.hit, x.miss, x.load, x.maxsize, x.size) == (12,88,0,100,88)
    x = results[2]
    assert (x.hit, x.miss, x.load, x.maxsize, x.size) == (11,89,0,100,89)
    x = results[3]
    assert (x.hit, x.miss, x.load, x.maxsize, x.size) == (11,89,0,100,89)
    x = results[4]
    assert (x.hit, x.miss, x.load, x.maxsize, x.size) == (11,89,0,None,89)
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
    # clean-up
    if os.path.exists('cache.pkl'): os.remove('cache.pkl')

    x = results[0]
    assert (x.hit, x.miss, x.load, x.maxsize, x.size) == (11,89,0,100,89)
    x = results[1]
    assert (x.hit, x.miss, x.load, x.maxsize, x.size) == (10,66,24,100,90)
    x = results[2]
    assert (x.hit, x.miss, x.load, x.maxsize, x.size) == (10,58,32,100,90)
    x = results[3]
    assert (x.hit, x.miss, x.load, x.maxsize, x.size) == (10,37,53,100,90)
    x = results[4]
    assert (x.hit, x.miss, x.load, x.maxsize, x.size) == (5,37,58,None,95)
    x = results[5]
    assert (x.hit, x.miss, x.load, x.maxsize, x.size) == (0,25,75,0,0)
   #for cache in caches:
   #    msg = cache.__name__ + ":"
   #    msg += "%s" % str(_test_hits(cache, maxsize=100,
   #                                 rangelimit=20, tries=100, archived=True))
   #    print (msg)

   ### again, w/o purging ###

    # clean-up
    if os.path.exists('cache.pkl'): os.remove('cache.pkl')

   #print ("WITHOUT ARCHIVE")
    results = [_test_hits(cache, maxsize=50,
                          rangelimit=20, tries=100) for cache in caches]
    x = results[0]
    maxsize = x.maxsize
    assert x.size == x.maxsize # skip due to hash randomization
    x = results[1]
    assert x.size == x.maxsize # skip due to hash randomization
    x = results[2]
    assert x.size == x.maxsize # skip due to hash randomization
    x = results[3]
    assert x.size <= x.maxsize # skip due to hash randomization
    x = results[4]
    assert x.size > maxsize # skip due to hash randomization
    x = results[5]
    assert (x.hit, x.miss, x.load, x.maxsize, x.size) == (0,100,0,0,0)
   #for cache in caches:
   #    msg = cache.__name__ + ":"
   #    msg += "%s" % str(_test_hits(cache, maxsize=50, 
   #                                 rangelimit=20, tries=100))
   #    print (msg)

   #print ("\nWITH ARCHIVE")
    results = [_test_hits(cache, maxsize=50, rangelimit=20,
                          tries=100, archived=True) for cache in caches]
    # clean-up
    if os.path.exists('cache.pkl'): os.remove('cache.pkl')

    x = results[0]
    assert x.size <= x.maxsize # skip due to hash randomization
    x = results[1]
    assert x.size <= x.maxsize # skip due to hash randomization
    x = results[2]
    assert x.size <= x.maxsize # skip due to hash randomization
    x = results[3]
    assert x.size <= x.maxsize # skip due to hash randomization
    x = results[4]
    assert x.size > maxsize # skip due to hash randomization
    x = results[5]
    assert x.hit == x.maxsize == x.size # skip due to hash randomization
   #for cache in caches:
   #    msg = cache.__name__ + ":"
   #    msg += "%s" % str(_test_hits(cache, maxsize=50,
   #                                 rangelimit=20, tries=100, archived=True))
   #    print (msg)


if __name__ == '__main__':
   test_info()
