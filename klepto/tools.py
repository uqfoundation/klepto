#!/usr/bin/env python
#
# Author: Mike McKerns (mmckerns @caltech and @uqfoundation)
# Copyright (c) 2013-2016 California Institute of Technology.
# Copyright (c) 2016-2023 The Uncertainty Quantification Foundation.
# License: 3-clause BSD.  The full license text is available at:
#  - https://github.com/uqfoundation/klepto/blob/master/LICENSE
"""
Assorted python tools

Main functions exported are:: 
    - isiterable: check if an object is iterable

"""

try:
    import ctypes
    # if using `pypy`, pythonapi is not found
    IS_PYPY = not hasattr(ctypes, 'pythonapi')
except ImportError:
    IS_PYPY = False

from collections import namedtuple
CacheInfo = namedtuple("CacheInfo", ['hit','miss','load','maxsize','size'])

__all__ = ['isiterable']

def isiterable(x):
    """check if an object is iterable"""
   #try:
   #    from collections import Iterable
   #    return isinstance(x, Iterable)
   #except ImportError:
    try:
        iter(x)
        return True
    except TypeError: return False
   #return hasattr(x, '__len__') or hasattr(x, '__iter__')

def _b(message):
    """convert string to correct format for buffer object"""
    import codecs
    return codecs.latin_1_encode(message)[0]


if __name__=='__main__':
    pass


# End of file
