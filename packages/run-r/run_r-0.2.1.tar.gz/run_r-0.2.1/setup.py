"""Setup script for run-r package."""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="run-r",
    version="0.2.1",
    author="bsgarcia",
    author_email="",
    description="A lightweight Python plugin to execute R scripts and retrieve workspace variables",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bsgarcia/run-r",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=3.0",
        ],
        "pandas": [
            "pandas>=1.0.0",
            "numpy>=1.18.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "run-r=run_r.run_r:main",
        ],
    },
    keywords="R statistics data-science subprocess interoperability",
    project_urls={
        "Bug Reports": "https://github.com/bsgarcia/run-r/issues",
        "Source": "https://github.com/bsgarcia/run-r",
    },
)
