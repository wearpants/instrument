import unittest
import fakesleep

class MeasureItTestCase(unittest.TestCase):

    def setUp(self):
        fakesleep.monkey_patch()

    def tearDown(self):
        fakesleep.monkey_restore()