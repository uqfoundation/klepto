klepto
====
persistent caching to memory, disk, or database

About Klepto
------------
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
or suggestions are highly appreciated.  A list of issues is located at https://github.com/uqfoundation/klepto/issues, with a legacy list maintained at https://uqfoundation.github.io/pathos-issues.html.


Major Features
--------------
``klepto`` has standard and *"safe"* variants of the following:

* ``lfu_cache`` - the least-frequently-used caching algorithm
* ``lru_cache`` - the least-recently-used caching algorithm
* ``mru_cache`` - the most-recently-used caching algorithm
* ``rr_cache`` - the random-replacement caching algorithm
* ``no_cache`` - a dummy caching interface to archiving
* ``inf_cache`` - an infinitely-growing cache

``klepto`` has the following archive types:

* ``file_archive`` - a dictionary-style interface to a file
* ``dir_archive`` - a dictionary-style interface to a folder of files
* ``sqltable_archive`` - a dictionary-style interface to a sql database table
* ``sql_archive`` - a dictionary-style interface to a sql database
* ``hdfdir_archive`` - a dictionary-style interface to a folder of hdf5 files
* ``hdf_archive`` - a dictionary-style interface to a hdf5 file
* ``dict_archive`` - a dictionary with an archive interface
* ``null_archive`` - a dictionary-style interface to a dummy archive 

``klepto`` provides the following keymaps:

* ``keymap`` - keys are raw python objects
* ``hashmap`` - keys are a hash for the python object
* ``stringmap`` - keys are the python object cast as a string
* ``picklemap`` - keys are the serialized python object

``klepto`` also includes a few useful decorators providing:

* simple, shallow, or deep rounding of function arguments
* cryptographic key generation, with masking of selected arguments


Current Release
---------------
The latest released version of ``klepto`` is available from:
    https://pypi.org/project/klepto

``klepto`` is distributed under a 3-clause BSD license.


Development Version
[![Documentation Status](https://readthedocs.org/projects/klepto/badge/?version=latest)](https://klepto.readthedocs.io/en/latest/?badge=latest)
[![Travis Build Status](https://img.shields.io/travis/uqfoundation/klepto.svg?label=build&logo=travis&branch=master)](https://travis-ci.org/uqfoundation/klepto)
[![codecov](https://codecov.io/gh/uqfoundation/klepto/branch/master/graph/badge.svg)](https://codecov.io/gh/uqfoundation/klepto)
[![Downloads](https://pepy.tech/badge/klepto)](https://pepy.tech/project/klepto)
-------------------
You can get the latest development version with all the shiny new features at:
    https://github.com/uqfoundation

If you have a new contribution, please submit a pull request.


More Information
----------------
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
--------
If you use ``klepto`` to do research that leads to publication, we ask that you
acknowledge use of ``klepto`` by citing the following in your publication::

    Michael McKerns and Michael Aivazis,
    "pathos: a framework for heterogeneous computing", 2010- ;
    https://uqfoundation.github.io/pathos.html

Please see https://uqfoundation.github.io/pathos.html or
http://arxiv.org/pdf/1202.1056 for further information.

