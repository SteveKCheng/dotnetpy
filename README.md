dotnetpy
========

This module allows Python code to invoke .NET functions using the hosting API of .NET Core.

It does not do anything fundamentally different than what is described in Microsoft's documentation, 
“[Write a custom .NET Core host to control the .NET runtime from your native code](https://docs.microsoft.com/en-us/dotnet/core/tutorials/netcore-hosting)”.  Where Microsoft's example invokes the C-based hosting API from a C++ program, 
this module invokes the API using Python's [``ctypes``](https://docs.python.org/3.7/library/ctypes.html) module.

This module wraps the C-based hosting API at a slightly higher level, but does not attempt to solve the 
more difficult problem of passing richly-structured data and objects between Python and .NET.
 .NET functions can only be called through a C-based interface using function pointers
and standard C types like integers and pointers, in the same manner one uses 
[``Marshal.GetFunctionPointerForDelegate``](https://docs.microsoft.com/en-us/dotnet/api/system.runtime.interopservices.marshal.getfunctionpointerfordelegate?view=netcore-3.1) to call between .NET and C/C++.  

On top of the raw C call interface, the user can choose to layer any kind of structure
formatting or message serialization to pass more complex data.

Supported platforms
-------------------

   * Python 3.7+
   * .NET Core 3.1+
   * Windows or Linux

This module does not work with Python 2.7 or the older (Windows-only) .NET Framework.
