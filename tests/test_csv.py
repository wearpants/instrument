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

        list(measure_iter(math_is_hard(20), metric=csvfm.metric, name="alice"))

        csvfm.dump()

        with open(tmp) as fh:
            s = fh.read()

        self.assertMultiLineEqual(s, 'alice,10,10.000000\r\nbob,10,10.000000\r\nalice,20,20.000000\r\n')

class CSVDirMetricTestCase(MeasureItTestCase):

    def test_csv(self):
        tmp = tempfile.mktemp()
        self.addCleanup(shutil.rmtree, tmp)

        CSVDirMetric.dump_atexit = False
        CSVDirMetric.outdir = tmp

        assert not os.path.exists(tmp)

        # directory should exist after first metric
        list(measure_iter(math_is_hard(10), metric=CSVDirMetric.metric, name="alice"))
        assert os.path.exists(tmp)

        list(measure_iter(math_is_hard(20), metric=CSVDirMetric.metric, name="alice"))

        list(measure_iter(math_is_hard(10), metric=CSVDirMetric.metric, name="bob"))

        # unnamed metrics are dropped
        list(measure_iter(math_is_hard(10), metric=CSVDirMetric.metric))

        CSVDirMetric.dump()
        self.assertItemsEqual(os.listdir(tmp), ['alice.csv', 'bob.csv'])

        with open(os.path.join(tmp, 'alice.csv')) as fh:
            s = fh.read()
        self.assertMultiLineEqual(s, '10,10.000000\r\n20,20.000000\r\n')

        with open(os.path.join(tmp, 'bob.csv')) as fh:
            s = fh.read()
        self.assertMultiLineEqual(s, '10,10.000000\r\n')