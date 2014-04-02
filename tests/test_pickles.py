import dill
import klepto

@klepto.lru_cache()
def squared(x):
    return x**2

squared(2)
squared(4)
squared(6)

_s = dill.loads(dill.dumps(squared))
assert _s.lookup(4) == 16
assert squared.__cache__() == _s.__cache__()

