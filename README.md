klepto
======
persistent caching to memory, disk, or database

About Klepto
------------
``klepto`` extends Python's ``lru_cache`` to utilize different keymaps and
alternate caching algorithms, such as ``lfu_cache`` and ``mru_cache``.
While caching is meant for fast access to saved results, ``klepto`` also
has archiving capabilities, for longer-term storage. ``klepto`` uses a
simple dictionary-sytle interface for all caches and archives, and all
caches can be applied to any Python function as a decorator. Keymaps
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

``klepto`` is part of ``pathos``, a Python framework for heterogeneous computing.
``klepto`` is in active development, so any user feedback, bug reports, comments,
or suggestions are highly appreciated.  A list of issues is located at https://github.com/uqfoundation/klepto/issues, with a legacy list maintained at https://uqfoundation.github.io/project/pathos/query.


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

* ``keymap`` - keys are raw Python objects
* ``hashmap`` - keys are a hash for the Python object
* ``stringmap`` - keys are the Python object cast as a string
* ``picklemap`` - keys are the serialized Python object

``klepto`` also includes a few useful decorators providing:

* simple, shallow, or deep rounding of function arguments
* cryptographic key generation, with masking of selected arguments


Current Release
[![Downloads](https://static.pepy.tech/personalized-badge/klepto?period=total&units=international_system&left_color=grey&right_color=blue&left_text=pypi%20downloads)](https://pepy.tech/project/klepto)
[![Conda Downloads](https://img.shields.io/conda/dn/conda-forge/klepto?color=blue&label=conda%20downloads)](https://anaconda.org/conda-forge/klepto)
[![Stack Overflow](https://img.shields.io/badge/stackoverflow-get%20help-black.svg)](https://stackoverflow.com/questions/tagged/klepto)
---------------
The latest released version of ``klepto`` is available from:
    https://pypi.org/project/klepto

``klepto`` is distributed under a 3-clause BSD license.


Development Version
[![Support](https://img.shields.io/badge/support-the%20UQ%20Foundation-purple.svg?style=flat&colorA=grey&colorB=purple)](http://www.uqfoundation.org/pages/donate.html)
[![Documentation Status](https://readthedocs.org/projects/klepto/badge/?version=latest)](https://klepto.readthedocs.io/en/latest/?badge=latest)
[![Build Status](https://travis-ci.com/uqfoundation/klepto.svg?label=build&logo=travis&branch=master)](https://travis-ci.com/github/uqfoundation/klepto)
[![codecov](https://codecov.io/gh/uqfoundation/klepto/branch/master/graph/badge.svg)](https://codecov.io/gh/uqfoundation/klepto)
-------------------
You can get the latest development version with all the shiny new features at:
    https://github.com/uqfoundation

If you have a new contribution, please submit a pull request.


Installation
------------
``klepto`` can be installed with ``pip``::

    $ pip install klepto

To include optional archive backends, such as HDF5 and SQL, in the install::

    $ pip install klepto[archives]

To include optional serializers, such as ``jsonpickle``, in the install::

    $ pip install klepto[crypto]


Requirements
------------
``klepto`` requires:

* ``python`` (or ``pypy``), **>=3.7**
* ``setuptools``, **>=42**
* ``dill``, **>=0.3.7**
* ``pox``, **>=0.3.3**

Optional requirements:

* ``h5py``, **>=2.8.0**
* ``pandas``, **>=0.17.0**
* ``sqlalchemy``, **>=1.4.0**
* ``jsonpickle``, **>=0.9.6**
* ``cloudpickle``, **>=0.5.2**


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
    https://uqfoundation.github.io/project/pathos

Please see https://uqfoundation.github.io/project/pathos or
http://arxiv.org/pdf/1202.1056 for further information.

