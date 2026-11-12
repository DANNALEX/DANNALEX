@echo off
chcp 65001 >nul
title Dezinstalare Completa - hidden-scan v3.0 (Metadate)
echo ============================================================================
echo   DEZINSTALARE COMPLETA - hidden-scan v3.0 (Scanare si Stergere Metadate)
echo ============================================================================
echo.
echo Ce doresti sa dezinstalezi?
echo   [1] Doar meniul Clic-Dreapta din Windows Explorer (pastreaza fisierele)
echo   [2] Dezinstalare TOTALA (elimina meniul Clic-Dreapta + sterge folderul aplicatiei)
echo   [0] Anuleaza
echo.
set /p OPT="Alege optiunea (1 / 2 / 0): "

if "%OPT%"=="0" exit /b 0
if not "%OPT%"=="1" if not "%OPT%"=="2" (
    echo Optiune invalida. Operatie anulata.
    pause
    exit /b 1
)

echo.
echo ============================================================================
echo   PASUL 1: Eliminare Meniu Clic-Dreapta din Registru (HKCU)
echo ============================================================================

reg delete "HKCU\Software\Classes\*\shell\HiddenScan_1_Clean" /f >nul 2>&1
reg delete "HKCU\Software\Classes\*\shell\HiddenScan_2_Scan" /f >nul 2>&1
reg delete "HKCU\Software\Classes\Directory\shell\HiddenScan_1_CleanDir" /f >nul 2>&1
reg delete "HKCU\Software\Classes\Directory\shell\HiddenScan_2_ScanDir" /f >nul 2>&1
reg delete "HKCU\Software\Classes\Directory\Background\shell\HiddenScan_1_CleanBg" /f >nul 2>&1
reg delete "HKCU\Software\Classes\Directory\Background\shell\HiddenScan_2_ScanBg" /f >nul 2>&1
reg delete "HKCU\Software\Classes\Folder\shell\HiddenScan_1_Clean" /f >nul 2>&1
reg delete "HKCU\Software\Classes\Folder\shell\HiddenScan_2_Scan" /f >nul 2>&1
reg delete "HKCU\Software\Classes\*\shell\AfiseazaStergeMetadate" /f >nul 2>&1
reg delete "HKCU\Software\Classes\Directory\shell\AfiseazaStergeMetadate" /f >nul 2>&1
reg delete "HKCU\Software\Classes\Directory\Background\shell\AfiseazaStergeMetadate" /f >nul 2>&1

powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference = 'SilentlyContinue'; $locations = @('HKCU:\Software\Classes\*\shell', 'HKCU:\Software\Classes\Directory\shell', 'HKCU:\Software\Classes\Directory\Background\shell', 'HKCU:\Software\Classes\Folder\shell'); foreach($loc in $locations) { if (Test-Path $loc) { Get-ChildItem -Path $loc | Where-Object { $_.PSChildName -like '*HiddenScan*' -or $_.PSChildName -like '*Metadate*' -or (Get-ItemProperty $_.PSPath '(Default)' -ErrorAction SilentlyContinue).'(Default)' -like '*Metadate*' } | Remove-Item -Recurse -Force } }; $sendTo = [Environment]::GetFolderPath('SendTo'); if ($sendTo -and (Test-Path $sendTo)) { Get-ChildItem $sendTo -Filter '*Metadate*.lnk' | Remove-Item -Force; Get-ChildItem $sendTo -Filter '*hidden-scan*.lnk' | Remove-Item -Force }; $desk = [Environment]::GetFolderPath('Desktop'); if ($desk -and (Test-Path $desk)) { Get-ChildItem $desk -Filter '*Metadate*.lnk' | Remove-Item -Force }"

echo [OK] Meniul Clic-Dreapta si scurtaturile au fost eliminate din registru.

if "%OPT%"=="2" (
    echo.
    echo ============================================================================
    echo   PASUL 2: Stergere Fisiere Aplicatie
    echo ============================================================================
    set "DROPBOX_APP=C:\Users\Dell\Dropbox\0000.EU\0000.Claude acces\00000.LUCRU\Identificare date invizibile-METADATE\hidden-scan"
    if exist "%DROPBOX_APP%" (
        echo Se sterge folderul din Dropbox: %DROPBOX_APP%
        rmdir /s /q "%DROPBOX_APP%" >nul 2>&1
        echo [OK] Folderul aplicatiei din Dropbox a fost sters.
    )
    if exist "%~dp0hidden-scan" (
        echo Se sterge folderul local: %~dp0hidden-scan
        rmdir /s /q "%~dp0hidden-scan" >nul 2>&1
        echo [OK] Folderul local hidden-scan a fost sters.
    )
)

echo.
echo ============================================================================
echo   PASUL 3: Repornire Windows Explorer (pentru aplicare instantanee)
echo ============================================================================
set /p RESTART_EXP="Reporneste Windows Explorer acum? (D/N, apasa Enter pentru D): "
if /i "%RESTART_EXP%"=="" set RESTART_EXP=D
if /i "%RESTART_EXP%"=="D" (
    echo Se reporneste Explorer...
    taskkill /f /im explorer.exe >nul 2>&1
    start explorer.exe
    echo [OK] Windows Explorer a fost repornit.
)

echo.
echo ============================================================================
echo   DEZINSTALARE FINALIZATA CU SUCCES!
echo ============================================================================
pause
