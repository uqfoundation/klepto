klepto
====
persistent caching to memory, disk, or database

About Klepto
------------
`klepto` extends python's `lru_cache` to utilize different keymaps and
alternate caching algorithms, such as `lfu_cache` and `mru_cache`.
While caching is meant for fast access to saved results, `klepto` also
has archiving capabilities, for longer-term storage. `klepto` uses a
simple dictionary-sytle interface for all caches and archives, and all
caches can be applied to any python function as a decorator. Keymaps
are algorithms for converting a function's input signature to a unique
dictionary, where the function's results are the dictionary value.
Thus for `y = f(x)`, `y` will be stored in `cache[x]` (e.g. `{x:y}`).

`klepto` provides both standard and 'safe' caching, where safe caches
are slower but can recover from hashing errors. `klepto` is intended
to be used for distributed and parallel computing, where several of
the keymaps serialize the stored objects. Caches and archives are
intended to be read/write accessible from different threads and
processes. `klepto` enables a user to decorate a function, save the
results to a file or database archive, close the interpreter,
start a new session, and reload the function and it's cache.

`klepto` is part of `pathos`, a python framework for heterogenous computing.
`klepto` is in active development, so any user feedback, bug reports, comments,
or suggestions are highly appreciated.  A list of known issues is maintained
at http://trac.mystic.cacr.caltech.edu/project/pathos/query, with a public
ticket list at https://github.com/uqfoundation/klepto/issues.


Major Features
--------------
`klepto` has standard and 'safe' variants of the following::

* `lfu_cache` - the least-frequently-used caching algorithm
* `lru_cache` - the least-recently-used caching algorithm
* `mru_cache` - the most-recently-used caching algorithm
* `rr_cache` - the random-replacement caching algorithm
* `no_cache` - a dummy caching interface to archiving
* `inf_cache` - an infinitely-growing cache

`klepto` has the following archive types::

* `file_archive` - a dictionary-style interface to a file
* `dir_archive` - a dictionary-style interface to a folder of files
* `sqltable_archive` - a dictionary-style interface to a sql database table
* `sql_archive` - a dictionary-style interface to a sql database
* `hdfdir_archive` - a dictionary-style interface to a folder of hdf5 files
* `hdf_archive` - a dictionary-style interface to a hdf5 file
* `dict_archive` - a dictionary with an archive interface
* `null_archive` - a dictionary-style interface to a dummy archive 

`klepto` provides the following keymaps::

* `keymap` - keys are raw python objects
* `hashmap` - keys are a hash for the python object
* `stringmap` - keys are the python object cast as a string
* `picklemap` - keys are the serialized python object

`klepto` also includes a few useful decorators providing::

* simple, shallow, or deep rounding of function arguments
* cryptographic key generation, with masking of selected arguments


Current Release
---------------
The latest released version of `klepto` is available from::
    http://trac.mystic.cacr.caltech.edu/project/pathos

or::
    https://github.com/uqfoundation/klepto/releases

or also::
    https://pypi.python.org/pypi/klepto

`klepto` is distributed under a 3-clause BSD license.


Development Version
-------------------
You can get the latest development version with all the shiny new features at::
    https://github.com/uqfoundation

If you have a new contribution, please submit a pull request.


More Information
----------------
Probably the best way to get started is to look at the tests
that are provide within `klepto`. See `klepto.tests` for a set of scripts
that test the caching and archiving functionalities in `klepto`. The
source code is also generally well documented, so further questions may
be resolved by inspecting the code itself. Please also feel free to submit
a ticket on github, or ask a question on stackoverflow (@Mike McKerns).

`klepto` is an active research tool. There are a growing number of publications
and presentations that discuss real-world examples and new features of `klepto`
in greater detail than presented in the user's guide.  If you would like to
share how you use `klepto` in your work, please post a link or send an email
(to mmckerns at uqfoundation dot org).


Citation
--------
If you use `klepto` to do research that leads to publication, we ask that you
acknowledge use of `klepto` by citing the following in your publication::

    Michael McKerns and Michael Aivazis,
    "pathos: a framework for heterogeneous computing", 2010- ;
    http://dev.danse.us/trac/pathos

Please see http://trac.mystic.cacr.caltech.edu/project/pathos for
further information.

