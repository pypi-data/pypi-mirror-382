#!/usr/bin/env python3
"""
Setup script for Memara Python SDK
Uses traditional setup.py to generate compatible metadata for PyPI
"""

from setuptools import setup, find_packages

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
install_requires = [
    "httpx>=0.24.0",
    "pydantic>=2.0.0",
]

dev_requires = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0", 
    "black>=23.7.0",
    "mypy>=1.4.1",
    "isort>=5.12.0",
    "httpx[dev]>=0.24.0",
]

setup(
    name="memara",
    version="0.1.0",
    description="Official Python SDK for the Memara API - Give your AI a perfect memory",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Memara Team",
    author_email="hello@memara.io",
    url="https://memara.io",
    project_urls={
        "Homepage": "https://memara.io",
        "Documentation": "https://memara.io/docs",
        "Repository": "https://github.com/memara-ai/memara-python-sdk",
        "Bug Tracker": "https://github.com/memara-ai/memara-python-sdk/issues",
        "Changelog": "https://github.com/memara-ai/memara-python-sdk/blob/main/CHANGELOG.md",
    },
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=install_requires,
    extras_require={
        "dev": dev_requires,
    },
    keywords=["ai", "memory", "api", "sdk", "artificial-intelligence", "llm", "gpt", "claude"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers", 
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    license="MIT",
)
