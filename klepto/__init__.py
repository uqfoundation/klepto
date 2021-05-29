#!/usr/bin/env python
#
# Author: Mike McKerns (mmckerns @caltech and @uqfoundation)
# Copyright (c) 2013-2016 California Institute of Technology.
# Copyright (c) 2016-2021 The Uncertainty Quantification Foundation.
# License: 3-clause BSD.  The full license text is available at:
#  - https://github.com/uqfoundation/klepto/blob/master/LICENSE

# get version numbers, license, and long description
try:
    from .info import this_version as __version__
    from .info import readme as __doc__, license as __license__
except ImportError:
    msg = """First run 'python setup.py build' to build klepto."""
    raise ImportError(msg)

__author__ = 'Mike McKerns'

__doc__ = """
""" + __doc__

__license__ = """
""" + __license__


from ._cache import no_cache, inf_cache, lfu_cache, \
                    lru_cache, mru_cache, rr_cache
from ._inspect import signature, isvalid, validate, \
                      keygen, strip_markup, NULL, _keygen
from . import rounding
from . import safe
from . import archives
from . import keymaps
from . import tools
from . import crypto


def license():
    """print license"""
    print (__license__)
    return

def citation():
    """print citation"""
    print (__doc__[-238:-83])
    return

# end of file
