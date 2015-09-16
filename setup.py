#!/usr/bin/env python
import sys

from setuptools import setup, find_packages

requires = [
    'requests==2.0',
    'boto3==1.1.1',
    'paramiko==1.15.2',
    'scp==0.10.2',
    'pyyaml==3.11'
]

setup_options = dict(
    name='coreec2',
    version='0.1.3',
    description='Command line interface for CoreOS EC2 cluster formation',
    long_description='Command line interface for CoreOS EC2 cluster formation',
    author='Petr Janda',
    url='http://github.com/petrjanda/coreos-ec2/',
    scripts=['bin/coreec2'],
    packages=find_packages(exclude=['tests*']),
    install_requires=requires,
    license="Apache License 2.0",
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ),
)

setup(**setup_options)
