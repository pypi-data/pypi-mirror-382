#!/usr/bin/env python
from setuptools import setup

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')


setup(
    long_description=readme + '\n\n' + history,
)
