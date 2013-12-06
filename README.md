klepto
====
a utility for caching and archiving

About Klepto
----------
Klepto extends python's 'lru_cache' to utilize different keymaps and
alternate caching algorithms, such as 'lfu_cache' and 'mru_cache'.
While caching is meant for fast access to saved results, klepto also
has archiving capabilities, for longer-term storage. Klepto uses a
simple dictionary-sytle interface for all caches and archives, and all
caches can be applied to any python function as a decorator. Keymaps
are algorithms for converting a function's input signature to a unique
dictionary, where the function's results are the dictionary value.
Thus for `y = f(x)`, `y` will be stored in `cache[x]` (e.g. `{x:y}`).

Klepto provides both standard and 'safe' caching, where safe caches
are slower but can recover from hashing errors. Klepto is intended
to be used for distributed and parallel computing, where several of
the keymaps serialize the stored objects. Caches and archives are
intended to be read/write accessible from different threads and
processes. Klepto enables a user to decorate a function, save the
results to a file or database archive, close the interpreter,
start a new session, and reload the function and it's cache.

Klepto is part of pathos, a python framework for heterogenous computing.
Klepto is in the early development stages, and any user feedback is
highly appreciated. Contact Mike McKerns [mmckerns at caltech dot edu]
with comments, suggestions, and any bugs you may find. A list of known
issues is maintained at http://trac.mystic.cacr.caltech.edu/project/pathos/query.


Major Features
--------------
Klepto has standard and 'safe' variants of the following::

* 'lfu_cache' - the least-frequently-used caching algorithm
* 'lru_cache' - the least-recently-used caching algorithm
* 'mru_cache' - the most-recently-used caching algorithm
* 'rr_cache' - the random-replacement caching algorithm
* 'no_cache' - a dummy caching interface to archiving
* 'inf_cache' - an infinitely-growing cache

Klepto has the following archive types::

* 'file_archive' - a dictionary-style interface to a file
* 'db_archive' - a dictionary-style interface to a database
* 'null_archive' - a dictionary-style interface to a dummy archive 

Klepto provides the following keymaps::

* 'keymap' - keys are raw python objects
* 'hashmap' - keys are the hash for the python object
* 'stringmap' - keys are the `__repr__` for the python object
* 'picklemap' - keys are the serialized python object

Klepto also includes a few useful decorators providing::

* simple, shallow, or deep rounding

Current Release
---------------
The latest released version of klepto is available from::
    http://dev.danse.us/trac/pathos

Klepto is distributed under a 3-clause BSD license.

Development Release
-------------------
You can get the latest development release with all the shiny new features at::
    http://dev.danse.us/packages.

or even better, fork us on our github mirror of the svn trunk::
    https://github.com/uqfoundation

Citation
--------
If you use klepto to do research that leads to publication, we ask that you
acknowledge use of klepto by citing the following in your publication::

    Michael McKerns and Michael Aivazis,
    "pathos: a framework for heterogeneous computing", 2010- ;
    http://dev.danse.us/trac/pathos

More Information
----------------
Probably the best way to get started is to look at the tests
that are provide within klepto. See `klepto.tests` for a set of scripts
that test klepto's caching and archiving functionalities. Klepto's
source code is also generally well documented, so further questions may
be resolved by inspecting the code itself, or through browsing the reference
manual. For those who like to leap before they look, you can jump right to
the installation instructions. If the aforementioned documents do not
adequately address your needs, please send us feedback.

Klepto is an active research tool. There are a growing number of publications and presentations that
discuss real-world examples and new features of klepto in greater detail than presented in the user's guide. 
If you would like to share how you use klepto in your work, please send us a link.
