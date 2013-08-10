#!/usr/bin/env python
from distutils.core import setup

setup(name='measure-it',
      version="0.2.1",
      description='time and count measurement for iterators',
      author='Pete Fein',
      author_email='pete@wearpants.org',
      url='http://github.com/wearpants/measure_it',
      py_modules=['measure_it'],
      license = "BSD",
      classifiers = [
      "Programming Language :: Python :: 2",
      "Programming Language :: Python :: 3",
      "Development Status :: 5 - Production/Stable",
      "Intended Audience :: Developers",
      "License :: OSI Approved :: BSD License",],
      long_description=open('README.rst').read(),
      )
