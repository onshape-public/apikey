#!/usr/bin/env python

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

config = {
    'name': 'onshapepy',
    'version': '0.0.1',
    'description': 'Sample package to demonstrate using Onshape API keys',
    'long_description': open('README.md').read(),
    'author': 'Len Wanger',
    'author_email': 'lwanger@impossible-objects.com',
    'url': 'https://github.com/lwanger/onshapepy',
    'license': open('LICENSE').read(),
    #'packages': [ 'onshapepy' ],
    'packages': find_packages(),
    'classifiers': [
        'Programming Language :: Python',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
}

setup(**config)
