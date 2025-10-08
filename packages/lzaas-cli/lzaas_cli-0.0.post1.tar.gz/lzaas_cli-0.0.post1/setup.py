#!/usr/bin/env python3
"""
LZaaS CLI Tool Setup
Landing Zone as a Service - Account Factory Automation Command Line Interface
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="lzaas-cli",
    use_scm_version={
        "version_scheme": "post-release",
        "local_scheme": "dirty-tag",
        "tag_regex": r"^(?P<prefix>v)?(?P<version>[^\+]+?)(?P<suffix>.*)?$"
    },
    setup_requires=['setuptools_scm'],
    author="SSE Platform Team",
    author_email="platform@spitzkop.io",
    description="Landing Zone as a Service - AWS Account Factory Automation Command Line Interface",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SPITZKOP/lzaas-cli",
    packages=find_packages(),
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
    ],
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
        "boto3>=1.26.0",
        "pyyaml>=6.0",
        "requests>=2.28.0",
        "rich>=12.0.0",
        "tabulate>=0.9.0",
        "jsonschema>=4.0.0",
        "python-dateutil>=2.8.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=0.991",
        ],
    },
    entry_points={
        "console_scripts": [
            "lzaas=lzaas.cli.main:cli",
        ],
    },
)
