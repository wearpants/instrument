"""you are not expected to understand this implementation.
that's why it has tests.
the above-mentioned 'you' includes the author. :-}
"""

from __future__ import print_function, division

__version__ = '0.4.1'

import time
from functools import wraps
from contextlib import contextmanager
import inspect

import wsgiref.headers
import cgi

__all__ = ['measure_iter', 'measure_each', 'measure_first', 'measure_reduce',
           'measure_produce', 'measure_func', 'measure_block', 'MeasureWSGIMiddleware']

def print_metric(name, count, elapsed):
    """A metric function that prints

    :arg str name: name of the metric
    :arg int count: number of elements
    :arg float elapsed: time in seconds
    """
    if name is not None:
        print("%s: %d elements in %.2f seconds"%(name, count, elapsed))
    else:
        print("%d elements in %.2f seconds"%(count, elapsed))


default_metric = print_metric #: user-supplied function to use as global default metric

def call_default(name, count, elapsed):
    """call the :func:`default_metric` global in this module

    :arg str name: name of the metric
    :arg int count: number of elements
    :arg float elapsed: time in seconds
    """
    return default_metric(name, count, elapsed)


def make_multi_metric(*metrics):
    """Make a new metric function that calls the supplied metrics

    :arg functions metrics: metric functions
    :rtype: function
    """
    def multi_metric(name, count, elapsed):
        """Calls multiple metrics (closure)"""
        for m in metrics:
            m(name, count, elapsed)
    return multi_metric

def measure_iter(iterable, name = None, metric = call_default):
    """Measure total time and element count for consuming an iterable

    :arg iterable: any iterable
    :arg function metric: f(name, count, total_time)
    :arg str name: name for the metric
    """
    total_time = 0
    count = 0
    it = enumerate(iterable, 1) # count, element
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
def measure_each(iterable, name = None, metric = call_default):
    """Measure time elapsed to produce each item of an iterable

    :arg iterable: any iterable
    :arg function metric: f(name, 1, time)
    :arg str name: name for the metric
    """
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

def measure_first(iterable, name = None, metric = call_default):
    """Measure time elapsed to produce first item of an iterable

    :arg iterable: any iterable
    :arg function metric: f(name, 1, time)
    :arg str name: name for the metric
    """
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

    for x in it: yield x

def _make_decorator(measuring_func):
    """morass of closures for making decorators/descriptors"""
    def _decorator(name = None, metric = call_default):
        def wrapper(func):

            name_ = name if name is not None else func.__module__ + '.' +func.__name__
            class measure_it_decorator(object): # must be a class for descriptor magic to work
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
            return measure_it_decorator()

        return wrapper
    return _decorator

measure_iter.func = _make_decorator(measure_iter)
measure_each.func = _make_decorator(measure_each)
measure_first.func = _make_decorator(measure_first)
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

    next = __next__ # python2 compatibility

def measure_reduce(name = None, metric = call_default):
    """Decorator to measure a function that consumes many items.

    The wrapped ``func`` should take either a single ``iterable`` argument or
    ``*args`` (plus keyword arguments).

    :arg function metric: f(name, count, total_time)
    :arg str name: name for the metric
    """
    class measure_reduce_decorator(object):
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

    return measure_reduce_decorator

def measure_produce(name = None, metric = call_default):
    """Decorator to measure a function that produces many items.

    The function should return an object that supports ``__len__`` (ie, a
    list). If the function returns an iterator, use ``measure_iter.func()`` instead.

    :arg function metric: f(name, count, total_time)
    :arg str name: name for the metric
    """

    def wrapper(func):
        def measurer(name_, *args, **kwargs):
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
        class measure_it_decorator(object): # must be a class for descriptor magic to work
            @wraps(func)
            def __call__(self, *args, **kwargs):
                return measurer(name_, *args, **kwargs)

            def __get__(self, instance, class_):
                name_ = name if name is not None else\
                    ".".join((class_.__module__, class_.__name__, func.__name__))
                @wraps(func)
                def wrapped_method(*args, **kwargs):
                    return measurer(name_, instance, *args, **kwargs)
                return wrapped_method

        return measure_it_decorator()
    return wrapper

def measure_func(name = None, metric = call_default):
    """Decorator to measure function execution time.

    :arg function metric: f(name, 1, total_time)
    :arg str name: name for the metric
    """
    def wrapper(func):
        def measurer(name_, *args, **kwargs):
            t = time.time()
            try:
                return func(*args, **kwargs)
            finally:
                metric(name_, 1, time.time() - t)

        name_ = name if name is not None else func.__module__ + '.' +func.__name__
        class measure_it_decorator(object): # must be a class for descriptor magic to work
            @wraps(func)
            def __call__(self, *args, **kwargs):
                return measurer(name_, *args, **kwargs)

            def __get__(self, instance, class_):
                name_ = name if name is not None else\
                    ".".join((class_.__module__, class_.__name__, func.__name__))
                @wraps(func)
                def wrapped_method(*args, **kwargs):
                    return measurer(name_, instance, *args, **kwargs)
                return wrapped_method

        return measure_it_decorator()
    return wrapper

@contextmanager
def measure_block(name = None, metric = call_default, count = 1):
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

# based on http://lucumr.pocoo.org/2007/5/21/getting-started-with-wsgi/
# and http://blog.dscpl.com.au/2012/10/obligations-for-calling-close-on.html
# and also http://blog.dscpl.com.au/2012/10/wsgi-middleware-and-hidden-write.html
# and a deeper reading of PEP-3333 than is healthy.

class MeasureWSGIMiddleware(object):
    """Middleware that measures WSGI
        
    The following metrics record response body size in bytes & total processing time:
    
    * `wsgi.request.method.*`: request HTTP method, lower case
    * `wsgi.request.scheme.*`: request scheme, usually `http` or `https`
    * `wsgi.request.host.*`: host name with `.` replaced by `_`
    * `wsgi.request.port.*`: port number, or `false` if no port supplied
    * `wsgi.request.query.{true, false}`: did the request have a query string
    * `wsgi.request.cookie.{true, false}`: did the request have a cookie set
    * `wsgi.response.status.*`: numeric response code
    * `wsgi.response.content_type.*`: response content type, with `/` replaced by `_`

    The following metrics record request body size in bytes & time to read it:
    
    * `wsgi.input.method.*`: request HTTP method, lower case
    * `wsgi.input.scheme.*`: request scheme, usually `http` or `https`
    * `wsgi.input.host.*`: host name with `.` replaced by `_`
    * `wsgi.input.port.*`: port number, or `false` if no port supplied
    * `wsgi.input.query.{true, false}`: did the request have a query string
    * `wsgi.input.cookie.{true, false}`: did the request have a cookie set
    * `wsgi.input.status.*`: numeric response code
    * `wsgi.input.content_type.*`: request content type, with `/` replaced by `_`
   
    :ivar app: the WSGI application to wrap
    :ivar metric: the metric function to use for output
   
    """

    def __init__(self, app, metric = call_default):
        self.app = app
        self.metric = metric

    def __call__(self, environ, start_response):
        iterable = None

        try:
            t = time.time()
            bytes = 0
            status = None
            headers = None

            # XXX Wrap environ['wsgi.input'] in measure_file... when I write it.

            # there's two ways to send data. TWO!
            # The first is by yielding a sequence of bytes.
            # This is an accumulator to count them as a side effect.
            def accumulator(s):
                nonlocal bytes
                bytes += len(s)
                return s

            # The second is this 'write' thing.
            # Here's closures around the start_response callable we got from the server.
            # The outer closure updates the status & headers, and the inner one accumulates bytes.
            def start_response_wrapper(status_, headers_, *args):
                nonlocal status, headers
                status = status_
                headers = headers_

                # call the wrapped 'start_response' callable to get
                # get the 'write' callable that we're wrapping. Really.
                write = start_response(status_, headers_, *args)

                def write_wrapper(s):
                    nonlocal bytes
                    bytes += len(s)
                    write(s)

                return write_wrapper

            # guess what? there's actually a THIRD way to send output!
            # environ['wsgi.file_wrapper'] is a server-specific wrapper for
            # sendfile(2) and it's unlikely we could succesfully instrument it.
            # Besiides, this is getting a little ridiculous.

            # get the iterable from our wrapped app, and wrap it in the accumulator
            iterable = self.app(environ, start_response_wrapper)
            yield from map(accumulator, iterable)

        finally:
            # call close on the iterable, then output the metrics
            try:
                if hasattr(iterable, 'close'):
                    iterable.close()
            finally:
                _t = time.time() - t

                if status is not None and headers is not None:
                    self.wsgi_metrics(environ, status, headers, bytes, _t)


    def wsgi_metrics(self, environ, status, headers, bytes, _t):
        """do the work of outputting metrics. may be extended by subclasses"""

        # a little helper
        def _metric(name):
            self.metric('wsgi.%s' % name, bytes, _t)

        # generate some metrics from the request environ
        # XXX is this a security problem using untrusted headers like this?
        _metric('request.method.%s' % environ['REQUEST_METHOD'].lower())
        _metric('request.scheme.%s' % environ['wsgi.url_scheme'].lower())

        # XXX duplicate nonsense with SERVER_NAME/SERVER_PORT from PEP-3333 
        host, *port = environ['HTTP_HOST'].split(':')
        _metric('request.host.%s' % host.replace('.', '_')
        _metric('request.port.%s' % port[0] if port else 'null')

        _metric('request.query.true' if environ.get('QUERY_STRING', '') else 'request.query.false')
        _metric('request.cookie.true' if 'HTTP_COOKIE' in environ else 'request.cookie.false')

        # XXX request content length for uploads? user agent detection?


        # generate a metric for the response status
        _metric('response.status.%s' % status[:3])

        # generate some metrics from response headers
        h = wsgiref.headers.Headers(headers)
        if 'Content-Type' in h:
            _metric('response.content_type.%s' % cgi.parse_header(h['content-type'])[0].replace('/', '_').lower())
        else:
            _metric('response.content_type.null')
