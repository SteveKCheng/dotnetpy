# PowerShell script for HTTP download
# for Windows systems with corporate HTTP proxies
param ([Parameter(Mandatory=$true)][string]$url, [Parameter(Mandatory=$true)][string]$file)

$ErrorActionPreference = "Stop"

$client = New-Object System.Net.WebClient

$client.Proxy = [System.Net.WebRequest]::GetSystemWebProxy()
$client.Proxy.Credentials = [System.Net.CredentialCache]::DefaultNetworkCredentials

# Force TLS 1.2 for badly implemented proxies
if ($client.Proxy.GetProxy($url))
{
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12
}

$client.DownloadFile($url, $file)
