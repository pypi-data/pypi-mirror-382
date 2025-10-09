#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="simplesitesearch",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A simple Django app for site search functionality with Django CMS integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/simplesitesearch",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Framework :: Django",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
        "Framework :: Django :: 4.1",
        "Framework :: Django :: 4.2",
        "Framework :: Django :: 5.0",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "Django>=3.2",
        "django-cms>=3.2",
        "requests>=2.25.0",
    ],
    include_package_data=True,
    package_data={
        "simplesitesearch": [
            "templates/simplesitesearch/*.html",
        ],
    },
    zip_safe=False,
)
