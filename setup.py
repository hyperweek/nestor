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
    'eventlet>=0.9.15',
    'django-extensions==0.8',
    'django-grappelli==2.3.8',
    'django-reversion==1.5.1',
    'djutils==0.3.2',
    'dnsimple-api==0.1',
    'Jinja2==2.6',
    'raven==1.4.6',
    'South>=0.7',
    # dependency_links
    'dploi-server',
    'Fabric',
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
        'https://github.com/zyegfryed/fabric/tarball/master#egg=Fabric'
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
