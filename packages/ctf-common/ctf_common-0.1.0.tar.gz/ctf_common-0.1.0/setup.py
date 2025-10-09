from setuptools import setup, find_packages

setup(
    name="ctf_common",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "pyyaml>=6.0.1",
    ],
    author="Joanney Wang",
    author_email="wcyan1013@qq.com",
    description="Common library for CTF projects",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/joanne-cyw/ctf_common",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)