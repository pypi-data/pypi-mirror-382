#!/usr/bin/env python
"""Distribution Utilities setup program for MyProxy Client Package

NERC DataGrid Project
"""
__author__ = "P J Kershaw"
__date__ = "12/12/08"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = """BSD - See LICENSE file in top-level package directory

Software adapted from myproxy_logon.  - For myproxy_logon see Access Grid
Toolkit Public License (AGTPL)

This product includes software developed by and/or derived from the Access
Grid Project (http://www.accessgrid.org) to which the U.S. Government retains
certain rights."""
__contact__ = "Philip.Kershaw@stfc.ac.uk"

# Bootstrap setuptools if necessary.
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

import os

THIS_DIR = os.path.dirname(__file__)

# Read succeeds for sdist creation but fails for build with pip install.  Added
# catch here for latter case.
try:
    LONG_DESCR = open(os.path.join(THIS_DIR, 'README.md')).read()

except IOError:
    LONG_DESCR = (
        'Python implementation of a client to the MyProxy Credential Management '
        'Server (http://grid.ncsa.uiuc.edu/myproxy/) '
    )

setup(
    name =            	'MyProxyClient',
    version =         	'2.2.0',
    description =     	'MyProxy Client',
    long_description = 	LONG_DESCR,
    long_description_content_type='text/markdown',
    author =          	'Philip Kershaw',
    author_email =    	'Philip.Kershaw@stfc.ac.uk',
    maintainer =        'Philip Kershaw',
    maintainer_email =  'Philip.Kershaw@stfc.ac.uk',
    url =             	'https://github.com/cedadev/MyProxyClient',
    platforms =         ['POSIX', 'Linux', 'Windows'],
    install_requires =  ['pyOpenSSL', 'six'],
    license =           __license__,
    test_suite =        'myproxy.test',
    packages =          find_packages(),
    include_package_data = True,
    package_data =      {
        '': ['README.md'],
        'myproxy.client': ['LICENSE'],
        'myproxy.test': [
            '*.cfg', '*.conf', '*.crt', '*.csr', '*.key', 'README'
            ]
    },
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Security',
        'Topic :: Internet',
        'Topic :: Scientific/Engineering',
        'Topic :: System :: Distributed Computing',
        'Topic :: System :: Systems Administration :: Authentication/Directory',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    zip_safe = False,
    entry_points = {
        'console_scripts': ['myproxyclient = myproxy.client.script:main',
                            ],
        }
)
