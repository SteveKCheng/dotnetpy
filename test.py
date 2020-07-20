from dotnetpy import DotNetSession
import os.path
import sys

this_dir = os.path.dirname(__file__)

assembly_path = os.path.join(this_dir, "example/CSharpExample/bin/Debug/CSharpExample.dll")
if not os.path.exists(assembly_path):
    print(f"{assembly_path} not found; please compile the .NET assembly first", file=sys.stderr)
    sys.exit(2)

session = DotNetSession(config_path=os.path.join(this_dir, "example/DotNetRuntimeConfig.json"))

properties = session.get_runtime_properties()
for key, value in properties: 
    print("%s = %s" % (key, value)) 

my_function = session.load_assembly_and_get_function_pointer( 
    assembly_path,
    "CSharpExample.LibraryFunctions, CSharpExample", 
    r"PrintHelloWorld", 
    None) 

my_function(None, 0) 
