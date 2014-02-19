#!/usr/bin/env python
"""
custom caching dict, which archives results to memory, file, or database
"""
from __future__ import absolute_import
from ._archives import cache
from ._archives import dict_archive as _dict_archive
from ._archives import null_archive as _null_archive
from ._archives import dir_archive as _dir_archive
from ._archives import file_archive as _file_archive
from ._archives import sql_archive as _sql_archive

__all__ = ['cache','dict_archive','null_archive',\
           'dir_archive','file_archive','sql_archive']

class dict_archive(_dict_archive):
    def __new__(dict_archive, dict=None, cached=True, **kwds):
        """initialize a dictionary with an in-memory dictionary archive backend

    Inputs:
        dict: initial dictionary to seed the archive
        cached: if True, use an in-memory cache interface to the archive
        """
        if dict is None: dict = {}
        archive = _dict_archive()
        if cached: archive = cache(archive=archive)
        archive.update(dict)
        return archive
    pass

class null_archive(_null_archive):
    def __new__(null_archive, dict=None, cached=True, **kwds):
        """initialize a dictionary with a permanently-empty archive backend

    Inputs:
        dict: initial dictionary to seed the archive
        cached: if True, use an in-memory cache interface to the archive
        """
        if dict is None: dict = {}
        archive = _null_archive()
        if cached: archive = cache(archive=archive)
        archive.update(dict)
        return archive
    pass

class dir_archive(_dir_archive):
    def __new__(dir_archive, name=None, dict=None, cached=True, **kwds):
        """initialize a dictionary with a file-folder archive backend

    Inputs:
        name: name of the root archive directory [default: memo]
        dict: initial dictionary to seed the archive
        cached: if True, use an in-memory cache interface to the archive
        serialized: if True, pickle file contents; otherwise save python objects
        compression: compression level (0 to 9) [default: 0 (no compression)]
        memmode: access mode for files, one of {None, 'r+', 'r', 'w+', 'c'}
        memsize: approximate size (in MB) of cache for in-memory compression
        """
        if dict is None: dict = {}
        archive = _dir_archive(name, **kwds)
        if cached: archive = cache(archive=archive)
        archive.update(dict)
        return archive
    pass

class file_archive(_file_archive):
    def __new__(file_archive, name=None, dict=None, cached=True, **kwds):
        """initialize a dictionary with a single file archive backend

    Inputs:
        name: name of the file archive [default: memo.pkl or memo.py]
        dict: initial dictionary to seed the archive
        cached: if True, use an in-memory cache interface to the archive
        serialized: if True, pickle file contents; otherwise save python objects
        """
        if dict is None: dict = {}
        archive = _file_archive(name, **kwds)
        if cached: archive = cache(archive=archive)
        archive.update(dict)
        return archive
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
    the default database is 'defaultdb'. Connections should be given as
    database?table=tablename; for example, name='sqlite:///foo.db?table=bar'.
    If not provided, the default tablename is 'memo'. If sqlalchemy is not
    installed, storable values are limited to strings, integers, floats, and
    other basic objects. If sqlalchemy is installed, additional keyword
    options can provide database configuration, such as connection pooling.
    To use a mysql or postgresql database, sqlalchemy must be installed.

    Inputs:
        name: url for the sql database and table [default: (see note above)]
        dict: initial dictionary to seed the archive
        cached: if True, use an in-memory cache interface to the archive
        serialized: if True, pickle table contents; otherwise cast as strings
        """
        if dict is None: dict = {}
        key = '?table='
        if name is None: db, table = None, None # name=None
        elif name.startswith((key,'table=')): # name='table=memo'
            db, table = None, name.lstrip('?').lstrip('table').lstrip('=')
        elif name.count('/'): # name='sqlite:///'
            db, table = name.split(key,1) if name.count(key) else (name, None)
        else: db, table = None, name # name='memo'
        archive = _sql_archive(db, table, **kwds)
        if cached: archive = cache(archive=archive)
        archive.update(dict)
        return archive
    pass


# EOF
