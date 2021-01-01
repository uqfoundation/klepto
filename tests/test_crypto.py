#!/usr/bin/env python
#
# Author: Mike McKerns (mmckerns @caltech and @uqfoundation)
# Copyright (c) 2013-2016 California Institute of Technology.
# Copyright (c) 2016-2021 The Uncertainty Quantification Foundation.
# License: 3-clause BSD.  The full license text is available at:
#  - https://github.com/uqfoundation/klepto/blob/master/LICENSE

from klepto.crypto import *
from klepto.tools import _b
from klepto.keymaps import *


def test_encoding():
    assert string('1') == '1'
    assert string('1', encoding='repr') == "'1'"

    x = [1,2,3,'4',"'5'", min]
    assert hash(x, 'sha1') == '3bdd73e79be4277dcb874d193b8dd08a46bc6885'
    assert pickle(x) == string(x, 'repr')
    assert string(x) == '[1, 2, 3, \'4\', "\'5\'", <built-in function min>]'
    assert string(x, encoding='repr') == '[1, 2, 3, \'4\', "\'5\'", <built-in function min>]'
    assert string(x, encoding='utf_8') == _b('[1, 2, 3, \'4\', "\'5\'", <built-in function min>]')
    # some encodings 'missing' from klepto in python 3.x (due to bytes madness)
    if 'unicode' in encodings():
        assert string(x, encoding='unicode') == unicode('[1, 2, 3, \'4\', "\'5\'", <built-in function min>]')
    if 'zlib_codec' in encodings():
        assert string(x, encoding='zlib_codec') == 'x\x9c\x8b6\xd4Q0\xd2Q0\xd6QP7Q\xd7QPR7UW\xd2Q\xb0I*\xcd\xcc)\xd1\xcd\xccSH+\xcdK.\xc9\xcc\xcfS\xc8\xcd\xcc\xb3\x8b\x05\x00\xf6(\x0c\x9c'
    if 'hex_codec' in encodings():
        assert string(x, encoding='hex_codec') == '5b312c20322c20332c202734272c2022273527222c203c6275696c742d696e2066756e6374696f6e206d696e3e5d'

    s = stringmap()
    assert s(x) == '([1, 2, 3, \'4\', "\'5\'", <built-in function min>],)'
    s = stringmap(encoding='utf_8')
    assert s(x) == _b('([1, 2, 3, \'4\', "\'5\'", <built-in function min>],)')
    # some encodings 'missing' from klepto in python 3.x (due to bytes madness)
    if 'unicode' in encodings():
        s = stringmap(encoding='unicode')
        assert s(x) == unicode('([1, 2, 3, \'4\', "\'5\'", <built-in function min>],)')
    if 'zlib_codec' in encodings():
        s = stringmap(encoding='zlib_codec')
        assert s(x) == 'x\x9c\xd3\x886\xd4Q0\xd2Q0\xd6QP7Q\xd7QPR7UW\xd2Q\xb0I*\xcd\xcc)\xd1\xcd\xccSH+\xcdK.\xc9\xcc\xcfS\xc8\xcd\xcc\xb3\x8b\xd5\xd1\x04\x00\x17\x99\r\x19'
    if 'hex_codec' in encodings():
        s = stringmap(encoding='hex_codec')
        assert s(x) == '285b312c20322c20332c202734272c2022273527222c203c6275696c742d696e2066756e6374696f6e206d696e3e5d2c29'


if __name__ == '__main__':
    test_encoding()
