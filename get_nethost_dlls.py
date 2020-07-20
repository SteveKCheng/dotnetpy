#!/usr/bin/env python3

import urllib.request
import argparse
import os
import os.path
import sys
import zipfile

default_nupkg_version="3.1.6"
default_nuget_url="https://www.nuget.org/api/v2/package/"

def download_nupkg(nuget_url: str, 
                   nupkg_name: str, 
                   nupkg_version: str, 
                   platform: str,
                   output_dir: str,
                   use_powershell: bool):

    url = f"{nuget_url}{nupkg_name}.{platform}/{nupkg_version}"
    nupkg_file = f"{nupkg_name}.{platform}.{nupkg_version}.nupkg"
    nupkg_path = os.path.join(output_dir, nupkg_file)

    if os.path.exists(nupkg_path):
        print(f"{nupkg_file} already exists")
        return nupkg_path

    print(f"Downloading {url} -> {nupkg_file}")

    if use_powershell:
        powershell_script = os.path.join(os.path.abspath(os.path.dirname(__file__)), "download.ps1")
        system_dir = os.environ.get("SystemRoot")
        powershell_exe = f"{system_dir}\\system32\\WindowsPowerShell\\v1.0\\powershell.exe"
        import subprocess
        args = [powershell_exe, 
                "-ExecutionPolicy", "Unrestricted",
                "-Command", powershell_script,
                '"%s"' % url , '"%s"' % nupkg_path]
        print(" ".join(args))
        p = subprocess.run(args)
        if p.returncode != 0:
            raise ValueError("Failure running PowerShell")

    else:
        urllib.request.urlretrieve(url, nupkg_path)

    return nupkg_path


def extract_dll(nupkg_file: str, platform: str):
    pass

def main():
    parser = argparse.ArgumentParser(description="Downloads and extracts the 'nethost' DLL for supported platforms of .NET Core. ")
    parser.add_argument("output_dir", metavar="DIR", type=str, 
                        help="Destination directory")
    parser.add_argument("--platform", "-p", dest='platform', nargs='*',
                        default=None,
                        help="Desired .NET Core runtime platform")
    parser.add_argument("--url", "-u", dest='nuget_url',
                        default=default_nuget_url,
                        help="URL of NuGet repository")
    parser.add_argument("--version", "-v", dest='nupkg_version', 
                        default=default_nupkg_version,
                        help="Desired version of the NuGet packages")
    
    if sys.platform == 'win32':
        parser.add_argument('--powershell', dest='use_powershell', action='store_true',
                            default=False,
                            help="Download files with PowerShell to work with corporate HTTP proxies")

    args = parser.parse_args()

    if args.platform is None:
        args.platform = [ "win-x64", "win-x86", "linux-x64" ]

    for platform in args.platform:
        platform: str
        nupkg_path = download_nupkg(args.nuget_url, 
                                    "Microsoft.NETCore.App.Host", 
                                    args.nupkg_version, 
                                    platform,
                                    args.output_dir,
                                    args.use_powershell if sys.platform == 'win32' else False)

        archive = zipfile.ZipFile(nupkg_path)

        dll_file = "nethost.dll" if platform.startswith("win-") else "libnethost.so"
        member_path = f"runtimes/{platform}/native/{dll_file}"

        subdir = f"{args.output_dir}/{platform}"
        try:
            os.mkdir(subdir)
        except FileExistsError:
            pass

        print(f"Extracting {member_path} to {subdir}/{dll_file}")
        member = archive.getinfo(member_path)
        member.filename = dll_file
        archive.extract(member, subdir)

if __name__ == '__main__':
    main()
