Backwards Incompatibilities
===========================

0.5 -> 0.6
----------
* drop support for Python 2.7
* `name` and `metric` are keyword only arguments
* various renames; see :doc:`changelog` for details

0.4 -> 0.5
----------
* main package renamed from ``measure_it`` to ``instrument``
* prefixed ``measure_iter``, etc. functions no longer available; use ``instrument.iter`` instead

0.3 -> 0.4
----------
* remove deprecated :func:`.measure`; use :func:`.measure_iter` instead
* convert to package; :func:`.statsd_metric` moved to its own module
* swap order of name & metric arguments
