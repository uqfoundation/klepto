#!/usr/bin/env python
"""
custom caching dict, which archives results to memory, file, or database
"""
from __future__ import absolute_import
import os
import sys
from random import random
try:
  from collections import KeysView, ValuesView, ItemsView
  _view = True if sys.version_info[0] < 3 else False # True if 2.7
except ImportError:
  _view = False
try:
  from sqlalchemy import create_engine, delete, select, Column, MetaData, Table
  from sqlalchemy.types import PickleType, String, Text#, BLOB
  __alchemy = True
except ImportError:
  __alchemy = False
import dill
from dill.source import getimportable
from pox import mkdir, rmtree, walk
from .crypto import hash
from . import _pickle

__all__ = ['cache','dict_archive','null_archive',\
           'dir_archive','file_archive','sql_archive']

PREFIX = "K_"  # hash needs to be importable
TEMP = "I_"    # indicates 'temporary' file
#DEAD = "D_"    # indicates 'deleted' key


class cache(dict):
    """dictionary augmented with an archive backend"""
    def __init__(self, *args, **kwds):
        """initialize a dictionary with an archive backend

    Additional Inputs:
        archive: instance of archive object
        """
        self.__swap__ = null_archive()
        self.__archive__ = kwds.pop('archive', null_archive())
        dict.__init__(self, *args, **kwds)
        return
    def load(self, *args):
        """load archive contents

    If arguments are given, only load the specified keys
        """
        if not args:
            self.update(self.archive.__asdict__())
        for arg in args:
            try:
                self.update({arg:self.archive[arg]})
            except KeyError:
                pass
        return
    def dump(self, *args):
        """dump contents to archive

    If arguments are given, only dump the specified keys
        """
        if not args:
            self.archive.update(self)
        for arg in args:
            if arg in self:
                self.archive.update({arg:self.__getitem__(arg)})
        return
    def archived(self, *on):
        """check if the dict is archived, or toggle archiving

    If on is True, turn on the archive; if on is False, turn off the archive
        """
        L = len(on)
        if not L:
            return not isinstance(self.archive, null_archive)
        if L > 1:
            raise TypeError("archived expected at most 1 argument, got %s" % str(L+1))
        if bool(on[0]):
            if not isinstance(self.__swap__, null_archive):
                self.__swap__, self.__archive__ = self.__archive__, self.__swap__
            elif isinstance(self.__archive__, null_archive):
                raise ValueError("no valid archive has been set")
        else:
            if not isinstance(self.__archive__, null_archive):
                self.__swap__, self.__archive__ = self.__archive__, self.__swap__
    def __get_archive(self):
       #if not isinstance(self.__archive__, null_archive):
       #    return
        return self.__archive__
    def __archive(self, archive):
        if not isinstance(self.__swap__, null_archive):
            self.__swap__, self.__archive__ = self.__archive__, self.__swap__
        self.__archive__ = archive
    # interface
    archive = property(__get_archive, __archive)
    pass


class dict_archive(dict):
    """dictionary with an archive interface"""
    def __asdict__(self):
        """build a dictionary containing the archive contents"""
        return self
    def __repr__(self):
        return "archive(%s)" % (self.__asdict__())
    __repr__.__doc__ = dict.__repr__.__doc__


class null_archive(dict):
    """dictionary interface to nothing -- it's always empty"""
    def __init__(self):
        """initialize a permanently-empty dictionary"""
        dict.__init__(self)
        return
    def __asdict__(self):
        """build a dictionary containing the archive contents"""
        return self
    def __setitem__(self, key, value):
        pass
    __setitem__.__doc__ = dict.__setitem__.__doc__
    def update(self, adict, **kwds):
        pass
    update.__doc__ = dict.update.__doc__
    def setdefault(self, key, *value):
        return self.get(key, *value)
    setdefault.__doc__ = dict.setdefault.__doc__
    def __repr__(self):
        return "archive(NULL)"
    __repr__.__doc__ = dict.__repr__.__doc__
    pass


class dir_archive(dict):
    """dictionary-style interface to a folder of files"""
    def __init__(self, dirname=None, serialized=True, compression=0, **kwds):
        """initialize a file folder with a synchronized dictionary interface

    Inputs:
        dirname: name of the root archive directory [default: memo]
        serialized: if True, pickle file contents; otherwise save python objects
        compression: compression level (0 to 9) [default: 0 (no compression)]
        memmode: access mode for files, one of {None, 'r+', 'r', 'w+', 'c'}
        memsize: approximate size (in MB) of cache for in-memory compression
        """
        #XXX: if compression or mode is given, use joblib-style pickling
        #     (ignoring 'serialized'); else if serialized, use dill unless
        #     fast=True (then use joblib-style pickling). If not serialized,
        #     then write raw objects and load objects with import.
        """dirname = full filepath"""
        if dirname is None: #FIXME: default root as /tmp or something better
            dirname = 'memo' #FIXME: need better default
        # undocumented: set file permissions (takes an octal)
        self._perm = kwds.get('permissions', None)
        # undocumented: True=joblib-style, False=dill-style pickling
        self._fast = kwds.get('fast', False)
        #
        self._serialized = serialized
        self._compression = compression
        self._mode = kwds.get('memmode', None)
        self._size = kwds.get('memsize', 100)
        # if not serialized, then set fast=False
        if not self._serialized:
            self._compression = 0
            self._mode = None
            self._fast = False
        # if compression or mode, then set fast=True
        elif self._compression or self._mode:
            self._fast = True
        # ELSE: use dill if fast=False, else use _pickle

        try:
            self._root = mkdir(dirname, mode=self._perm)
        except OSError: # then directory already exists
            self._root = os.path.abspath(dirname)
        return
    def __asdict__(self):
        """build a dictionary containing the archive contents"""
        # get the names of all directories in the directory
        keys = self._keydict()
        # get the values
        return dict((key,self.__getitem__(key)) for key in keys)
    #FIXME: missing a bunch of __...__
    def __getitem__(self, key):
        _dir = self._getdir(key)
        if self._serialized:
            _file = os.path.join(_dir, self._file)
            try:
                if self._fast: #XXX: enable override of self._mode ?
                    memo = _pickle.load(_file, mmap_mode=self._mode)
                else:
                    f = open(_file, 'rb')
                    memo = dill.load(f)
                    f.close()
            except: #XXX: should only catch the appropriate exceptions
                memo = None
                raise KeyError(key)
               #raise OSError("error reading directory for '%s'" % key)
        else:
            import tempfile
            base = os.path.basename(_dir) #XXX: PREFIX+key
            root = os.path.realpath(self._root)
            name = tempfile.mktemp(prefix="_____", dir="").replace("-","_")
            string = "from %s import memo as %s; sys.modules.pop('%s')" % (base, name, base)
            try:
                sys.path.insert(0, root)
                exec(string, globals()) #FIXME: unsafe, potential name conflict
                memo = globals().get(name)# None) #XXX: error if not found?
                globals().pop(name, None)
            except: #XXX: should only catch the appropriate exceptions
                raise KeyError(key)
               #raise OSError("error reading directory for '%s'" % key)
            finally:
                sys.path.remove(root)
        return memo
    __getitem__.__doc__ = dict.__getitem__.__doc__
    def __repr__(self):
        name = os.path.basename(self._root)
        return "archive(%s: %s)" % (name, self.__asdict__())
    __repr__.__doc__ = dict.__repr__.__doc__
    def __setitem__(self, key, value):
        _key = TEMP+hash(random(), 'md5')
        # create a temporary directory, and dump the results
        try:
            _file = os.path.join(self._mkdir(_key), self._file)
            if self._serialized:
                if self._fast:
                    _pickle.dump(value, _file, compress=self._compression)
                else:
                    f = open(_file, 'wb')
                    dill.dump(value, f)  #XXX: byref=True ?
                    f.close()
            else: # try to get an import for the object
                try:
                    memo = getimportable(value, alias='memo', byname=False)
                except AttributeError: #XXX: HACKY... get classes by name
                    memo = getimportable(value, alias='memo')
                #XXX: instances of classes and such fail... abuse pickle here?
                from .tools import _b
                open(_file, 'wb').write(_b(memo))
        except OSError:
            "failed to populate directory for '%s'" % key
        # move the results to the proper place
        try: #XXX: possible permissions issues here
            self._rmdir(key)
            os.renames(self._getdir(_key), self._getdir(key))
        except OSError: #XXX: if rename fails, may need cleanup (_rmdir ?)
            "error in populating directory for '%s'" % key
    __setitem__.__doc__ = dict.__setitem__.__doc__
    def clear(self):
        rmtree(self._root, self=False, ignore_errors=True)
        return
    clear.__doc__ = dict.clear.__doc__
    #FIXME: copy
    def fromkeys(self, *args): #XXX: build a dict (not an archive)?
        return dict.fromkeys(*args)
    fromkeys.__doc__ = dict.fromkeys.__doc__
    def get(self, key, value=None):
        try:
            return self.__getitem__(key)
        except:
            return value
    get.__doc__ = dict.get.__doc__
    def __contains__(self, key):
        _dir = self._getdir(key)
        return os.path.exists(_dir)
    __contains__.__doc__ = dict.__contains__.__doc__
    if getattr(dict, 'has_key', None):
        has_key = __contains__
        has_key.__doc__ = dict.has_key.__doc__
        def __iter__(self):
            return self._keydict().iterkeys()
        def iteritems(self): #XXX: should be dictionary-itemiterator
            keys = self._keydict()
            return ((key,self.__getitem__(key)) for key in keys)
        iteritems.__doc__ = dict.iteritems.__doc__
        iterkeys = __iter__
        iterkeys.__doc__ = dict.iterkeys.__doc__
        def itervalues(self): #XXX: should be dictionary-valueiterator
            keys = self._keydict()
            return (self.__getitem__(key) for key in keys)
        itervalues.__doc__ = dict.itervalues.__doc__
    else:
        def __iter__(self):
            return iter(self._keydict().keys())
    __iter__.__doc__ = dict.__iter__.__doc__
    def keys(self):
        if sys.version_info[0] < 3:
            return self._keydict().keys()
        else: return KeysView(self) #XXX: show keys not dict
    keys.__doc__ = dict.keys.__doc__
    def items(self):
        if sys.version_info[0] < 3:
            keys = self._keydict()
            return [(key,self.__getitem__(key)) for key in keys]
        else: return ItemsView(self) #XXX: show items not dict
    items.__doc__ = dict.items.__doc__
    def values(self):
        if sys.version_info[0] < 3:
            keys = self._keydict()
            return [self.__getitem__(key) for key in keys]
        else: return ValuesView(self) #XXX: show values not dict
    values.__doc__ = dict.values.__doc__
    if _view:
        def viewkeys(self):
            return KeysView(self) #XXX: show keys not dict
        viewkeys.__doc__ = dict.viewkeys.__doc__
        def viewvalues(self):
            return ValuesView(self) #XXX: show values not dict
        viewvalues.__doc__ = dict.viewvalues.__doc__
        def viewitems(self):
            return ItemsView(self) #XXX: show items not dict
        viewitems.__doc__ = dict.viewitems.__doc__
    def pop(self, key, *value): #XXX: or make DEAD ?
        try:
            memo = {key: self.__getitem__(key)}
            self._rmdir(key)
        except:
            memo = {}
        res = memo.pop(key, *value)
        return res
    pop.__doc__ = dict.pop.__doc__
    def popitem(self):
        key = self.__iter__()
        try: key = key.next()
        except StopIteration: raise KeyError("popitem(): dictionary is empty")
        return (key, self.pop(key))
    popitem.__doc__ = dict.popitem.__doc__
    def setdefault(self, key, *value):
        res = self.get(key, *value)
        self.__setitem__(key, res)
        return res
    setdefault.__doc__ = dict.setdefault.__doc__
    def update(self, adict, **kwds):
        if hasattr(adict,'__asdict__'): adict = adict.__asdict__()
        memo = {}
        memo.update(adict, **kwds) #XXX: could be better ?
        for (key,val) in memo.items():
            self.__setitem__(key,val)
        return
    update.__doc__ = dict.update.__doc__
    def __len__(self):
        return len(self._lsdir())

    def _mkdir(self, key):
        "create results subdirectory corresponding to given key"
        key = str(key) # enable non-strings, however 1=='1' #XXX: better repr?
        try:
            return mkdir(PREFIX+key, root=self._root, mode=self._perm)
        except OSError: # then directory already exists
            return self._getdir(key)

    def _getdir(self, key):
        "get results directory name corresponding to given key"
        key = str(key) # enable non-strings, however 1=='1' #XXX: better repr?
        return os.path.join(self._root, PREFIX+key)

    def _rmdir(self, key):
        "remove results subdirectory corresponding to given key"
        rmtree(self._getdir(key), self=True, ignore_errors=True)
        return
    def _lsdir(self):
        "get a list of subdirectories in the root directory"
        return walk(self._root,patterns=PREFIX+'*',recurse=False,folders=True,files=False,links=False)
    def _keydict(self):
        "get a dict of subdirectories in the root directory, with dummy values"
        base = os.path.basename
        keys = self._lsdir()
        return dict((base(key)[2:],None) for key in keys)

    def _get_file(self):
        if self._serialized: return 'output.pkl'
        return '__init__.py'
    def _set_file(self, file):
        raise NotImplementedError("cannot set attribute '_file'")

    # interface
    _file = property(_get_file, _set_file)
    pass


class file_archive(dict):
    """dictionary-style interface to a file"""
    def __init__(self, filename=None, serialized=True): # False
        """initialize a file with a synchronized dictionary interface

    Inputs:
        serialized: if True, pickle file contents; otherwise save python objects
        filename: name of the file backend [default: memo.pkl or memo.py]
        """
        """filename = full filepath"""
        if filename is None:
            if serialized: filename = 'memo.pkl' #FIXME: need better default
            else: filename = 'memo.py' #FIXME: need better default
        self._filename = filename
        self._serialized = serialized
        if not os.path.exists(filename):
            self.__save__({})
        return
    def __asdict__(self):
        """build a dictionary containing the archive contents"""
        if self._serialized:
            try:
                f = open(self._filename, 'rb')
                memo = dill.load(f)
                f.close()
            except:
                memo = {}
               #raise OSError("error reading file archive %s" % self._filename)
        else:
            import tempfile
            file = os.path.basename(self._filename)
            root = os.path.realpath(self._filename).rstrip(file)[:-1]
            curdir = os.path.realpath(os.curdir)
            file = file.rstrip('.py') or file.rstrip('.pyc') \
                or file.rstrip('.pyo') or file.rstrip('.pyd')
            name = tempfile.mktemp(prefix="_____", dir="").replace("-","_")
            os.chdir(root)
            string = "from %s import memo as %s; sys.modules.pop('%s')" % (file, name, file)
            try:
                exec(string, globals()) #FIXME: unsafe, potential name conflict
                memo = globals().get(name, {}) #XXX: error if not found ?
                globals().pop(name, None)
            except: #XXX: should only catch appropriate exceptions
                memo = {}
               #raise OSError("error reading file archive %s" % self._filename)
            finally:
                os.chdir(curdir)
        return memo
    def __save__(self, memo=None):
        """create an archive from the given dictionary"""
        if memo == None: return
        _filename = TEMP+hash(random(), 'md5')
        # create a temporary file, and dump the results
        try:
            if self._serialized:
                f = open(_filename, 'wb')
                dill.dump(memo, f)  #XXX: byref=True ?
                f.close()
            else: #XXX: likely_import for each item in dict... ?
                from .tools import _b
                open(_filename, 'wb').write(_b('memo = %s' % repr(memo)))
        except OSError:
            "failed to populate file for %s" % self._filename
        # move the results to the proper place
        try:
            os.remove(self._filename)
        except: pass
        try:
            os.renames(_filename, self._filename)
        except OSError:
            "error in populating %s" % self._filename
        return
    #FIXME: missing a bunch of __...__
    def __getitem__(self, key):
        memo = self.__asdict__()
        return memo[key]
    __getitem__.__doc__ = dict.__getitem__.__doc__
    def __repr__(self):
        return "archive(%s: %s)" % (self._filename, self.__asdict__())
    __repr__.__doc__ = dict.__repr__.__doc__
    def __setitem__(self, key, value):
        memo = self.__asdict__()
        memo[key] = value
        self.__save__(memo)
        return
    __setitem__.__doc__ = dict.__setitem__.__doc__
    def clear(self):
        self.__save__({})
        return
    clear.__doc__ = dict.clear.__doc__
    #FIXME: copy
    def fromkeys(self, *args): #XXX: build a dict (not an archive)?
        return dict.fromkeys(*args)
    fromkeys.__doc__ = dict.fromkeys.__doc__
    def get(self, key, value=None):
        memo = self.__asdict__()
        return memo.get(key, value)
    get.__doc__ = dict.get.__doc__
    def __contains__(self, key):
        return key in self.__asdict__()
    __contains__.__doc__ = dict.__contains__.__doc__
    if getattr(dict, 'has_key', None):
        has_key = __contains__
        has_key.__doc__ = dict.has_key.__doc__
        def __iter__(self):
            return self.__asdict__().iterkeys()
        def iteritems(self):
            return self.__asdict__().iteritems()
        iteritems.__doc__ = dict.iteritems.__doc__
        iterkeys = __iter__
        iterkeys.__doc__ = dict.iterkeys.__doc__
        def itervalues(self):
            return self.__asdict__().itervalues()
        itervalues.__doc__ = dict.itervalues.__doc__
    else:
        def __iter__(self):
            return iter(self.__asdict__().keys())
    __iter__.__doc__ = dict.__iter__.__doc__
    def keys(self):
        if sys.version_info[0] < 3:
            return self.__asdict__().keys()
        else: return KeysView(self) #XXX: show keys not dict
    keys.__doc__ = dict.keys.__doc__
    def items(self):
        if sys.version_info[0] < 3:
            return self.__asdict__().items()
        else: return ItemsView(self) #XXX: show items not dict
    items.__doc__ = dict.items.__doc__
    def values(self):
        if sys.version_info[0] < 3:
            return self.__asdict__().values()
        else: return ValuesView(self) #XXX: show values not dict
    values.__doc__ = dict.values.__doc__
    if _view:
        def viewkeys(self):
            return KeysView(self) #XXX: show keys not dict
        viewkeys.__doc__ = dict.viewkeys.__doc__
        def viewvalues(self):
            return ValuesView(self) #XXX: show values not dict
        viewvalues.__doc__ = dict.viewvalues.__doc__
        def viewitems(self):
            return ItemsView(self) #XXX: show items not dict
        viewitems.__doc__ = dict.viewitems.__doc__
    def pop(self, key, *value):
        memo = self.__asdict__()
        res = memo.pop(key, *value)
        self.__save__(memo)
        return res
    pop.__doc__ = dict.pop.__doc__
    def popitem(self):
        memo = self.__asdict__()
        res = memo.popitem()
        self.__save__(memo)
        return res
    popitem.__doc__ = dict.popitem.__doc__
    def setdefault(self, key, *value):
        res = self.__asdict__().get(key, *value)
        self.__setitem__(key, res)
        return res
    setdefault.__doc__ = dict.setdefault.__doc__
    def update(self, adict, **kwds):
        if hasattr(adict,'__asdict__'): adict = adict.__asdict__()
        memo = self.__asdict__()
        memo.update(adict, **kwds)
        self.__save__(memo)
        return
    update.__doc__ = dict.update.__doc__
    def __len__(self):
        return len(self.__asdict__())
    pass


if __alchemy:
  class sql_archive(dict):
      """dictionary-style interface to a sql database"""
      def __init__(self, database=None, table=None, **kwds):
          """initialize a sql database with a synchronized dictionary interface

      Connect to an existing database, or initialize a new database, at the
      selected database url. For example, to use a sqlite database 'foo.db'
      in the current directory, database='sqlite:///foo.db'.  To use a mysql
      database 'foo' on localhost, database='mysql://user:pass@localhost/foo'.
      For postgresql, use database='postgresql://user:pass@localhost/foo'. 
      When connecting to sqlite, the default database is ':memory:'; otherwise,
      the default database is 'defaultdb'.  Allows keyword options for database
      configuration, such as connection pooling.

      Inputs:
          database: url of the database backend [default: sqlite:///:memory:]
          table: name of the associated database table [default: 'memo']
          serialized: if True, pickle table contents; otherwise cast as strings
          """
          self._serialized = bool(kwds.pop('serialized', True))
          # create database, if doesn't exist
          if database is None: database = 'sqlite:///:memory:'
          elif database == 'sqlite:///': database = 'sqlite:///:memory:'
          self._database = database
          url, dbname = self._database.rsplit('/', 1)
          if url.endswith(":/") or dbname == '': # then no dbname was given
              url = self._database
              dbname = 'defaultdb'
              self._database = "%s/%s" % (url,dbname)
          if dbname == ':memory:':
              self._engine = create_engine(url, **kwds)
          elif self._database.startswith('sqlite'):
              self._engine = create_engine(self._database, **kwds)
          else:
              self._engine = create_engine(url) #XXX: **kwds ?
              try:
                  conn = self._engine.connect()
                  if self._database.startswith('postgres'):
                      conn.connection.connection.set_isolation_level(0)
                  conn.execute("CREATE DATABASE %s;" % dbname)
              except Exception: pass
              finally:
                  if self._database.startswith('postgres'):
                      conn.connection.connection.set_isolation_level(1)
              try:
                  self._engine.execute("USE %s;" % dbname)
              except Exception:
                  pass
              self._engine = create_engine(self._database, **kwds)
          # create table, if doesn't exist
          self._metadata = MetaData()
          self._key = 'key' # primary key name    #XXX: or table name ?
          self._val = 'val' # object storage name #XXX: ???
          keytype = String(255) #XXX: other better fixed size?
          if self._serialized:
              valtype = PickleType(pickler=dill)
          else:
              valtype = Text() #XXX: String(255) or BLOB() ???
          if table is None: table = 'memo' #XXX: better random unique id ?
          if isinstance(table, str): #XXX: better str-variants ? or no if ?
              table = Table(table, self._metadata,
                  Column(self._key, keytype, primary_key=True),
                  Column(self._val, valtype)
              )
          self._key = table.c[self._key]
          self._table = table
          # initialize
          self._metadata.create_all(self._engine)
          return
      def __drop__(self, **kwds):
          """drop the database table

      EXPERIMENTAL: also drop the associated database. For certain
      database engines, this may not work due to permission issues.
      Caller may need to be connected as a superuser and database owner.
      To drop associated database, use __drop__(database=True)
          """
          if not bool(kwds.get('database', False)):
              self._table.drop(self._engine)
              self._metadata = self._engine = self._table = None
              return
          url, dbname = self._database.rsplit('/', 1)
          self._engine = create_engine(url)
          try:
              conn = self._engine.connect()
              if self._database.startswith('postgres'):
                  # these two commands require superuser privs
                  conn.execute("update pg_database set datallowconn = 'false' WHERE datname = '%s';" % dbname)
                  conn.execute("SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '%s';" % dbname) # 'pid' used in postgresql >= 9.2
                  conn.connection.connection.set_isolation_level(0)
              conn.execute("DROP DATABASE %s;" % dbname) # must be db owner
              if self._database.startswith('postgres'):
                  conn.connection.connection.set_isolation_level(1)
          except Exception:
              dbpath = self._database.split('///')[-1]
              if os.path.exists(dbpath): # else fail silently
                  os.remove(dbpath)
          self._metadata = self._engine = self._table = None
          return
      def __len__(self):
          query = self._table.count()
          return int(self._engine.execute(query).scalar())
      def __contains__(self, key):
          query = select([self._key], self._key == key)
          row = self._engine.execute(query).fetchone()
          return row is not None
      __contains__.__doc__ = dict.__contains__.__doc__
      def __setitem__(self, key, value):
          value = {self._val: value} #XXX: force into single item dict...?
          if key in self:
              values = value
              query = self._table.update().where(self._key == key)
          else:
              values = {self._key.name: key}
              values.update(value)
              query = self._table.insert()
          self._engine.execute(query.values(**values))
          return
      __setitem__.__doc__ = dict.__setitem__.__doc__
      #FIXME: missing a bunch of __...__
      def __getitem__(self, key):
          query = select([self._table], self._key == key)
          row = self._engine.execute(query).fetchone()
          if row is None: raise KeyError(key)
          return row[self._val]
      __getitem__.__doc__ = dict.__getitem__.__doc__
      def __iter__(self): #XXX: should be dictionary-keyiterator
          query = select([self._key])
          result = self._engine.execute(query)
          for row in result:
              yield row[0]
      __iter__.__doc__ = dict.__iter__.__doc__
      def get(self, key, value=None):
          query = select([self._table], self._key == key)
          row = self._engine.execute(query).fetchone()
          if row != None:
              _value = row[self._val]
          else: _value = value
          return _value
      get.__doc__ = dict.get.__doc__
      def clear(self):
          query = self._table.delete()
          self._engine.execute(query)
          return
      clear.__doc__ = dict.clear.__doc__
     #def insert(self, d): #XXX: don't allow this method, or hide ?
     #    query = self._table.insert(d)
     #    self._engine.execute(query)
     #    return
      #FIXME: copy
      def fromkeys(self, *args): #XXX: build a dict (not an archive)?
          return dict.fromkeys(*args)
      fromkeys.__doc__ = dict.fromkeys.__doc__
      def __asdict__(self):
          """build a dictionary containing the archive contents"""
          if getattr(dict, 'iteritems', None):
              return dict(self.iteritems())
          else: return dict(self.items())
      def __repr__(self):
          return "archive(%s: %s)" % (self._table, self.__asdict__())
      __repr__.__doc__ = dict.__repr__.__doc__
      if getattr(dict, 'has_key', None):
          def has_key(self, key): #XXX: different than contains... why?
              query = select([self._table], self._key == key)
              row = self._engine.execute(query).fetchone()
              return row != None
          has_key.__doc__ = dict.has_key.__doc__
          def iteritems(self): #XXX: should be dictionary-itemiterator
              query = select([self._table])
              result = self._engine.execute(query)
              for row in result:
                  yield (row[0], row[self._val])
          iteritems.__doc__ = dict.iteritems.__doc__
          iterkeys = __iter__
          iterkeys.__doc__ = dict.iterkeys.__doc__
          def itervalues(self): #XXX: should be dictionary-valueiterator
              query = select([self._table])
              result = self._engine.execute(query)
              for row in result:
                  yield row[self._val]
          itervalues.__doc__ = dict.itervalues.__doc__
          def keys(self):
              return list(self.__iter__())
          def items(self):
              return list(self.iteritems())
          def values(self):
              return list(self.itervalues())
      else:
          def keys(self):
              return KeysView(self) #XXX: show keys not dict
          def items(self):
              return ItemsView(self) #XXX: show keys not dict
          def values(self):
              return ValuesView(self) #XXX: show keys not dict
      keys.__doc__ = dict.keys.__doc__
      items.__doc__ = dict.items.__doc__
      values.__doc__ = dict.values.__doc__
      if _view:
          def viewkeys(self):
              return KeysView(self) #XXX: show keys not dict
          viewkeys.__doc__ = dict.viewkeys.__doc__
          def viewvalues(self):
              return ValuesView(self) #XXX: show values not dict
          viewvalues.__doc__ = dict.viewvalues.__doc__
          def viewitems(self):
              return ItemsView(self) #XXX: show items not dict
          viewitems.__doc__ = dict.viewitems.__doc__
      def pop(self, key, *value):
          L = len(value)
          if L > 1:
              raise TypeError("pop expected at most 2 arguments, got %s" % str(L+1))
          query = select([self._table], self._key == key)
          row = self._engine.execute(query).fetchone()
          if row != None:
              _value = row[self._val]
          else:
              if not L: raise KeyError(key)
              _value = value[0]
          query = delete(self._table, self._key == key)
          self._engine.execute(query)
          return _value
      pop.__doc__ = dict.pop.__doc__
      def popitem(self):
          key = self.__iter__()
          try: key = key.next()
          except StopIteration: raise KeyError("popitem(): dictionary is empty")
          return (key, self.pop(key))
      popitem.__doc__ = dict.popitem.__doc__
      def setdefault(self, key, *value):
          L = len(value)
          if L > 1:
              raise TypeError("setvalue expected at most 2 arguments, got %s" % str(L+1))
          query = select([self._table], self._key == key)
          row = self._engine.execute(query).fetchone()
          if row != None:
              _value = row[self._val]
          else:
              if not L: _value = None
              else: _value = value[0]
              self.__setitem__(key, _value)
          return _value
      setdefault.__doc__ = dict.setdefault.__doc__
      def update(self, adict, **kwds):
          if hasattr(adict,'__asdict__'): adict = adict.__asdict__()
          else: adict = adict.copy()
          adict.update(**kwds)
          [self.__setitem__(k,v) for (k,v) in adict.items()]
          return #XXX: should do the above all at once, and more efficiently
      update.__doc__ = dict.update.__doc__
      pass
else:
  class sql_archive(dict): #XXX: requires UTF-8 key; #FIXME: use sqlite3.dbapi2
      """dictionary-style interface to a sql database"""
      def __init__(self, database=None, table=None, **kwds): #serialized
          """initialize a  sql database with a synchronized dictionary interface

      Connect to an existing database, or initialize a new database, at the
      selected database url. For example, to use a sqlite database 'foo.db'
      in the current directory, database='sqlite:///foo.db'.  To use a mysql
      or postgresql database, sqlalchemy must be installed.  When connecting
      to sqlite, the default database is ':memory:'.  Storable values are
      limited to strings, integers, floats, and other basic objects.  To store
      functions, classes, and similar constructs, sqlalchemy must be installed.

      Inputs:
          database: url of the database backend [default: sqlite:///:memory:]
          table: name of the associated database table [default: 'memo']
          """
          import sqlite3 as db
          if database is None: database = 'sqlite:///:memory:'
          elif database == 'sqlite:///': database = 'sqlite:///:memory:'
          self._database = database
          if table is None: table = 'memo'
          self._table = table
          if not self._database.startswith('sqlite:///'):
              raise ValueError("install sqlalchemy for non-sqlite database support")
          dbname = self._database.split('sqlite:///')[-1]
          self._conn = db.connect(dbname)
          self._engine = self._conn.cursor()
          sql = "create table if not exists %s(argstr, fval)" % table
          self._engine.execute(sql)
          # compatibility
          self._metadata = None
          self._key = 'key'
          self._val = 'val'
          return
      def __drop__(self, **kwds):
          """drop the database table

      EXPERIMENTAL: also drop the associated database. For certain
      database engines, this may not work due to permission issues.
      Caller may need to be connected as a superuser and database owner.
      To drop associated database, use __drop__(database=True)
          """
          if not bool(kwds.get('database', False)):
              self._engine.executescript('drop table if exists %s;' % self._table)
              self._engine = self._conn = self._table = None
              return
          try:
              dbname = self._database.lstrip('sqlite:///')
              conn = db.connect(':memory:')
              conn.execute("DROP DATABASE %s;" % dbname) #FIXME: always fails
          except Exception:
              dbpath = self._database.split('///')[-1]
              if os.path.exists(dbpath): # else fail silently
                  os.remove(dbpath)
          self._engine = self._conn = self._table = None
          return
      def __len__(self):
          return len(self.__asdict__())
      def __contains__(self, key):
          return bool(self._select_key_items(key))
      __contains__.__doc__ = dict.__contains__.__doc__
      def __setitem__(self, key, value): #XXX: maintains 'history' of values
          sql = "insert into %s values(?,?)" % self._table
          self._engine.execute(sql, (key,value))
          self._conn.commit()
          return
      __setitem__.__doc__ = dict.__setitem__.__doc__
      #FIXME: missing a bunch of __...__
      def __getitem__(self, key):
          res = self._select_key_items(key)
          if res: return res[-1][-1] # always get the last one
          raise KeyError(key)
      __getitem__.__doc__ = dict.__getitem__.__doc__
      def __iter__(self): #XXX: should be dictionary-keyiterator
          sql = "select argstr from %s" % self._table
          return (k[-1] for k in set(self._engine.execute(sql)))
      __iter__.__doc__ = dict.__iter__.__doc__
      def get(self, key, value=None):
          res = self._select_key_items(key)
          if res: value = res[-1][-1]
          return value
      get.__doc__ = dict.get.__doc__
      def clear(self):
          [self.pop(k) for k in self.keys()] # better delete table, add empty ?
          return
      clear.__doc__ = dict.clear.__doc__
      #FIXME: copy
      def fromkeys(self, *args): #XXX: build a dict (not an archive)?
          return dict.fromkeys(*args)
      fromkeys.__doc__ = dict.fromkeys.__doc__
      def __asdict__(self):
          """build a dictionary containing the archive contents"""
          sql = "select * from %s" % self._table
          res = self._engine.execute(sql)
          d = {}
          [d.update({k:v}) for (k,v) in res] # always get the last one
          return d
      def __repr__(self):
          return "archive(%s: %s)" % (self._table, self.__asdict__())
      __repr__.__doc__ = dict.__repr__.__doc__
      if getattr(dict, 'has_key', None):
          has_key = __contains__
          has_key.__doc__ = dict.has_key.__doc__
          def iteritems(self): #XXX: should be dictionary-itemiterator
              return ((k,self.__getitem__(k)) for k in self.__iter__())
          iteritems.__doc__ = dict.iteritems.__doc__
          iterkeys = __iter__
          iterkeys.__doc__ = dict.iterkeys.__doc__
          def itervalues(self): #XXX: should be dictionary-valueiterator
              return (self.__getitem__(k) for k in self.__iter__())
          itervalues.__doc__ = dict.itervalues.__doc__
          def keys(self):
              return list(self.__iter__())
          def items(self):
              return list(self.iteritems())
          def values(self):
              return list(self.itervalues())
      else:
          def keys(self):
              return KeysView(self) #XXX: show keys not dict
          def items(self):
              return ItemsView(self) #XXX: show keys not dict
          def values(self):
              return ValuesView(self) #XXX: show keys not dict
      keys.__doc__ = dict.keys.__doc__
      items.__doc__ = dict.items.__doc__
      values.__doc__ = dict.values.__doc__
      if _view:
          def viewkeys(self):
              return KeysView(self) #XXX: show keys not dict
          viewkeys.__doc__ = dict.viewkeys.__doc__
          def viewvalues(self):
              return ValuesView(self) #XXX: show values not dict
          viewvalues.__doc__ = dict.viewvalues.__doc__
          def viewitems(self):
              return ItemsView(self) #XXX: show items not dict
          viewitems.__doc__ = dict.viewitems.__doc__
      def pop(self, key, *value):
          L = len(value)
          if L > 1:
              raise TypeError("pop expected at most 2 arguments, got %s" % str(L+1))
          res = self._select_key_items(key)
          if res:
              _value = res[-1][-1]
          else:
              if not L: raise KeyError(key)
              _value = value[0]
          sql = "delete from %s where argstr = ?" % self._table
          self._engine.execute(sql, (key,))
          self._conn.commit()
          return _value 
      pop.__doc__ = dict.pop.__doc__
      def popitem(self):
          key = self.__iter__()
          try: key = key.next()
          except StopIteration: raise KeyError("popitem(): dictionary is empty")
          return (key, self.pop(key))
      popitem.__doc__ = dict.popitem.__doc__
      def setdefault(self, key, *value):
          L = len(value)
          if L > 1:
              raise TypeError("setvalue expected at most 2 arguments, got %s" % str(L+1))
          res = self._select_key_items(key)
          if res:
              _value = res[-1][-1]
          else:
              if not L: _value = None
              else: _value = value[0]
              self.__setitem__(key, _value)
          return _value
      setdefault.__doc__ = dict.setdefault.__doc__
      def update(self, adict, **kwds):
          if hasattr(adict,'__asdict__'): adict = adict.__asdict__()
          else: adict = adict.copy()
          adict.update(**kwds)
          [self.__setitem__(k,v) for (k,v) in adict.items()]
          return
      update.__doc__ = dict.update.__doc__
      def _select_key_items(self, key):
          '''Return a tuple of (key, value) pairs that match the specified key'''
          sql = "select * from %s where argstr = ?" % self._table
          return tuple(self._engine.execute(sql, (key,)))
      pass


# backward compatibility
archive_dict = cache
db_archive = sql_archive

# EOF
