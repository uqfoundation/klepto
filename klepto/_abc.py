#!/usr/bin/env python
#
# Author: Mike McKerns (mmckerns @caltech and @uqfoundation)
# Copyright (c) 2021-2023 The Uncertainty Quantification Foundation.
# License: 3-clause BSD.  The full license text is available at:
#  - https://github.com/uqfoundation/klepto/blob/master/LICENSE
"""
base class for archive to memory, file, or database
"""
class archive(dict):
    """dictionary with an archive interface"""
    def __init__(self, *args, **kwds):
        """initialize an archive"""
        dict.__init__(self, *args, **kwds)
        self.__state__ = {'id': 'abc'}
        raise NotImplementedError("cannot instantiate archive base class")
        #return
    def __asdict__(self):
        """build a dictionary containing the archive contents"""
        return dict(self.items())
    def __repr__(self):
        return "%s(%s, cached=False)" % (self.__class__.__name__, self.__asdict__())
    __repr__.__doc__ = dict.__repr__.__doc__
    def copy(self, name=None): #XXX: always None? or allow other settings?
        "D.copy(name) -> a copy of D, with a new archive at the given name"
        adict = self.__class__()
        adict.update(self.__asdict__())
        adict.__state__ = self.__state__.copy()
        if name is not None:
            adict.__state__['id'] = name
        return adict
    # interface
    def load(self, *args):
        """does nothing. required to use an archive as a cache"""
        return
    dump = load
    def archived(self, *on):
        """check if the cache is a persistent archive"""
        L = len(on)
        if not L: return False
        if L > 1: raise TypeError("archived expected at most 1 argument, got %s" % str(L+1))
        raise ValueError("cannot toggle archive")
    def sync(self, clear=False):
        "does nothing. required to use an archive as a cache"
        pass
    def drop(self): #XXX: or actually drop the backend?
        "set the current archive to NULL"
        return self.__archive(None)
    def open(self, archive):
        "replace the current archive with the archive provided"
        return self.__archive(archive)
    def __get_archive(self):
        return self
    def __get_name(self):
        return self.__state__['id']
    def __get_state(self):
        return self.__state__.copy()
    def __archive(self, archive):
        raise ValueError("cannot set new archive")
    archive = property(__get_archive, __archive)
    name = property(__get_name, __archive)
    state = property(__get_state, __archive)
    pass

