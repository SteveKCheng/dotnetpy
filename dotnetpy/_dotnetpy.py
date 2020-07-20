import ctypes
import sys 
import os.path
from typing import Optional, Sequence

class DotNetHostError(Exception):
    def __init__(self, error_code, message):
        self.error_code = error_code
        self.message = message

is_64bit = (ctypes.sizeof(ctypes.c_void_p) == 8)

if sys.platform == 'win32': 
    windll = ctypes.windll 
    cdll = ctypes.cdll 

    nethost_dll_name = "nethost.dll"
    nethost_platform = "win-x64" if is_64bit else "win-x86"

    c_tchar_p = ctypes.c_wchar_p 
    c_tstring = c_tchar_p 

    def to_tstring(s):
        return s

    def create_tstring_buffer(init_or_size): 
        return ctypes.create_unicode_buffer(init_or_size) 

else: 
    # There is no "stdcall" on Unix; the .NET Core API  just revert 
    # to "cdecl calling" convention then. 
    windll = ctypes.cdll 
    cdll = ctypes.cdll 

    nethost_dll_name = "libnethost.so"
    nethost_platform = "linux-x64"

    if not is_64bit:
        raise ValueError("Unsupported platform for .NET Core")

    c_tchar_p = ctypes.c_char_p 

    def to_tstring(s): 
        return s.encode('utf-8') 

    def create_tstring_buffer(init_or_size): 
        if isinstance(init_or_size, str):
            init_or_size = to_tstring(init_or_size)
        return ctypes.create_string_buffer(init_or_size) 

def _c_int_error_check(result: ctypes.c_int, func, arguments): 
    if result != 0: 
        raise DotNetHostError(result, "API call failed")

class get_hostfxr_parameters(ctypes.Structure): 
    _fields_ =  [("size", ctypes.c_size_t), 
                 ("assembly_path", c_tchar_p), 
                 ("dotnet_root", c_tchar_p)] 


class hostfxr_initialize_parameters(ctypes.Structure): 
    _fields_ =  [("size", ctypes.c_size_t), 
                 ("host_path", c_tchar_p), 
                 ("dotnet_root", c_tchar_p)] 

class StatusCode: 
    Success                             = 1
    Success_HostAlreadyInitialized      = 2
    Success_DifferentRuntimeProperties  = 3

    # Failure 
    InvalidArgFailure                   = -2147450750 + 1 
    CoreHostLibLoadFailure              = -2147450750 + 2 
    CoreHostLibMissingFailure           = -2147450750 + 3 
    CoreHostEntryPointFailure           = -2147450750 + 4 
    CoreHostCurHostFindFailure          = -2147450750 + 5 
    #  unused                           = -2147450750 + 6
    CoreClrResolveFailure               = -2147450750 + 7 
    CoreClrBindFailure                  = -2147450750 + 8 
    CoreClrinitFailure                  = -2147450750 + 9 
    CoreClrExeFailure                   = -2147450750 + 10 
    ResolverInitFailure                 = -2147450750 + 11 
    ResolverResolveFailure              = -2147450750 + 12 
    LibHostCurExeFindFailure            = -2147450750 + 13 
    LibHostInitFailure                  = -2147450750 + 14 
    #  unused                           = -2147450750 + 15 
    LibHostExecModeFailure              = -2147450750 + 16 
    LibHostSdkFindFailure               = -2147450750 + 17 
    LibHostInvalidArgs                  = -2147450750 + 18 
    InvalidConfigFile                   = -2147450750 + 19 
    AppArgNotRunnable                   = -2147450750 + 20 
    AppHostExeNotBoundFailure           = -2147450750 + 21 
    FrameworkMissingFailure             = -2147450750 + 22 
    HostApiFailed                       = -2147450750 + 23 
    HostApiBufferTooSmall               = -2147450750 + 24 
    LibHostUnknownCommand               = -2147450750 + 25 
    LibHostAppRootFindFailure           = -2147450750 + 26 
    SdkResolverResolveFailure           = -2147450750 + 27 
    FrameworkCompatFailure              = -2147450750 + 28 
    FrameworkCompatRetry                = -2147450750 + 29 
    #  unused                           = -2147450750 + 30 
    BundleExtractionFailure             = -2147450750 + 31 
    BundleExtractionI0Error             = -2147450750 + 32 
    LibHostDuplicateProperty            = -2147450750 + 33 
    HostApiUnsupportedVersion           = -2147450750 + 34 
    HostInvalidState                    = -2147450750 + 35 
    HostPropertyNotFound                = -2147450750 + 36 
    CoreHostIncompatibleConfig          = -2147450750 + 37 
    HostApiUnsupportedScenario          = -2147450750 + 38 


class hostfxr_delegate_type: 
    hdt_com_activation = 0 
    hdt_load_in_memory_assembly = 1 
    hdt_winrt_activation = 2 
    hdt_com_register = 3 
    hdt_com_unregister = 4 
    hdt_load_assembly_and_get_function_pointer = 5 


c_hostfxr_handle = ctypes.c_void_p 


load_assembly_and_get_function_pointer_fn = \
   ctypes.WINFUNCTYPE (ctypes.c_int, 
                       c_tchar_p,         # assembly path 
                       c_tchar_p,         # type_name 
                       c_tchar_p,         # method_name 
                       c_tchar_p,         # delegate_type name, 
                       ctypes.c_void_p,   # reserved 
                       ctypes.POINTER(ctypes.c_void_p))  # OUT delegate 

component_entry_point_fn = \
   ctypes.WINFUNCTYPE(ctypes.c_int, 
                      ctypes.c_void_p, 
                      ctypes.c_int) 

_g_nethost = None 


class DotNetSession(): 

    @classmethod 
    def _get_nethost_dll(cls):
        """
        Get the ctypes object for the "nethost" DLL.  This DLL
        discovers installations of .NET Core.

        The "nethost" DLL should be packaged together with this Python module,
        for each supported platform of .NET Core.
        """

        global _g_nethost 
        nethost = _g_nethost 

        if nethost is None: 
            nethost_dll_path = os.path.join(os.path.dirname(__file__), nethost_platform, nethost_dll_name)
            nethost = windll.LoadLibrary(nethost_dll_path) 

        f = nethost.get_hostfxr_path 
        f.errcheck = _c_int_error_check 
        f.restype = ctypes.c_int 
        f.argtypes = [ c_tchar_p, 
                       ctypes.POINTER(ctypes.c_size_t), 
                       ctypes.POINTER(get_hostfxr_parameters) ] 

        _g_nethost = nethost 
        return nethost 

    @classmethod 
    def get_dll_path(cls) -> str:
        """
        Get the location of a "hostfxr" DLL for some installation
        of .NET Core.

        This location is discovered using the "nethost" DLL.
        """

        nethost = DotNetSession._get_nethost_dll() 

        pathBuf = create_tstring_buffer (4096) 
        pathBufLen = ctypes.c_size_t(len(pathBuf)) 

        nethost.get_hostfxr_path(pathBuf,  pathBufLen, None) 
        return pathBuf.value 

    @classmethod
    def _get_hostfxr_dll(cls, path: str):
        # hostfxr is cdecl even on Windows 
        hostfxr = cdll.LoadLibrary(path) 
 
        # See https://github.com/dotnet/runtime/blob/master/src/installer/corehost/cli/hostfxr.h 
 
        f = hostfxr.hostfxr_initialize_for_runtime_config 
        f.errcheck = _c_int_error_check 
        f.restype = ctypes.c_int 
        f.argtypes = [ c_tchar_p,                                       # runtime_config_path 
                       ctypes.POINTER(hostfxr_initialize_parameters), 
                       ctypes.POINTER(c_hostfxr_handle) ]               # OUT host_context_handle 
 
        f = hostfxr.hostfxr_get_runtime_property_value 
        f.errcheck = _c_int_error_check 
        f.restype = ctypes.c_int 
        f.argtypes = [ c_hostfxr_handle,            # host_context_handle 
                       c_tchar_p,                   # name 
                       ctypes.POINTER(c_tchar_p)]   # OUT value 
 
        f = hostfxr.hostfxr_set_runtime_property_value 
        f.errcheck = _c_int_error_check 
        f.restype = ctypes.c_int 
        f.argtypes = [ c_hostfxr_handle,            # host_context_handle 
                       c_tchar_p,                   # name 
                       c_tchar_p]                   # value 
 
        f = hostfxr.hostfxr_get_runtime_properties 
        f.errcheck = _c_int_error_check 
        f.restype = ctypes.c_int 
        f.argtypes =  [ c_hostfxr_handle,                   # host_context_handle 
                       ctypes.POINTER(ctypes.c_size_t),     # IN/OUT count 
                       ctypes.POINTER(c_tchar_p),           # OUT keys 
                       ctypes.POINTER(c_tchar_p) ]          # OUT values 
 
        f = hostfxr.hostfxr_get_runtime_delegate 
        f.errcheck = _c_int_error_check 
        f.restype = ctypes.c_int 
        f.argtypes = [ c_hostfxr_handle,             # host_context_handle 
                       ctypes.c_int,                 # enum hostfxr_delegate_ type 
                       ctypes.POINTER(ctypes.c_void_p)] # OUT void**  delegate 
 
        f = hostfxr.hostfxr_close 
        f.errcheck = _c_int_error_check 
        f.restype = ctypes.c_int 
        f.argtypes = [ c_hostfxr_handle ] 

        return hostfxr


    def __init__(self, 
                 config_path: Optional[str] = None,
                 host_path: Optional[str] = None,
                 dotnet_root: Optional[str] = None,
                 dll_path: Optional[str] = None):

        self._hostfxr_handle = None

        if dll_path is None: 
            dll_path = DotNetSession.get_dll_path() 

        self._dll = DotNetSession._get_hostfxr_dll(dll_path)

        parameters = None
        if host_path is not None or dotnet_root is not None:
            parameters = hostfxr_initialize_parameters()
            parameters.size = ctypes.sizeof(hostfxr_initialize_parameters)
            if host_path is not None:
                parameters.host_path = create_tstring_buffer(host_path)
            if dotnet_root is not None:
                parameters.dotnet_root = create_tstring_buffer(dotnet_root)

        handle = c_hostfxr_handle()
        self._dll.hostfxr_initialize_for_runtime_config(
            to_tstring(config_path),
            parameters,
            handle
        )

        self._hostfxr_handle = handle
        self._load_assembly_and_get_function_pointer = None

    def __del__(self):
        handle = self._hostfxr_handle
        if handle is not None:
            self._hostfxr_handle = None
            self._dll.hostfxr_close(handle)

    def load_assembly_and_get_function_pointer( 
            self, 
            assembly_path: str, 
            type_name: str, 
            method_name: str, 
            delegate_name: Optional[str] = None): 

        delegate = ctypes.c_void_p() 

        f = self._load_assembly_and_get_function_pointer
        if f is None:
            f = ctypes.c_void_p()
            self._dll.hostfxr_get_runtime_delegate( 
                self._hostfxr_handle, 
                hostfxr_delegate_type.hdt_load_assembly_and_get_function_pointer, 
                f) 
            f = ctypes.cast(f, load_assembly_and_get_function_pointer_fn) 
            self._load_assembly_and_get_function_pointer = f

        delegate = ctypes.c_void_p()
        err = f(assembly_path, type_name, method_name, delegate_name, None, delegate) 
        if err < 0: 
            raise ValueError("load_assembly_and_get_function_pointer failed") 

        if delegate_name is None: 
            delegate = ctypes.cast(delegate, component_entry_point_fn) 

        return delegate 

    def get_runtime_properties(self): 
        capacity = 4096 
        keys_array = (c_tchar_p * capacity)() 
        values_array = (c_tchar_p * capacity)() 
        count = ctypes.c_size_t(capacity) 
        self._dll.hostfxr_get_runtime_properties(self._hostfxr_handle, 
                                                 count, 
                                                 keys_array, 
                                                 values_array) 

        return [ (keys_array[i], values_array[i]) \
                 for i in range(count.value) ] 

