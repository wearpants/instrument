from __future__ import print_function, division, absolute_import

import time
import tempfile
import shutil
import os
import StringIO

from . import MeasureItTestCase, math_is_hard

from measure_it import measure_iter
from measure_it.numpy import StatsMetric, PlotMetric

class StatsMetricTestCase(MeasureItTestCase):

    def test_stats(self):
        StatsMetric.dump_atexit = False
        StatsMetric.outfile = StringIO.StringIO()

        list(measure_iter(math_is_hard(10), metric=StatsMetric.metric, name="alice"))
        list(measure_iter(math_is_hard(20), metric=StatsMetric.metric, name="alice"))

        list(measure_iter(math_is_hard(10), metric=StatsMetric.metric, name="bob"))

        # unnamed metrics are dropped
        list(measure_iter(math_is_hard(10), metric=StatsMetric.metric))

        StatsMetric.dump()
        result = 'Name         Count Mean        Count Stddev        Elapsed Mean        Elapsed Stddev        \nalice          15.00               5.00               15.00                 5.00             \nbob            10.00               0.00               10.00                 0.00             \n'
        self.assertMultiLineEqual(StatsMetric.outfile.getvalue(), result)