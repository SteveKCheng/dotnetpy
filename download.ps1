# PowerShell script for HTTP download
# for Windows systems with corporate HTTP proxies
param ([Parameter(Mandatory=$true)][string]$url, [Parameter(Mandatory=$true)][string]$file)
$ErrorActionPreference = "Stop"
$client = New-Object System.Net.WebClient
$client.UseDefaultCredentials = $true
$client.Proxy = [System.Net.WebRequest]::GetSystemWebProxy()
$client.DownloadFile($url, $file)
