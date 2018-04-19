Basic Usage
===========
.. currentmodule:: instrument

Measurements
------------

Iterators & generators often encapsulate I/O, number crunching or other
operations we want to gather metrics for:

>>> from time import sleep
>>> def math_is_hard(N):
...     x = 0
...     while x < N:
...         sleep(.1)
...         yield x * x
...         x += 1

Timing iterators is tricky. :func:`instrument.iter`, :func:`instrument.each` and
:func:`instrument.first` record metrics for time and element count for
iteratables.

>>> import instrument

Wrap an iterator in :func:`instrument.iter` to time how long it takes to consume
entirely:

>>> underlying = math_is_hard(5)
>>> underlying # doctest: +ELLIPSIS
<generator object math_is_hard at ...>
>>> _ = instrument.iter(underlying)
>>> squares = list(_)
5 elements in 0.50 seconds

The wrapped iterator yields the same results as the underlying iterable:

>>> squares
[0, 1, 4, 9, 16]

The :func:`instrument.each` wrapper measures the time taken to produce each
item:

>>> _ = instrument.each(math_is_hard(5))
>>> list(_)
1 elements in 0.10 seconds
1 elements in 0.10 seconds
1 elements in 0.10 seconds
1 elements in 0.10 seconds
1 elements in 0.10 seconds
[0, 1, 4, 9, 16]

The :func:`instrument.first` wrapper measures the time taken to produce the
first item:

>>> _ = instrument.first(math_is_hard(5))
>>> list(_)
1 elements in 0.10 seconds
[0, 1, 4, 9, 16]

You can provide a custom name for the metric:

>>> _ = instrument.iter(math_is_hard(5), name="bogomips")
>>> list(_)
bogomips: 5 elements in 0.50 seconds
[0, 1, 4, 9, 16]

Decorators
----------

If you have a generator function (one that uses ``yield``), you can wrap it
with a decorator using ``.func()``. You can pass the same ``name`` and ``metric``
arugments:

>>> @instrument.each.func()
... def slow(N):
...     for i in range(N):
...         sleep(.1)
...         yield i
>>> list(slow(3))
__main__.slow: 1 elements in 0.10 seconds
__main__.slow: 1 elements in 0.10 seconds
__main__.slow: 1 elements in 0.10 seconds
[0, 1, 2]

Decorators work inside classes too. If you don't provide a name, a decent one
will be inferred:

>>> class Database(object):
...     @instrument.iter.func()
...     def batch_get(self, ids):
...         # you'd actually hit database here
...         for i in ids:
...             sleep(.1)
...             yield {"id":i, "square": i*i}
>>> database = Database()
>>> _ = database.batch_get([1, 2, 3, 9000])
>>> list(_)
__main__.Database.batch_get: 4 elements in 0.40 seconds
[{'id': 1, 'square': 1}, {'id': 2, 'square': 4}, {'id': 3, 'square': 9}, {'id': 9000, 'square': 81000000}]

Reducers & Producers
--------------------

:func:`instrument.reducer` and :func:`instrument.producer` are decorators for
functions, *not* iterators.

The :func:`instrument.reducer` decorator measures functions that consume many
items. Examples include aggregators or a ``batch_save()``:

>>> @instrument.reducer()
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

This works with ``*args`` functions too:

>>> @instrument.reducer()
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

The :func:`instrument.producer` decorator measures a function that produces many
items. This is similar to ``instrument.iter.func()``, but for functions that
return lists instead of iterators (or other object supporting ``len()``):

>>> @instrument.producer()
... def list_squares(N):
...     sleep(0.1 * N)
...     return [i * i for i in range(N)]
>>> list_squares(5)
__main__.list_squares: 5 elements in 0.50 seconds
[0, 1, 4, 9, 16]

:func:`instrument.reducer` and :func:`instrument.producer` can be used inside
classes:

>>> class Database(object):
...     @instrument.reducer()
...     def batch_save(self, rows):
...         for r in rows:
...             # you'd actually commit to your database here
...             sleep(0.1)
...
...     @instrument.reducer()
...     def batch_save2(self, *rows):
...         for r in rows:
...             # you'd actually commit to your database here
...             sleep(0.1)
...
...     @instrument.producer()
...     def dumb_query(self, x):
...         # you'd actually talk to your database here
...         sleep(0.1 * x)
...         return [{"id":i, "square": i*i} for i in range(x)]
...
>>> rows = [{'id':i} for i in range(5)]
>>> database = Database()
>>> database.batch_save(rows)
__main__.Database.batch_save: 5 elements in 0.50 seconds
>>> database.batch_save2(*rows)
__main__.Database.batch_save2: 5 elements in 0.50 seconds
>>> database.dumb_query(3)
__main__.Database.dumb_query: 3 elements in 0.30 seconds
[{'id': 0, 'square': 0}, {'id': 1, 'square': 1}, {'id': 2, 'square': 4}]

Functions
---------

The :func:`instrument.function` decorator simply measures total function execution
time:

>>> @instrument.function()
... def slow():
...     # you'd do something useful here
...     sleep(.1)
...     return "SLOW"
>>> slow()
__main__.slow: 1 elements in 0.10 seconds
'SLOW'

This works in classes too:

>>> class CrunchCrunch(object):
...     @instrument.function()
...     def slow(self):
...         # you'd do something useful here
...         sleep(.1)
...         return "SLOW"
>>> CrunchCrunch().slow()
__main__.CrunchCrunch.slow: 1 elements in 0.10 seconds
'SLOW'

Blocks
------

To measure the excecution time of a block of code, use a
:func:`instrument.block` context manager:

>>> with instrument.block(name="slowcode"):
...     # you'd do something useful here
...     sleep(0.2)
slowcode: 1 elements in 0.20 seconds

You can also pass your own value for `count`; this is useful to measure a
resource used by a block (the number of bytes in a file, for example):

>>> with instrument.block(name="slowcode", count=42):
...     # you'd do something useful here
...     sleep(0.2)
slowcode: 42 elements in 0.20 seconds
