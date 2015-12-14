# -*- coding: utf-8 -*-
import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='fabric-aws-lambda',
    version='0.1',
    packages=['fabric_aws_lambda'],
    include_package_data=True,
    license='see LICENSE',
    description='Fabric tasks for AWS Lambda Python',
    long_description=README,
    url='https://github.com/kunihikokido/fabric-aws-lambda',
    author='Kunihiko Kido',
    author_email='kunihiko.kido@me.com',
)
