#!/usr/bin/env python

from setuptools import setup, find_packages

import yaenv


def read(fname):
    with open(fname) as fp:
        content = fp.read()
    return content


setup(
    name=yaenv.__name__,
    version=yaenv.__version__,
    description=yaenv.__doc__,
    long_description=read('README.rst'),
    long_description_content_type='text/x-rst',
    author=yaenv.__author__,
    author_email=yaenv.__contact__,
    license=yaenv.__license__,
    url=yaenv.__url__,
    packages=find_packages(),
    install_requires=[
        'python-dotenv',
        'typing; python_version<"3.5"',
    ],
    extras_require={
        'lint': [
            'flake8',
            # 'flake8-docstrings',
            'flake8-mypy',
        ],
        'docs': [
            'sphinx',
            'sphinx-rtd-theme',
            'sphinxcontrib-napoleon',
        ],
    },
    tests_require=[
        'pytest',
    ],
    entry_points={
        'flake8.extension': [
            'D = flake8_docstrings:pep257Checker',
        ],
    },
    keywords=[
        '12factor',
        'config',
        'configuration',
        'django',
        'dotenv',
        'environment',
        'variables',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    project_urls={
        'Issues': yaenv.__url__ + '/issues',
        'Documentation': 'https://yaenv.rtfd.io',
    },
)
