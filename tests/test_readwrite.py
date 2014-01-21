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


# EOF
