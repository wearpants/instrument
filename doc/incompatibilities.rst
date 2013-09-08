Backwards Incompatibilities
===========================

0.3 -> 0.4
----------
* remove deprecated :func:`measure`; use :func:`measure_iter` instead
* swap metric and name arguments
* convert to package; `statsd` metric moved to its own module