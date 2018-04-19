import time
import tempfile
import shutil
import os
import unittest

from . import math_is_hard

import instrument
from instrument.output.csv import CSVFileMetric, CSVDirMetric


def read_csv(fname):
    with open(fname, newline='') as fh:
        return fh.read()

class CSVFileMetricTestCase(unittest.TestCase):

    def test_csv(self):
        tmp = tempfile.mktemp()
        self.addCleanup(os.unlink, tmp)

        csvfm = CSVFileMetric(tmp, False)

        list(instrument.all(math_is_hard(10), metric=csvfm.metric, name="alice"))
        list(instrument.all(math_is_hard(10), metric=csvfm.metric, name="bob"))

        # unnamed metrics are dropped
        list(instrument.all(math_is_hard(10), metric=csvfm.metric))

        list(instrument.all(math_is_hard(20), metric=csvfm.metric, name="alice"))

        csvfm.dump()

        s = read_csv(tmp)
        self.assertMultiLineEqual(s, 'alice,10,10.000000\r\nbob,10,10.000000\r\nalice,20,20.000000\r\n')

class CSVDirMetricTestCase(unittest.TestCase):

    def test_csv(self):
        tmp = tempfile.mktemp()
        self.addCleanup(shutil.rmtree, tmp)

        CSVDirMetric.dump_atexit = False
        CSVDirMetric.outdir = tmp

        assert not os.path.exists(tmp)

        # directory should exist after first metric
        list(instrument.all(math_is_hard(10), metric=CSVDirMetric.metric, name="alice"))
        assert os.path.exists(tmp)

        list(instrument.all(math_is_hard(20), metric=CSVDirMetric.metric, name="alice"))

        list(instrument.all(math_is_hard(10), metric=CSVDirMetric.metric, name="bob"))

        # unnamed metrics are dropped
        list(instrument.all(math_is_hard(10), metric=CSVDirMetric.metric))

        CSVDirMetric.dump()
        self.assertEqual(sorted(os.listdir(tmp)), ['alice.csv', 'bob.csv'])

        s = read_csv(os.path.join(tmp, 'alice.csv'))
        self.assertMultiLineEqual(s, '10,10.000000\r\n20,20.000000\r\n')

        s = read_csv(os.path.join(tmp, 'bob.csv'))
        self.assertMultiLineEqual(s, '10,10.000000\r\n')
