#!/usr/bin/env python
#
# Author: Mike McKerns (mmckerns @caltech and @uqfoundation)
# Copyright (c) 2013-2016 California Institute of Technology.
# Copyright (c) 2016-2021 The Uncertainty Quantification Foundation.
# License: 3-clause BSD.  The full license text is available at:
#  - https://github.com/uqfoundation/klepto/blob/master/LICENSE

import os
import sys
# drop support for older python
unsupported = None
if sys.version_info < (2, 7):
    unsupported = 'Versions of Python before 2.7 are not supported'
elif (3, 0) <= sys.version_info < (3, 6):
    unsupported = 'Versions of Python before 3.6 are not supported'
if unsupported:
    raise ValueError(unsupported)

# set version numbers
stable_version = '0.2.1'
target_version = '0.2.1'
is_release = stable_version == target_version

# check if easy_install is available
try:
#   import __force_distutils__ #XXX: uncomment to force use of distutills
    from setuptools import setup
    has_setuptools = True
except ImportError:
    from distutils.core import setup
    has_setuptools = False

# generate version number
if os.path.exists('klepto/info.py'):
    # is a source distribution, so use existing version
    os.chdir('klepto')
    with open('info.py','r') as f:
        f.readline() # header
        this_version = f.readline().split()[-1].strip("'")
    os.chdir('..')
elif stable_version == target_version:
    # we are building a stable release
    this_version = target_version
else:
    # we are building a distribution
    this_version = target_version + '.dev0'
    if is_release:
        from datetime import date
        today = "".join(date.isoformat(date.today()).split('-'))
        this_version += "-" + today

# get the license info
with open('LICENSE') as file:
    license_text = file.read()

# generate the readme text
long_description = \
"""-------------------------------------------------------
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

This documentation is for version ``klepto-%(thisver)s``.

The latest released version of ``klepto`` is available from:

    https://pypi.org/project/klepto

``klepto`` is distributed under a 3-clause BSD license.

    >>> import klepto
    >>> klepto.license()


Development Version 
===================

You can get the latest development version with all the shiny new features at:

    https://github.com/uqfoundation

If you have a new contribution, please submit a pull request.


Installation
============

``klepto`` is packaged to install from source, so you must
download the tarball, unzip, and run the installer::

    [download]
    $ tar -xvzf klepto-%(relver)s.tar.gz
    $ cd klepto-%(relver)s
    $ python setup py build
    $ python setup py install

You will be warned of any missing dependencies and/or settings
after you run the "build" step above. 

Alternately, ``klepto`` can be installed with ``pip`` or ``easy_install``::

    $ pip install klepto


Requirements
============

``klepto`` requires:

    - ``python``, **version == 2.7** or **version >= 3.6**, or ``pypy``
    - ``dill``, **version >= 0.3.4**
    - ``pox``, **version >= 0.3.0**

Optional requirements:

    - ``h5py``, **version >= 2.8.0**
    - ``pandas``, **version >= 0.17.0**
    - ``sqlalchemy``, **version >= 0.8.4**
    - ``jsonpickle``, **version >= 0.9.6**
    - ``cloudpickle``, **version >= 0.5.2**
    - ``setuptools``, **version >= 0.6**


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

""" % {'relver' : stable_version, 'thisver' : this_version}

# write readme file
with open('README', 'w') as file:
    file.write(long_description)

# generate 'info' file contents
def write_info_py(filename='klepto/info.py'):
    contents = """# THIS FILE GENERATED FROM SETUP.PY
this_version = '%(this_version)s'
stable_version = '%(stable_version)s'
readme = '''%(long_description)s'''
license = '''%(license_text)s'''
"""
    with open(filename, 'w') as file:
        file.write(contents % {'this_version' : this_version,
                               'stable_version' : stable_version,
                               'long_description' : long_description,
                               'license_text' : license_text })
    return

# write info file
write_info_py()

# build the 'setup' call
setup_code = """
setup(name='klepto',
      version='%s',
      description='persistent caching to memory, disk, or database',
      long_description = '''%s''',
      author = 'Mike McKerns',
      maintainer = 'Mike McKerns',
      license = '3-clause BSD',
      platforms = ['Linux', 'Windows', 'Mac'],
      url = 'https://github.com/uqfoundation/klepto',
      download_url = 'https://github.com/uqfoundation/klepto/releases/download/klepto-%s/klepto-%s.tar.gz',
      classifiers = ['Development Status :: 5 - Production/Stable',
                     'Intended Audience :: Developers',
                     'Intended Audience :: Science/Research',
                     'License :: OSI Approved :: BSD License',
                     'Programming Language :: Python :: 2',
                     'Programming Language :: Python :: 2.7',
                     'Programming Language :: Python :: 3',
                     'Programming Language :: Python :: 3.6',
                     'Programming Language :: Python :: 3.7',
                     'Programming Language :: Python :: 3.8',
                     'Programming Language :: Python :: 3.9',
                     'Topic :: Database',
                     'Topic :: Scientific/Engineering',
                     'Topic :: Software Development'],

      packages = ['klepto','klepto.tests'],
      package_dir = {'klepto':'klepto','klepto.tests':'tests'},
""" % (target_version, long_description, stable_version, stable_version)

# add dependencies
sysversion = sys.version_info[:3]
dill_version = '>=0.3.4'
pox_version = '>=0.3.0'
sqlalchemy_version = '>=0.8.4'
h5py_version = '>=2.8.0, <3.0.0' #FIXME: see issue #88
if sysversion < (3,5,3):
    pandas_version = '>=0.17.0, <0.25.0'
elif sysversion < (3,6,1):
    pandas_version = '>=0.17.0, <1.0.0'
elif sysversion < (3,7,1):
    pandas_version = '>=0.17.0, <1.2.0'
else:
    pandas_version = '>=0.17.0'
if has_setuptools:
    setup_code += """
      zip_safe=False,
      install_requires = ['dill%s','pox%s'],
      extras_require = {'archives': ['h5py%s','sqlalchemy%s','pandas%s']},
""" % (dill_version, pox_version, h5py_version, sqlalchemy_version, pandas_version)

# add the scripts, and close 'setup' call
setup_code += """
      )
"""

# exec the 'setup' code
exec(setup_code)

# if dependencies are missing, print a warning
try:
    import dill
    import pox
   #import sqlalchemy
except ImportError:
    print ("\n***********************************************************")
    print ("WARNING: One of the following dependencies is unresolved:")
    print ("    dill %s" % dill_version)
    print ("    pox %s" % pox_version)
   #print ("    sqlalchemy %s" % sqlalchemy_version)
    print ("***********************************************************\n")


if __name__=='__main__':
    pass

# end of file
