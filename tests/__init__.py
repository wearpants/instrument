from __future__ import print_function, division, absolute_import

import unittest
import fakesleep
import time

def math_is_hard(N):
    x = 0
    while x < N:
        time.sleep(1)
        yield x * x
        x += 1


class MeasureItTestCase(unittest.TestCase):

    def setUp(self):
        fakesleep.monkey_patch()

    def tearDown(self):
        fakesleep.monkey_restore()