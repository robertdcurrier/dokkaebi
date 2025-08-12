#!/usr/bin/env python3
"""
DOKKAEBI Setup Script

Installs the DOKKAEBI algorithmic trading platform with HebbNet.
Includes the bulletproof price downloader CLI.

Viper's installation script - fucking flawless deployment.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read requirements
requirements = []
requirements_file = Path(__file__).parent / "requirements.txt"
if requirements_file.exists():
    with open(requirements_file, 'r') as f:
        requirements = [
            line.strip() for line in f 
            if line.strip() and not line.startswith('#')
        ]

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = ""
if readme_file.exists():
    with open(readme_file, 'r', encoding='utf-8') as f:
        long_description = f.read()

setup(
    name="dokkaebi",
    version="1.0.0",
    description="DOKKAEBI - Algorithmic trading platform with HebbNet",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Viper - The PEP-8 Code Warrior",
    author_email="viper@dokkaebi.ai",
    url="https://github.com/dokkaebi/dokkaebi",
    
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    
    install_requires=requirements,
    
    python_requires=">=3.11",
    
    entry_points={
        'console_scripts': [
            'dokkaebi=main:main',
            'dokkaebi-prices=price_downloader.cli:cli',
        ],
    },
    
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial :: Investment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    
    keywords="algorithmic trading, neural networks, hebbnet, finance, stocks",
    
    project_urls={
        "Bug Reports": "https://github.com/dokkaebi/dokkaebi/issues",
        "Source": "https://github.com/dokkaebi/dokkaebi",
        "Documentation": "https://dokkaebi.readthedocs.io/",
    },
    
    include_package_data=True,
    zip_safe=False,
)