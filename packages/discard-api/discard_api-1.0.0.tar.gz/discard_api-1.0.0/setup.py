"""
Discard Rest APIs Python SDK
Installation: pip install discard-api
"""

from setuptools import setup, find_packages

setup(
    name="discard-api",
    version="1.0.0",
    author="Qasim Ali",
    author_email="discardapi@gmail.com",
    description="Python SDK for Discard Rest APIs",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/GlobalTechInfo/discardapi-py",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
)
