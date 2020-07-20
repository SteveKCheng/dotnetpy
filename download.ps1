# PowerShell script for HTTP download
# for Windows systems with corporate HTTP proxies
param ([Parameter(Mandatory=$true)][string]$url, [Parameter(Mandatory=$true)][string]$file)
$ErrorActionPreference = "Stop"
$client = New-Object System.Net.WebClient
$client.Proxy = [System.Net.WebRequest]::GetSystemWebProxy()
$client.Proxy.Credentials = [System.Net.CredentialCache]::DefaultNetworkCredentials
$client.DownloadFile($url, $file)
