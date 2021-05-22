#!/usr/bin/env python
import os
from shiftmedia.version import version
from setuptools import setup, find_packages

# ----------------------------------------------------------------------------
# Building
#
# Create source distribution:
# ./setup.py sdist
#
#
# Create binary distribution (non-univeral, python 3 only):
# ./setup.py bdist_wheel --python-tag=py3
#
# Register on PyPI:
# twine register dist/mypkg.whl
#
#
# Upload to PyPI:
# twine upload dist/*
#
# ----------------------------------------------------------------------------

# project version
version = version

# development status
# dev_status = '1 - Planning'
# dev_status = '2 - Pre-Alpha'
dev_status = '3 - Alpha'
# dev_status = '4 - Beta'
# dev_status = '5 - Production/Stable'
# dev_status = '6 - Mature'
# dev_status = '7 - Inactive'

# github repository url
repo = 'https://github.com/projectshift/shift-media'
license_type = 'MIT License'

# monkey patch os for vagrant hardlinks
del os.link

# run setup
setup(**dict(

    # author
    author='Dmitry Belyakov',
    author_email='dmitrybelyakov@gmail.com',

    # project meta
    name='shiftmedia',
    version=version,
    url=repo,
    download_url=repo + '/archive/v' + version + '.tar.gz',
    description='External media and file storage for applications',
    keywords=[
        'python3',
        'aws',
        's3',
        'media',
        'images',
        'video',
        'storage',
    ],

    # classifiers
    # see: https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[

        # maturity
        'Development Status :: ' + dev_status,

        # license
        'License :: OSI Approved :: ' + license_type,

        # audience
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',

        # pythons
        'Programming Language :: Python :: 3',

        # categories
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: System :: Archiving',
        'Topic :: Utilities'
    ],

    # project packages
    packages=find_packages(
        exclude=[
            'shiftmedia.tests*',
            'shiftmedia.testing*'
        ]
    ),

    # include none-code data files from manifest.in (http://goo.gl/Uf0Yxc)
    include_package_data=True,

    # project dependencies
    install_requires=[
        'Pillow>=8.2.0,<9.0.0',
        'boto3>=1.17.78,<2.0',
        'click>=8.0.0,<9.0.0',
        'python-magic>=0.4.22,<1.0.0',
        'piexif>=1.1.3,<2'
    ],


    # project license
    license=license_type
))
