#!/usr/bin/env python
#
# Author: Mike McKerns (mmckerns @caltech and @uqfoundation)
# Copyright (c) 2013-2016 California Institute of Technology.
# Copyright (c) 2016-2021 The Uncertainty Quantification Foundation.
# License: 3-clause BSD.  The full license text is available at:
#  - https://github.com/uqfoundation/klepto/blob/master/LICENSE

import dill
import klepto

@klepto.lru_cache()
def squared(x):
    return x**2

squared(2)
squared(4)
squared(6)

def test_pickles():
    _s = dill.loads(dill.dumps(squared))
    assert _s.lookup(4) == 16
    assert squared.__cache__() == _s.__cache__()


if __name__ == '__main__':
    test_pickles()

