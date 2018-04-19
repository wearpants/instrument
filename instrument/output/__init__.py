def print_metric(name, count, elapsed):
    """A metric function that prints

    :arg str name: name of the metric
    :arg int count: number of items
    :arg float elapsed: time in seconds
    """
    if name is not None:
        print("%s: %d items in %.2f seconds"%(name, count, elapsed))
    else:
        print("%d items in %.2f seconds"%(count, elapsed))


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
