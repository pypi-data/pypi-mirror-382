"""
Setup script for the Kurdish Text Handler library
"""

from setuptools import setup, find_packages    # pyright: ignore[reportMissingModuleSource]

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="Kurdish_Characters",
    version="1.0.0",
    author="Kurdish Developer Community",
    author_email="neshwantaha@gmail.com",
    description="A Python library to properly display Kurdish characters in tkinter and other interfaces",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/neshwantaha/Kurdish_Characters",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Linguistic",
        # Removed invalid classifier "Natural Language :: Kurdish"
    ],
    python_requires=">=3.6",
    install_requires=[
        # No external dependencies required
    ],
    keywords="kurdish, text, tkinter, unicode, font, display",
)