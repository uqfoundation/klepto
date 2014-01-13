import sys
from functools import partial
from klepto.keymaps import hashmap
from klepto import NULL
from klepto import signature, keygen
from klepto import _keygen

def bar(x,y,z,a=1,b=2,*args):
  return x+y+z+a+b

s = signature(bar)
assert s == (('x', 'y', 'z', 'a', 'b'), {'a': 1, 'b': 2}, 'args', '')

# a partial with a 'fixed' x, thus x is 'unsettable' as a keyword
p = partial(bar, 0)
s = signature(p)
assert s == (('y', 'z', 'a', 'b'), {'a': 1, '!x': 0, 'b': 2}, 'args', '')
'''
>>> p(0,1)  
    4
>>> p(0,1,2,3,4,5)
    6
'''
# a partial where y is 'unsettable' as a positional argument
p = partial(bar, y=10)
s = signature(p)
assert s == (('x', '!y', 'z', 'a', 'b'), {'a': 1, 'y': 10, 'b': 2}, 'args', '')
'''
>>> p(0,1,2)
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    TypeError: bar() got multiple values for keyword argument 'y'
>>> p(0,z=2)
    15
>>> p(0,y=1,z=2)
    6
'''
# a partial with a 'fixed' x, and positionally 'unsettable' b
p = partial(bar, 0,b=10)
s = signature(p)
assert s == (('y', 'z', 'a', '!b'), {'a': 1, '!x': 0, 'b': 10}, 'args', '')


#################################################################
# test _keygen 
ignored = (0,1,3,5,'*','b','c')
user_args = ('0','1','2','3','4','5','6')
user_kwds = {'a':'10','b':'20','c':'30','d':'40'}
key_args,key_kwds = _keygen(p, ignored, *user_args, **user_kwds) 
assert key_args == ()
assert key_kwds == {'a': '2', 'c': NULL, 'b': NULL, 'd': '40', 'y': NULL, 'z': NULL}

ignored = (0,1,3,5,'**','b','c')
user_args = ('0','1','2','3','4','5','6')
user_kwds = {'a':'10','b':'20','c':'30','d':'40'}
key_args,key_kwds = _keygen(p, ignored, *user_args, **user_kwds) 
assert key_args == ('4', NULL, '6')
assert key_kwds == {'a': '2', 'b': NULL, 'y': NULL, 'z': NULL}

ignored = ('*','**')
user_args = ('0','1','2','3','4','5','6')
user_kwds = {'a':'10','b':'20','c':'30','d':'40'}
key_args,key_kwds = _keygen(p, ignored, *user_args, **user_kwds) 
assert key_args == ()
assert key_kwds == {'a': '2', 'b': '3', 'y': '0', 'z': '1'}

ignored = (0,2)
user_args = ('0','1','2','3','4','5','6')
user_kwds = {'a':'10','b':'20','c':'30','d':'40'}
key_args,key_kwds = _keygen(p, ignored, *user_args, **user_kwds) 
assert key_args == ('4', '5', '6')
assert key_kwds == {'a': NULL, 'c': '30', 'b': '3', 'd':'40', 'y': NULL, 'z': '1'}

ignored = (0,)
user_args = ('0','1','2','3','4','5','6')
user_kwds = {'a':'10','b':'20','c':'30','d':'40','y':50}
key_args,key_kwds = _keygen(p, ignored, *user_args, **user_kwds) 
assert key_args == ('4', '5', '6')
assert key_kwds == {'a': '2', 'c': '30', 'b': '3', 'd':'40', 'y': NULL, 'z': '1'}

ignored = ('a','y','c')
user_args = ('0','1','2','3','4','5','6')
user_kwds = {'a':'10','b':'20','c':'30','d':'40','y':50}
key_args,key_kwds = _keygen(p, ignored, *user_args, **user_kwds) 
assert key_args == ('4', '5', '6')
assert key_kwds == {'a': NULL, 'c': NULL, 'b': '3', 'd':'40', 'y': NULL, 'z': '1'}

ignored = (1,5,'a','y','c')
user_args = ('0','1')
user_kwds = {}
key_args,key_kwds = _keygen(p, ignored, *user_args, **user_kwds) 
assert key_args == ()
assert key_kwds == {'a': NULL, 'y': NULL, 'b': 10, 'z': NULL} #XXX: c?

ignored = (1,5,'a','y','c')
user_args = ()
user_kwds = {'c':'30','d':'40','y':50}
key_args,key_kwds = _keygen(p, ignored, *user_args, **user_kwds) 
assert key_args == ()
assert key_kwds == {'a': NULL, 'y': NULL, 'c': NULL, 'd': '40', 'b': 10, 'z': NULL}

ignored = (1,5,'a','c')
user_args = ('0','1')
user_kwds = {}
key_args,key_kwds = _keygen(p, ignored, *user_args, **user_kwds) 
assert key_args == ()
assert key_kwds == {'a': NULL, 'y': '0', 'b': 10, 'z': NULL} #XXX: c?

ignored = ()
user_args = ('0',)
user_kwds = {'c':'30'}
key_args,key_kwds = _keygen(p, ignored, *user_args, **user_kwds) 
assert key_args == ()
assert key_kwds == {'a': 1, 'y': '0', 'b': 10, 'c': '30'}


#################################################################
@keygen('x','**')
def foo(x,y,z=2):
    return x+y+z

assert foo(0,1,2) == (((), {'y': 1, 'x': NULL, 'z': 2}),)
assert foo.valid() == True
assert foo(10,1,2) == (((), {'y': 1, 'x': NULL, 'z': 2}),)
assert foo(0,1) == (((), {'y': 1, 'x': NULL, 'z': 2}),)
assert foo(0,1,3) == (((), {'y': 1, 'x': NULL, 'z': 3}),)
assert foo(0,1,r=3) == (((), {'y': 1, 'x': NULL, 'z': 2}),)
assert foo.valid() == False
assert foo(0,1,x=1) == (((), {'y': 1, 'x': NULL, 'z': 2}),)
assert foo.valid() == False
res2 = (((), {'y': 2, 'x': NULL, 'z': 10}),)
assert foo(10,y=2,z=10) == res2
assert foo.valid() == True
res1 = (((), {'y': 1, 'x': NULL, 'z': 10}),)
assert foo(0,1,z=10) == res1
assert foo.valid() == True
assert foo.call() == 11
h = hashmap(algorithm='md5')
foo.register(h)
if hex(sys.hexversion) < '0x30300f0':
    _hash1 = '6df3084851976459df23e86277ba6233'
    _hash2 = '4bce563a4168a6e452c1c404aa3bed30'
else: # python 3.3 has hash randomization, apparently
    from klepto.crypto import hash
    _hash1 = hash(res1, 'md5')
    _hash2 = hash(res2, 'md5')
assert foo(0,1,z=10) == _hash1
assert str(foo.keymap()) == str(h)
assert foo.key() == _hash1
assert foo(10,y=1,z=10) == _hash1
assert foo(10,y=2,z=10) == _hash2


# EOF
