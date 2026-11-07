@echo off
chcp 65001 >nul
cd /d "%~dp0"
start "" pythonw -m hidden_scan.gui
