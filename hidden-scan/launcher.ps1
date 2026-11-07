# launcher.ps1 — Lansator Clic-Dreapta pentru hidden-scan v3.0
param(
    [Parameter(Mandatory=$true)]
    [string]$Target,

    [ValidateSet("scan", "clean", "clean-inplace")]
    [string]$Mode = "clean"
)

$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$AppRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

# Găsește interpretorul Python
$PythonExe = $null
$Candidates = @(
    "$env:LOCALAPPDATA\Programs\Python\Python312\pythonw.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python311\pythonw.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python310\pythonw.exe"
)
foreach ($c in $Candidates) {
    if (Test-Path $c) {
        $PythonExe = $c
        break
    }
}
if (-not $PythonExe) {
    $cmd = Get-Command pythonw.exe -ErrorAction SilentlyContinue
    if ($cmd) { $PythonExe = $cmd.Source }
}
if (-not $PythonExe) {
    $cmd = Get-Command python.exe -ErrorAction SilentlyContinue
    if ($cmd) { $PythonExe = $cmd.Source }
}

if (-not $PythonExe) {
    Add-Type -AssemblyName PresentationFramework
    [System.Windows.MessageBox]::Show("Python nu a fost găsit pe acest sistem!", "Eroare hidden-scan", "OK", "Error")
    exit 1
}

$env:PYTHONPATH = $AppRoot

if ($Mode -eq "clean-inplace") {
    & $PythonExe -m hidden_scan.gui "$Target" --action clean --in-place
} elseif ($Mode -eq "clean") {
    & $PythonExe -m hidden_scan.gui "$Target" --action clean
} else {
    & $PythonExe -m hidden_scan.gui "$Target" --action scan
}
