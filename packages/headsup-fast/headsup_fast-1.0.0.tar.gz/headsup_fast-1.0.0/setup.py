#!/usr/bin/env python

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="headsup-fast",
    version="1.0.0",
    author="Ahmad Alam",
    author_email="ahmadalam@outlook.com",
    description="A trivial alternative to Ubuntu's landscape-info with no external dependencies",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ahmadalam/headsup-fast",
    py_modules=["headsup"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: System :: Systems Administration",
        "Topic :: System :: Monitoring",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "headsup=headsup:main",
        ],
    },
    keywords="system monitoring motd landscape ubuntu linux sysinfo",
    project_urls={
        "Bug Reports": "https://github.com/ahmadalam/headsup-fast/issues",
        "Source": "https://github.com/ahmadalam/headsup-fast",
    },
)
