#!/usr/bin/env python3
"""
PyTrading Toolkit Setup Script
"""

from setuptools import setup, find_packages
import os

# README 파일 읽기
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

# requirements.txt 읽기
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), '..', 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="pytrading-toolkit",
    version="1.1.0",
    author="SHY",
    author_email="yangoon81@gmail.com",
    description="Python 암호화폐 트레이딩 봇 개발을 위한 포괄적인 도구킷",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://pypi.org/project/pytrading-toolkit/",
    project_urls={
        "Bug Reports": "https://pypi.org/project/pytrading-toolkit/#issues",
        "Source": "https://pypi.org/project/pytrading-toolkit/",
        "Documentation": "https://pypi.org/project/pytrading-toolkit/",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
        "test": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-asyncio>=0.21.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "pytrading-config=pytrading_toolkit.tools.config_setup:main",
            "pytrading-manager=pytrading_toolkit.tools.multi_instance_manager:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="cryptocurrency trading bot upbit bybit binance technical analysis",
)