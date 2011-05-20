#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='django-chem',
      version='0.0.0',
      description='A cheminformatic extension of the Django DB abstraction layer',
      url='https://github.com/rvianello/django-chem',
      packages = find_packages(exclude = [
            'docs',
            'docs.*',
            ]),
     )
