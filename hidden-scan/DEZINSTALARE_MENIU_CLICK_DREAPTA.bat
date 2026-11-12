@echo off
chcp 65001 >nul
title Dezinstalare Meniu Clic-Dreapta - Metadate (hidden-scan)
echo ============================================================================
echo   DEZINSTALARE MENIU CLIC-DREAPTA (Afiseaza / Sterge Metadate)
echo ============================================================================
echo.
echo [1/3] Se sterg intrarile din Registrul Windows (HKCU)...

:: 1. Stergere directa garantata prin reg delete (nu depinde de permisiuni PowerShell)
reg delete "HKCU\Software\Classes\*\shell\HiddenScan_1_Clean" /f >nul 2>&1
reg delete "HKCU\Software\Classes\*\shell\HiddenScan_2_Scan" /f >nul 2>&1
reg delete "HKCU\Software\Classes\Directory\shell\HiddenScan_1_CleanDir" /f >nul 2>&1
reg delete "HKCU\Software\Classes\Directory\shell\HiddenScan_2_ScanDir" /f >nul 2>&1
reg delete "HKCU\Software\Classes\Directory\Background\shell\HiddenScan_1_CleanBg" /f >nul 2>&1
reg delete "HKCU\Software\Classes\Directory\Background\shell\HiddenScan_2_ScanBg" /f >nul 2>&1
reg delete "HKCU\Software\Classes\Folder\shell\HiddenScan_1_Clean" /f >nul 2>&1
reg delete "HKCU\Software\Classes\Folder\shell\HiddenScan_2_Scan" /f >nul 2>&1

:: In caz ca a fost instalat sub alte denumiri
reg delete "HKCU\Software\Classes\*\shell\AfiseazaStergeMetadate" /f >nul 2>&1
reg delete "HKCU\Software\Classes\Directory\shell\AfiseazaStergeMetadate" /f >nul 2>&1
reg delete "HKCU\Software\Classes\Directory\Background\shell\AfiseazaStergeMetadate" /f >nul 2>&1

echo [2/3] Se curata scurtaturile SendTo si eventualele chei reziduale...
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0uninstall_context_menu.ps1"

echo.
echo [3/3] Aplicare modificari:
echo Doresti repornirea procesului Windows Explorer pentru aplicarea imediata?
echo (Recomandat: optiunile de Clic-Dreapta vor disparea instant, fara repornire PC)
echo.
set /p RESTART_EXP="Reporneste Windows Explorer acum? (D/N, apasa Enter pentru D): "
if /i "%RESTART_EXP%"=="" set RESTART_EXP=D
if /i "%RESTART_EXP%"=="D" (
    echo Se reporneste Explorer...
    taskkill /f /im explorer.exe >nul 2>&1
    start explorer.exe
    echo [OK] Windows Explorer a fost repornit cu succes!
)

echo.
echo ============================================================================
echo   DEZINSTALARE FINALIZATA! Meniul Clic-Dreapta a fost eliminat.
echo ============================================================================
pause
