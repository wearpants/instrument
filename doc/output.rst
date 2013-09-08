Data Output
===========

By default, metrics are printed to standard out. You can provide your own
metric recording funtion. It should take three arguments: `count` of items,
`elapsed` time in seconds, and `name`, which can be None:

>>> def my_metric(name, count, elapsed):
...     print("Iterable %s produced %d items in %d milliseconds"%(name, count, int(round(elapsed*1000))))
...
>>> _ = measure_iter(math_is_hard(5), metric=my_metric, name="bogomips")
>>> list(_)
Iterable bogomips produced 5 items in 502 milliseconds
[0, 1, 4, 9, 16]

Unless individually specified, metrics are reported using the global
:func:`.default_metric`. To change the active default, simply assign another
metric function to this attribute. In general, you should configure your
metric functions at program startup, **before** recording any metrics.
:func:`.make_multi_metric` creates a single metric function that records to
several outputs.


csv
---

:mod:`.csv` saves raw metrics as comma separated text files.
This is useful for conducting external analysis. :mod:`.csv` is threadsafe; use
under multiprocessing requires some care.

:class:`.CSVFileMetric` saves all metrics to a single file with three
columns: metric name, item count & elapsed time. Create an instance of this
class and pass its :meth:`.CSVFileMetric.metric` method to measurement
functions. The `outfile` parameter controls where to write data; an existing
file will be overwritten.

>>> from measure_it.csv import CSVFileMetric
>>> csvfm = CSVFileMetric("/tmp/my_metrics_file.csv")
>>> _ = measure_iter(math_is_hard(5), metric=csvfm.metric, name="bogomips")
>>> list(_)
[0, 1, 4, 9, 16]

:class:`.CSVDirMetric` saves metrics to multiple files, named after each
metric, with two columns: item count & elapsedtime. This class is global to
your program; do not manually create instances. Instead, use the classmethod
:meth:`.CSVDirMetric.metric`. Set the class variable `outdir` to a directory
in which to store files. The contents of this directory will be deleted on
startup.

>>> from measure_it.csv import CSVDirMetric
>>> CSVDirMetric.outdir = "/tmp/my_metrics_dir"
>>> _ = measure_iter(math_is_hard(5), metric=CSVDirMetric.metric, name="bogomips")
>>> list(_)
[0, 1, 4, 9, 16]

Both classes support at `dump_atexit` flag, which will register a handler to
write data when the interpreter finishes execution. Set to false to manage
yourself.

statsd
------

For monitoring production systems, the :func:`.statsd_metric` function can be
used to record metrics to `statsd <https://pypi.python.org/pypi/statsd>`__.
Each metric will generate two buckets: a count and a timing.
