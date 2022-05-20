#!/usr/bin/env python
#
# Author: Mike McKerns (mmckerns @caltech and @uqfoundation)
# Copyright (c) 2013-2016 California Institute of Technology.
# Copyright (c) 2016-2022 The Uncertainty Quantification Foundation.
# License: 3-clause BSD.  The full license text is available at:
#  - https://github.com/uqfoundation/klepto/blob/master/LICENSE

# author, version, license, and long description
__version__ = '0.2.2'
__author__ = 'Mike McKerns'

__doc__ = """
-------------------------------------------------------
klepto: persistent caching to memory, disk, or database
-------------------------------------------------------

About Klepto
============

``klepto`` extends python's ``lru_cache`` to utilize different keymaps and
alternate caching algorithms, such as ``lfu_cache`` and ``mru_cache``.
While caching is meant for fast access to saved results, ``klepto`` also
has archiving capabilities, for longer-term storage. ``klepto`` uses a
simple dictionary-sytle interface for all caches and archives, and all
caches can be applied to any python function as a decorator. Keymaps
are algorithms for converting a function's input signature to a unique
dictionary, where the function's results are the dictionary value.
Thus for ``y = f(x)``, ``y`` will be stored in ``cache[x]`` (e.g. ``{x:y}``).

``klepto`` provides both standard and *"safe"* caching, where *"safe"* caches
are slower but can recover from hashing errors. ``klepto`` is intended
to be used for distributed and parallel computing, where several of
the keymaps serialize the stored objects. Caches and archives are
intended to be read/write accessible from different threads and
processes. ``klepto`` enables a user to decorate a function, save the
results to a file or database archive, close the interpreter,
start a new session, and reload the function and it's cache.

``klepto`` is part of ``pathos``, a python framework for heterogeneous computing.
``klepto`` is in active development, so any user feedback, bug reports, comments,
or suggestions are highly appreciated.  A list of issues is located at https://github.com/uqfoundation/klepto/issues, with a legacy list maintained at https://uqfoundation.github.io/project/pathos/query.


Major Features
==============

``klepto`` has standard and *"safe"* variants of the following:

    - ``lfu_cache`` - the least-frequently-used caching algorithm
    - ``lru_cache`` - the least-recently-used caching algorithm
    - ``mru_cache`` - the most-recently-used caching algorithm
    - ``rr_cache`` - the random-replacement caching algorithm
    - ``no_cache`` - a dummy caching interface to archiving
    - ``inf_cache`` - an infinitely-growing cache

``klepto`` has the following archive types:

    - ``file_archive`` - a dictionary-style interface to a file
    - ``dir_archive`` - a dictionary-style interface to a folder of files
    - ``sqltable_archive`` - a dictionary-style interface to a sql database table
    - ``sql_archive`` - a dictionary-style interface to a sql database
    - ``hdfdir_archive`` - a dictionary-style interface to a folder of hdf5 files
    - ``hdf_archive`` - a dictionary-style interface to a hdf5 file
    - ``dict_archive`` - a dictionary with an archive interface
    - ``null_archive`` - a dictionary-style interface to a dummy archive 

``klepto`` provides the following keymaps:

    - ``keymap`` - keys are raw python objects
    - ``hashmap`` - keys are a hash for the python object
    - ``stringmap`` - keys are the python object cast as a string
    - ``picklemap`` - keys are the serialized python object

``klepto`` also includes a few useful decorators providing:

    - simple, shallow, or deep rounding of function arguments
    - cryptographic key generation, with masking of selected arguments


Current Release
===============

The latest released version of ``klepto`` is available from:

    https://pypi.org/project/klepto

``klepto`` is distributed under a 3-clause BSD license.


Development Version 
===================

You can get the latest development version with all the shiny new features at:

    https://github.com/uqfoundation

If you have a new contribution, please submit a pull request.


Installation
============

``klepto`` can be installed with ``pip``::

    $ pip install klepto

To include optional archive backends, such as HDF5 and SQL, in the install::

    $ pip install klepto[archives]

To include optional serializers, such as ``jsonpickle``, in the install::

    $ pip install klepto[crypto]


Requirements
============

``klepto`` requires:

    - ``python`` (or ``pypy``), **==2.7** or **>=3.7**
    - ``setuptools``, **>=42**
    - ``dill``, **>=0.3.5.1**
    - ``pox``, **>=0.3.1**

Optional requirements:

    - ``h5py``, **>=2.8.0**
    - ``pandas``, **>=0.17.0**
    - ``sqlalchemy``, **>=0.8.4**
    - ``jsonpickle``, **>=0.9.6**
    - ``cloudpickle``, **>=0.5.2**


More Information
================

Probably the best way to get started is to look at the documentation at
http://klepto.rtfd.io. Also see ``klepto.tests`` for a set of scripts that
test the caching and archiving functionalities in ``klepto``.
You can run the test suite with ``python -m klepto.tests``.  The
source code is also generally well documented, so further questions may
be resolved by inspecting the code itself. Please feel free to submit
a ticket on github, or ask a question on stackoverflow (**@Mike McKerns**).
If you would like to share how you use ``klepto`` in your work, please send
an email (to **mmckerns at uqfoundation dot org**).


Citation
========

If you use ``klepto`` to do research that leads to publication, we ask that you
acknowledge use of ``klepto`` by citing the following in your publication::

    Michael McKerns and Michael Aivazis,
    "pathos: a framework for heterogeneous computing", 2010- ;
    https://uqfoundation.github.io/project/pathos

Please see https://uqfoundation.github.io/project/pathos or
further information.

"""

__license__ = """
Copyright (c) 2004-2016 California Institute of Technology.
Copyright (c) 2016-2022 The Uncertainty Quantification Foundation.
All rights reserved.

This software is available subject to the conditions and terms laid
out below. By downloading and using this software you are agreeing
to the following conditions.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met::

    - Redistribution of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.

    - Redistribution in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentations and/or other materials provided with the distribution.

    - Neither the names of the copyright holders nor the names of any of
      the contributors may be used to endorse or promote products derived
      from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""

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
