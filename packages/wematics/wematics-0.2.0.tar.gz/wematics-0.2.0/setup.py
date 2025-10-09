from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="wematics",  
    version="0.2.0",              # Major bug fix - updated from 0.1.3
    author="Wematics",
    author_email="info@wematics.com",
    description="A client library for Wematics sky cameras",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(), 
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "requests", 
        "tqdm",
        "timezonefinder",
    ],
    python_requires='>=3.6',
)