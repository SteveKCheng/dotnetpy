from dotnetpy import HostFxr
import os.path
import sys

hostfxr = HostFxr() 

this_dir = os.path.dirname(__file__)

assembly_path = os.path.join(this_dir, "example/CSharpExample/bin/Debug/CSharpExample.dll")
if not os.path.exists(assembly_path):
    print(f"{assembly_path} not found; please compile the .NET assembly first", file=sys.stderr)
    sys.exit(2)

handle = hostfxr.initialize_for_runtime_config( 
            os.path.join(this_dir, "example/DotNetRuntimeConfig.json"),
            None) 

properties = hostfxr.get_runtime_properties(handle) 
for key, value in properties: 
    print("%s = %s" % (key, value)) 

my_function = hostfxr.load_assembly_and_get_function_pointer( 
    handle, 
    assembly_path,
    "CSharpExample.LibraryFunctions, CSharpExample", 
    r"PrintHelloWorld", 
    None) 

my_function(None, 0) 

