Future Plans
============
Some rough thoughts.

Automagic Instrumentation
-------------------------
Support for automagic instrumentation of popular 3rd-party packages:

* django, using introspection logic from `django-statsd <https://github.com/django-statsd/django-statsd>`__
* `generic WSGI middleware <http://blog.dscpl.com.au/2015/05/performance-monitoring-of-real-wsgi.html>`__. Possibly flask.
* any `dbapi <http://www.python.org/dev/peps/pep-0249/>`__-compatible database, with names derived by parsing SQL for table/query type
* HTTP clients: `requests <http://docs.python-requests.org/en/latest/>`__ and `urllib <http://docs.python.org/2/library/urllib2.html>`__
* storage engines: MongoDB, memcached, redis, Elastic Search. Possibly sqlalchemy

More metric backends
--------------------

* lightweight running stats, based on forthcoming `stdlib statistics <http://www.python.org/dev/peps/pep-0450/>`__ module. May include support for periodic stats output, as a low-budget alternative to statsd.
* Prometheus, Datadog, etc.

Bonus features
--------------

* sampling & filtering for metric functions
* integration of nice Jupyter notebook for analysis

Modernization
-------------

* rip out old 2.7 compatibility stuff
* pypy test & support
