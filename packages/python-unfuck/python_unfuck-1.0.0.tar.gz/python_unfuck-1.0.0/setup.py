#!/usr/bin/env python3
"""
unfuck - The magical Python error fixing tool
Because life's too short to debug 🚀
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="python-unfuck",
    version="1.0.0",
    author="Sherin Joseph",
    author_email="sherin.joseph2217@gmail.com",
    description="The magical Python error fixing tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Sherin-SEF-AI/unfuck",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Debuggers",
        "Topic :: Software Development :: Quality Assurance",
    ],
    python_requires=">=3.8",
    install_requires=[
        "colorama>=0.4.4",
        "rich>=13.0.0",
        "click>=8.0.0",
    ],
    extras_require={
        "ai": [
            "ollama>=0.1.0",
            "requests>=2.25.0",
        ],
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.10.0",
            "black>=21.0.0",
            "flake8>=3.8.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "unfuck=unfuck.cli:main",
        ],
    },
    keywords="python debug error fix automation tool",
    project_urls={
        "Bug Reports": "https://github.com/Sherin-SEF-AI/unfuck/issues",
        "Source": "https://github.com/Sherin-SEF-AI/unfuck",
        "Documentation": "https://github.com/Sherin-SEF-AI/unfuck#readme",
        "LinkedIn": "https://www.linkedin.com/in/sherin-roy-deepmost/",
    },
)
