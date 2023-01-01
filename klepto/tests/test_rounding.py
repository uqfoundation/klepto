#!/usr/bin/env python
#
# Author: Mike McKerns (mmckerns @caltech and @uqfoundation)
# Copyright (c) 2013-2016 California Institute of Technology.
# Copyright (c) 2016-2023 The Uncertainty Quantification Foundation.
# License: 3-clause BSD.  The full license text is available at:
#  - https://github.com/uqfoundation/klepto/blob/master/LICENSE

from klepto.rounding import *

def test_deep_round():
    @deep_round(tol=1)
    def add(x,y):
        return x+y

    result = add(2.54, 5.47)
    assert result == 8.0

    # rounds each float, regardless of depth in an object
    result = add([2.54, 'x'],[5.47, 'y'])
    assert result == [2.5, 'x', 5.5, 'y']

    # rounds each float, regardless of depth in an object
    result = add([2.54, 'x'],[5.47, [8.99, 'y']])
    assert result == [2.5, 'x', 5.5, [9.0, 'y']]

def test_simple_round():
    @simple_round(tol=1)
    def add(x,y):
        return x+y

    result = add(2.54, 5.47)
    assert result == 8.0

    # does not round elements of iterables, only rounds at the top-level
    result = add([2.54, 'x'],[5.47, 'y'])
    assert result == [2.54, 'x', 5.4699999999999998, 'y']

    # does not round elements of iterables, only rounds at the top-level
    result = add([2.54, 'x'],[5.47, [8.99, 'y']])
    assert result == [2.54, 'x', 5.4699999999999998, [8.9900000000000002, 'y']]

def test_shallow_round():
    @shallow_round(tol=1)
    def add(x,y):
        return x+y

    result = add(2.54, 5.47)
    assert result == 8.0

    # rounds each float, at the top-level or first-level of each object.
    result = add([2.54, 'x'],[5.47, 'y'])
    assert result == [2.5, 'x', 5.5, 'y']

    # rounds each float, at the top-level or first-level of each object.
    result = add([2.54, 'x'],[5.47, [8.99, 'y']])
    assert result == [2.5, 'x', 5.5, [8.9900000000000002, 'y']]


# rounding integrated with key generation
from klepto import keygen, NULL

def test_keygen():
    @keygen('x',2,tol=2)
    def add(w,x,y,z):
        return x+y+z+w

    assert add(1.11111,2.222222,3.333333,4.444444) == ('w', 1.11, 'x', NULL, 'y', NULL, 'z', 4.44)
    assert add.call() == 11.111108999999999
    assert add(1.11111,2.2229,100,4.447) == ('w', 1.11, 'x', NULL, 'y', NULL, 'z', 4.45)
    assert add.call() == 107.78101
    assert add(1.11111,100,100,4.441) == ('w', 1.11, 'x', NULL, 'y', NULL, 'z', 4.44)
    assert add.call() == 205.55211


if __name__ == '__main__':
    test_deep_round()
    test_simple_round()
    test_shallow_round()
    test_keygen()
