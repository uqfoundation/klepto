#!/usr/bin/env python
#
# Author: Mike McKerns (mmckerns @caltech and @uqfoundation)
# Copyright (c) 2013-2016 California Institute of Technology.
# Copyright (c) 2016-2023 The Uncertainty Quantification Foundation.
# License: 3-clause BSD.  The full license text is available at:
#  - https://github.com/uqfoundation/klepto/blob/master/LICENSE
"""
custom caching dict, which archives results to memory, file, or database
"""
from ._archives import cache, archive
from ._archives import dict_archive as _dict_archive
from ._archives import null_archive as _null_archive
from ._archives import dir_archive as _dir_archive
from ._archives import file_archive as _file_archive
from ._archives import sql_archive as _sql_archive
from ._archives import sqltable_archive as _sqltable_archive
from ._archives import hdf_archive as _hdf_archive
from ._archives import hdfdir_archive as _hdfdir_archive
from ._archives import _sqlname, _from_frame, _to_frame

__all__ = ['cache','dict_archive','null_archive','dir_archive',\
           'file_archive','sql_archive','sqltable_archive',\
           'hdf_archive','hdfdir_archive']

class dict_archive(_dict_archive):
    def __new__(dict_archive, name=None, dict=None, cached=True, **kwds):
        """initialize a dictionary with an in-memory dictionary archive backend

    Args:
        name (str, default=None): (optional) identifier string
        dict (dict, default={}): initial dictionary to seed the archive
        cached (bool, default=True): interact through an in-memory cache
        """
        if dict is None: dict = {}
        archive = _dict_archive()
        archive.__state__['id'] = None if name is None else str(name)
        if cached: archive = cache(archive=archive)
        archive.update(dict)
        return archive

    @classmethod
    def from_frame(dict_archive, dataframe):
        try:
            dataframe = dataframe.copy()
            dataframe.columns.name = dict_archive.__name__
        except AttributeError: pass
        return _from_frame(dataframe)
    pass

class null_archive(_null_archive):
    def __new__(null_archive, name=None, dict=None, cached=True, **kwds):
        """initialize a dictionary with a permanently-empty archive backend

    Args:
        name (str, default=None): (optional) identifier string
        dict (dict, default={}): initial dictionary to seed the archive
        cached (bool, default=True): interact through an in-memory cache
        """
        if dict is None: dict = {}
        archive = _null_archive()
        archive.__state__['id'] = None if name is None else str(name)
        if cached: archive = cache(archive=archive)
        archive.update(dict)
        return archive

    @classmethod
    def from_frame(null_archive, dataframe):
        try:
            dataframe = dataframe.copy()
            dataframe.columns.name = null_archive.__name__
        except AttributeError: pass
        return _from_frame(dataframe)
    pass

class dir_archive(_dir_archive):
    def __new__(dir_archive, name=None, dict=None, cached=True, **kwds):
        """initialize a dictionary with a file-folder archive backend

    Args:
        name (str, default='memo'): path of the archive root directory
        dict (dict, default={}): initial dictionary to seed the archive
        cached (bool, default=True): interact through an in-memory cache
        serialized (bool, default=True): save python objects in pickled files
        compression (int, default=0): compression level (0 to 9), 0 is None
        permissions (octal, default=0o775): read/write permission indicator
        memmode (str, default=None): mode, one of ``{None, 'r+', 'r', 'w+', 'c'}``
        memsize (int, default=100): size (MB) of cache for in-memory compression
        protocol (int, default=DEFAULT_PROTOCOL): pickling protocol
        """
        if dict is None: dict = {}
        archive = _dir_archive(name, **kwds)
        if cached: archive = cache(archive=archive)
        archive.update(dict)
        return archive

    @classmethod
    def from_frame(dir_archive, dataframe):
        try:
            dataframe = dataframe.copy()
            dataframe.columns.name = dir_archive.__name__
        except AttributeError: pass
        return _from_frame(dataframe)
    pass

class file_archive(_file_archive):
    def __new__(file_archive, name=None, dict=None, cached=True, **kwds):
        """initialize a dictionary with a single file archive backend

    Args:
        name (str, default='memo.pkl'): path of the file archive
        dict (dict, default={}): initial dictionary to seed the archive
        cached (bool, default=True): interact through an in-memory cache
        serialized (bool, default=True): save python objects in pickled file
        protocol (int, default=DEFAULT_PROTOCOL): pickling protocol
        """
        if dict is None: dict = {}
        archive = _file_archive(name, **kwds)
        if cached: archive = cache(archive=archive)
        archive.update(dict)
        return archive

    @classmethod
    def from_frame(file_archive, dataframe):
        try:
            dataframe = dataframe.copy()
            dataframe.columns.name = file_archive.__name__
        except AttributeError: pass
        return _from_frame(dataframe)
    pass

class sqltable_archive(_sqltable_archive):
    def __new__(sqltable_archive, name=None, dict=None, cached=True, **kwds):
        """initialize a dictionary with a sql database table archive backend

    Connect to an existing database, or initialize a new database, at the
    selected database url. For example, to use a sqlite database 'foo.db'
    in the current directory, database='sqlite:///foo.db'. To use a mysql
    database 'foo' on localhost, database='mysql://user:pass@localhost/foo'.
    For postgresql, use database='postgresql://user:pass@localhost/foo'. 
    When connecting to sqlite, the default database is ':memory:'; otherwise,
    the default database is 'defaultdb'. Connections should be given as
    database?table=tablename; for example, name='sqlite:///foo.db?table=bar'.
    If not provided, the default tablename is 'memo'. If sqlalchemy is not
    installed, storable values are limited to strings, integers, floats, and
    other basic objects. If sqlalchemy is installed, additional keyword
    options can provide database configuration, such as connection pooling.
    To use a mysql or postgresql database, sqlalchemy must be installed.

    Args:
        name (str, default=None): url for database table (see above note)
        dict (dict, default={}): initial dictionary to seed the archive
        cached (bool, default=True): interact through an in-memory cache
        serialized (bool, default=True): save objects as pickled strings
        protocol (int, default=DEFAULT_PROTOCOL): pickling protocol
        """
        if dict is None: dict = {}
        db, table = _sqlname(name)
        archive = _sqltable_archive(db, table, **kwds)
        if cached: archive = cache(archive=archive)
        archive.update(dict)
        return archive

    @classmethod
    def from_frame(sqltable_archive, dataframe):
        try:
            dataframe = dataframe.copy()
            dataframe.columns.name = sqltable_archive.__name__
        except AttributeError: pass
        return _from_frame(dataframe)
    pass

class sql_archive(_sql_archive):
    def __new__(sql_archive, name=None, dict=None, cached=True, **kwds):
        """initialize a dictionary with a sql database archive backend

    Connect to an existing database, or initialize a new database, at the
    selected database url. For example, to use a sqlite database 'foo.db'
    in the current directory, database='sqlite:///foo.db'. To use a mysql
    database 'foo' on localhost, database='mysql://user:pass@localhost/foo'.
    For postgresql, use database='postgresql://user:pass@localhost/foo'. 
    When connecting to sqlite, the default database is ':memory:'; otherwise,
    the default database is 'defaultdb'. If sqlalchemy is not installed,
    storable values are limited to strings, integers, floats, and other
    basic objects. If sqlalchemy is installed, additional keyword options
    can provide database configuration, such as connection pooling.
    To use a mysql or postgresql database, sqlalchemy must be installed.

    Args:
        name (str, default=None): database url (see above note)
        dict (dict, default={}): initial dictionary to seed the archive
        cached (bool, default=True): interact through an in-memory cache
        serialized (bool, default=True): save objects as pickled strings
        protocol (int, default=DEFAULT_PROTOCOL): pickling protocol
        """
        if dict is None: dict = {}
        archive = _sql_archive(name, **kwds)
        if cached: archive = cache(archive=archive)
        archive.update(dict)
        return archive

    @classmethod
    def from_frame(sql_archive, dataframe):
        try:
            dataframe = dataframe.copy()
            dataframe.columns.name = sql_archive.__name__
        except AttributeError: pass
        return _from_frame(dataframe)
    pass

class hdfdir_archive(_hdfdir_archive):
    def __new__(hdfdir_archive, name=None, dict=None, cached=True, **kwds):
        """initialize a dictionary with a hdf5 file-folder archive backend

    Args:
        name (str, default='memo'): path of the archive root directory
        dict (dict, default={}): initial dictionary to seed the archive
        cached (bool, default=True): interact through an in-memory cache
        serialized (bool, default=True): pickle saved python objects
        permissions (octal, default=0o775): read/write permission indicator
        protocol (int, default=DEFAULT_PROTOCOL): pickling protocol
        meta (bool, default=False): store in root metadata (not in dataset)
        """
        if dict is None: dict = {}
        archive = _hdfdir_archive(name, **kwds)
        if cached: archive = cache(archive=archive)
        archive.update(dict)
        return archive

    @classmethod
    def from_frame(hdfdir_archive, dataframe):
        try:
            dataframe = dataframe.copy()
            dataframe.columns.name = hdfdir_archive.__name__
        except AttributeError: pass
        return _from_frame(dataframe)
    pass

class hdf_archive(_hdf_archive):
    def __new__(hdf_archive, name=None, dict=None, cached=True, **kwds):
        """initialize a dictionary with a single hdf5 file archive backend

    Args:
        name (str, default='memo.hdf5'): path of the file archive
        dict (dict, default={}): initial dictionary to seed the archive
        cached (bool, default=True): interact through an in-memory cache
        serialized (bool, default=True): pickle saved python objects
        protocol (int, default=DEFAULT_PROTOCOL): pickling protocol
        meta (bool, default=False): store in root metadata (not in dataset)
        """
        if dict is None: dict = {}
        archive = _hdf_archive(name, **kwds)
        if cached: archive = cache(archive=archive)
        archive.update(dict)
        return archive

    @classmethod
    def from_frame(hdf_archive, dataframe):
        try:
            dataframe = dataframe.copy()
            dataframe.columns.name = hdf_archive.__name__
        except AttributeError: pass
        return _from_frame(dataframe)
    pass


# EOF
