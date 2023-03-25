#!/usr/bin/env python
#
# Author: Mike McKerns (mmckerns @caltech and @uqfoundation)
# Copyright (c) 2013-2016 California Institute of Technology.
# Copyright (c) 2016-2023 The Uncertainty Quantification Foundation.
# License: 3-clause BSD.  The full license text is available at:
#  - https://github.com/uqfoundation/klepto/blob/master/LICENSE

#FIXME: klepto's caches ignore names/index, however ignore should be in keymap

import inspect
from klepto.tools import IS_PYPY
def signature(func, variadic=True, markup=True, safe=False):
    """get the input signature of a function

    func: the function to inspect
    variadic: if True, also return names of (*args, **kwds) used in func
    markup: if True, show a "!" before any 'unsettable' parameters
    safe: if True, return (None,None,None,None) instead of throwing an error

    Returns a tuple of variable names and a dict of keywords with defaults.
    If variadic=True, additionally return names of func's (*args, **kwds).

    Python functions, methods, lambdas, and partials can be inspected.
    If safe=False, non-python functions (e.g. builtins) will raise an error.

    For partials, 'fixed' args correspond to positional arguments given in
    when the partial was defined. Partials have 'unsettalble' parameters,
    where, these parameters may be given as input but will throw errors.
    If markup=True, 'unsettable' parameters are denoted by a prepended '!'.

    For example:

    >>> def bar(x,y,z,a=1,b=2,*args):
    ...   return x+y+z+a+b
    ... 
    >>> signature(bar)
    (('x', 'y', 'z', 'a', 'b'), {'a': 1, 'b': 2}, 'args', '')
    >>> 
    >>> # a partial with a 'fixed' x, thus x is 'unsettable' as a keyword
    >>> p = partial(bar, 0)
    >>> signature(p)
    (('y', 'z', 'a', 'b'), {'a': 1, '!x': 0, 'b': 2}, 'args', '')
    >>> p(0,1)  
    4
    >>> p(0,1,2,3,4,5)
    6
    >>> 
    >>> # a partial where y is 'unsettable' as a positional argument
    >>> p = partial(bar, y=10)
    >>> signature(p)
    (('x', '!y', 'z', 'a', 'b'), {'a': 1, 'y': 10, 'b': 2}, 'args', '')
    >>> p(0,1,2)
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    TypeError: bar() got multiple values for keyword argument 'y'
    >>> p(0,z=2)
    15
    >>> p(0,y=1,z=2)
    6
    >>> 
    >>> # a partial with a 'fixed' x, and positionally 'unsettable' b
    >>> p = partial(bar, 0,b=10)
    >>> signature(p)
    (('y', 'z', 'a', '!b'), {'a': 1, '!x': 0, 'b': 10}, 'args', '')
    >>> 
    >>> # apply some options that reduce information content
    >>> signature(p, markup=False)
    (('y', 'z', 'a', 'b'), {'a': 1, 'b': 10}, 'args', '')
    >>> signature(p, markup=False, variadic=False)
    (('y', 'z', 'a', 'b'), {'a': 1, 'b': 10})
    """
    TINY_FAIL = None,None  #XXX: or (),{} ?
    LONG_FAIL = None,None,None,None #XXX: or (),{},'','' ?
    if safe and inspect.isbuiltin(func) and not IS_PYPY:
        return LONG_FAIL if variadic else TINY_FAIL

    #"""fixed: if True, include any 'fixed' args in returned keywords"""
    # maybe it's less confusing to tie 'fixed' to 'markup'... so do that.
    fixed = markup

    identified = False
    if not inspect.ismethod(func) and not inspect.isfunction(func):
        try: # then it could be a partial...
            p_args = func.args           # list of default arg values
            p_kwds = func.keywords or {} # dict of default kwd values
            func = func.func
            identified = True
        except AttributeError:
            if hasattr(func, '__call__') and not hasattr(func, '__name__'):
                func = func.__call__ # treat callable instance as __call__
            else: #XXX: anything else to try? No? Give up.
                pass
    if not identified:
        p_args = ()
        p_kwds = {}

    FULL_ARGS = hasattr(inspect, 'getfullargspec')
    try:
        if FULL_ARGS: arg_spec = inspect.getfullargspec(func)
        else: arg_spec = inspect.getargspec(func)
    except TypeError:
        if safe: return LONG_FAIL if variadic else TINY_FAIL
        raise TypeError('%r is not a Python function' % func)

    if hasattr(arg_spec, 'args'):
        arg_names = arg_spec.args         # list of input variable names
        arg_defaults = arg_spec.defaults  # list of kwd default values
        arg_varargs = arg_spec.varargs    # name of *args
        if FULL_ARGS:                     # name of **kwds
            arg_keywords = getattr(arg_spec, 'varkw') or {}
            arg_kwdefault = getattr(arg_spec, 'kwonlydefaults') or {}
        else:
            arg_keywords = arg_spec.keywords
            arg_kwdefault = {}
    else:
        arg_names, arg_varargs, arg_keywords, arg_defaults = arg_spec
        arg_kwdefault = {}

    if not arg_defaults or not arg_names:
        defaults = {}
        explicit = tuple(arg_names) or ()
    else:
        defaults = dict(zip(arg_names[-len(arg_defaults):],arg_defaults))
        explicit = tuple(arg_names) or ()  # always return all names
       #explicit = tuple(arg_names[:-len(arg_defaults)]) # only return args

    # for a partial, the first p_args are now at fixed values
    _fixed = dict(zip(arg_names[:len(p_args)],p_args))

    # deal with the stupid case that the partial always fails
    errors = [i for i in _fixed if i in p_kwds]
    if errors:
        if safe: return LONG_FAIL if variadic else TINY_FAIL
        raise TypeError("%s() got multiple values for keyword argument '%s'" % (func.__name__,errors[0]))
        # the above could fail if taking a partial of a partial

    # include any keyword-only defaults
    defaults.update(arg_kwdefault)
    # for a partial, arguments given in p_kwds have new defaults
    defaults.update(p_kwds)
    if markup: X = '!'
    else: X = ''
    # remove args 'fixed' by the partial; prepend 'unsettable' args with '!'
    explicit = tuple(X+i if i in p_kwds else i for i in explicit \
                                                 if i not in _fixed)
    if fixed:
       #defaults.update(_fixed)
        defaults = dict((k,v) for (k,v) in defaults.items() if k not in _fixed)
        defaults.update(dict((X+k,v) for (k,v) in _fixed.items()))

    if inspect.ismethod(func) and func.__self__:
        # then it's a bound method
        explicit = explicit[1:] #XXX: correct to remove 'self' ?

    if variadic:
        varargs = arg_varargs or ''
        varkwds = arg_keywords or ''
        return explicit, defaults, varargs, varkwds
    return explicit, defaults


import sys
def isvalid(func, *args, **kwds):
    """check if func(*args,**kwds) is a valid call for function 'func'

    returns True if valid, returns False if an error is thrown"""
    try:
        validate(func, *args, **kwds)
        return True
    except:
        error = sys.exc_info()[1]
        # check for the special case of builtins, etc
        if str(error).endswith('is not a Python function'):
           #return None  # None distinguishes from False, as "I don't know"
            try: # probably inexpensive, so just try evaluating it... (yikes?)
                func(*args, **kwds)
                return True
            except: pass
        return False

def validate(func, *args, **kwds):
    """validate a function's arguments and keywords against the call signature

    Raises an exception when args and kwds do not match the call signature.
    If valid args and kwds are provided, "None" is returned.

    NOTE: 'validate' does not call f(*args,**kwds), instead checks *args,**kwds
    against the call signature of func. Thus, 'validate' will fail when
    called to inspect builtins and other non-python functions."""
    named, defaults, hasargs, haskwds = signature(func)

    # if it's a partial, set func = func.func
    identified = False
    if not inspect.ismethod(func) and not inspect.isfunction(func):
        try: # then it could be a partial...
            p_args = func.args           # list of default arg values
            p_kwds = func.keywords or {} # dict of default kwd values
            p_named,p_defaults = signature(func.func, markup=False, variadic=False)
            func = func.func
            p_required = set(p_named) - set(p_defaults)
            identified = True
        except AttributeError:
            if hasattr(func, '__call__') and not hasattr(func, '__name__'):
                func = func.__call__ # treat callable instance as __call__
            else: #XXX: anything else to try? No? Give up.
                pass
    if not identified:
        p_args = p_named = ()
        p_kwds = p_defaults = {}
        p_required = set()

    # get bad args/kwds from markup
    bad_args = set(i.strip('!') for i in named if i.startswith('!'))
    bad_kwds = set(i.strip('!') for i in defaults if i.startswith('!'))
    # strip markup
    named, defaults = strip_markup(named, defaults)

    # FAIL if partial built for **kwds, but **kwds not used in func.func
    p_varkwds = set(p_kwds) - bad_kwds - bad_args
    if p_varkwds and not haskwds:
        raise TypeError("%s() got an unexpected keyword argument '%s'" % (func.__name__,p_varkwds.pop()))

    # FAIL if partial built for *args, but *args not used in func.func
    p_varargs = max(0, len(p_args) - len(p_required))
    if p_varargs and not hasargs:
        raise TypeError("%s() takes at most %d arguments (%d given)" % (func.__name__, len(p_named), len(p_args)+len(args)+len(kwds)))

    # get any varargs; FAIL if func doesn't take varargs
    var_args = args[len(named):]
    if var_args and not hasargs:
        var_kwds = set(kwds) - set(named)
        raise TypeError("%s() takes at most %d arguments (%d given)" % (func.__name__, len(named)+len(p_args), len(p_args)+len(args)+len(kwds)))

    # check any varkwds; FAIL if func doesn't take varkwds
    var_kwds = set(kwds) - set(named)
    if var_kwds and not haskwds:
        raise TypeError("%s() got an unexpected keyword argument '%s'" % (func.__name__,var_kwds.pop()))

    # get user_args as a dict
    args_kwds = dict(zip(named,args))

    # check if user has given one of the bad_args or bad_kwds
    bad_args = bad_args.intersection(args_kwds)
    if bad_args:
        raise TypeError("%s() got multiple values for keyword argument '%s'" % (func.__name__, bad_args.pop()))
    bad_kwds = bad_kwds.intersection(kwds)
    if bad_kwds:
        raise TypeError("%s() got multiple values for keyword argument '%s'" % (func.__name__, bad_kwds.pop()))

    # check for duplicates; FAIL if anything is defined twice
    duplicates = set(args_kwds).intersection(kwds)
    if duplicates:
        raise TypeError("%s() got multiple values for keyword argument '%s'" % (func.__name__, duplicates.pop()))

    # get names of required args
    required = set(named) - set(defaults)

    # mixin defaults
    defaults.update(kwds)

    # now there are no duplicates, build a dict of all known names/values
    defaults.update(args_kwds)

    # check if all required are provided; FAIL if any required are missing
    provided = required.intersection(defaults)
    _required = len(required)
    if len(provided) < _required:
        p_bad = len(p_args) + len(set(named).intersection(p_kwds))
       #p_bad = len(bad_args) + len(bad_kwds)
        _required = max(len(p_required), _required)
        provided = len(provided) + p_bad
        raise TypeError("%s() takes at least %d arguments (%d given)" % (func.__name__, _required, provided))

    # if you are here, then success!
    return None #XXX: better return (args, kwds.copy()) ?

from klepto.keymaps import keymap as kleptokeymap
from klepto.rounding import simple_round, deep_round
def keygen(*ignored, **kwds):
  """decorator for generating a cache key for a given function

  ignored: names and/or indicies of the function's arguments to 'ignore'
  tol: integer tolerance for rounding (default is None)
  deep: boolean for rounding depth (default is False, i.e. 'shallow')

  The decorator accepts integers (for the index of positional args to ignore,
  or strings (the names of the kwds to ignore). A cache key is returned,
  built with the registered keymap. Ignored arguments are stored in the
  keymap with a value of klepto.NULL.  Note that for class methods, it may
  be useful to ignore 'self'.

  The decorated function will gain new methods for working with cache keys
      - call: __call__ the function with the most recently provided arguments
      - valid: True if the most recently provided arguments are valid
      - key: get the cache key for the most recently provided arguments
      - keymap: get the registered keymap [default: klepto.keymaps.keymap]
      - register: register a new keymap

  The function is not evaluated until the 'call' method is called.  Both
  generating the key and checking for validity avoid calling the function
  by inspecting the function's input signature.

  The default keymap is keymaps.keymap(flat=True). Alternate keymaps can be
  set with the 'register' method on the decorated function."""
  # returns (*varargs, **kwds) where all info in kwds except varargs
  # however, special cases (builtins, etc) return (*args, **kwds)
  _map = kwds.get('keymap', None)
  if _map is None: _map = kleptokeymap()
  tol = kwds.get('tol', None)
  deep = kwds.get('deep', False)
  if deep: rounded = deep_round
  else: rounded = simple_round
  # enable rounding
  @rounded(tol)
  def rounded_args(*args, **kwds):
    return (args, kwds)
  def dec(f):
    _args = [(),{}]
    _keymap = [_map] #[kleptokeymap()]
    def last_args():
      "get the most recently provided (*args, **kwds)"
      return _args[0],_args[1]
    def func(*args, **kwds):
      _args[0] = args
      _args[1] = kwds
      _map = _keymap[0]
      args,kwds = rounded_args(*args, **kwds)
      args,kwds = _keygen(f, ignored, *args, **kwds)
      return _map(*args, **kwds)
    def call():
      "call func with the most recently provided (*args, **kwds)"
      ar,kw = last_args()
      return f(*ar,**kw)
    def valid():
      "check if func(*args, **kwds) is valid (without calling the function)"
      ar,kw = last_args()
      return isvalid(f,*ar,**kw) #XXX: better validate? (raises errors)
    def key():
      "get cache 'key' for most recently provided (*args, **kwds)"
      ar,kw = last_args()
      _map = _keymap[0]
      ar,kw = rounded_args(*ar, **kw)
      ar,kw = _keygen(f, ignored, *ar, **kw) #XXX: better lookup saved key?
      return _map(*ar, **kw)
    def register(mapper):
      "register a new keymap instance" 
      if isinstance(mapper, type): mapper = mapper()
      if not isinstance(mapper, kleptokeymap):
        raise TypeError("'%s' is not a klepto keymap instance" % getattr(mapper,'__name__',mapper))
      _keymap[0] = mapper
      return
    def keymap():
      "get the registered keymap instance"
      return _keymap[0]
    func.__ignored__ = ignored
    func.__func__ = f
    func.__args__ = last_args
    func.call = call
    func.valid = valid
    func.key = key
    func.keymap = keymap
    func.register = register
    return func
  return dec


###################################
def strip_markup(names, defaults):
    """strip markup ('!') from function argument names and defaults"""
    names = tuple(i.strip('!') for i in names)
    defaults = dict((k,v) for (k,v) in defaults.items() if not k.startswith('!'))
    return names, defaults


class _Null(object):
    """build a stub object for the NULL singleton"""
    def __repr__(self):
        return "NULL"
NULL = _Null()


#try:
#    from collections import OrderedDict as odict
#except ImportError:
#    #XXX: adds a new dependency
#    from ordereddict import OrderedDict as odict

from copy import copy
def _keygen(func, ignored, *args, **kwds):
    """generate a 'key' from the (*args,**kwds) suitable for use in caching

    func is the function being called
    ignored is the list of names and/or indicies to ignore
    args and kwds are func's input arguments and keywords

    returns the archive 'key' -- does not call the function

    ignored can include names (e.g. 'x','y'), indicies (e.g. 0,1), or '*','**'.
    if '*' in ignored, all varargs are ignored. Similarly for '**' and varkwds.`
    Note that for class methods, it may be useful to ignore 'self'.
    """
    # hard-wire cross-populate names and indicies to True
#   crossref = True
    # hard-wire discover and apply function defaults to True
    defaults = True
    # hard-wire that keygen is 'safe' (doesn't throw errors from signature)
    safe = True

    # get variable names and defaults from func signature
    explicitly_named,user_kwds = signature(func,markup=False,variadic=False, safe=safe)
    # start off with user_args as the user provided args
    user_args = copy(args)
    # if safe and signature failed, return unmolested *args, **kwds
    if explicitly_named is None and user_kwds is None:
        return user_args, kwds.copy()
    # mix-in the function's defaults to the user provided kwds
    if defaults:
        user_kwds.update(kwds)
    else: # don't apply the function defaults (why, you wouldn't, I don't know)
        user_kwds = kwds.copy()

    # decompose the list of things to ignore to names and indicies
    if isinstance(ignored, (str,int)): ignored = [ignored]
    index_to_ignore = set(i for i in ignored if isinstance(i,int))
    names_to_ignore = set(i for i in ignored if isinstance(i,str))

    # if ignore self, remove self instead of NULL it
    if inspect.isfunction(func):
        try: # this is a pretty good filter that: user_args[0] is self
            _bound = getattr(user_args[0], func.__name__)
            _self = getattr(_bound, '__self__')
            assert _self == user_args[0]
        except:
            _bound = None
        if _bound and explicitly_named[0] in ignored:
            user_args = user_args[1:]                # remove 'self' instance
            user_kwds.pop(explicitly_named[0], None) #XXX: unnecessary?
            explicitly_named = explicitly_named[1:]  # remove 'self' name
            #XXX: hopefully, this doesn't mess up arg counting and other stuff

    # remove markers for ignoring all varagrs and all varkwds
    varargs_to_ignore = '*' in names_to_ignore
    varkwds_to_ignore = '**' in names_to_ignore
    names_to_ignore -= set(['*','**'])
#   var_index_to_ignore = {i for i in index_to_ignore if i >= len(explicitly_named)}
#   fix_index_to_ignore = index_to_ignore - var_index_to_ignore
#   fix_names_to_ignore = {i for i in names_to_ignore if i in explicitly_named}
#   var_names_to_ignore = names_to_ignore - fix_names_to_ignore - set(['*','**'])

    # cross-populate names_to_ignore and index_to_ignore for explicitly_named
    names_index = dict(enumerate(explicitly_named))
    _index = set(i for (i,k) in names_index.items() if k in names_to_ignore)
    _names = set(k for (i,k) in names_index.items() if i in index_to_ignore)
    names_to_ignore = names_to_ignore.union(_names)
    index_to_ignore = index_to_ignore.union(_index)

    # NULL out the ignored args (and also drop not in user_args)
    #XXX: better if user_args always include NAMES/INDEX from ignored?  NO.
    user_args = tuple(NULL if i in index_to_ignore else k for i,k in enumerate(user_args))
    # if ignoring *args, clip off all args that are varargs
    if varargs_to_ignore:
        user_args = user_args[:len(explicitly_named)]

    # NULL out the ignored kwds (also drop not in user_kwds + explicitly_named)
    #XXX: better if user_kwds always include NAMES/INDEX from ignored?  MAYBE.
   #user_kwds.update(dict([(k,NULL) for k in names_to_ignore])) #(see above)
    _keys = tuple(user_kwds.keys()) + explicitly_named
    user_kwds.update(dict([(k,NULL) for k in names_to_ignore if k in _keys]))
    # if ignoring **kwds, then pop all not in explicitly_named
    if varkwds_to_ignore:
        [user_kwds.pop(k) for k in kwds if k not in explicitly_named]

    # NULL out args that are NULL'ed as kwds, and vice-versa 
#   if crossref:
#       inputs = odict(zip(explicitly_named,user_args)) 
#       vararg = user_args[len(explicitly_named):]
#       user_kwds.update([(k,v) for (k,v) in inputs.items() if v == NULL and k in user_kwds])
#       inputs.update(dict((k,v) for (k,v) in user_kwds.items() if v == NULL and k in inputs))
#       user_args = tuple(inputs.values()) + vararg

    # transfer all from user_args to user_kwds, except for any varargs
    user_kwds.update(dict(zip(explicitly_named,user_args))) #XXX: if double-defined, prefer value in args
   #user_kwds.update(dict((k,v) for (k,v) in zip(explicitly_named,user_args) if k not in user_kwds)) #XXX: if double-defined, prefer value in kwds
    user_args = user_args[len(explicitly_named):]

    return user_args, user_kwds


# EOF
