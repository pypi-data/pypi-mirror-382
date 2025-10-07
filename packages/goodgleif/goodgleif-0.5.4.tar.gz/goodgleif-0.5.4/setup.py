#!/usr/bin/env python3
from setuptools import setup, find_packages
import re
from pathlib import Path

# Read version from __init__.py without importing the package
def get_version():
    init_file = Path(__file__).parent / "goodgleif" / "__init__.py"
    with open(init_file) as f:
        content = f.read()
    match = re.search(r'__version__ = ["\']([^"\']+)["\']', content)
    if match:
        return match.group(1)
    raise RuntimeError("Unable to find version string")

setup(
    name="goodgleif",
    version=get_version(),
    description="Lightweight tools for working with GLEIF LEI data: preprocess, load, fuzzy query.",
    author="Peter Cotton",
    python_requires=">=3.10",
    packages=find_packages(),
    install_requires=[
        "pandas>=2.1",
        "pyarrow>=14.0",
        "rapidfuzz>=3.6",
        "platformdirs>=4.2",
        "pyyaml>=6.0.1",
        "requests>=2.25.0",
    ],
    extras_require={
        "polars": ["polars>=1.8"],
        "dev": ["pytest>=7.4", "ruff>=0.5.0"],
    },
    include_package_data=True,   # works with MANIFEST.in for sdists
    entry_points={
        "console_scripts": [
            "goodgleif=goodgleif.cli:main",
        ],
    },
)
