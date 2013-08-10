measure_it
==========

`measure_it <http://github.com/wearpants/measure_it>`__ provides timing and counting for iterators.

.. currentmodule:: measure_it

Basic Usage
===========

Iterators & generators often encapsulate I/O, number crunching or other
operations we want to gather metrics for:

>>> from time import sleep
>>> def math_is_hard(N):
...     x = 0
...     while x < N:
...         sleep(.1)
...         yield x * x
...         x += 1

Timing iterators is tricky. :func:`measure` and :func:`measure_each` record
metrics for time and element count for iteratables.

>>> from measure_it import measure, measure_each

Wrap an iterator in :func:`measure` to time how long it takes to consume entirely:

>>> underlying = math_is_hard(5)
>>> underlying # doctest: +ELLIPSIS
<generator object math_is_hard at ...>
>>> _ = measure(underlying)
>>> squares = list(_)
5 elements in 0.50 seconds

The wrapped iterator yields the same results as the underlying iterable:

>>> squares
[0, 1, 4, 9, 16]

The :func:`measure_each` wrapper measures the time taken to produce each item:

>>> _ = measure_each(math_is_hard(5))
>>> list(_)
1 elements in 0.10 seconds
1 elements in 0.10 seconds
1 elements in 0.10 seconds
1 elements in 0.10 seconds
1 elements in 0.10 seconds
[0, 1, 4, 9, 16]

You can provide a custom name for the metric:

>>> _ = measure(math_is_hard(5), name="bogomips")
>>> list(_)
bogomips: 5 elements in 0.50 seconds
[0, 1, 4, 9, 16]

Decorators
==========

If you have a generator function (one that uses `yield`), you can wrap it with a decorator using `.func()`. You can pass the same `name` and `metric` arugments:

>>> @measure_each.func()
... def slow(N):
...     for i in range(N):
...         sleep(.1)
...         yield i
>>> list(slow(3))
__main__.slow: 1 elements in 0.10 seconds
__main__.slow: 1 elements in 0.10 seconds
__main__.slow: 1 elements in 0.10 seconds
[0, 1, 2]

Decorators work inside classes too. If you don't provide a name, a decent one will be inferred:

>>> class Database(object):
...     @measure.func()
...     def batch_get(self, ids):
...         # you'd actually hit database here
...         for i in ids:
...             sleep(.1)
...             yield {"id":i, "square": i*i}
>>> database = Database()
>>> _ = database.batch_get([1, 2, 3, 9000])
>>> list(_)
__main__.Database.batch_get: 4 elements in 0.40 seconds
[{'square': 1, 'id': 1}, {'square': 4, 'id': 2}, {'square': 9, 'id': 3}, {'square': 81000000, 'id': 9000}]

Reducers
========

The `measure_reduce` decorator measures functions that consume many items.
Examples include aggregators or a `batch_save()`:

>>> from measure_it import measure_reduce 

`measure_reduce` is a decorator for functions, *not* iterators:

>>> @measure_reduce()
... def sum_squares(L):
...     total = 0
...     for i in L:
...         sleep(.1)
...         total += i*i
...     return total
... 
>>> sum_squares(range(5))
__main__.sum_squares: 5 elements in 0.50 seconds
30

This works with `*args` functions too:

>>> @measure_reduce()
... def sum_squares2(*args):
...     total = 0
...     for i in args:
...         sleep(.1)
...         total += i*i
...     return total
... 
>>> sum_squares2(*range(5))
__main__.sum_squares2: 5 elements in 0.50 seconds
30

And inside classes:

>>> class Database(object):
...     @measure_reduce()
...     def batch_save(self, rows):
...         for r in rows:
...             # you'd actually commit to your database here
...             sleep(0.1)
... 
...     @measure_reduce()
...     def batch_save2(self, *rows):
...         for r in rows:
...             # you'd actually commit to your database here
...             sleep(0.1)
... 
>>> rows = [{'id':i} for i in range(5)]
>>> database = Database()
>>> database.batch_save(rows)
__main__.Database.batch_save: 5 elements in 0.50 seconds
>>> database.batch_save2(*rows)
__main__.Database.batch_save2: 5 elements in 0.50 seconds

Customizing Output
==================

By default, metrics are printed to standard out. You can provide your own
metric recording funtion. It should take three arguments: `count` of items,
`elapsed` time in seconds, and `name`, which can be None:

>>> def my_metric(name, count, elapsed):
...     print("Iterable %s produced %d items in %d milliseconds"%(name, count, int(round(elapsed*1000))))
... 
>>> _ = measure(math_is_hard(5), name="bogomips", metric=my_metric)
>>> list(_)
Iterable bogomips produced 5 items in 502 milliseconds
[0, 1, 4, 9, 16]

If you have `statsd <https://pypi.python.org/pypi/statsd>`__ installed, the
:func:`statsd_metric` function can be used to record metrics to it. Or write
your own!

API Documentation
=================

.. automodule:: measure_it
    :members: measure, measure_each, measure_reduce, print_metric

Changelog
=========

0.2
---
add `measure_reduce`

0.1
---
Initial release
