# setup.py

from setuptools import find_packages, setup

setup(
    name='polaris-cli-tool',
    version='1.0.7',
    description='Polaris CLI - Modern Development Workspace Manager for Distributed Compute Resources',
    author='Polaris Team',
    author_email='fred@polariscloud.ai',
    url='https://github.com/bigideainc/polaris-subnet',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click',
        'tabulate',
        'click-spinner',
        'rich',
        'inquirer',
        'requests',
        'xlsxwriter',
        'pyyaml',
        'psutil',
        'python-dotenv',
        'pid',  # Added pid package
    ],
    entry_points={
        'console_scripts': [
            'polaris=polaris_cli.cli:cli',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
