import fakesleep

from measure_it import measure_iter

from tests import math_is_hard

def globs(globs):
    globs['measure_iter'] = measure_iter
    globs['math_is_hard'] = math_is_hard
    return globs

def setup():
    fakesleep.monkey_patch()

def teardown():
    fakesleep.monkey_restore()