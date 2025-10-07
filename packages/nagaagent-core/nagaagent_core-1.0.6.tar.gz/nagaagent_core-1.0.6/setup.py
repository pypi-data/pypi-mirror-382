#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NagaAgent Core Package Setup
核心依赖包，包含核心功能和API服务器相关依赖
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="nagaagent-core",
    version="1.0.4",
    author="NagaAgent Team",
    author_email="nagaagent@example.com",
    description="NagaAgent核心依赖包，包含核心功能和API服务器相关依赖",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nagaagent/nagaagent-core",
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
    ],
    python_requires=">=3.8",
    install_requires=[
        # 核心依赖
        "mcp>=1.6.0",
        "openai>=1.76.0", 
        "python-dotenv>=1.1.0",
        "requests>=2.32.3",
        "aiohttp>=3.11.18",

        # API服务器相关依赖
        "flask>=3.1.0",
        "gevent>=25.5.1",
        "fastapi>=0.115.0",
        "uvicorn[standard]>=0.34.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-asyncio>=0.21.0",
            "black>=22.0",
            "flake8>=4.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "nagaagent-core=nagaagent_core.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
