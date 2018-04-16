Changelog
=========
See also: :doc:`incompatibilities`.

0.5.0
-----
* rename project to `instrument` from `measure_it`
* update to modern tooling: pytest, pipenv, etc..
* improved testing: tox, travis
* fix to work with newer versions of statsd, including its django support

0.4
---
* add default_metric
* add make_multi_metric
* add TableMetric and PlotMetric, based on numpy
* add CSVDirMetric and CSVFileMetric
* measure_block supports user-supplied count

0.3
---
* add measure_first, measure_produce, measure_func, measure_block
* rename measure to measure_iter and deprecate old name

0.2
---
* add measure_reduce

0.1
---
Initial release
