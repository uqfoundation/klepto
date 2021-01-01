#!/usr/bin/env python
#
# Author: Mike McKerns (mmckerns @caltech and @uqfoundation)
# Copyright (c) 2014-2016 California Institute of Technology.
# Copyright (c) 2016-2021 The Uncertainty Quantification Foundation.
# License: 3-clause BSD.  The full license text is available at:
#  - https://github.com/uqfoundation/klepto/blob/master/LICENSE

from klepto import inf_cache as memoized
from klepto.archives import *
from klepto.keymaps import picklemap

try:
    import ___________ #XXX: enable test w/o numpy.arrays
    import numpy as np
    data = np.arange(20)
    nprun = True
except ImportError:
    data = range(20)
    nprun = False

def remove(name):
    try:
        import os
        os.remove(name)
    except: #FileNotFoundError
        import pox
        pox.shutils.rmtree(name, self=True, ignore_errors=True)
    return

archives = [
### OK
  null_archive,
  dict_archive,
  file_archive,
### FIXME: on numpy array, throws ValueError('I/O operation on closed file')
  dir_archive,
### FIXME: throws RecursionError  NOTE: '\x80' not valid, but r'\x80' is valid
# sql_archive,
### FIXME: throws sql ProgrammingError (warns to use unicode strings)
# sqltable_archiver,
]


def runme(arxiv, expected=None):

    pm = picklemap(serializer='dill')

    @memoized(cache=arxiv, keymap=pm)
    def doit(x):
        return x

    doit(1)
    doit('2')
    doit(data)
    doit(lambda x:x**2)

    doit.load()
    doit.dump()
    c = doit.__cache__()
    r = getattr(c, '__archive__', '')
    info = doit.info()
    ck = c.keys()
    rk = r.keys() if r else ck
   #print(type(c))
   #print(c)
   #print(r)
   #print(info)

    # check keys are identical in cache and archive
    assert sorted(ck) == sorted(rk)

    xx = len(ck) or max(info.hit, info.miss, info.load)

    # check size and behavior
    if expected == 'hit':
        assert (info.hit, info.miss, info.load) == (xx, 0, 0)
    elif expected == 'load':
        assert (info.hit, info.miss, info.load) == (0, 0, xx)
    else:
        assert (info.hit, info.miss, info.load) == (0, xx, 0)
    return

def _test_cache(archive, name, delete=True):

    arname = 'xxxxxx'+ str(name)
    acname = 'xxxyyy'+ str(name)

    import os
    rerun = 'hit'
    hit = 'hit' if os.path.exists(arname) else None
    load = 'load' if os.path.exists(acname) else None

    # special cases
    if archive == null_archive:
        rerun, hit, load = None, None, None
    elif archive == dict_archive:
        hit, load = None, None

    ar = archive(arname, serialized=True, cached=False)
    runme(ar, hit)
    #FIXME: numpy.array fails on any 'rerun' of runme below
    if not nprun:
       runme(ar, rerun)
    if delete:
        remove(arname)
    if not nprun:
        ac = archive(acname, serialized=True, cached=True)
        runme(ac, load)
        runme(ac, 'hit')
    if delete:
        remove(acname)
    return


def test_archives():
    if not nprun:
        count = 0
        for archive in archives:
            _test_cache(archive, count, delete=False)
            count += 1

    count = 0
    for archive in archives:
        _test_cache(archive, count, delete=True)
        count += 1


if __name__ == '__main__':
    test_archives()
