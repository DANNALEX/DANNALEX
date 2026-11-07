# uninstall_context_menu.ps1 — Dezinstalează opțiunile Clic-Dreapta din Windows Explorer
$ErrorActionPreference = "SilentlyContinue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$Paths = @(
    "HKCU:\Software\Classes\*\shell\HiddenScan_1_Clean",
    "HKCU:\Software\Classes\*\shell\HiddenScan_2_Scan",
    "HKCU:\Software\Classes\Directory\shell\HiddenScan_1_CleanDir",
    "HKCU:\Software\Classes\Directory\shell\HiddenScan_2_ScanDir",
    "HKCU:\Software\Classes\Directory\Background\shell\HiddenScan_1_CleanBg",
    "HKCU:\Software\Classes\Directory\Background\shell\HiddenScan_2_ScanBg"
)

foreach ($p in $Paths) {
    if (Test-Path $p) {
        Remove-Item -Path $p -Recurse -Force
    }
}

$SendToLnk = Join-Path ([Environment]::GetFolderPath("SendTo")) "Șterge Metadate (hidden-scan).lnk"
if (Test-Path $SendToLnk) { Remove-Item $SendToLnk -Force }

Write-Host "[OK] Intrările din meniul Clic-Dreapta au fost eliminate." -ForegroundColor Yellow
