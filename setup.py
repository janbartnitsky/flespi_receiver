# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='flespi_receiver',
    version='0.1.0',
    description='Messages retranslator for flespi.io',
    long_description=readme,
    author='Jan Bartnitsky',
    author_email='baja@gurtam.com',
    url='https://github.com/janbartnitsky/flespi_receiver',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)

