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

.. module:: measure_it.numpy

numpy-based metrics

.. class:: NumpyMetric

    Do not create instances of this class directly. Simply pass the
    classmethod :func:`metric` to a measurement function. Output using
    :func:`dump`. These are the only public methods. This is an abstract base
    class; you should use one of the concrete subclases in this module
    instead.

    Each metric consumes one open file and 32K of memory while running.
    Output requires enough memory to load all data points for each metric.

    :cvar dump_atexit: automatically call :func:`dump` when the interpreter exits. Defaults to True.

    .. classmethod:: metric(name, count, elapsed)

        A metric function that buffers through numpy

        :arg str name: name of the metric
        :arg int count: number of elements
        :arg float elapsed: time in seconds


    .. classmethod:: dump()

        Output all recorded metrics

.. class:: TableMetric

    Print a table of statistics

    :cvar outfile: output file. Defaults to ``sys.stderr``.


.. class:: PlotMetric

    Plot graphs of metrics.

    :cvar outdir: directory to save plots in. Defaults to ``./mit_plots``.

measure_it.statsd
-----------------

.. module:: measure_it.statsd

save metrics to `statsd <http://codeascraft.com/2011/02/15/measure-anything-measure-everything/>`__

.. function:: statsd_metric(name, count, elapsed)

    Metric that records to statsd/graphite
