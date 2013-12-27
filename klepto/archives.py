#!/usr/bin/env python
"""
custom caching dict, which archives results to memory, file, or database
"""
from __future__ import absolute_import
try:
  from sqlalchemy import create_engine, delete, select, Column, MetaData, Table
  from sqlalchemy.types import PickleType, String, Text#, BLOB
  __alchemy = True
except ImportError:
  __alchemy = False
import dill

__all__ = ['cache','dict_archive','null_archive','file_archive','sql_archive']

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


class file_archive(dict):
    """dictionary-style interface to a file"""
    def __init__(self, filename=None, serialized=True): # False
        """initialize a file with a synchronized dictionary interface

    Inputs:
        serialized: if True, pickle file contents; otherwise save python objects
        filename: name of the file backend [default: memo.pkl or memo.py]
        """
        import os
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
        else:
            import os
            import tempfile
            file = os.path.basename(self._filename)
            root = os.path.realpath(self._filename).rstrip(file)[:-1]
            curdir = os.path.realpath(os.curdir)
            file = file.rstrip('.py') or file.rstrip('.pyc') \
                or file.rstrip('.pyo') or file.rstrip('.pyd')
            name = tempfile.mktemp(prefix="_____", dir="").replace("-","_")
            string = 'from %s import memo as %s' % (file, name)
            os.chdir(root)
            exec(string, globals()) #FIXME: unsafe, and potential name conflict
            memo = globals().get(name, {}) #XXX: or throw error if not found ?
            globals().pop(name, None)
            os.chdir(curdir)
        return memo
    def __save__(self, memo=None):
        """create an archive from the given dictionary"""
        if memo == None: return
        if self._serialized:
            try:
                f = open(self._filename, 'wb')
                dill.dump(memo, f)  #XXX: byref=True ?
                f.close()
            except:
                pass  #XXX: warning? fail?
        else:
            from .tools import _b
            open(self._filename, 'wb').write(_b('memo = %s' % memo))
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
    #FIXME: copy, fromkeys
    def get(self, key, value=None):
        memo = self.__asdict__()
        return memo.get(key, value)
    get.__doc__ = dict.get.__doc__
    if getattr(dict, 'has_key', None):
        def has_key(self, key):
            return key in self.__asdict__()
        has_key.__doc__ = dict.has_key.__doc__
        def __iter__(self):
            return self.__asdict__().iterkeys()
        def iteritems(self):
            return self.__asdict__().iteritems()
        iteritems.__doc__ = dict.iteritems.__doc__
        iterkeys = __iter__
        def itervalues(self):
            return self.__asdict__().itervalues()
        itervalues.__doc__ = dict.itervalues.__doc__
    else:
        def __iter__(self):
            return self.__asdict__().keys()
    __iter__.__doc__ = dict.__iter__.__doc__
    def keys(self):
        return self.__asdict__().keys()
    keys.__doc__ = dict.keys.__doc__
    def items(self):
        return self.__asdict__().items()
    items.__doc__ = dict.items.__doc__
    def values(self):
        return self.__asdict__().values()
    values.__doc__ = dict.values.__doc__
    def pop(self, key, *value):
        memo = self.__asdict__()
        res = memo.pop(key, *value)
        self.__save__(memo)
        return res
    pop.__doc__ = dict.pop.__doc__
    #FIXME: popitem
    def setdefault(self, key, *value):
        res = self.__asdict__().get(key, *value)
        self.__setitem__(key, res)
        return res
    setdefault.__doc__ = dict.setdefault.__doc__
    def update(self, adict, **kwds):
        memo = self.__asdict__()
        memo.update(adict, **kwds)
        self.__save__(memo)
        return
    update.__doc__ = dict.update.__doc__
    #FIXME: viewitems, viewkeys, viewvalues
    def __len__(self):
        return len(self.__asdict__())
    def __contains__(self, key):
        return self.has_key(key)
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
          if serialized:
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
              import os
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
      def __iter__(self): #FIXME: should be dict_keys(...) instance
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
      #FIXME: copy, fromkeys
      def __asdict__(self):
          """build a dictionary containing the archive contents"""
          return dict(self.iteritems())
      def __repr__(self):
          return "archive(%s: %s)" % (self._table, self.__asdict__())
      __repr__.__doc__ = dict.__repr__.__doc__
      if getattr(dict, 'has_key', None):
          def has_key(self, key):
              query = select([self._table], self._key == key)
              row = self._engine.execute(query).fetchone()
              return row != None
          has_key.__doc__ = dict.has_key.__doc__
          def iteritems(self): #FIXME: should be dict_items(...) instance
              query = select([self._table])
              result = self._engine.execute(query)
              for row in result:
                  yield (row[0], row[self._val])
          iteritems.__doc__ = dict.iteritems.__doc__
          iterkeys = __iter__
          def itervalues(self): #FIXME: should be dict_values(...) instance
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
          def keys(self): #FIXME: should be dict_keys(...) instance
              return self.__iter__()
          def items(self): #FIXME: should be dict_items(...) instance
              query = select([self._table])
              result = self._engine.execute(query)
              for row in result:
                  yield (row[0], row[self._val])
          def values(self): #FIXME: should be dict_values(...) instance
              query = select([self._table])
              result = self._engine.execute(query)
              for row in result:
                  yield row[self._val]
      keys.__doc__ = dict.keys.__doc__
      items.__doc__ = dict.items.__doc__
      values.__doc__ = dict.values.__doc__
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
      #FIXME: popitem
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
          _dict = adict.copy()
          _dict.update(**kwds)
          [self.__setitem__(k,v) for (k,v) in _dict.items()]
          return #XXX: should do the above all at once, and more efficiently
      update.__doc__ = dict.update.__doc__
      #FIXME: viewitems, viewkeys, viewvalues
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
              import os
              dbpath = self._database.split('///')[-1]
              if os.path.exists(dbpath): # else fail silently
                  os.remove(dbpath)
          self._engine = self._conn = self._table = None
          return
      def __len__(self):
          return len(self.__asdict__())
      def __contains__(self, key):
          return self.has_key(key)
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
      def __iter__(self): #FIXME: should be dict_keys(...) instance
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
      #FIXME: copy, fromkeys
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
          def has_key(self, key):
              return bool(self._select_key_items(key))
          has_key.__doc__ = dict.has_key.__doc__
          def iteritems(self): #FIXME: should be dict_items(...) instance
              return ((k,self.__getitem__(k)) for k in self.__iter__())
          iteritems.__doc__ = dict.iteritems.__doc__
          iterkeys = __iter__
          def itervalues(self): #FIXME: should be dict_values(...) instance
              return (self.__getitem__(k) for k in self.__iter__())
          itervalues.__doc__ = dict.itervalues.__doc__
          def keys(self):
              return list(self.__iter__())
          def items(self):
              return list(self.iteritems())
          def values(self):
              return list(self.itervalues())
      else:
          def keys(self): #FIXME: should be dict_keys(...) instance
              return self.__iter__()
          def items(self): #FIXME: should be dict_items(...) instance
              return ((k,self.__getitem__(k)) for k in self.__iter__())
          def values(self): #FIXME: should be dict_values(...) instance
              return (self.__getitem__(k) for k in self.__iter__())
      keys.__doc__ = dict.keys.__doc__
      items.__doc__ = dict.items.__doc__
      values.__doc__ = dict.values.__doc__
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
      #FIXME: popitem
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
          _dict = adict.copy()
          _dict.update(**kwds)
          [self.__setitem__(k,v) for (k,v) in _dict.items()]
          return
      update.__doc__ = dict.update.__doc__
      #FIXME: viewitems, viewkeys, viewvalues
      def _select_key_items(self, key):
          '''Return a tuple of (key, value) pairs that match the specified key'''
          sql = "select * from %s where argstr = ?" % self._table
          return tuple(self._engine.execute(sql, (key,)))
      pass


# backward compatibility
archive_dict = cache
db_archive = sql_archive

# EOF
