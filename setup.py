# -*- encoding: utf-8 -*-
import os
from setuptools import setup, find_packages
import crma as app


install_requires = open('requirements.txt').read().splitlines()


def read(fname):
    try:
        return open(os.path.join(os.path.dirname(__file__), fname)).read()
    except IOError:
        return ''

setup(
    name="emencia-crma",
    version="1.0",
    description="CRMA app",
    long_description=read('README.rst'),
    license='BSD License',
    platforms=['OS Independent'],
    keywords='emencia crma django',
    author='emencia',
    author_email='contact@emencia.com',
    url="https://www.emencia.com",
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
)
