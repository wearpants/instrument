Customizing Output
==================

By default, metrics are printed to standard out. You can provide your own
metric recording funtion. It should take three arguments: `count` of items,
`elapsed` time in seconds, and `name`, which can be None:

>>> def my_metric(name, count, elapsed):
...     print("Iterable %s produced %d items in %d milliseconds"%(name, count, int(round(elapsed*1000))))
...
>>> _ = measure_iter(math_is_hard(5), name="bogomips", metric=my_metric)
>>> list(_)
Iterable bogomips produced 5 items in 502 milliseconds
[0, 1, 4, 9, 16]

If you have `statsd <https://pypi.python.org/pypi/statsd>`__ installed, the
:func:`statsd_metric` function can be used to record metrics to it. Or write
your own!

Unless individually specified, metrics are reported using the global
:data:`default_metric`. To change the active default, simply assign another metric
function to this attribute.
