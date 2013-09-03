Changelog
=========
0.4
---
* add default_metric
* add make_multi_metric
* add StatsMetric and PlotMetric, based on numpy
* add CSVDirMetric and CSVFileMetric

**Backwards-incompatible changes**

* remove deprecated :func:`measure`; use :func:`measure_iter` instead
* convert to package
* swap metric and name arguments

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
