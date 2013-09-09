Backwards Incompatibilities
===========================

0.3 -> 0.4
----------
* remove deprecated :func:`.measure`; use :func:`.measure_iter` instead
* convert to package; :func:`.statsd_metric` moved to its own module
* swap order of name & metric arguments
