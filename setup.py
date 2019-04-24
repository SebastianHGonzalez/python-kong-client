import io
import os
from os.path import dirname
from os.path import join

from pip._internal.req import parse_requirements
from setuptools import setup

__version__ = '0.1.7'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def read(*names, **kwargs):
    return io.open(
        join(dirname(__file__), *names),
        encoding=kwargs.get('encoding', 'utf8')
    ).read()


with open(os.path.join(BASE_DIR, 'requirements', 'base.txt')) as f:
    requirements = f.read().splitlines()

with open(os.path.join(BASE_DIR, 'requirements', 'testing.txt')) as f:
    requirements_test = f.read().splitlines()


setup(
    name='python-kong-client',
    version=__version__,
    license='BSD',
    description='A Python client for the Kong API 0.13.x (http://getkong.org/)',
    author='Sebastian Gonzalez',
    author_email='sebastian.h.gonzalez@gmail.com',
    url='',
    packages=['kong'],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Topic :: Utilities',
    ],
    keywords=[],
    install_requires=requirements,
    extras_require={
        "tests": requirements_test
    },
)
