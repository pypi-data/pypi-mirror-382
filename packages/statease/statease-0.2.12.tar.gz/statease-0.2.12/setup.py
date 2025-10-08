""" Python interface to Stat-Ease 360.

This package implements an API to connect Python code with Stat-Ease 360.

See: https://statease.com/docs/se360/python-integration/
"""

from setuptools import setup
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

VERSION = '0.2.12'
DOCLINES = (__doc__ or '').split("\n")

CLASSIFIERS = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Intended Audience :: Manufacturing",
    "Intended Audience :: End Users/Desktop",
    "Intended Audience :: Science/Research",
    "Operating System :: OS Independent",
    "Natural Language :: English",
    "License :: Other/Proprietary License",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Topic :: Scientific/Engineering",
    "Topic :: Scientific/Engineering :: Mathematics",
    "Topic :: Scientific/Engineering :: Information Analysis",
]

def run_setup():
    setup(
        name='statease',
        version=VERSION,
        description=DOCLINES[0],
        long_description=long_description,
        classifiers=CLASSIFIERS,
        author='Stat-Ease, Inc.',
        author_email='support@statease.com',
        license='Other/Proprietary License',
        url='https://statease.com/docs/se360/python-integration/',
        packages=['statease'],
        install_requires=['pyzmq'],
        long_description_content_type='text/markdown',
    )

run_setup()
