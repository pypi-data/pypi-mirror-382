##############################################################################
#
# Copyright (c) 2012-2023 Federico Di Gregorio and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
#############################################################################

import os

from setuptools import find_packages
from setuptools import setup


def _read(filename):
    with open(os.path.join(os.path.dirname(__file__), filename)) as fp:
        return fp.read()


long_description = (
    _read('README.rst')
    + '\n' +
    _read('CONTRIBUTORS.txt')
    + '\n' +
    _read('CHANGES.rst')
    + '\n'
)

setup(
    name='Products.ZPsycopgDA',
    version='4.3',
    license='ZPL-2.1',
    license_files=['LICENSE*'],
    author='Federico Di Gregorio',
    author_email='fog@initd.org',
    maintainer='Jens Vagelpohl',
    maintainer_email='jens@dataflake.org',
    url='https://github.com/dataflake/Products.ZPsycopgDA',
    project_urls={
        'Documentation': 'https://zpsycopgda.readthedocs.io',
        'Issue Tracker': ('https://github.com/dataflake'
                          '/Products.ZPsycopgDA/issues'),
        'Sources': 'https://github.com/dataflake/Products.ZPsycopgDA',
    },
    description='Zope database adapter for PostGreSQL',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Zope',
        'Framework :: Zope :: 5',
        'License :: OSI Approved :: Zope Public License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Database',
        'Topic :: Database :: Front-Ends',
    ],
    packages=find_packages('src'),
    include_package_data=True,
    namespace_packages=['Products'],
    package_dir={'': 'src'},
    zip_safe=False,
    python_requires='>=3.9',
    install_requires=[
        'setuptools',
        'psycopg2 >= 2.4.2',
        'Zope >= 5',
        'Products.ZSQLMethods',
    ],
    extras_require={
        'docs': ['Sphinx', 'furo', 'pkginfo'],
    },
)
