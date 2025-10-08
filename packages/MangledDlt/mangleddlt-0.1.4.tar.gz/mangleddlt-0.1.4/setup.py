#!/usr/bin/env python
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="MangledDlt",
    version="0.1.4",
    author="MangledDLT Team",
    author_email="team@mangledlt.io",
    description="Local Databricks Development Bridge - Intercept Spark operations for local Unity Catalog access",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mangledlt/mangledlt",
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=[
        "databricks-sql-connector>=2.9.0",
        "configparser>=5.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "all": ["pyspark>=3.4.0"],
        "dev": [
            "pytest>=7.0",
            "pytest-mock>=3.0",
            "pytest-cov>=4.0",
            "black>=23.0",
            "mypy>=1.0",
            "coverage>=6.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "mangledlt=mangledlt.cli:main",
        ],
    },
)