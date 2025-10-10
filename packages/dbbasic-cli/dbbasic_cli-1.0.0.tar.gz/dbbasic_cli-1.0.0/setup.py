#!/usr/bin/env python3
"""
Setup script for dbbasic-cli
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text() if (this_directory / "README.md").exists() else ""

setup(
    name="dbbasic-cli",
    version="1.0.0",
    author="DBBasic Project",
    author_email="hello@dbbasic.com",
    description="Command-line tool for creating and managing DBBasic apps",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/askrobots/dbbasic-cli-new",
    project_urls={
        "Bug Reports": "https://github.com/askrobots/dbbasic-cli-new/issues",
        "Source": "https://github.com/askrobots/dbbasic-cli-new",
        "Documentation": "http://dbbasic.com/cli-spec",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[],  # No dependencies!
    entry_points={
        'console_scripts': [
            'dbbasic=dbbasic_cli.cli:main',
        ],
    },
    keywords="web framework cli database tsv dbbasic generator scaffold",
)
