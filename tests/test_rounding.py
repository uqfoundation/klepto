from klepto.rounding import *

@deep_round(tol=1)
def add(x,y):
  return x+y

result = add(2.54, 5.47)
assert result == 8.0

# rounds each float, regardless of depth in an object
result = add([2.54, 5.47],['x','y'])
assert result == [2.5, 5.5, 'x', 'y']

# rounds each float, regardless of depth in an object
result = add([2.54, 5.47],['x',[8.99, 'y']])
assert result == [2.5, 5.5, 'x', [9.0, 'y']]

@simple_round(tol=1)
def add(x,y):
  return x+y

result = add(2.54, 5.47)
assert result == 8.0

# does not round elements of iterables, only rounds at the top-level
result = add([2.54, 5.47],['x','y'])
assert result == [2.54, 5.4699999999999998, 'x', 'y']

# does not round elements of iterables, only rounds at the top-level
result = add([2.54, 5.47],['x',[8.99, 'y']])
assert result == [2.54, 5.4699999999999998, 'x', [8.9900000000000002, 'y']]

@shallow_round(tol=1)
def add(x,y):
  return x+y

result = add(2.54, 5.47)
assert result == 8.0

# rounds each float, at the top-level or first-level of each object.
result = add([2.54, 5.47],['x','y'])
assert result == [2.5, 5.5, 'x', 'y']

# rounds each float, at the top-level or first-level of each object.
result = add([2.54, 5.47],['x',[8.99, 'y']])
assert result == [2.5, 5.5, 'x', [8.9900000000000002, 'y']]


# rounding integrated with key generation
from klepto import keygen, NULL

@keygen('x',2,tol=2)
def add(w,x,y,z):
    return x+y+z+w

assert add(1.11111,2.222222,3.333333,4.444444) == ('w', 1.11, 'x', NULL, 'y', NULL, 'z', 4.44)
assert add.call() == 11.111108999999999
assert add(1.11111,2.2229,100,4.447) == ('w', 1.11, 'x', NULL, 'y', NULL, 'z', 4.45)
assert add.call() == 107.78101
assert add(1.11111,100,100,4.441) == ('w', 1.11, 'x', NULL, 'y', NULL, 'z', 4.44)
assert add.call() == 205.55211



# EOF
