#!/usr/bin/env python
#
# Author: Mike McKerns (mmckerns @caltech and @uqfoundation)
# Copyright (c) 2013-2016 California Institute of Technology.
# Copyright (c) 2016-2023 The Uncertainty Quantification Foundation.
# License: 3-clause BSD.  The full license text is available at:
#  - https://github.com/uqfoundation/klepto/blob/master/LICENSE

from klepto.keymaps import *
h = hashmap(algorithm='md5')
p = picklemap(serializer='dill')
hp = p + h

def test_bigdata():
    try:
        import numpy as np
        x = np.arange(2000)
        y = x.copy()
        y[1000] = -1

        assert h(x) == h(y) # equal because repr for large np arrays uses '...'
        assert p(x) != p(y)
        assert hp(x) != hp(y)
    except ImportError:
        print("to test big data, install numpy")


if __name__ == '__main__':
    test_bigdata()
