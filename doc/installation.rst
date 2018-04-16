Installation
============
instrument subscribes to the Python batteries-included philosophy. It ships
with support for a number of different :doc:`metric backends <output>`, and
eventually instrumentation for popular packages. Since most users will want only a subset of this functionality, optional dependencies are not installed by default.

Note that the included ``requirements.txt`` file includes *all* depedencies
(for build/test purposes), and is almost certainly not what you want.

Minimal
-------

To install the base package (with no depedencies beyond the standard library):

  ``pip install instrument``

This includes: all generic measurement functions, :func:`.print_metric` and :mod:`.csv` metrics.

Batteries Included
------------------

You should have completed the minimal install already. To install the
dependencies for an optional component, specify it in brackets with ``--upgrade``:

  ``pip install --upgrade instrument[statsd]``

The following extra targets are supported:

* ``statsd``: statsd metric
* ``numpy``: statistics metrics, based on numpy
* ``plot``: graphs of metrics, based on matplotlib. Because Python packaging is brain damaged, you must install the ``numpy`` target first. You'll need the `agg backend <http://matplotlib.org/users/installing.html#installing-from-source>`__.
