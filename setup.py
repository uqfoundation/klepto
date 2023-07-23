#!/usr/bin/env python
#
# Author: Mike McKerns (mmckerns @caltech and @uqfoundation)
# Copyright (c) 2013-2016 California Institute of Technology.
# Copyright (c) 2016-2023 The Uncertainty Quantification Foundation.
# License: 3-clause BSD.  The full license text is available at:
#  - https://github.com/uqfoundation/klepto/blob/master/LICENSE

import os
import sys
# drop support for older python
if sys.version_info < (3, 7):
    unsupported = 'Versions of Python before 3.7 are not supported'
    raise ValueError(unsupported)

# get distribution meta info
here = os.path.abspath(os.path.dirname(__file__))
sys.path.append(here)
from version import (__version__, __author__, __contact__ as AUTHOR_EMAIL,
                     get_license_text, get_readme_as_rst, write_info_file)
LICENSE = get_license_text(os.path.join(here, 'LICENSE'))
README = get_readme_as_rst(os.path.join(here, 'README.md'))
    
# write meta info file
write_info_file(here, 'klepto', doc=README, license=LICENSE,
                version=__version__, author=__author__)
del here, get_license_text, get_readme_as_rst, write_info_file

# check if setuptools is available
try:
    from setuptools import setup
    from setuptools.dist import Distribution
    has_setuptools = True
except ImportError:
    from distutils.core import setup
    Distribution = object
    has_setuptools = False

# build the 'setup' call
setup_kwds = dict(
    name='klepto',
    version=__version__,
    description='persistent caching to memory, disk, or database',
    long_description = README.strip(),
    author = __author__,
    author_email = AUTHOR_EMAIL,
    maintainer = __author__,
    maintainer_email = AUTHOR_EMAIL,
    license = 'BSD-3-Clause',
    platforms = ['Linux', 'Windows', 'Mac'],
    url = 'https://github.com/uqfoundation/klepto',
    download_url = 'https://pypi.org/project/klepto/#files',
    project_urls = {
        'Documentation':'http://klepto.rtfd.io',
        'Source Code':'https://github.com/uqfoundation/klepto',
        'Bug Tracker':'https://github.com/uqfoundation/klepto/issues',
    },
    python_requires = '>=3.7',
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Database',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development',
    ],
    packages = ['klepto','klepto.tests'],
    package_dir = {'klepto':'klepto', 'klepto.tests':'klepto/tests'},
)

# force python-, abi-, and platform-specific naming of bdist_wheel
class BinaryDistribution(Distribution):
    """Distribution which forces a binary package with platform name"""
    def has_ext_modules(foo):
        return True

# define dependencies
sysversion = sys.version_info[:3]
dill_version = 'dill>=0.3.7'
pox_version = 'pox>=0.3.3'
jsonpickle_version = 'jsonpickle>=0.9.6'
cloudpickle_version = 'cloudpickle>=0.5.2'
sqlalchemy_version = 'sqlalchemy>=1.4.0'
h5py_version = 'h5py>=2.8.0'
if sysversion < (3,7,1):
    pandas_version = 'pandas>=0.17.0, <1.2.0'
else:
    pandas_version = 'pandas>=0.17.0'
# add dependencies
depend = [pox_version, dill_version]
extras = {'archives': [h5py_version, sqlalchemy_version, pandas_version], 'crypto': [jsonpickle_version, cloudpickle_version]}
# update setup kwds
if has_setuptools:
    setup_kwds.update(
        zip_safe=False,
        # distclass=BinaryDistribution,
        install_requires=depend,
        extras_require=extras,
    )

# call setup
setup(**setup_kwds)

# if dependencies are missing, print a warning
try:
    import dill
    import pox
    #import jsonpickle
    #import cloudpickle
    #import sqlalchemy
    #import h5py
    #import pandas
except ImportError:
    print ("\n***********************************************************")
    print ("WARNING: One of the following dependencies is unresolved:")
    print ("    %s" % dill_version)
    print ("    %s" % pox_version)
    print ("    %s (optional)" % jsonpickle_version)
    print ("    %s (optional)" % cloudpickle_version)
    print ("    %s (optional)" % sqlalchemy_version)
    print ("    %s (optional)" % h5py_version)
    print ("    %s (optional)" % pandas_version)
    print ("***********************************************************\n")


if __name__=='__main__':
    pass

# end of file
