"""numpy-based metrics"""
import struct
import tempfile
import warnings
import threading
import atexit

import numpy as np

class NumpyMetric(object):
    """Base class for numpy-based metrics

    Do not create instances of this class directly. Simply pass the
    classmethod :func:`metric` to a measurement function. Output using
    :func:`dump`. These are the only public methods. This is an abstract base
    class; you should use one of the concrete subclases in this module
    instead.

    Each metric consumes one open file and 32K of memory while running.
    Output requires enough memory to load all data points for each metric.

    :cvar bool dump_atexit: automatically call :func:`dump` when the interpreter exits. Defaults to True.
    """

    dump_atexit = True
    calc_stats = True #: should mean/stddev be calculated?
    struct = struct.Struct('<Id')
    dtype = np.dtype([('count', np.uint32), ('elapsed', np.float64)])
    lock = threading.Lock()
    instances = None #: replace with dict in each subclass

    mktemp = lambda self: tempfile.TemporaryFile(mode = 'w+b', buffering = 32768)

    def __init__(self, name):
        self.name = name
        self.temp = self.mktemp()

    @classmethod
    def metric(cls, name, count, elapsed):
        """A metric function that buffers through numpy

        :arg str name: name of the metric
        :arg int count: number of items
        :arg float elapsed: time in seconds
        """

        if name is None:
            warnings.warn("Ignoring unnamed metric", stacklevel=3)
            return

        with cls.lock:
            # register with atexit on first call
            if cls.dump_atexit and not cls.instances:
                atexit.register(cls.dump)

            try:
                self = cls.instances[name]
            except KeyError:
                self = cls.instances[name] = cls(name)

            self.temp.write(self.struct.pack(count, elapsed))

    @classmethod
    def dump(cls):
        """Output all recorded metrics"""
        with cls.lock:
            if not cls.instances: return
            atexit.unregister(cls.dump)

            cls._pre_dump()

            for self in cls.instances.values():
                self._dump()

            cls._post_dump()

    def _dump(self):
        """dump data for an individual metric. For internal use only."""

        try:
            self.temp.seek(0) # seek to beginning
            arr = np.fromfile(self.temp, self.dtype)
            self.count_arr = arr['count']
            self.elapsed_arr = arr['elapsed']

            if self.calc_stats:
                # calculate mean & standard deviation
                self.count_mean = np.mean(self.count_arr)
                self.count_std = np.std(self.count_arr)
                self.elapsed_mean = np.mean(self.elapsed_arr)
                self.elapsed_std = np.std(self.elapsed_arr)

            self._output()
        finally:
            self.temp.close()
            self._cleanup()

    @classmethod
    def _pre_dump(cls):
        """subclass hook, called before dumping metrics"""
        pass

    @classmethod
    def _post_dump(cls):
        """subclass hook, called after dumping metrics"""
        pass

    def _output(self):
        """subclass hook, called to output a single metric"""
        pass

    def _cleanup(self):
        """subclass hook, called to clean up after outputting a single metric"""
        pass

