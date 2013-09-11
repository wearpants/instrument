API Documentation
=================

measure_it
----------

.. automodule:: measure_it
    :members: measure_iter, measure_each, measure_reduce, measure_produce, measure_func, measure_first, measure_block, print_metric, default_metric, make_multi_metric


measure_it.csv
--------------

.. automodule:: measure_it.csv
    :members:

measure_it.numpy
----------------

.. automodule:: measure_it.numpy
    :members: NumpyMetric, PlotMetric, StatsMetric


measure_it.statsd
-----------------

.. module:: measure_it.statsd

save metrics to `statsd <http://codeascraft.com/2011/02/15/measure-anything-measure-everything/>`__

.. function:: statsd_metric(name, count, elapsed)

    Metric that records to statsd/graphite
