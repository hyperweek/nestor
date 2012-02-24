#-*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='nestor',
    version='0.1',
    description='Deployment app for Hyperweek',
    author=u'Sébastien Fievet',
    author_email='sebastien@hyperweek.com',
    url='https://github.com/hyperweek/nestor',
    packages=find_packages(),
    install_requires=[
        'Django==1.3.1',
        'South==0.7.3',
    ],
    dependency_links=[
        'https://github.com/hyperweek/dploi-server/tarball/master#dploi-server',
    ]
)
