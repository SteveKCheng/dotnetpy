dotnetpy
========

This module allows Python code to invoke .NET functions using the hosting API of .NET Core.

How it works
------------

This module launches and controls the .NET Core run-time by invoking its C-based hosting 
API through Python's [``ctypes``](https://docs.python.org/3.7/library/ctypes.html) module.
It wraps a subset of that API into a slightly higher-level interface, but 
does not attempt to solve the more difficult problem of passing richly-structured data 
and objects between Python and .NET.  .NET functions can only be called through a C-based interface 
using function pointers and standard C types like integers and pointers, in the same manner one uses 
[``Marshal.GetFunctionPointerForDelegate``](https://docs.microsoft.com/en-us/dotnet/api/system.runtime.interopservices.marshal.getfunctionpointerfordelegate?view=netcore-3.1) to call between .NET and C/C++.  

On top of the raw C call interface, the user can choose to layer any kind of structure
formatting or message serialization to pass more complex data.  It should also be
possible to get .NET code to work with Python objects by calling CPython's API
through [P/Invoke](https://docs.microsoft.com/en-us/dotnet/standard/native-interop/pinvoke).

Example
-------

After compiling the [example C# source code](example/CSharpExample/LibraryFunctions.cs), running ``test.py`` results in:

    > python test.py
    Hello world! 世界に挨拶します　argPtr=0 argSize=0

Supported platforms
-------------------

   * Python 3.7+
   * .NET Core 3.1+
   * Windows or Linux

This module does not work with Python 2.7 or the older (Windows-only) .NET Framework.

Limitations
-----------

   * Despite the object-oriented interface, you cannot launch multiple instances of
     a .NET Core run-time.  This is a limitation of .NET Core itself, even though
     its ``hostfxr`` API takes in handles to specify “host initialization contexts”.
     If you create more than one “host initialization contexts”, all of them will
     be linked together, and they cannot actually be set to use different run-time
     parameters.  

     Fortunately, in most situation a single .NET run-time is desirable.  Imagine
     you have two Python modules that do not know about each other, but both
     call upon .NET code.  If they both started their own run-times, your process
     will have two copies of .NET framework libraries loaded, two     
     garbage collectors running in background threads, etc.

     .NET Core does provide some degree of isolation between different “components”
     through its [Assembly Load Contexts](https://docs.microsoft.com/en-us/dotnet/core/dependency-loading/understanding-assemblyloadcontext).  The same process may run more than one
     component that deploy different versions of the same third-party dependency,
     e.g. the Newtonsoft JSON library.  _dotnetpy_ exposes the control over the assembly 
     load context that the ``hostfxr`` API provides.

   * You cannot launch “managed applications”, only “managed components”
     through _dotnetpy_.  “Managed applications” refer to programs having a ``Main`` 
     function taking a list of string arguments.  
     
     The ``hostfxr`` API only allows running one application in the whole process: 
     the functionality is useful only if the whole process is to be basically just 
     that one program.  If you do need to run managed applications, you are better off 
     just launching them as separate processes.

   * You cannot retrieve [COM](https://docs.microsoft.com/en-us/windows/win32/com/component-object-model--com--portal) interface pointers through _dotnetpy_, even though
     ``hostfxr`` supports doing so.  Clearly such functionality would only work on
     Windows, and it is not idiomatic at all to use COM from Python, 
     so this author has not deemed it worth the effort.  
     
     You can always activate .NET Core-authored COM components using its built-in 
     COM hosting and the ``pythoncom`` module, without going through _dotnetpy_.

Relevant technical information on .NET Core
-------------------------------------------

   * [.NET Core GitHub: design for native hosting](https://github.com/dotnet/runtime/blob/3b5a51a297c8fe2ea1780adbfdbb5ae6cf48b18a/docs/design/features/native-hosting.md)
   * [.NET Core GitHub: support custom hosting a hybrid between an application and a component](https://github.com/dotnet/runtime/issues/35465): background on how ``hostfxr`` works
   * [.NET Core GitHub: ``hostfxr.h`` header file](https://github.com/dotnet/runtime/blob/master/src/installer/corehost/cli/hostfxr.h)
   * [.NET Core guide: Write a custom .NET Core host to control the .NET runtime from your native code](https://docs.microsoft.com/en-us/dotnet/core/tutorials/netcore-hosting)
   * [.NET Core GitHub: summary of older hosting APIs](https://github.com/dotnet/runtime/blob/4f9ae42d861fcb4be2fcd5d3d55d5f227d30e723/docs/design/features/hosting-layer-apis.md)
   * [.NET Core GitHub: summary of AssemblyLoadContext](https://github.com/dotnet/coreclr/blob/master/Documentation/design-docs/assemblyloadcontext.md)
   * [Deep dive into .NET Core primitives: ``deps.json``, ``runtimeconfig.json``, and DLLs](https://natemcmaster.com/blog/2017/12/21/netcore-primitives/)
   * [.NET Core source code: ``Internal.Runtime.InteropServices.ComponentActivator.cs``](https://github.com/dotnet/runtime/blob/6072e4d3a7a2a1493f514cdf4be75a3d56580e84/src/coreclr/src/System.Private.CoreLib/src/Internal/Runtime/InteropServices/ComponentActivator.cs): what ``load_assembly_and_get_function_pointer`` really does
   * [.NET Core source code: ``hostpolicy/hostpolicy.cpp``](https://github.com/dotnet/runtime/blob/6072e4d3a7a2a1493f514cdf4be75a3d56580e84/src/installer/corehost/cli/hostpolicy/hostpolicy.cpp#L454): what ``get_runtime_delegate`` really does

