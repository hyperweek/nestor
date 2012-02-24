#-*- coding: utf-8 -*-
from setuptools import setup, find_packages

install_requires = [
    'Django>=1.2,<1.4',
    'South>=0.7',
    'dploi-server',
]

setup(
    name='nestor',
    version='0.1',
    description='Deployment app for Hyperweek',
    author=u'Sébastien Fievet',
    author_email='sebastien@hyperweek.com',
    url='https://github.com/hyperweek/nestor',
    packages=find_packages(),
    install_requires=install_requires,
    dependency_links=[
        'https://github.com/hyperweek/dploi-server/tarball/master#egg=dploi-server',
    ]
)
