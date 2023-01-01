#!/usr/bin/env python
#
# Author: Mike McKerns (mmckerns @caltech and @uqfoundation)
# Copyright (c) 2013-2016 California Institute of Technology.
# Copyright (c) 2016-2023 The Uncertainty Quantification Foundation.
# License: 3-clause BSD.  The full license text is available at:
#  - https://github.com/uqfoundation/klepto/blob/master/LICENSE

from klepto.keymaps import *
from dill import dumps, loads

args = (1,2); kwds = {"a":3, "b":4}

def test_keymap():
    encode = keymap(typed=False, flat=True, sentinel=NOSENTINEL)
    assert encode(*args, **kwds) == (1, 2, 'a', 3, 'b', 4)
    encode = keymap(typed=False, flat=False, sentinel=NOSENTINEL)
    assert encode(*args, **kwds) == (args, kwds)
    encode = keymap(typed=True, flat=True, sentinel=NOSENTINEL)
    assert encode(*args, **kwds) == (1, 2, 'a', 3, 'b', 4, type(1), type(2), type(3), type(4))
    encode = keymap(typed=True, flat=False, sentinel=NOSENTINEL)
    assert encode(*args, **kwds) == (args, kwds, (type(1), type(2)), (type(3), type(4)))

def test_hashmap():
    encode = hashmap(typed=False, flat=True, sentinel=NOSENTINEL)
    assert encode(*args, **kwds) == hash((1, 2, 'a', 3, 'b', 4))
    #encode = hashmap(typed=False, flat=False, sentinel=NOSENTINEL)
    #assert encode(*args, **kwds) == TypeError("unhashable type: 'dict'")
    encode = hashmap(typed=True, flat=True, sentinel=NOSENTINEL)
    assert encode(*args, **kwds) == hash((1, 2, 'a', 3, 'b', 4, type(1), type(2), type(3), type(4)))
    #encode = hashmap(typed=True, flat=False, sentinel=NOSENTINEL)
    #assert encode(*args, **kwds) == TypeError("unhashable type: 'dict'")

def test_stringmap():
    encode = stringmap(typed=False, flat=True, sentinel=NOSENTINEL)
    assert encode(*args, **kwds) == "(1, 2, 'a', 3, 'b', 4)"
    encode = stringmap(typed=False, flat=False, sentinel=NOSENTINEL)
    assert eval(encode(*args, **kwds)) == (args, kwds)
    #res = encode(*args, **kwds)
    #assert res in ("({}, {})".format(str(args),_kwds), "({}, {})".format(str(args),kwds_))
    encode = stringmap(typed=True, flat=True, sentinel=NOSENTINEL)
    assert encode(*args, **kwds) == str( (1, 2, 'a', 3, 'b', 4, type(1), type(2), type(3), type(4)) )
    encode = stringmap(typed=True, flat=False, sentinel=NOSENTINEL)
    assert eval(encode(*args, **kwds).replace(str((type(1), type(2))), "''")) == (args, kwds, '', '')

def test_picklemap():
    encode = picklemap(typed=False, flat=True, serializer='dill')
    assert encode(*args, **kwds) == dumps((1, 2, 'a', 3, 'b', 4))
    encode = picklemap(typed=False, flat=False, serializer='dill')
    assert loads(encode(*args, **kwds)) == loads(dumps((args, kwds)))
    encode = picklemap(typed=True, flat=True, serializer='dill')
    assert encode(*args, **kwds) == dumps( (1, 2, 'a', 3, 'b', 4, type(1), type(2), type(3), type(4)) )
    encode = picklemap(typed=True, flat=False, serializer='dill')
    assert loads(encode(*args, **kwds)) == loads(dumps( (args, kwds, (type(1), type(2)), (type(3), type(4))) ))


if __name__ == '__main__':
    test_keymap()
    test_hashmap()
    test_stringmap()
    test_picklemap()
