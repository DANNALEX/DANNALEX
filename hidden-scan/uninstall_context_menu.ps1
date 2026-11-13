# uninstall_context_menu.ps1 — Dezinstalează complet opțiunile Clic-Dreapta din Windows Explorer
param(
    [switch]$RestartExplorer
)

$ErrorActionPreference = "SilentlyContinue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "  DEZINSTALARE MENIU CLIC-DREAPTA (Scanare si Stergere Metadate - hidden-scan)" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

$DeletedCount = 0

# 1. Chei specifice cunoscute in HKCU
$KnownPaths = @(
    "HKCU:\Software\Classes\*\shell\HiddenScan_1_Clean",
    "HKCU:\Software\Classes\*\shell\HiddenScan_2_Scan",
    "HKCU:\Software\Classes\Directory\shell\HiddenScan_1_CleanDir",
    "HKCU:\Software\Classes\Directory\shell\HiddenScan_2_ScanDir",
    "HKCU:\Software\Classes\Directory\Background\shell\HiddenScan_1_CleanBg",
    "HKCU:\Software\Classes\Directory\Background\shell\HiddenScan_2_ScanBg",
    "HKCU:\Software\Classes\Folder\shell\HiddenScan_1_Clean",
    "HKCU:\Software\Classes\Folder\shell\HiddenScan_2_Scan",
    "HKCU:\Software\Classes\*\shell\AfiseazaStergeMetadate",
    "HKCU:\Software\Classes\Directory\shell\AfiseazaStergeMetadate",
    "HKCU:\Software\Classes\Directory\Background\shell\AfiseazaStergeMetadate"
)

foreach ($p in $KnownPaths) {
    if (Test-Path $p) {
        Remove-Item -Path $p -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host " [ELIMINAT] Cheie registru: $p" -ForegroundColor Green
        $DeletedCount++
    }
}

# 2. Căutare dinamică pentru orice alte chei legate de metadate / HiddenScan
$ShellLocations = @(
    "HKCU:\Software\Classes\*\shell",
    "HKCU:\Software\Classes\Directory\shell",
    "HKCU:\Software\Classes\Directory\Background\shell",
    "HKCU:\Software\Classes\Folder\shell"
)

foreach ($loc in $ShellLocations) {
    if (Test-Path $loc) {
        Get-ChildItem -Path $loc -ErrorAction SilentlyContinue | ForEach-Object {
            $keyName = $_.PSChildName
            $defaultVal = (Get-ItemProperty -Path $_.PSPath -Name "(Default)" -ErrorAction SilentlyContinue)."(Default)"
            $muiVal = (Get-ItemProperty -Path $_.PSPath -Name "MUIVerb" -ErrorAction SilentlyContinue)."MUIVerb"
            
            $isTarget = $false
            if ($keyName -like "*HiddenScan*" -or $keyName -like "*Metadate*" -or $keyName -like "*metadata*") {
                $isTarget = $true
            }
            if ($defaultVal -and ($defaultVal -like "*Metadate*" -or $defaultVal -like "*Date Ascunse*" -or $defaultVal -like "*hidden-scan*")) {
                $isTarget = $true
            }
            if ($muiVal -and ($muiVal -like "*Metadate*" -or $muiVal -like "*Date Ascunse*")) {
                $isTarget = $true
            }
            
            if ($isTarget) {
                Remove-Item -Path $_.PSPath -Recurse -Force -ErrorAction SilentlyContinue
                Write-Host " [ELIMINAT] Cheie registru suplimentară: $($_.PSPath)" -ForegroundColor Green
                $DeletedCount++
            }
        }
    }
}

# 3. Verificare HKLM (dacă a fost rulat cândva cu drepturi de Administrator)
$HklmLocations = @(
    "HKLM:\Software\Classes\*\shell",
    "HKLM:\Software\Classes\Directory\shell",
    "HKLM:\Software\Classes\Directory\Background\shell"
)
foreach ($loc in $HklmLocations) {
    if (Test-Path $loc) {
        Get-ChildItem -Path $loc -ErrorAction SilentlyContinue | ForEach-Object {
            if ($_.PSChildName -like "*HiddenScan*") {
                Remove-Item -Path $_.PSPath -Recurse -Force -ErrorAction SilentlyContinue
                Write-Host " [ELIMINAT HKLM] $($_.PSPath)" -ForegroundColor Green
                $DeletedCount++
            }
        }
    }
}

# 4. Eliminare scurtături din SendTo
$SendToDir = [Environment]::GetFolderPath("SendTo")
if ($SendToDir -and (Test-Path $SendToDir)) {
    Get-ChildItem -Path $SendToDir -Filter "*Metadate*.lnk" -ErrorAction SilentlyContinue | ForEach-Object {
        Remove-Item $_.FullName -Force -ErrorAction SilentlyContinue
        Write-Host " [ELIMINAT] Scurtătură SendTo: $($_.Name)" -ForegroundColor Green
        $DeletedCount++
    }
    Get-ChildItem -Path $SendToDir -Filter "*hidden-scan*.lnk" -ErrorAction SilentlyContinue | ForEach-Object {
        Remove-Item $_.FullName -Force -ErrorAction SilentlyContinue
        Write-Host " [ELIMINAT] Scurtătură SendTo: $($_.Name)" -ForegroundColor Green
        $DeletedCount++
    }
}

# 5. Eliminare scurtături de pe Desktop (dacă există)
$DesktopDir = [Environment]::GetFolderPath("Desktop")
if ($DesktopDir -and (Test-Path $DesktopDir)) {
    Get-ChildItem -Path $DesktopDir -Filter "*Metadate*.lnk" -ErrorAction SilentlyContinue | ForEach-Object {
        Remove-Item $_.FullName -Force -ErrorAction SilentlyContinue
        Write-Host " [ELIMINAT] Scurtătură Desktop: $($_.Name)" -ForegroundColor Green
        $DeletedCount++
    }
}

Write-Host ""
Write-Host "============================================================================" -ForegroundColor Green
Write-Host "  DEZINSTALARE MENIU FINALIZATĂ!" -ForegroundColor Green
Write-Host "  Intrările pentru metadate au fost eliminate din meniul Clic-Dreapta." -ForegroundColor Green
Write-Host "============================================================================" -ForegroundColor Green

if ($RestartExplorer) {
    Write-Host "Se repornește Windows Explorer pentru aplicarea imediată..." -ForegroundColor Cyan
    Stop-Process -Name explorer -Force -ErrorAction SilentlyContinue
    Start-Process explorer.exe
    Write-Host "[OK] Windows Explorer a fost repornit." -ForegroundColor Green
}
