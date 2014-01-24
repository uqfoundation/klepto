from klepto.archives import dir_archive
from pox import rmtree

# start fresh
rmtree('foo', ignore_errors=True)


d = dir_archive('foo')
key = '1234TESTMETESTMETESTME1234'
d._mkdir(key)
#XXX: repeat mkdir does nothing, should it clear?  I think not.
_dir = d._mkdir(key)
assert d._getdir(key) == _dir
d._rmdir(key)

# with _pickle
x = [1,2,3,4,5]
d._fast = True
d[key] = x
assert d[key] == x
d._rmdir(key)

# with dill
d._fast = False
d[key] = x
assert d[key] == x
d._rmdir(key)

# with import
d._serialized = False
d[key] = x
assert d[key] == x
d._rmdir(key)
d._serialized = True


try: 
    import numpy as np
    y = np.array(x)

    # with _pickle
    d._fast = True
    d[key] = y
    assert all(d[key] == y)
    d._rmdir(key)

    # with dill
    d._fast = False
    d[key] = y
    assert all(d[key] == y)
    d._rmdir(key)

    # with import
    d._serialized = False
    d[key] = y
    assert all(d[key] == y)
    d._rmdir(key)
    d._serialized = True

except ImportError:
    pass


# clean up
rmtree('foo')

# check archiving basic stuff
def check_basic(archive):
    d = archive
    d['a'] = 1
    d['b'] = '1'
    d['c'] = min
    squared = lambda x:x**2
    d['d'] = squared
    d['e'] = None
    assert d['a'] == 1
    assert d['b'] == '1'
    assert d['c'] == min
    assert d['d'](2) == squared(2)
    assert d['e'] == None
    return

# check archiving numpy stuff
def check_numpy(archive):
    try:
        import numpy as np
    except ImportError:
        return
    d = archive
    x = np.array([1,2,3,4,5])
    y = np.arange(1000)
    t = np.dtype([('int',np.int),('float32',np.float32)])
    d['a'] = x
    d['b'] = y
    d['c'] = np.inf
    d['d'] = np.ptp
    d['e'] = t
    assert all(d['a'] == x)
    assert all(d['b'] == y)
    assert d['c'] == np.inf
    assert d['d'](x) == np.ptp(x)
    assert d['e'] == t
    return

# XXX: tests for non-string keys (e.g. d[1234] = 'hello')

# try some of the different __init__
archive = dir_archive()
check_basic(archive)
check_numpy(archive)
#rmtree('memo')

archive = dir_archive(fast=True)
check_basic(archive)
check_numpy(archive)
#rmtree('memo')

archive = dir_archive(compression=3)
check_basic(archive)
check_numpy(archive)
#rmtree('memo')

archive = dir_archive(memmode='r+')
check_basic(archive)
check_numpy(archive)
#rmtree('memo')

archive = dir_archive(serialized=False)
check_basic(archive)
check_numpy(archive)
rmtree('memo')


# EOF
