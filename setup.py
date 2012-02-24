#-*- coding: utf-8 -*-
#!/usr/bin/env python
"""
Nestor
======

:copyright: (c) 2012 by the Hyperweek Team, see AUTHORS for more details.
:lic
"""
from setuptools import setup, find_packages

install_requires = [
    'Django>=1.2,<1.4',
    'South>=0.7',
    'dploi-server',
]

setup(
    name='nestor',
    version='0.1',
    author=u'Sébastien Fievet',
    author_email='sebastien@hyperweek.com',
    url='https://github.com/hyperweek/nestor',
    description='Deployment app for Hyperweek',
    packages=find_packages(),
    zip_safe=False,
    install_requires=install_requires,
    dependency_links=[
        'https://github.com/hyperweek/dploi-server/tarball/develop#egg=dploi-server',
    ],
    license='BSD',
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Software Development'
    ],
)
