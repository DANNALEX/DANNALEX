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
echo [2/3] Se curata scurtaturile SendTo si cheile reziduale...

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0uninstall_context_menu.ps1" -RestartExplorer

echo.
echo ============================================================================
echo   DEZINSTALARE FINALIZATA! Meniul Clic-Dreapta a fost eliminat.
echo ============================================================================
pause
