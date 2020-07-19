#!/usr/bin/env python3
import setuptools

setuptools.setup(
    name="dotnetpy",
    version="0.0.1",
    author="Steve Cheng",
    author_email="steve.ckp@gmail.com",
    description="Runs a .NET Core host under the control of Python code",
    url="https://github.com/SteveKCheng/dotnetpy",
    packages=setuptools.find_packages(),
    classifiers=[
       "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
