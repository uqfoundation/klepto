from klepto.keymaps import *
h = hashmap(algorithm='md5')
p = picklemap(serializer='dill')
hp = p + h

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


# EOF
