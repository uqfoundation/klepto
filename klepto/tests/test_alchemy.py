#!/usr/bin/env python
#
# Author: Mike McKerns (mmckerns @caltech and @uqfoundation)
# Copyright (c) 2013-2016 California Institute of Technology.
# Copyright (c) 2016-2023 The Uncertainty Quantification Foundation.
# License: 3-clause BSD.  The full license text is available at:
#  - https://github.com/uqfoundation/klepto/blob/master/LICENSE

from klepto.archives import sqltable_archive as sqltable
from klepto.archives import sql_archive as sql

try:
    import sqlalchemy
    __alchemy = True
except ImportError:
    __alchemy = False

try:
    import psycopg2
    __postgresql = True
except ImportError:
    __postgresql = False

try:
    import MySQLdb
    __mysqldb = True
except ImportError:
    __mysqldb = False


def test_basic(d):
    d['a'] = 1
    d['b'] = '1'
    assert d['a'] == 1
    assert d['b'] == '1'

def test_alchemy(d):
    if __alchemy:
        d['c'] = min
        squared = lambda x:x**2
        d['d'] = squared
        assert d['c'] == min
        assert d['d'](2) == squared(2)
    else:
        print("for greater capabilities, install sqlalchemy")

def test_methods(d):
    if __alchemy:
        # __delitem__
        del d['d']
        # copy
        test = d.copy()
        # __eq__
        assert d == test
        # __getitem__
        i = d['a']
        # get pop
        assert d.get('a') == d.pop('a')
        # __ne__ __setitem__
        assert d != test
        d['a'] = i
        # __contains__
        assert 'a' in d
        # fromkeys
        assert d.fromkeys('abc') == dict(a=None, b=None, c=None)
        # keys
        assert set(d.keys()) == set(test.keys())
        # items
        assert set(d.items()) == set(test.items())
        # values
        assert set(d.values()) == set(test.values())
        # popitem setdefault
        d.setdefault(*d.popitem())
        assert d == test
        # update popkeys``
        d.update({'z':0})
        d.popkeys(['z'])
        assert d == test
        # __iter__
        assert next(iter(d)) in d
        # clear
        d.clear()
        # __asdict__
        assert d.__asdict__() == {}
        # __len__
        assert len(d) == 0
        # __drop__
        d.__drop__()
    else:
        pass

def test_new():
    if __alchemy:
        if __postgresql:
            z = sql('postgresql://user:pass@localhost/defaultdb', cached=False)
            z.__drop__()
        if __mysqldb:
            z = sql('mysql://user:pass@localhost/defaultdb', cached=False)
            z.__drop__()
    else:
        pass


if __name__ == '__main__':

    test_new()
    z = sqltable(cached=False)
    test_basic(z)
    test_alchemy(z)
    test_methods(z)
    z = sql(cached=False)
    test_basic(z)
    test_alchemy(z)
    test_methods(z)
