import unittest
from io import StringIO

from . import math_is_hard

import instrument
from instrument.output.table import TableMetric

class TableMetricTestCase(unittest.TestCase):

    def test_stats(self):
        TableMetric.dump_atexit = False
        TableMetric.outfile = StringIO()

        list(instrument.all(math_is_hard(10), metric=TableMetric.metric, name="alice"))
        list(instrument.all(math_is_hard(20), metric=TableMetric.metric, name="alice"))

        list(instrument.all(math_is_hard(10), metric=TableMetric.metric, name="bob"))

        # unnamed metrics are dropped
        list(instrument.all(math_is_hard(10), metric=TableMetric.metric))

        TableMetric.dump()
        result = 'Name         Count Mean        Count Stddev        Elapsed Mean        Elapsed Stddev        \nalice          15.00               5.00               15.00                 5.00             \nbob            10.00               0.00               10.00                 0.00             \n'
        self.assertMultiLineEqual(TableMetric.outfile.getvalue(), result)
