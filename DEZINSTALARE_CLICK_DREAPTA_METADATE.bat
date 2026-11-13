@echo off
chcp 65001 >nul
title Dezinstalare Meniu Clic-Dreapta - Afiseaza / Sterge Metadate
echo ============================================================================
echo   DEZINSTALARE AUTOMATA - MENIU CLIC-DREAPTA (Afiseaza / Sterge Metadate)
echo ============================================================================
echo.
echo [1/3] Se sterg cheile din Registrul Windows (HKCU si HKLM)...

:: 1. Stergere chei HKCU (Current User)
reg delete "HKCU\Software\Classes\*\shell\HiddenScan_1_Clean" /f >nul 2>&1
reg delete "HKCU\Software\Classes\*\shell\HiddenScan_2_Scan" /f >nul 2>&1
reg delete "HKCU\Software\Classes\*\shell\AfiseazaStergeMetadate" /f >nul 2>&1
reg delete "HKCU\Software\Classes\Directory\shell\HiddenScan_1_CleanDir" /f >nul 2>&1
reg delete "HKCU\Software\Classes\Directory\shell\HiddenScan_2_ScanDir" /f >nul 2>&1
reg delete "HKCU\Software\Classes\Directory\shell\AfiseazaStergeMetadate" /f >nul 2>&1
reg delete "HKCU\Software\Classes\Directory\Background\shell\HiddenScan_1_CleanBg" /f >nul 2>&1
reg delete "HKCU\Software\Classes\Directory\Background\shell\HiddenScan_2_ScanBg" /f >nul 2>&1
reg delete "HKCU\Software\Classes\Directory\Background\shell\AfiseazaStergeMetadate" /f >nul 2>&1
reg delete "HKCU\Software\Classes\Folder\shell\HiddenScan_1_Clean" /f >nul 2>&1
reg delete "HKCU\Software\Classes\Folder\shell\HiddenScan_2_Scan" /f >nul 2>&1
reg delete "HKCU\Software\Classes\Folder\shell\AfiseazaStergeMetadate" /f >nul 2>&1
reg delete "HKCU\Software\Classes\AllFilesystemObjects\shell\HiddenScan_1_Clean" /f >nul 2>&1
reg delete "HKCU\Software\Classes\AllFilesystemObjects\shell\HiddenScan_2_Scan" /f >nul 2>&1
reg delete "HKCU\Software\Classes\AllFilesystemObjects\shell\AfiseazaStergeMetadate" /f >nul 2>&1

:: 2. Stergere chei HKLM (in caz ca a fost rulat ca Administrator)
reg delete "HKLM\SOFTWARE\Classes\*\shell\HiddenScan_1_Clean" /f >nul 2>&1
reg delete "HKLM\SOFTWARE\Classes\*\shell\HiddenScan_2_Scan" /f >nul 2>&1
reg delete "HKLM\SOFTWARE\Classes\*\shell\AfiseazaStergeMetadate" /f >nul 2>&1
reg delete "HKLM\SOFTWARE\Classes\Directory\shell\HiddenScan_1_CleanDir" /f >nul 2>&1
reg delete "HKLM\SOFTWARE\Classes\Directory\shell\HiddenScan_2_ScanDir" /f >nul 2>&1
reg delete "HKLM\SOFTWARE\Classes\Directory\shell\AfiseazaStergeMetadate" /f >nul 2>&1
reg delete "HKLM\SOFTWARE\Classes\Directory\Background\shell\HiddenScan_1_CleanBg" /f >nul 2>&1
reg delete "HKLM\SOFTWARE\Classes\Directory\Background\shell\HiddenScan_2_ScanBg" /f >nul 2>&1
reg delete "HKLM\SOFTWARE\Classes\Directory\Background\shell\AfiseazaStergeMetadate" /f >nul 2>&1
reg delete "HKLM\SOFTWARE\Classes\Folder\shell\HiddenScan_1_Clean" /f >nul 2>&1
reg delete "HKLM\SOFTWARE\Classes\Folder\shell\HiddenScan_2_Scan" /f >nul 2>&1
reg delete "HKLM\SOFTWARE\Classes\Folder\shell\AfiseazaStergeMetadate" /f >nul 2>&1
reg delete "HKLM\SOFTWARE\Classes\AllFilesystemObjects\shell\HiddenScan_1_Clean" /f >nul 2>&1
reg delete "HKLM\SOFTWARE\Classes\AllFilesystemObjects\shell\HiddenScan_2_Scan" /f >nul 2>&1
reg delete "HKLM\SOFTWARE\Classes\AllFilesystemObjects\shell\AfiseazaStergeMetadate" /f >nul 2>&1

echo [OK] Cheile de registru au fost sterse.
echo.
echo [2/3] Se curata scurtaturile SendTo si cheile reziduale prin PowerShell...

powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference = 'SilentlyContinue'; $locations = @('HKCU:\Software\Classes\*\shell', 'HKCU:\Software\Classes\Directory\shell', 'HKCU:\Software\Classes\Directory\Background\shell', 'HKCU:\Software\Classes\Folder\shell', 'HKCU:\Software\Classes\AllFilesystemObjects\shell', 'HKLM:\SOFTWARE\Classes\*\shell', 'HKLM:\SOFTWARE\Classes\Directory\shell', 'HKLM:\SOFTWARE\Classes\Directory\Background\shell', 'HKLM:\SOFTWARE\Classes\Folder\shell', 'HKLM:\SOFTWARE\Classes\AllFilesystemObjects\shell'); foreach($loc in $locations) { if (Test-Path $loc) { Get-ChildItem -Path $loc -ErrorAction SilentlyContinue | Where-Object { $_.PSChildName -like '*HiddenScan*' -or $_.PSChildName -like '*Metadate*' -or (Get-ItemProperty $_.PSPath '(Default)' -ErrorAction SilentlyContinue).'(Default)' -like '*Metadate*' -or (Get-ItemProperty $_.PSPath 'MUIVerb' -ErrorAction SilentlyContinue).'MUIVerb' -like '*Metadate*' } | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue } }; $sendTo = [Environment]::GetFolderPath('SendTo'); if ($sendTo -and (Test-Path $sendTo)) { Get-ChildItem $sendTo -Filter '*Metadate*.lnk' -ErrorAction SilentlyContinue | Remove-Item -Force; Get-ChildItem $sendTo -Filter '*hidden-scan*.lnk' -ErrorAction SilentlyContinue | Remove-Item -Force }; $desk = [Environment]::GetFolderPath('Desktop'); if ($desk -and (Test-Path $desk)) { Get-ChildItem $desk -Filter '*Metadate*.lnk' -ErrorAction SilentlyContinue | Remove-Item -Force }"

echo [OK] Scurtaturile SendTo si Desktop au fost eliminate.
echo.
echo [3/3] Aplicare modificari:
echo Se reporneste automat Windows Explorer pentru stergerea imediata din meniu...
taskkill /f /im explorer.exe >nul 2>&1
start explorer.exe
echo [OK] Windows Explorer a fost repornit cu succes!

echo.
echo ============================================================================
echo   DEZINSTALARE FINALIZATA CU SUCCES!
echo   Optiunile de Clic-Dreapta pentru Metadate au fost eliminate complet.
echo ============================================================================
pause
