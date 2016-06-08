"""Instrumentation for WSGI via middleware"""

# based on http://lucumr.pocoo.org/2007/5/21/getting-started-with-wsgi/
# and http://blog.dscpl.com.au/2012/10/obligations-for-calling-close-on.html
# and also http://blog.dscpl.com.au/2012/10/wsgi-middleware-and-hidden-write.html
# and a deeper reading of PEP-3333 than is healthy.

from __future__ import print_function, division

import wsgiref.headers
import cgi
import time

from . import call_default, measure_produce

class MeasureWSGIMiddleware(object):
    """Middleware that measures WSGI
        
    The following metrics record response body size in bytes & total processing time:
    
    * `wsgi.request.method.*`: request HTTP method, lower case
    * `wsgi.request.scheme.*`: request scheme, usually `http` or `https`
    * `wsgi.request.host.*`: host name with `.` replaced by `_`
    * `wsgi.request.port.*`: port number, or `null` if no port supplied
    * `wsgi.request.query.{true, false}`: did the request have a query string
    * `wsgi.request.cookie.{true, false}`: did the request have a cookie set
    * `wsgi.response.status.*`: numeric response code
    * `wsgi.response.content_type.*`: response content type, with `/` replaced by `_`

    The following metrics record request body size in bytes & time to read it:
    
    * `wsgi.input.method.*`: request HTTP method, lower case
    * `wsgi.input.scheme.*`: request scheme, usually `http` or `https`
    * `wsgi.input.host.*`: host name with `.` replaced by `_`
    * `wsgi.input.port.*`: port number, or `null` if no port supplied
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
            output_bytes = 0
            status = None
            headers = None

            # Wrap environ['wsgi.input'] to measure upload bytes & time.
            # We pass a closure as a metric function to update our local vars (like a callback).
            input_bytes = 0
            input_elapsed = 0.0

            def input_metric(name, count, elapsed):
                nonlocal input_bytes, input_elapsed
                input_bytes += count
                input_elapsed += elapsed
                
            wsgi_input = environ['wsgi.input']
            wsgi_input.read = measure_produce(name='wsgi.input', metric=input_metric)(wsgi_input.read)
            wsgi_input.readline = measure_produce(name='wsgi.input', metric=input_metric)(wsgi_input.readline)            
            
            # there's two ways to send data. TWO!
            # The first is by yielding a sequence of bytes.
            # This is an accumulator to count them as a side effect.
            def accumulator(s):
                nonlocal output_bytes
                output_bytes += len(s)
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
                    nonlocal output_bytes
                    output_bytes += len(s)
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
                output_elapsed = time.time() - t

                if status is not None and headers is not None:
                    self.wsgi_metrics(environ, status, headers,
                                      output_bytes, output_elapsed,
                                      input_bytes, input_elapsed)


    def wsgi_metrics(self, environ, status, headers,
                     output_bytes, output_elapsed,
                     input_bytes, input_elapsed):
        """do the work of outputting metrics. may be extended by subclasses"""

        # some common vars
        # XXX is this a security problem using untrusted headers like this?
        method = environ['REQUEST_METHOD'].lower()
        scheme = environ['wsgi.url_scheme'].lower()

        # XXX duplicate nonsense with SERVER_NAME/SERVER_PORT from PEP-3333 
        host, *port = environ['HTTP_HOST'].split(':')
        host = host.replace('.', '_')
        port = port[0] if port else 'null'
        
        query = str('QUERY_STRING' in environ).lower()
        cookie = str('HTTP_COOKIE' in environ).lower()
        status = status[:3]

        # a little helper
        def _output_metric(name):
            self.metric('wsgi.%s' % name, output_bytes, output_elapsed)

        # generate some metrics from the request environ
        _output_metric('request.method.%s' % method)
        _output_metric('request.scheme.%s' % scheme)

        _output_metric('request.host.%s' % host)
        _output_metric('request.port.%s' % port)

        _output_metric('request.query.%s' % query)
        _output_metric('request.cookie.%s' % cookie)

        # XXX user agent detection?

        # generate a metric for the response status
        _output_metric('response.status.%s' % status)

        # generate some metrics from response headers
        h = wsgiref.headers.Headers(headers)
        if 'Content-Type' in h:
            _output_metric('response.content_type.%s' % cgi.parse_header(h['content-type'])[0].replace('/', '_').lower())
        else:
            _output_metric('response.content_type.null')
        
        # generate metrics for uploads, if present
        if input_bytes != 0:
            # a little helper
            def _input_metric(name):
                self.metric('wsgi.input.%s' % name, input_bytes, input_elapsed)
        
            _input_metric('method.%s' % method)
            _input_metric('scheme.%s' % scheme)
    
            _input_metric('host.%s' % host)
            _input_metric('port.%s' % port)
    
            _input_metric('query.%s' % query)
            _input_metric('cookie.%s' % cookie)
    
            _input_metric('status.%s' % status)            