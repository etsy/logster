#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

tests_require = [
        'mock>=2.0.0;python_version<"3.3"',
        'contextlib2;python_version<"3.5"',
        'pathlib;python_version<="3.3"', 
        'nose',
        'portalocker'
    ]

setup(
    name='logster',
    version='1.0.1',
    description='Parse log files, generate metrics for Graphite and Ganglia',
    author='Etsy',
    url='https://github.com/etsy/logster',
    packages=[
        'logster',
        'logster/parsers',
        'logster/tailers',
        'logster/outputs'
    ],
    install_requires = [
        'pygtail>=0.5.1'
    ],
    tests_require = tests_require,
    extras_require={'test': tests_require},
    zip_safe=False,
    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # `pip` to create the appropriate form of executable for the target
    # platform.
    entry_points={  # Optional
        'console_scripts': [
            'logster=logster.logster_cli:main',
        ],
    },
    license='GPL3',
)
