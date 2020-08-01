#!/usr/bin/env python3
import setuptools
import sys
from wheel.pep425tags import get_platform
from wheel.bdist_wheel import bdist_wheel

# Determine relative file path for nethost DLL
# depending on platform
is_64bit = (sys.maxsize > 2**32)
if sys.platform == 'win32':
    binary_subdir = "win-x64" if is_64bit else "win-x86"
    nethost_dll = f"{binary_subdir}/nethost.dll"
elif sys.platform == 'linux' and is_64bit:
    binary_subdir = "linux-x64"
    nethost_dll = f"{binary_subdir}/libnethost.so"
else:
    raise NotImplementedError("Unsupported platform for dotnetpy")

# See https://stackoverflow.com/questions/45150304/how-to-force-a-python-wheel-to-be-platform-specific-when-building-it
# and source code of wheel.bdist_wheel.bdist_wheel.get_tag.
# PEP425 explains how platform/ABI tagging is supposed to work.
class my_bdist_wheel(bdist_wheel):
    """
    Monkey-patch bdist_wheel so that the resulting
    package is always platform-specific, but has no ABI
    dependency on the Python implementation.  We need
    to include native DLLs/shared objects but they have
    nothing to do with Python.
    """
    def get_tag(self):
        return ('py3', 'none', 
                self.plat_name if self.plat_name_supplied \
                               else get_platform(self.bdist_dir))

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
        "Programming Language :: C#",
        "Programming Language :: F#",
        "Programming Language :: Visual Basic",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3.6",
    package_data={"dotnetpy": [ nethost_dll ]},
    cmdclass={"bdist_wheel": my_bdist_wheel},
    zip_safe=False,
)
