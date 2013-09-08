Installation
============
measure_it subscribes to the Python batteries-included philosophy. It ships
with support for a number of different :doc:`metric backends <output>`, and
eventually instrumentation for popular packages. Since most users will want only a subset of this functionality, optional dependencies are not installed by default.

Note that the included `requirements.txt` file includes *all* depedencies
(for build/test purposes), and is almost certainly not what you want.

Minimal
-------

To install the base package (with no depedencies beyond the standard library):

  `pip install measure_it`

This includes: all generic measurement functions, :func:`print_metric` and :mod:`csv` metrics.

Batteries Included
------------------

To install the dependencies for an optional component, specify it in brackets
during installation (see also: `setuptools extras
<http://pythonhosted.org/setuptools/setuptools.html#declaring-extras-optional-features-with-their-own-dependencies>`__):

  `pip install measure_it[statsd]`

The following extra targets are supported:

* :mod:`statsd <measure_it.statsd>`: statsd metric
* :mod:`numpy <measure_it.numpy>`: numpy & matplotlib metrics
