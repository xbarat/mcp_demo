"""
Setup script for SQLite MCP Client.
"""
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as f:
    requirements = f.read().splitlines()

setup(
    name="sqlite-mcp-client",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A client for interacting with SQLite MCP Server",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/sqlite_client",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "sqlite-mcp-client=src.client_sqlite:main",
        ],
    },
) 