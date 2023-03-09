#!/usr/bin/python

from setuptools import setup
from setuptools import find_packages


setup(
        name = 'py2port',
        version = '2.0',
        description = 'Two-Port Linear Circuit Analysis',
        author = 'Charles Eidsness',
        author_email = 'charles@ccxtechnologies.com',
        license = "GPL",
        packages=find_packages(),
        install_requires=['matplotlib', 'numpy']
        )

