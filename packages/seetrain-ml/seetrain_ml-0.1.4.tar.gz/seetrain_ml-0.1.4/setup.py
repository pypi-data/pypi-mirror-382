#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SeeTrain 深度学习实验跟踪和框架集成工具
"""

from setuptools import setup, find_packages
import os

# 读取README文件
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "SeeTrain - 深度学习实验跟踪和框架集成工具"

# 读取requirements.txt
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="seetrain-ml",
    version="0.1.4",
    author="SeeTrain Team",
    author_email="seetrain@example.com",
    description="深度学习实验跟踪和框架集成工具",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/seetrain/seetrain",
    project_urls={
        "Bug Reports": "https://github.com/seetrain/seetrain/issues",
        "Source": "https://github.com/seetrain/seetrain",
        "Documentation": "https://seetrain.readthedocs.io/",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "flake8",
            "mypy",
        ],
        "docs": [
            "sphinx",
            "sphinx-rtd-theme",
            "myst-parser",
        ],
    },
    entry_points={
        "console_scripts": [
            "seetrain=seetrain.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="deep learning, experiment tracking, pytorch, tensorflow, keras, mlflow, wandb",
)
