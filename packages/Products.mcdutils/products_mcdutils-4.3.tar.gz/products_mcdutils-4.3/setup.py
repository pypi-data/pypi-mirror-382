##############################################################################
#
# Copyright (c) 2008-2023 Tres Seaver and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
#############################################################################

from setuptools import find_packages
from setuptools import setup


def _read(name):
    with open(name) as fp:
        return fp.read()


setup(name='Products.mcdutils',
      version='4.3',
      description=('A Zope product with memcached-backed ZCache and '
                   'Zope session implementations.'),
      long_description=_read('README.rst') + '\n\n' + _read('CHANGES.rst'),
      long_description_content_type='text/x-rst',
      classifiers=[
          'Development Status :: 6 - Mature',
          'Environment :: Web Environment',
          'Framework :: Zope',
          'Framework :: Zope :: 5',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Zope Public License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.9',
          'Programming Language :: Python :: 3.10',
          'Programming Language :: Python :: 3.11',
          'Programming Language :: Python :: 3.12',
          'Programming Language :: Python :: 3.13',
          'Topic :: Internet :: WWW/HTTP :: Session',
      ],
      keywords='zope session memcache memcached Products',
      author='Tres Seaver and contributors',
      author_email='tseaver@palladion.com',
      maintainer='Jens Vagelpohl',
      maintainer_email='jens@dataflake.org',
      url='https://mcdutils.readthedocs.io',
      project_urls={
          'Documentation': 'https://mcdutils.readthedocs.io',
          'Issue Tracker': ('https://github.com/dataflake/Products.mcdutils'
                            '/issues'),
          'Sources': 'https://github.com/dataflake/Products.mcdutils',
      },
      license='ZPL-2.1',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      include_package_data=True,
      namespace_packages=['Products'],
      zip_safe=False,
      python_requires='>=3.9',
      install_requires=[
          'setuptools',
          'python-memcached',
          'Zope >= 5',
      ],
      extras_require={
          'docs': ['sphinx',
                   'repoze.sphinx.autointerface',
                   'furo'],
      },
      )
