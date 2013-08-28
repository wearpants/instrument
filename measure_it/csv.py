from __future__ import print_function, division, absolute_import

import warnings
import os.path
import shutil
import threading
import atexit
import sys
import csv

class CSVMetric(object):
    """Write metrics to individual CSV files

    Do not create instances of this class directly. Simply pass the
    classmethod :func:`metric` to a measurement function. Output using
    :func:`dump`. These are the only public methods.

    Each metric consumes one open file and 32K of memory while running.

    :cvar dump_atexit: automatically call :func:`dump` when the interpreter exits. Defaults to True.
    :cvar outdir: directory to save plots in. Defaults to `./mit_csv`.
    """
    outdir = os.path.abspath("mit_csv")
    dump_atexit = True

    lock = threading.Lock()
    instances = {}

    def __init__(self, name):
        self.name = name
        self.outfile = open(os.path.join(self.outdir, ".".join((self.name, 'csv'))),
                            'w', buffering=32768)
        self.writer = csv.writer(self.outfile)

    @classmethod
    def metric(cls, name, count, elapsed):
        """A metric function that writes individual CSV files

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
                os.mkdir(cls.outdir)

                if cls.dump_atexit: atexit.register(cls.dump)

            try:
                self = cls.instances[name]
            except KeyError:
                self = cls.instances[name] = cls(name)

            self.writer.writerow((count, "%f"%elapsed))

    @classmethod
    def dump(cls):
        """Output all recorded stats"""
        with cls.lock:
            if not cls.instances: return
            if cls.dump_atexit and sys.version_info.major >= 3:
                # python2.7 has no unregister function
                atexit.unregister(cls.dump)

            for self in cls.instances.values():
                self.outfile.close()