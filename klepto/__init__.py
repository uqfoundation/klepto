#!/usr/bin/env python
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#                              Mike McKerns, Caltech
#                        (C) 2008-2013  All Rights Reserved
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#

# get version numbers, license, and long description
try:
    from info import this_version as __version__
    from info import readme as __doc__, license as __license__
except ImportError:
    msg = """First run 'python setup.py build' to build klepto."""
    raise ImportError(msg)

__author__ = 'Mike McKerns'

__doc__ = """
""" + __doc__

__license__ = """
""" + __license__


from _cache import *
import rounding
import safe
import archives
import keymaps
import tools


def license():
    """print license"""
    print __license__
    return

def citation():
    """print citation"""
    print __doc__[-247:-106]
    return


# end of file
