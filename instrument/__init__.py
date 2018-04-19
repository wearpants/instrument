"""you are not expected to understand this implementation.
that's why it has tests.
the above-mentioned 'you' includes the author. :-}
"""

__version__ = '0.6.0'

import time
from functools import wraps
from contextlib import contextmanager
import inspect

from .output import print_metric

# builtins we shadow
_builtin_all = all

default_metric = print_metric #: user-supplied function to use as global default metric

def call_default(name, count, elapsed):
    """call the :func:`default_metric` global in this module

    :arg str name: name of the metric
    :arg int count: number of items
    :arg float elapsed: time in seconds
    """
    return default_metric(name, count, elapsed)

def _do_all(iterable, name, metric):
    total_time = 0
    count = 0
    it = enumerate(iterable, 1) # count, item
    try:
        while True:
            t = time.time()
            try:
                count, x = next(it)
            finally:
                total_time += time.time() - t
            yield x
    finally:
        # underlying iterable is exhausted (StopIteration) or errored. Record
        # the `metric` and allow exception to propogate
        metric(name, count, total_time)

def _do_each(iterable, name, metric):
    it = iter(iterable)
    while True:
        t = time.time()
        try:
            x = next(it)
        except StopIteration:
            # don't record a metric for final next() call
            raise
        except Exception:
            # record a metric for other exceptions, than raise
            metric(name, 1, time.time() - t)
            raise
        else:
            # normal path, record metric and yield
            metric(name, 1, time.time() - t)
            yield x

def _do_first(iterable, name, metric):
    it = iter(iterable)
    t = time.time()
    try:
        x = next(it)
    except StopIteration:
        # don't record a metric for final next() call
        raise
    except Exception:
        # record a metric for other exceptions, than raise
        metric(name, 1, time.time() - t)
        raise
    else:
        # normal path, record metric and yield
        metric(name, 1, time.time() - t)
        yield x

    yield from it

def _make_decorator(measuring_func):
    """morass of closures for making decorators/descriptors"""
    def _decorator(name = None, metric = call_default):
        def wrapper(func):

            name_ = name if name is not None else func.__module__ + '.' +func.__name__
            class instrument_decorator(object): # must be a class for descriptor magic to work
                @wraps(func)
                def __call__(self, *args, **kwargs):
                    return measuring_func(func(*args, **kwargs), name_, metric)

                def __get__(self, instance, class_):
                    name_ = name if name is not None else\
                        ".".join((class_.__module__, class_.__name__, func.__name__))
                    @wraps(func)
                    def wrapped_method(*args, **kwargs):
                        return measuring_func(func(instance, *args, **kwargs), name_, metric)
                    return wrapped_method
            return instrument_decorator()

        return wrapper
    return _decorator

# decorator variants
_iter_decorator = _make_decorator(_do_all)
_each_decorator = _make_decorator(_do_each)
_first_decorator = _make_decorator(_do_first)

def all(iterable = None, *, name = None, metric = call_default):
    """Measure total time and item count for consuming an iterable

    :arg iterable: any iterable
    :arg function metric: f(name, count, total_time)
    :arg str name: name for the metric
    """
    if iterable is None:
        return _iter_decorator(name, metric)
    else:
        return _do_all(iterable, name, metric)


def each(iterable = None, *, name = None, metric = call_default):
    """Measure time elapsed to produce each item of an iterable

    :arg iterable: any iterable
    :arg function metric: f(name, 1, time)
    :arg str name: name for the metric
    """
    if iterable is None:
        return _each_decorator(name, metric)
    else:
        return _do_each(iterable, name, metric)


def first(iterable = None, *, name = None, metric = call_default):
    """Measure time elapsed to produce first item of an iterable

    :arg iterable: any iterable
    :arg function metric: f(name, 1, time)
    :arg str name: name for the metric
    """
    if iterable is None:
        return _first_decorator(name, metric)
    else:
        return _do_first(iterable, name, metric)


def _iterable_to_varargs_func(func):
    """decorator to convert a func taking a iterable to a *args one"""
    def wrapped(*args, **kwargs):
        return func(args, **kwargs)
    return wrapped

def _varargs_to_iterable_func(func):
    """decorator to convert a *args func to one taking a iterable"""
    def wrapped(iterable, **kwargs):
        return func(*iterable, **kwargs)
    return wrapped

def _iterable_to_varargs_method(func):
    """decorator to convert a method taking a iterable to a *args one"""
    def wrapped(self, *args, **kwargs):
        return func(self, args, **kwargs)
    return wrapped

def _varargs_to_iterable_method(func):
    """decorator to convert a *args method to one taking a iterable"""
    def wrapped(self, iterable, **kwargs):
        return func(self, *iterable, **kwargs)
    return wrapped

class counted_iterable(object):
    """helper class that wraps an iterable and counts items"""
    __slots__ = ['iterable', 'count']

    def __init__(self, iterable):
        self.iterable = iter(iterable)
        self.count = 0

    def __iter__(self):
        return self

    def __next__(self):
        ret = next(self.iterable)
        self.count += 1
        return ret

def reducer(*, name = None, metric = call_default):
    """Decorator to measure a function that consumes many items.

    The wrapped ``func`` should take either a single ``iterable`` argument or
    ``*args`` (plus keyword arguments).

    :arg function metric: f(name, count, total_time)
    :arg str name: name for the metric
    """
    class instrument_reducer_decorator(object):
        def __init__(self, func):
            self.orig_func = func
            self.wrapping = wraps(func)
            self.metric_name = name if name is not None else func.__module__ + '.' +func.__name__
            self.varargs = inspect.getargspec(func).varargs is not None
            if self.varargs:
                self.method = _varargs_to_iterable_method(func)
                self.func = _varargs_to_iterable_func(func)
                self.callme = _iterable_to_varargs_func(self._call)
            else:
                self.method = func
                self.func = func
                self.callme = self._call

        # we need _call/callme b/c CPython short-circurits CALL_FUNCTION to
        # directly access __call__, bypassing our varargs decorator
        def __call__(self, *args, **kwargs):
            return self.callme(*args, **kwargs)

        def _call(self, iterable, **kwargs):
            it = counted_iterable(iterable)
            t = time.time()
            try:
                return self.func(it, **kwargs)
            finally:
                metric(self.metric_name, it.count, time.time() - t)

        def __get__(self, instance, class_):
            metric_name = name if name is not None else\
                ".".join((class_.__module__, class_.__name__, self.orig_func.__name__))

            def wrapped_method(iterable, **kwargs):
                it = counted_iterable(iterable)
                t = time.time()
                try:
                    return self.method(instance, it, **kwargs)
                finally:
                    metric(metric_name, it.count, time.time() - t)

            # wrap in func version b/c self is handled for us by descriptor (ie, `instance`)
            if self.varargs: wrapped_method = _iterable_to_varargs_func(wrapped_method)
            wrapped_method = self.wrapping(wrapped_method)
            return wrapped_method

    return instrument_reducer_decorator

def producer(*, name = None, metric = call_default):
    """Decorator to measure a function that produces many items.

    The function should return an object that supports ``__len__`` (ie, a
    list). If the function returns an iterator, use :func:`iter` instead.

    :arg function metric: f(name, count, total_time)
    :arg str name: name for the metric
    """

    def wrapper(func):
        def instrumenter(name_, *args, **kwargs):
            t = time.time()
            try:
                ret = func(*args, **kwargs)
            except Exception:
                # record a metric for other exceptions, than raise
                metric(name_, 0, time.time() - t)
                raise
            else:
                # normal path, record metric & return
                metric(name_, len(ret), time.time() - t)
                return ret

        name_ = name if name is not None else func.__module__ + '.' +func.__name__
        class instrument_decorator(object): # must be a class for descriptor magic to work
            @wraps(func)
            def __call__(self, *args, **kwargs):
                return instrumenter(name_, *args, **kwargs)

            def __get__(self, instance, class_):
                name_ = name if name is not None else\
                    ".".join((class_.__module__, class_.__name__, func.__name__))
                @wraps(func)
                def wrapped_method(*args, **kwargs):
                    return instrumenter(name_, instance, *args, **kwargs)
                return wrapped_method

        return instrument_decorator()
    return wrapper

def function(*, name = None, metric = call_default):
    """Decorator to measure function execution time.

    :arg function metric: f(name, 1, total_time)
    :arg str name: name for the metric
    """
    def wrapper(func):
        def instrumenter(name_, *args, **kwargs):
            t = time.time()
            try:
                return func(*args, **kwargs)
            finally:
                metric(name_, 1, time.time() - t)

        name_ = name if name is not None else func.__module__ + '.' +func.__name__
        class instrument_decorator(object): # must be a class for descriptor magic to work
            @wraps(func)
            def __call__(self, *args, **kwargs):
                return instrumenter(name_, *args, **kwargs)

            def __get__(self, instance, class_):
                name_ = name if name is not None else\
                    ".".join((class_.__module__, class_.__name__, func.__name__))
                @wraps(func)
                def wrapped_method(*args, **kwargs):
                    return instrumenter(name_, instance, *args, **kwargs)
                return wrapped_method

        return instrument_decorator()
    return wrapper

@contextmanager
def block(*, name = None, metric = call_default, count = 1):
    """Context manager to measure execution time of a block

    :arg function metric: f(name, 1, time)
    :arg str name: name for the metric
    :arg int count: user-supplied number of items, defaults to 1
    """
    t = time.time()
    try:
        yield
    finally:
        metric(name, count, time.time() - t)
