from klepto import inf_cache as memoized
from klepto.archives import *
from klepto.keymaps import picklemap

pm = picklemap(serializer='dill')
fname = 'xxxxxx'
delete = False

### OK
#ar = file_archive(fname, serialized=True, cached=False)
#ar = file_archive(fname, serialized=True, cached=True)
#ar = null_archive(fname, serialized=True, cached=False)
#ar = null_archive(fname, serialized=True, cached=True)
#ar = dict_archive(fname, serialized=True, cached=False)
#ar = dict_archive(fname, serialized=True, cached=True)
#ar = dir_archive(fname, serialized=True, cached=False)
ar = dir_archive(fname, serialized=True, cached=True)
### throws RecursionError   NOTE: '\x80' not valid, but r'\x80' is valid
#ar = sql_archive(fname, serialized=True, cached=False)
#ar = sql_archive(fname, serialized=True, cached=True)
### throws sql ProgrammingError (warns to use unicode strings)
#ar = sqltable_archive(fname, serialized=True, cached=False)
#ar = sqltable_archive(fname, serialized=True, cached=True)

@memoized(cache=ar, keymap=pm)
def testit(x):
  return x

testit(1)
testit(2)
# testit(numpy.array([1,2]))

testit.load()
testit.dump()
c = testit.__cache__()
print(c)
print(getattr(c, '__archive__', ''))

print(testit.info())

if delete:
    try:
        import os
        os.remove(fname)
    except: #FileNotFoundError
        import pox
        pox.shutils.rmtree(fname, self=True, ignore_errors=True)


# EOF
