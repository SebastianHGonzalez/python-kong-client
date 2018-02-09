import io
import os
import re
from glob import glob
from os.path import basename
from os.path import dirname
from os.path import join
from os.path import splitext

from pip.req import parse_requirements

from setuptools import find_packages
from setuptools import setup

__version__ = '0.0.0'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def read(*names, **kwargs):
    return io.open(
        join(dirname(__file__), *names),
        encoding=kwargs.get('encoding', 'utf8')
    ).read()


# parse_requirements() returns generator of pip.req.InstallRequirement objects
requirements = [str(ir.req) for ir in parse_requirements(os.path.join(BASE_DIR, 'requirements.txt'), session=False)]
# requirements_test = [str(ir.req) for ir in parse_requirements('./requirements-test.txt', session=False)]

setup(
    name='python-kong-manager',
    version=__version__,
    license='BSD',
    description='A Python client for the Kong API (http://getkong.org/)',
    long_description='%s\n%s' % (read('README.rst'), re.sub(':[a-z]+:`~?(.*?)`', r'``\1``', read('CHANGELOG.rst'))),
    author='',
    author_email='',
    url='',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
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
    extras_require={},
)
