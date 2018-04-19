import tempfile
import shutil
import os
import unittest

from . import math_is_hard

import instrument
from instrument.output.plot import PlotMetric

class PlotMetricTestCase(unittest.TestCase):

    def test_plot(self):
        tmp = tempfile.mktemp()
        self.addCleanup(shutil.rmtree, tmp)

        PlotMetric.dump_atexit = False
        PlotMetric.outdir = tmp

        assert not os.path.exists(tmp)

        list(instrument.all(math_is_hard(10), metric=PlotMetric.metric, name="alice"))
        list(instrument.all(math_is_hard(20), metric=PlotMetric.metric, name="alice"))
        list(instrument.all(math_is_hard(10), metric=PlotMetric.metric, name="bob"))

        # unnamed metrics are dropped
        list(instrument.all(math_is_hard(10), metric=PlotMetric.metric))

        PlotMetric.dump()

        # just test that files were created
        self.assertEqual(sorted(os.listdir(tmp)), ['alice.png', 'bob.png'])
