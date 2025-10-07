from setuptools import setup, find_packages
import os
import sys
import glob
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

def get_install_requires():
    return []

setup(
    name="acce",
    version="1.0.1",
    author="Programmer Seo Hook : @LAEGER_MO : @sis_c",
    author_email="",
    description="مكتبة acce للطباعة",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7", 
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=2.7",
    entry_points={
        'console_scripts': [
            'acce-install=acce.installer:main',
            'acce-setup=acce.installer:install_all_versions',
        ],
    },
    include_package_data=True,
    install_requires=get_install_requires(),
)