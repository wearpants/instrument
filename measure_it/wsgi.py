"""Instrumentation for WSGI via middleware"""

# based on http://lucumr.pocoo.org/2007/5/21/getting-started-with-wsgi/
# and http://blog.dscpl.com.au/2012/10/obligations-for-calling-close-on.html
# and also http://blog.dscpl.com.au/2012/10/wsgi-middleware-and-hidden-write.html
# and a deeper reading of PEP-3333 than is healthy.

from __future__ import print_function, division

import wsgiref.headers
import cgi
import time

import measure_it # XXX ugly

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

    def __init__(self, app, metric = measure_it.call_default):
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
        _metric('request.host.%s' % host.replace('.', '_'))
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
