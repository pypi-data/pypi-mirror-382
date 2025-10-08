"""
numpy-json: JSON encoder for NumPy arrays and Python data types

Copyright (c) 2025 Featrix, Inc.
Licensed under the MIT License
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README for long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="numpy-json",
    version="0.1.0",
    author="Featrix, Inc.",
    author_email="info@featrix.com",
    description="JSON encoder for NumPy arrays and extended Python data types",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/featrix/numpy-json",
    project_urls={
        "Bug Tracker": "https://github.com/featrix/numpy-json/issues",
        "Documentation": "https://github.com/featrix/numpy-json#readme",
        "Source Code": "https://github.com/featrix/numpy-json",
    },
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.20.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "pandas>=1.3.0",  # for testing pandas support
        ],
    },
    keywords=[
        "numpy",
        "json",
        "encoder",
        "serialization",
        "array",
        "scientific computing",
        "data science",
    ],
    license="MIT",
    zip_safe=False,
)

