#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="onecite",
    version="0.0.9",
    author="OneCite Team",
    author_email="onecite@example.com",
    description="Universal citation management and academic reference toolkit",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/HzaCode/OneCite",
    packages=find_packages(exclude=["tests", "tests.*", "*.tests", "*.tests.*"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
        "beautifulsoup4>=4.9.0",
        "lxml>=4.6.0",
        "bibtexparser>=1.4.0",
        "PyYAML>=6.0",
        "thefuzz>=0.19.0",
        "python-Levenshtein>=0.12.0",
        "scholarly>=1.7.0",
        "PyPDF2>=3.0.0",
    ],
    entry_points={
        "console_scripts": [
            "onecite=onecite.cli:main",
            "onecite-mcp=onecite_mcp.server:main",
        ],
    },
    package_data={
        "onecite": ["templates/*.yaml"],
    },
    include_package_data=True,
)
