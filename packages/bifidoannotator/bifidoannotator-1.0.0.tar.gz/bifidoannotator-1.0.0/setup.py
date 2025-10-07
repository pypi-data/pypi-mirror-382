#!/usr/bin/env python3
"""
Setup script for bifidoAnnotator
"""

from setuptools import setup, find_packages
import os

# Read README for long description
def get_long_description():
    if os.path.exists('README.md'):
        with open('README.md', 'r', encoding='utf-8') as f:
            return f.read()
    return "Complete pipeline for bifidobacterial enzymes annotation"

# Package data - only small files (database downloaded from Zenodo)
package_data = {
    'bifidoannotator': [
        'data/mapping_file.txt'
        # Database excluded - downloaded from Zenodo on first run
    ]
}

setup(
    name="bifidoannotator",
    version="1.0.0",
    author="Nicholas Pucci & Daniel R. Mende",
    author_email="n.pucci@amsterdamumc.nl",
    description="Fine-grained annotation of bifidobacterial glycoside hydrolases",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/nicholaspucci/bifidoAnnotator",
    packages=find_packages(),
    package_data=package_data,
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pandas>=1.0.0",
        "numpy>=1.18.0", 
        "matplotlib>=3.3.0",
        "seaborn>=0.11.0",
        "scipy>=1.5.0",
        # Note: mmseqs2 must be installed separately (available via conda)
    ],
    entry_points={
        'console_scripts': [
            'bifidoAnnotator=bifidoannotator.cli:main',
        ],
    },
    zip_safe=False,
)
