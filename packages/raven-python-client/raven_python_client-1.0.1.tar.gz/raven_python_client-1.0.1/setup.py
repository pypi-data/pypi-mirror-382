#!/usr/bin/env python3
"""Setup configuration for raven-python-client package."""

from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "A Python client library for the Raven Captcha API"

setup(
    name="raven-python-client",
    version="1.0.1",
    author="Raven Team",
    author_email="support@ravens.best",
    description="A Python client library for the Raven Captcha API with sync and async support",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/ravens-best/raven-python-client",
    project_urls={
        "Bug Tracker": "https://github.com/ravens-best/raven-python-client/issues",
        "Documentation": "https://ai.ravens.best/docs",
        "Source Code": "https://github.com/ravens-best/raven-python-client",
        "Homepage": "https://ai.ravens.best",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Security",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Typing :: Typed",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.28.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=22.0.0",
            "mypy>=1.0.0",
            "flake8>=5.0.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
    keywords=[
        "captcha",
        "recaptcha",
        "google",
        "automation",
        "api",
        "client",
        "async",
        "sync",
        "raven",
        "solver",
    ],
    license="MIT",
    zip_safe=False,
    include_package_data=True,
    package_data={
        "raven": ["py.typed"],
    },
)