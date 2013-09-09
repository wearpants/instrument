from __future__ import print_function, division, absolute_import

import time
import tempfile
import shutil
import os

from . import MeasureItTestCase, math_is_hard

from measure_it import measure_iter
from measure_it.csv import CSVFileMetric, CSVDirMetric

class CSVFileMetricTestCase(MeasureItTestCase):

    def test_csv(self):
        tmp = tempfile.mktemp()
        self.addCleanup(os.unlink, tmp)

        csvfm = CSVFileMetric(tmp, False)

        list(measure_iter(math_is_hard(10), metric=csvfm.metric, name="alice"))
        list(measure_iter(math_is_hard(10), metric=csvfm.metric, name="bob"))

        # unnamed metrics are dropped
        list(measure_iter(math_is_hard(10), metric=csvfm.metric))

        csvfm.dump()

        with open(tmp) as fh:
            s = fh.read()

        self.assertMultiLineEqual(s, 'alice,10,10.000000\r\nbob,10,10.000000\r\n')