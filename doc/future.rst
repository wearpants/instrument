Future Plans
============
Some rough thoughts.

0.5: instrument all the things
------------------------------
Support for automagic instrumentation of popular 3rd-party packages:

* django, using introspection logic from `django-statsd <https://django-statsd.readthedocs.org/en/latest/>`__
* generic WSGI middleware. Possibly flask.
* any `dbapi <http://www.python.org/dev/peps/pep-0249/>`__-compatible database, with names derived by parsing SQL for table/query type
* HTTP clients: `requests <http://docs.python-requests.org/en/latest/>`__ and `urllib <http://docs.python.org/2/library/urllib2.html>`__
* storage engines: MongoDB, memcached, redis, Elastic Search. Possibly sqlalchemy

More metric backends:

* lightweight running stats, based on forthcoming `stdlib statistics <http://www.python.org/dev/peps/pep-0450/>`__ module. May include support for periodic stats output, as a low-budget alternative to statsd.

Improved testing:

* support for tox (2.7 & 3.3+ only)
* support for http://travis-ci.org