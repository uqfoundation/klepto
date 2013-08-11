#!/usr/bin/env python
#
# Mike McKerns, Caltech

"""
Assorted python tools

Main functions exported are:: 
    - isiterable: check if an object is iterable

"""

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


if __name__=='__main__':
    pass


# End of file
