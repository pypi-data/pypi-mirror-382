#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name="spice-seismic",
    version="0.1.0",
    author="Shyla Kupis",
    author_email="shyla.kupis@utas.edu.au",
    description="Seismic Processing and Inversion for Cryosphere Exploration",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/shylarae10/SPIce",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "obspy>=1.3.0",
        "scipy>=1.7.0",
        "pandas>=1.3.0",
        "numpy>=1.21.0",
        "matplotlib>=3.4.0",
        "pyproj>=3.0.0",
        "pykonal>=0.3.0",
    ],
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
    ],
)
