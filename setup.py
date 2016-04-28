import codecs
import os
import re

from setuptools import setup, find_packages

requirements = [
    "python-dockercloud >= 1.0.3, < 2",
    "docker-compose >= 1.6.0, <2"
    ]


def read(*parts):
    path = os.path.join(os.path.dirname(__file__), *parts)
    with codecs.open(path, encoding='utf-8') as fobj:
        return fobj.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')


with open('./test-requirements.txt') as test_reqs_txt:
    test_requirements = [line for line in test_reqs_txt]

setup(
    name='dockercloud-haproxy',
    version=find_version('haproxy', '__init__.py'),
    packages=find_packages(),
    install_requires=requirements,
    tests_require=test_requirements,
    entry_points={
        'console_scripts':
            ['dockercloud-haproxy = haproxy.main:main']
    },
    include_package_data=True,
    author='Docker, Inc.',
    author_email='info@docker.com',
    description='Auto self-configured haproxy on Docker Cloud',
    license='Apache v2',
    keywords='docker cloud haproxy',
    url='http://cloud.docker.com/',
    test_suite='tests',
)
