#!/usr/bin/env python
# coding: utf-8

if bytes is not str:
    raise Exception("""
        Python3 has not been supported yet.
        """)


from setuptools import setup


setup(
    name='one_fmt',
    version='1.0.3',
    author='publicqi',
    author_email='qisu@ucsb.edu',
    url='https://github.com/publicqi/one_fmt/',
    description='A module to generate format string exploit shorter than a given length. Currently only supports python2',
    packages=['one_fmt'],
    install_requires=[],
    entry_points={
    }
)
