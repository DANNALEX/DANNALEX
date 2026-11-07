@echo off
chcp 65001 >nul
title Instalare Aplicatie Scanare si Stergere Metadate (hidden-scan v3.0)
echo ============================================================================
echo   INSTALARE APLICATIE: SCANARE SI STERGERE METADATE (hidden-scan v3.0)
echo   (Documente PDF, Word, Excel, Imagini JPG/PNG, Text + Meniu Clic-Dreapta)
echo ============================================================================
echo.

cd /d "%~dp0"

echo [1/4] Verificare Python si instalare dependente...
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
if %ERRORLEVEL% NEQ 0 (
    echo [EROARE] Instalarea pachetelor Python a esuat! Verifica daca Python este instalat.
    pause
    exit /b 1
)

echo.
echo [2/4] Generare fisiere de test si rulare verificare automata (pytest)...
python scripts\make_fixtures.py
python -m pytest -v

echo.
echo [3/4] Inregistrare Meniu Clic-Dreapta (pe fisiere si directoare) si Scurtatura Desktop...
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0install_context_menu.ps1"

echo.
echo [4/4] Copiere automata in folderul Dropbox (daca exista pe acest PC)...
set "DROPBOX_TARGET=C:\Users\Dell\Dropbox\0000.EU\0000.Claude acces\00000.LUCRU\Identificare date invizibile-METADATE\hidden-scan"
if exist "C:\Users\Dell\Dropbox\0000.EU\0000.Claude acces\00000.LUCRU\Identificare date invizibile-METADATE" (
    if /I not "%~dp0"=="%DROPBOX_TARGET%\" (
        robocopy "%~dp0." "%DROPBOX_TARGET%" /E /XD .venv __pycache__ .pytest_cache /NFL /NDL /NJH /NJS
        powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%DROPBOX_TARGET%\install_context_menu.ps1"
        echo [OK] Aplicatia a fost sincronizata si in Dropbox: %DROPBOX_TARGET%
    )
)

echo.
echo ============================================================================
echo   INSTALARE COMPLETA!
echo   Acum poti da CLIC-DREAPTA pe orice fisier sau director in Windows Explorer:
echo     - "Sterge Metadate (Copie Curata)" / "Sterge Metadate (Toate fisierele din director)"
echo     - "Scaneaza Metadate si Date Ascunse"
echo ============================================================================
pause
