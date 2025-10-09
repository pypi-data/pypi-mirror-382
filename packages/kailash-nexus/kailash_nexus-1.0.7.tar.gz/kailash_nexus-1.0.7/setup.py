"""Setup script for Kailash Nexus."""

from setuptools import find_packages, setup

setup(
    name="kailash-nexus",
    version="1.0.7",
    description="Multi-channel platform built on Kailash SDK",
    author="Integrum",
    author_email="info@integrum.com",
    license="Apache-2.0 WITH Additional-Terms",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "kailash>=0.9.21",
    ],
    python_requires=">=3.11",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
