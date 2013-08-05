>>> from measure_it import measure, measure_each
>>> from time import sleep
>>> def math_is_hard(N):
...     x = 0
...     while x < N:
...         sleep(.1)
...         yield x * x
...         x += 1
... 
>>> it = measure(math_is_hard(5))
>>> squares = list(it)
5 elements in 0.501616 seconds
>>> squares
[0, 1, 4, 9, 16]
>>> list(measure_each(math_is_hard(5)))
1 elements in 0.100337 seconds
1 elements in 0.100347 seconds
1 elements in 0.100363 seconds
1 elements in 0.100297 seconds
1 elements in 0.100320 seconds
[0, 1, 4, 9, 16]
>>> list(measure(math_is_hard(5), name="bogomips"))
bogomips: 5 elements in 0.502684 seconds
[0, 1, 4, 9, 16]
>>> def my_metric(name, count, elapsed):
...     print("Iterable %s produced %d items over %d milliseconds"%(name, count, int(round(elapsed*1000))))
... 
>>> list(measure(math_is_hard(5), name="bogomips", metric=my_metric))
Iterable bogomips produced 5 items over 502 milliseconds
[0, 1, 4, 9, 16]
>>> @measure_each.func()
... def slow(N):
...     for i in range(N):
...         sleep(.1)
...         yield i
... 
>>> list(slow(3))
__main__.slow: 1 elements in 0.100304 seconds
__main__.slow: 1 elements in 0.100300 seconds
__main__.slow: 1 elements in 0.102409 seconds
[0, 1, 2]
>>> class Database(object):
...     @measure.func()
...     def batch_get(self, ids):
...         # you'd actually hit database here
...         for i in ids:
...             sleep(.1)
...             yield {"id":i, "square": i*i}
... 
>>> database = Database()
>>> list(database.batch_get([1, 2, 3, 9000]))
__main__.Database.batch_get: 4 elements in 0.401198 seconds
[{'square': 1, 'id': 1}, {'square': 4, 'id': 2}, {'square': 9, 'id': 3}, {'square': 81000000, 'id': 9000}]
>>> 
(measure_it)~/Projects/measure_it$ 
