#!/usr/bin/env python
from setuptools import setup, find_packages

setup(name='instrument',
      version="0.5.1",
      description='instrumentation primitives for metrics and benchmarking',
      author='Pete Fein',
      author_email='pete@wearpants.org',
      url='http://github.com/wearpants/instrument',
      packages=find_packages(exclude=['tests', 'doc']),
      extras_require={
        'statsd': ['statsd'],
        'numpy': ['numpy', 'prettytable'],
        'plot': ['matplotlib'],
        },
      license = "BSD",
      classifiers = [
      "Programming Language :: Python :: 2",
      "Programming Language :: Python :: 3",
      "Development Status :: 5 - Production/Stable",
      "Intended Audience :: Developers",
      "License :: OSI Approved :: BSD License",],
      long_description=open('README.rst').read(),
      )
