"""
HLA-Compass Python SDK
SDK for developing modules on the HLA-Compass platform
"""

from setuptools import setup, find_packages
import os
import re
import json
import urllib.request
import urllib.error


# Read version from hla_compass/_version.py to single-source the version
def get_version():
    with open(os.path.join("hla_compass", "_version.py"), "r") as f:
        content = f.read()
        match = re.search(
            r'^__version__\s*=\s*[\'\"]([^\'\"]*)[\'\"]', content, re.MULTILINE
        )
        if match:
            return match.group(1)
        raise RuntimeError("Unable to find version string in _version.py")


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="hla-compass",  # Shorter name for easier installation
    version=get_version(),
    author="Alithea Bio",
    author_email="armanas.povilionis@alithea.bio",
    description="Python SDK for HLA-Compass bioinformatics platform - Build powerful modules for immuno-peptidomics analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AlitheaBio/HLA-Compass-platform",
    project_urls={
        "Bug Tracker": "https://github.com/AlitheaBio/HLA-Compass-platform/issues",
        "Documentation": "https://docs.alithea.bio",
        "Source Code": "https://github.com/AlitheaBio/HLA-Compass-platform/tree/main/sdk/python",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.28.0",  # API communication
        "boto3>=1.26.0",  # AWS S3 storage operations
        "click>=8.0.0",  # CLI framework
        "rich>=12.0.0",  # Terminal formatting
        "PyYAML>=6.0",  # YAML configuration parsing
        "setuptools>=45.0.0",  # Required for pkg_resources compatibility
        "cryptography>=41.0.0",  # RSA signing for module deployment
        "jsonschema>=4.17.0",  # Manifest validation
        "questionary>=2.0.0",  # Interactive wizard
        "jinja2>=3.1.0",  # Template rendering
        "watchdog>=3.0.0",  # File watching for dev mode
        "aiohttp>=3.9.0",  # Dev server
    ],
    extras_require={
        "dev": [  # Development tools (testing, linting)
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "pytest-mock>=3.6.0",
            "black>=22.0.0",
            "isort>=5.10.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
        "data": [  # Data science features (optional)
            # Latest pandas for modern Python; fallback for Python 3.8
            "pandas>=2.2.0; python_version >= '3.9'",
            "pandas>=1.5,<2.0; python_version < '3.9'",
            "xlsxwriter>=3.0.0",  # For Excel export functionality
        ],
        "ml": [  # Machine learning features (optional)
            "scikit-learn>=1.0.0",
            "torch>=1.10.0",
            "transformers>=4.20.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "hla-compass=hla_compass.cli:main",
            "module-runner=hla_compass.runtime.runner:main",
        ],
    },
    package_data={
        "hla_compass": ["templates/**/*", "data/*"],
    },
    include_package_data=True,
)
