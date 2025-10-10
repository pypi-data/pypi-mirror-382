#!/usr/bin/env python
"""
Setup script for rai-temp-sdk package.

This setup.py is provided for legacy compatibility and for commands like:
    python setup.py sdist --formats=zip

For modern packaging, use pyproject.toml with:
    python -m build
"""

import os
from setuptools import setup, find_packages

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read version from pyproject.toml or define it here
VERSION = "1.0.0"

# Package information
PACKAGE_NAME = "rai-temp-sdk"
PACKAGE_DIR = "RAI_SDK"
MAIN_PACKAGE = "rai_agent_functions_api"

setup(
    # Basic package information
    name=PACKAGE_NAME,
    version=VERSION,
    author="MAQ Software",
    author_email="divyanshur@maqsoftware.com",
    description="MAQ Software RAI SDK - Azure Functions API client for RAI (Responsible AI) operations including prompt review and testcase generation",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    
    # URLs
    url="https://github.com/DivyanshuMaq/rai-temp-sdk",
    project_urls={
        "Homepage": "https://github.com/DivyanshuMaq/rai-temp-sdk",
        "Documentation": "https://github.com/DivyanshuMaq/rai-temp-sdk#readme",
        "Repository": "https://github.com/DivyanshuMaq/rai-temp-sdk.git",
        "Bug Tracker": "https://github.com/DivyanshuMaq/rai-temp-sdk/issues",
    },
    
    # Package discovery
    package_dir={"": PACKAGE_DIR},
    packages=find_packages(where=PACKAGE_DIR),
    
    # Include package data
    package_data={
        MAIN_PACKAGE: ["py.typed"],
    },
    include_package_data=True,
    
    # Python version requirement
    python_requires=">=3.8",
    
    # Dependencies
    install_requires=[
        "azure-core>=1.24.0",
        "typing-extensions>=4.0.0",
        "isodate>=0.6.0",
    ],
    
    # Optional dependencies
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-asyncio",
            "black",
            "flake8",
            "mypy",
        ],
    },
    
    # Package classification
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
    ],
    
    # Keywords
    keywords="azure functions api responsible-ai rai prompt-review testcase-generation",
    
    # License
    license="MIT",
    
    # Zip safe
    zip_safe=False,
)