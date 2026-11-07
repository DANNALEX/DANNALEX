"""Generează un singur fișier .bat autonom (polyglot BAT + PowerShell) care conține
toate fișierele sursă ale aplicației hidden-scan v3.0 și o instalează complet automat."""
from __future__ import annotations
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

FILES_TO_EMBED = [
    "pyproject.toml",
    "requirements.txt",
    "README.md",
    "PLAN_DE_LUCRU.md",
    "RAPORT_VERIFICARE_PLAN_SI_SPECIFICATIE_V2.1.md",
    "launcher.ps1",
    "install_context_menu.ps1",
    "uninstall_context_menu.ps1",
    "PORNESTE_APLICATIA.bat",
    "INSTALARE_APLICATIE.bat",
    "hidden_scan/__init__.py",
    "hidden_scan/model.py",
    "hidden_scan/config.py",
    "hidden_scan/utils.py",
    "hidden_scan/cleaner.py",
    "hidden_scan/core.py",
    "hidden_scan/report.py",
    "hidden_scan/cli.py",
    "hidden_scan/gui.py",
    "hidden_scan/scanners/__init__.py",
    "hidden_scan/scanners/metadata.py",
    "hidden_scan/scanners/ooxml.py",
    "hidden_scan/scanners/pdf.py",
    "hidden_scan/scanners/images.py",
    "hidden_scan/scanners/unicode_scan.py",
    "hidden_scan/scanners/dual_extraction.py",
    "hidden_scan/scanners/external.py",
    "hidden_scan/templates/report.html.j2",
    "scripts/make_fixtures.py",
    "tests/conftest.py",
    "tests/test_core.py",
    "tests/test_images.py",
    "tests/test_ooxml.py",
    "tests/test_pdf.py",
    "tests/test_report.py",
    "tests/test_scoring.py",
    "tests/test_unicode.py",
]


def build_installer() -> str:
    lines: list[str] = [
        "<# :",
        "@echo off",
        "chcp 65001 >nul",
        "title Instalator Automat Complet - hidden-scan v3.0 (Scanare si Stergere Metadate)",
        "echo ============================================================================",
        "echo   INSTALATOR AUTOMAT COMPLET - hidden-scan v3.0",
        "echo   (Extrage toate fisierele, instaleaza bibliotecile, meniul Clic-Dreapta",
        "echo    pentru fisiere si directoare, scurtatura Desktop si ruleaza testele)",
        "echo ============================================================================",
        "echo.",
        'powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "$script = [System.IO.File]::ReadAllText(\'%~f0\', [System.Text.Encoding]::UTF8); Invoke-Expression $script"',
        "if %ERRORLEVEL% NEQ 0 (",
        "    echo.",
        "    echo [EROARE] Instalarea a intampinat o problema. Verifica mesajele de mai sus.",
        "    pause",
        "    exit /b %ERRORLEVEL%",
        ")",
        "echo.",
        "pause",
        "exit /b 0",
        "#>",
        "",
        "$ErrorActionPreference = 'Stop'",
        "[Console]::OutputEncoding = [System.Text.Encoding]::UTF8",
        "",
        "$DropboxParent = 'C:\\Users\\Dell\\Dropbox\\0000.EU\\0000.Claude acces\\00000.LUCRU\\Identificare date invizibile-METADATE'",
        "if (Test-Path $DropboxParent) {",
        "    $TargetRoot = Join-Path $DropboxParent 'hidden-scan'",
        "} else {",
        "    $TargetRoot = Join-Path (Get-Location).Path 'hidden-scan'",
        "}",
        "",
        "Write-Host \"[1/5] Creare structura de directoare in: $TargetRoot\" -ForegroundColor Cyan",
        "New-Item -ItemType Directory -Force -Path $TargetRoot | Out-Null",
        "",
        "function Write-AppFile {",
        "    param([string]$RelPath, [string]$Content)",
        "    $FullPath = Join-Path $TargetRoot ($RelPath -replace '/', '\\')",
        "    $Dir = Split-Path -Parent $FullPath",
        "    if (-not (Test-Path $Dir)) {",
        "        New-Item -ItemType Directory -Force -Path $Dir | Out-Null",
        "    }",
        "    $Utf8NoBom = New-Object System.Text.UTF8Encoding($false)",
        "    [System.IO.File]::WriteAllText($FullPath, $Content, $Utf8NoBom)",
        "}",
        "",
        "Write-Host '[2/5] Extragere fisiere sursa aplicatie (26 fisiere)...' -ForegroundColor Cyan",
    ]

    for rel in FILES_TO_EMBED:
        fpath = ROOT / rel
        content = fpath.read_text(encoding="utf-8")
        if "\n'@" in content or content.startswith("'@"):
            raise ValueError(f"File {rel} contains literal closing here-string marker")
        lines.append(f"\n# --- {rel} ---")
        lines.append(f"Write-AppFile -RelPath '{rel}' -Content @'")
        lines.append(content.rstrip("\n"))
        lines.append("'@")

    lines.extend([
        "",
        "Write-Host '[OK] Toate fisierele aplicatiei au fost scrise pe disc.' -ForegroundColor Green",
        "",
        "Write-Host '[3/5] Instalare pachet Python si dependente (pikepdf, Pillow, pdfminer.six, customtkinter, pytest)...' -ForegroundColor Cyan",
        "Push-Location $TargetRoot",
        "try {",
        "    python -m pip install --upgrade pip",
        "    python -m pip install -e \".[dev]\"",
        "",
        "    Write-Host '[4/5] Generare fisiere de test si verificare automata (pytest)...' -ForegroundColor Cyan",
        "    python scripts\\make_fixtures.py",
        "    python -m pytest -v",
        "",
        "    Write-Host '[5/5] Inregistrare Meniu Clic-Dreapta in Windows Explorer + Scurtatura Desktop...' -ForegroundColor Cyan",
        "    & (Join-Path $TargetRoot 'install_context_menu.ps1')",
        "",
        "    Write-Host ''",
        "    Write-Host '============================================================================' -ForegroundColor Green",
        "    Write-Host '  INSTALARE FINALIZATA CU SUCCES!' -ForegroundColor Green",
        "    Write-Host \"  Locatie aplicatie: $TargetRoot\" -ForegroundColor Green",
        "    Write-Host '  Acum poti da CLIC-DREAPTA pe orice fisier sau director in Explorer:' -ForegroundColor Green",
        "    Write-Host '    1. Sterge Metadate (Copie Curata) / (Toate fisierele din director)' -ForegroundColor Yellow",
        "    Write-Host '    2. Scaneaza Metadate si Date Ascunse' -ForegroundColor Yellow",
        "    Write-Host '============================================================================' -ForegroundColor Green",
        "",
        "    Start-Process pythonw.exe -ArgumentList '-m', 'hidden_scan.gui' -WorkingDirectory $TargetRoot",
        "} finally {",
        "    Pop-Location",
        "}",
        "",
    ])

    return "\r\n".join(lines)


if __name__ == "__main__":
    out_text = build_installer()
    out_repo_root = ROOT.parent / "INSTALARE_COMPLETA_AUTOMATA_HIDDEN_SCAN_V3.bat"
    out_app_root = ROOT / "INSTALARE_COMPLETA_AUTOMATA_HIDDEN_SCAN_V3.bat"
    out_repo_root.write_bytes(out_text.encode("utf-8"))
    out_app_root.write_bytes(out_text.encode("utf-8"))
    print(f"Generat cu succes: {out_repo_root} ({len(out_text)} caractere)")
