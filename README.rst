Timing and measurement tools for iterators

`measure_it<http://github.com/wearpants/measure_it>`_ is awesome. It does
cool things with iterators. Includes optional statsd support.

>>> from measure_it import measure, measure_each
>>> from time import sleep
>>> def math_is_hard(N):
...     x = 0
...     while x < N:
...         sleep(.1)
...         yield x * x
...         x += 1
... 

Wrap an iterator in `measure` to time how long it takes to consume entirely &
how many items it produces:

>>> it = measure(math_is_hard(5))
>>> squares = list(it)
5 elements in 0.50 seconds

The wrapped iterator yields the same results as the underlying iterable:

>>> squares
[0, 1, 4, 9, 16]

The `measure_each` wrapper measures the time taken to produce each item:

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

By default, metrics are printed to standard out. You can provide your own
metric funtion. It should take three arguments: `count` of items, `elapsed`
time in seconds, and `name`, which can be None:

>>> def my_metric(name, count, elapsed):
...     print("Iterable %s produced %d items over %d milliseconds"%(name, count, int(round(elapsed*1000))))
... 
>>> _ = measure(math_is_hard(5), name="bogomips", metric=my_metric)
>>> list(_)
Iterable bogomips produced 5 items over 502 milliseconds
[0, 1, 4, 9, 16]

If you have a generator function (one that uses `yield`), you can wrap it with a decorator:

>>> @measure_each.func()
... def slow(N):
...     for i in range(N):
...         sleep(.1)
...         yield i
... 
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
... 
>>> database = Database()
>>> _ = database.batch_get([1, 2, 3, 9000])
>>> list(_)
__main__.Database.batch_get: 4 elements in 0.40 seconds
[{'square': 1, 'id': 1}, {'square': 4, 'id': 2}, {'square': 9, 'id': 3}, {'square': 81000000, 'id': 9000}]
