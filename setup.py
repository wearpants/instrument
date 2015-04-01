#!/usr/bin/env python
from setuptools import setup, find_packages

setup(name='measure-it',
      version="0.4.1",
      description='time and count measurement for iterators and other code',
      author='Pete Fein',
      author_email='pete@wearpants.org',
      url='http://github.com/wearpants/measure_it',
      packages=find_packages(exclude=['tests', 'doc']),
      extras_require={
        'statsd': ['statsd'],
        'numpy': ['numpy', 'prettytable'],
        'plot': ['matplotlib'],
        'tests': ['nose', 'fakesleep'],
        'doc': ['Sphinx'],
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
