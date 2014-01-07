"""
The decorator should produce the behavior as displayed in the following:

>>> s = Spam()
>>> s.eggs()
new: (), {}
42
>>> s.eggs()
42
>>> s.eggs(1)
new: (1,), {}
64
>>> s.eggs(1)
64
>>> s.eggs(1, bar='spam')
new: (1,), {'bar': 'spam'}
78
>>> s2 = Spam()
>>> s2.eggs(1, bar='spam')
78
"""

from klepto.safe import inf_cache as memoized
#from klepto import inf_cache as memoized
from klepto.keymaps import picklemap
dumps = picklemap(flat=False, serializer='dill')

class Spam(object):
    """A simple class with a memoized method"""

    @memoized(keymap=dumps)
    def eggs(self, *args, **kwds):
       #print ('new:', args, kwds)
        from random import random
        return int(100 * random())

s = Spam()
assert s.eggs() == s.eggs()
assert s.eggs(1) == s.eggs(1)
s2 = Spam() 
assert s.eggs(1, bar='spam') == s2.eggs(1, bar='spam')
assert s.eggs.info().hit  == 3
assert s.eggs.info().miss == 3
assert s.eggs.info().load == 0

#print ('=' * 30)


# here caching saves time in a recursive function...
@memoized(keymap=dumps)
def fibonacci(n):
    "Return the nth fibonacci number."
   #print ('calculating %s' % n)
    if n in (0, 1):
        return n
    return fibonacci(n-1) + fibonacci(n-2)

fibonacci(7)
fibonacci(9)
fibonacci(3)
assert fibonacci.info().hit  == 9
assert fibonacci.info().miss == 10
assert fibonacci.info().load == 0

#print ('=' * 30)

try:
    from numpy import sum, asarray
    @memoized(keymap=dumps, tol=3)
    def add(*args):
       #print ('new:', args)
        return sum(args)

    assert add(1,2,3.0001)  == 6.0000999999999998
    assert add(1,2,3.00012) == 6.0000999999999998
    assert add(1,2,3.0234)  == 6.0234000000000005
    assert add(1,2,3.023)   == 6.0234000000000005
    assert add.info().hit  == 2
    assert add.info().miss == 2
    assert add.info().load == 0

    def cost(x,y):
       #print ('new: %s or %s' % (str(x), str(y)))
        x = asarray(x)
        y = asarray(y)
        return sum(x**2 - y**2)

    cost1 = memoized(keymap=dumps, tol=1)(cost)
    cost0 = memoized(keymap=dumps, tol=0)(cost)
    costD = memoized(keymap=dumps, tol=0, deep=True)(cost)

   #print ("rounding to one decimals...")
    cost1([1,2,3.1234], 3.9876)# == -32.94723372
    cost1([1,2,3.1234], 3.9876)# == -32.94723372
    cost1([1,2,3.1234], 3.6789)# == -25.84728807
    cost1([1,2,3.4321], 3.6789)# == -23.82360522
    assert cost1.info().hit  == 1
    assert cost1.info().miss == 3
    assert cost1.info().load == 0

   #print ("\nrerun the above with rounding to zero decimals...")
    cost0([1,2,3.1234], 3.9876)# == -32.94723372
    cost0([1,2,3.1234], 3.9876)# == -32.94723372
    cost0([1,2,3.1234], 3.6789)# == -32.94723372
    cost0([1,2,3.4321], 3.6789)# == -23.82360522
    assert cost0.info().hit  == 2
    assert cost0.info().miss == 2
    assert cost0.info().load == 0

   #print ("\nrerun again with deep rounding to zero decimals...")
    costD([1,2,3.1234], 3.9876)# == -32.94723372
    costD([1,2,3.1234], 3.9876)# == -32.94723372
    costD([1,2,3.1234], 3.6789)# == -32.94723372
    costD([1,2,3.4321], 3.6789)# == -32.94723372
    assert costD.info().hit  == 3
    assert costD.info().miss == 1
    assert costD.info().load == 0
   #print ("")
except ImportError:
    pass


from klepto.archives import cache, sql_archive 
import dill
@memoized(cache=cache(archive=sql_archive()))
def add(x,y):
    return x+y
add(1,2)
add(1,2)
add(1,3)
#print ("sql_cache = %s" % add.__cache__())
assert add.__cache__() == {'((1, 3), {})':4, '((1, 2), {})':3}

@memoized(cache=dict())
def add(x,y):
    return x+y
add(1,2)
add(1,2)
add(1,3)
#print ("dict_cache = %s" % add.__cache__())
assert add.__cache__() == {'((1, 3), {})':4, '((1, 2), {})':3}

@memoized(cache=add.__cache__())
def add(x,y):
    return x+y
add(1,2)
add(2,2)
#print ("re_dict_cache = %s" % add.__cache__())
assert add.__cache__() == {'((1, 3), {})': 4, '((1, 2), {})': 3, '((2, 2), {})': 4}

@memoized(keymap=dumps)
def add(x,y):
    return x+y
add(1,2)
add(1,2)
add(1,3)
#print ("pickle_dict_cache = %s" % add.__cache__())

import sys
if hex(sys.hexversion) >= '0x30000f0':
    picklekey1 = '\x80\x03K\x01K\x02\x86q\x00}q\x01\x86q\x02.'
    picklekey2 = '\x80\x03K\x01K\x03\x86q\x00}q\x01\x86q\x02.'
else:
    picklekey1 = '\x80\x02K\x01K\x02\x86q\x00}q\x01\x86q\x02.'
    picklekey2 = '\x80\x02K\x01K\x03\x86q\x00}q\x01\x86q\x02.'
from klepto.tools import _b
assert add.__cache__() == {_b(picklekey1): 3, _b(picklekey2): 4}


# EOF
