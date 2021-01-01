#!/usr/bin/env python
#
# Author: Mike McKerns (mmckerns @caltech and @uqfoundation)
# Copyright (c) 2019-2021 The Uncertainty Quantification Foundation.
# License: 3-clause BSD.  The full license text is available at:
#  - https://github.com/uqfoundation/klepto/blob/master/LICENSE

import klepto as kl

def test_roundtrip(archive):
    db = archive
    try:
        db_ = db.__type__.from_frame(db.to_frame())
    except ValueError:
        db_ = db
    assert db_ == db
    assert db_.archive == db.archive
    assert db_.archive.state == db.archive.state
    assert db_.__type__ == db.__type__

def test_dict_archive():
    d = kl.archives.dict_archive('foo', dict(a=1,b=2,c=3), cached=True)
    d.dump()
    test_roundtrip(d)

def test_null_archive():
    d = kl.archives.null_archive('foo', dict(a=1,b=2,c=3), cached=True)
    d.dump()
    test_roundtrip(d)

def test_dir_archive():
    d = kl.archives.dir_archive('foo', dict(a=1,b=2,c=3), cached=True)
    d.dump()
    test_roundtrip(d)

def test_file_archive():
    d = kl.archives.file_archive('foo.pkl', dict(a=1,b=2,c=3), cached=True)
    d.dump()
    test_roundtrip(d)

def test_sql_archive():
    d = kl.archives.sql_archive(None, dict(a=1,b=2,c=3), cached=True)
    d.dump()
    test_roundtrip(d)

def test_sqltable_archive():
    d = kl.archives.sqltable_archive(None, dict(a=1,b=2,c=3), cached=True)
    d.dump()
    test_roundtrip(d)

def test_hdf_archvie():
    d = kl.archives.hdf_archive('foo.h5', dict(a=1,b=2,c=3), cached=True)
    d.dump()
    test_roundtrip(d)

def test_hdfdir_archive():
    d = kl.archives.hdfdir_archive('bar', dict(a=1,b=2,c=3), cached=True)
    d.dump()
    test_roundtrip(d)

def _cleanup():
    import os
    import pox
    try: os.remove('foo.pkl')
    except: pass
    try: os.remove('foo.h5')
    except: pass
    try: pox.rmtree('foo')
    except: pass
    try: pox.rmtree('bar')
    except: pass
    return


if __name__ == '__main__':
    test_dict_archive()
    test_null_archive()
    test_dir_archive()
    test_file_archive()
    test_sql_archive()
    test_sqltable_archive()
    try:
        test_hdf_archvie()
        test_hdfdir_archive()
    except ImportError: pass
    _cleanup()


#EOF
