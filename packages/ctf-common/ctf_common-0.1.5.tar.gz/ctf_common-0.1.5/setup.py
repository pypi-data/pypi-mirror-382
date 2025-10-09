from setuptools import setup, find_packages
import codecs
import os

def read_readme():
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        return f.read()

setup(
    name="ctf_common",
    version="0.1.5",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "pyyaml>=6.0.1",
    ],
    author="Joanney Wang",
    author_email="joanne.cyw@hotmail.com",
    description="Common library for CTF projects",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/joanne-cyw/ctf_common",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)