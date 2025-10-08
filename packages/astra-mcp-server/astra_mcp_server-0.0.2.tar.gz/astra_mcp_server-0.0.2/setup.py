#!/usr/bin/env python3
"""
Setup script for astra-mcp-server package.
This setup.py works alongside pyproject.toml for PyPI publishing.
"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return "Astra MCP Server"

# Read the LICENSE file
def read_license():
    license_path = os.path.join(os.path.dirname(__file__), "LICENSE")
    if os.path.exists(license_path):
        with open(license_path, "r", encoding="utf-8") as f:
            return f.read()
    return "MIT"

setup(
    name="astra-mcp-server",
    version="0.0.2",
    description="Astra MCP Server",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="Samuel Matioli",
    author_email="smatioli@gmail.com",
    maintainer="Samuel Matioli",
    maintainer_email="samuel.matioli@ibm.com",
    url="https://github.com/smatiolids/astra-mcp-server",
    project_urls={
        "Homepage": "https://github.com/smatiolids/astra-mcp-server",
        "Repository": "https://github.com/smatiolids/astra-mcp-server",
        "Issues": "https://github.com/smatiolids/astra-mcp-server/issues",
    },
    license=read_license(),
    license_files=["LICENSE"],
    keywords=["mcp", "astra", "datastax", "server"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Database",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
    ],
    python_requires=">=3.12",
    packages=find_packages(exclude=["tests*", "__pycache__*"]),
    py_modules=[
        "catalog",
        "database", 
        "load_tools",
        "logger",
        "run_tool",
        "server",
        "utils"
    ],
    install_requires=[
        "astrapy>=2.0.1",
        "fastmcp>=2.12.1",
        "python-dotenv>=1.1.1",
        "uvicorn[standard]>=0.30.0",
    ],
    extras_require={
        "dev": [
            "pytest>=8.4.2",
            "pytest-asyncio>=1.2.0",
            "build>=1.3.0",
            "twine>=6.2.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "astra-mcp-server=server:run_server",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    # Additional metadata for PyPI
    download_url="https://github.com/smatiolids/astra-mcp-server/archive/v0.0.1.tar.gz",
    platforms=["any"],
    # Ensure compatibility with modern Python packaging
    setup_requires=["setuptools>=45", "wheel"],
)
