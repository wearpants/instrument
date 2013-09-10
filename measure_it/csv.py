from __future__ import print_function, division, absolute_import

import warnings
import os.path
import shutil
import threading
import atexit
import sys
import csv

__all__ = ['CSVDirMetric', 'CSVFileMetric']

# python2.7: open a file for writing as csv, from http://stackoverflow.com/a/11235483
if sys.version_info.major >= 3:
    open_fh = lambda fname: open(fname, 'w', newline='', buffering=32768)
else:
    open_fh = lambda fname: open(fname, 'wb', buffering=32768)

class CSVDirMetric(object):
    """Write metrics to multiple CSV files

    Do not create instances of this class directly. Simply pass the
    classmethod :func:`metric` to a measurement function. Output using
    :func:`dump`. These are the only public methods.

    Each metric consumes one open file and 32K of memory while running.

    :cvar dump_atexit: automatically call :func:`dump` when the interpreter exits. Defaults to True.
    :cvar outdir: directory to save CSV files in. Defaults to ``./mit_csv``.
    """
    outdir = os.path.abspath("mit_csv")
    dump_atexit = True

    lock = threading.Lock()
    instances = {}

    def __init__(self, name):
        self.name = name
        self.fh = open_fh(os.path.join(self.outdir, ".".join((self.name, 'csv'))))
        self.writer = csv.writer(self.fh)

    @classmethod
    def metric(cls, name, count, elapsed):
        """A metric function that writes multiple CSV files

        :arg str name: name of the metric
        :arg int count: number of elements
        :arg float elapsed: time in seconds
        """

        if name is None:
            warnings.warn("Ignoring unnamed metric", stacklevel=3)
            return

        with cls.lock:
            if not cls.instances:
                # first call
                shutil.rmtree(cls.outdir, ignore_errors=True)
                os.makedirs(cls.outdir)

                if cls.dump_atexit: atexit.register(cls.dump)

            try:
                self = cls.instances[name]
            except KeyError:
                self = cls.instances[name] = cls(name)

            self.writer.writerow((count, "%f"%elapsed))

    @classmethod
    def dump(cls):
        """Output all recorded metrics"""
        with cls.lock:
            if not cls.instances: return
            if cls.dump_atexit and sys.version_info.major >= 3:
                # python2.7 has no unregister function
                atexit.unregister(cls.dump)

            for self in cls.instances.values():
                self.fh.close()

class CSVFileMetric(object):
    """Write metrics to a single CSV file

    Pass the method :func:`metric` to a measurement function. Output using
    :func:`dump`. These are the only public methods.

    :ivar outfile: file to save to. Defaults to ``./mit.csv``.
    :ivar dump_atexit: automatically call :func:`dump` when the interpreter exits. Defaults to True.
    """

    def __init__(self, outfile="mit.csv", dump_atexit = True):
        self.outfile = os.path.abspath(outfile)
        if os.path.exists(self.outfile):
            os.remove(self.outfile)

        dirname = os.path.dirname(outfile)
        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname)

        self.dump_atexit = dump_atexit
        if dump_atexit:
            atexit.register(self.dump)

        self.lock = threading.Lock()
        self.fh = open_fh(self.outfile)
        self.writer = csv.writer(self.fh)

    def metric(self, name, count, elapsed):
        """A metric function that writes a single CSV file

        :arg str name: name of the metric
        :arg int count: number of elements
        :arg float elapsed: time in seconds
        """

        if name is None:
            warnings.warn("Ignoring unnamed metric", stacklevel=3)
            return

        with self.lock:
            self.writer.writerow((name, count, "%f"%elapsed))

    def dump(self):
        """Output all recorded metrics"""
        with self.lock:
            if self.dump_atexit and sys.version_info.major >= 3:
                # python2.7 has no unregister function
                atexit.unregister(self.dump)
            self.fh.close()