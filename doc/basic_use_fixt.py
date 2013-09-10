from __future__ import print_function, division, absolute_import

import fakesleep

def globs(globs):
    # hack so that introspection works in doctest module
    globs['__name__'] = '__main__'
    return globs

def setup():
    fakesleep.monkey_patch()

def teardown():
    fakesleep.monkey_restore()