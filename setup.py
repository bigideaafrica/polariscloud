#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import find_packages, setup

# Read version from the package
with open('src/polaris/__init__.py', 'r') as f:
    for line in f:
        if line.startswith('__version__'):
            version = line.split('=')[1].strip().strip('"\'')
            break

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='polaris-subnet',
    version=version,
    description='Polaris - Modern Development Workspace Manager for Distributed Compute Resources',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Polaris Team',
    author_email='help@polariscloud.ai',
    url='https://github.com/bigideainc/polaris-subnet',
    package_dir={"": "src"},
    packages=find_packages(where="src", exclude=['tests', 'tests.*']),
    include_package_data=True,
    install_requires=[
        'click',
        'tabulate',
        'GitPython',
        'click-spinner',
        'rich',
        'loguru',
        'questionary',  # Changed from inquirer to questionary to match the imports
        'requests',
        'xlsxwriter',
        'pyyaml',
        'psutil',
        'python-dotenv',
        'pid',
        'bittensor',  # Added explicitly
    ],
    entry_points={
        'console_scripts': [
            'polaris=polaris.cli.commands:cli',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
) 