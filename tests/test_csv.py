from __future__ import print_function, division, absolute_import

import time
import tempfile
import shutil
import os
import sys

from . import MeasureItTestCase, math_is_hard

from measure_it import measure_iter
from measure_it.csv import CSVFileMetric, CSVDirMetric


def read_csv(fname):
    # read a CSV file directly, dealing with python2.7 differences
    if sys.version_info.major >= 3:
        with open(fname, newline='') as fh:
            return fh.read()
    else:
        with open(fname) as fh:
            return fh.read()

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

        s = read_csv(tmp)
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
        self.assertEqual(sorted(os.listdir(tmp)), ['alice.csv', 'bob.csv'])

        s = read_csv(os.path.join(tmp, 'alice.csv'))
        self.assertMultiLineEqual(s, '10,10.000000\r\n20,20.000000\r\n')

        s = read_csv(os.path.join(tmp, 'bob.csv'))
        self.assertMultiLineEqual(s, '10,10.000000\r\n')