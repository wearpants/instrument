API Documentation
=================

instrument
----------

.. automodule:: instrument
    :members: all, each, first, reducer, producer, function, block, print_metric, default_metric, make_multi_metric


instrument.output.csv
---------------------

.. automodule:: instrument.output.csv
    :members:


instrument.output.logging
-------------------------

.. automodule:: instrument.output.logging
    :members:

.. function:: logging_metric(name, count, elapsed)

    Metric that records to standard library logging at `INFO` level

instrument.output.table
-----------------------

.. module:: instrument.output.table

.. class:: TableMetric

    Print a table of statistics. See :class:`NumpyMetric <._numpy.NumpyMetric>` for usage.

    :cvar outfile: output file. Defaults to ``sys.stderr``.

instrument.output.plot
-----------------------

.. module:: instrument.output.plot

.. class:: PlotMetric

    Plot graphs of metrics. See :class:`NumpyMetric <._numpy.NumpyMetric>` for usage.

    :cvar outdir: directory to save plots in. Defaults to ``./mit_plots``.

instrument.output.statsd
------------------------

.. module:: instrument.output.statsd

save metrics to `statsd <http://codeascraft.com/2011/02/15/measure-anything-measure-everything/>`__

.. function:: statsd_metric(name, count, elapsed)

    Metric that records to statsd/graphite

instrument.output._numpy
------------------------

.. module:: instrument.output._numpy

numpy-based metrics

.. class:: NumpyMetric

    Do not create instances of this class directly. Simply pass the
    classmethod :func:`metric` to a measurement function. Output using
    :func:`dump`. These are the only public methods. This is an abstract base
    class; you should use one of the concrete subclases in this module
    instead.

    Each metric consumes one open file and 32K of memory while running.
    Output requires enough memory to load all data points for each metric.

    :cvar bool dump_atexit: automatically call :func:`dump` when the interpreter exits. Defaults to True.

    .. classmethod:: metric(name, count, elapsed)

        A metric function that buffers through numpy

        :arg str name: name of the metric
        :arg int count: number of items
        :arg float elapsed: time in seconds


    .. classmethod:: dump()

        Output all recorded metrics
