#!/usr/bin/env python3
"""
aitoolkit_cam 修复版本安装脚本
"""

from setuptools import setup, find_packages
import os

# 读取版本号
version = "3.5.0"

# 读取README
readme_path = os.path.join(os.path.dirname(__file__), "README.md")
try:
    with open(readme_path, "r", encoding="utf-8") as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = "aitoolkit_cam 修复版本 - MJPEG流显示问题修复"

setup(
    name="aitoolkit-cam",
    version=version,
    author="Haitao Wang",
    author_email="dianx12@163.com",
    description="ARM摄像头工具包 v3.0 - 专为Jupyter环境和ARM设备优化，修复MJPEG流问题",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dianx12/aitoolkit-cam",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Multimedia :: Video :: Capture",
        "Topic :: Scientific/Engineering :: Image Processing",
    ],
    python_requires=">=3.8",
    install_requires=[
        "opencv-python-headless>=4.5.0",
        "numpy>=1.19.0",
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
        ],
        "jupyter": [
            "jupyter>=1.0.0",
            "ipython>=7.0.0",
            "matplotlib>=3.3.0",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="camera opencv arm jupyter fastapi mjpeg streaming",
    project_urls={
        "Bug Reports": "https://github.com/dianx12/aitoolkit-cam/issues",
        "Source": "https://github.com/dianx12/aitoolkit-cam",
        "Documentation": "https://github.com/dianx12/aitoolkit-cam/blob/main/README.md",
    },
)