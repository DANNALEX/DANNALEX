# install_context_menu.ps1 — Înregistrează opțiunile Clic-Dreapta în Windows Explorer (HKCU)
$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$AppRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$Launcher = Join-Path $AppRoot "launcher.ps1"

function Add-MenuEntry {
    param(
        [string]$BaseRegPath,
        [string]$KeyName,
        [string]$Label,
        [string]$Icon,
        [string]$CommandStr
    )
    $MenuPath = "$BaseRegPath\shell\$KeyName"
    $CmdPath  = "$MenuPath\command"
    New-Item -Path $MenuPath -Force | Out-Null
    Set-ItemProperty -Path $MenuPath -Name "(Default)" -Value $Label
    Set-ItemProperty -Path $MenuPath -Name "Icon" -Value $Icon
    New-Item -Path $CmdPath -Force | Out-Null
    Set-ItemProperty -Path $CmdPath -Name "(Default)" -Value $CommandStr
}

# 1. Pe orice fișier (HKCU:\Software\Classes\*\shell)
$CmdCleanFile   = "powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$Launcher`" -Target `"%1`" -Mode clean"
$CmdScanFile    = "powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$Launcher`" -Target `"%1`" -Mode scan"

Add-MenuEntry -BaseRegPath "HKCU:\Software\Classes\*" `
              -KeyName "HiddenScan_1_Clean" `
              -Label "Șterge Metadate (Copie Curată)" `
              -Icon "shell32.dll,240" `
              -CommandStr $CmdCleanFile

Add-MenuEntry -BaseRegPath "HKCU:\Software\Classes\*" `
              -KeyName "HiddenScan_2_Scan" `
              -Label "Scanează Metadate și Date Ascunse" `
              -Icon "shell32.dll,23" `
              -CommandStr $CmdScanFile

# 2. Pe un Director (HKCU:\Software\Classes\Directory\shell)
$CmdCleanDir    = "powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$Launcher`" -Target `"%1`" -Mode clean"
$CmdScanDir     = "powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$Launcher`" -Target `"%1`" -Mode scan"

Add-MenuEntry -BaseRegPath "HKCU:\Software\Classes\Directory" `
              -KeyName "HiddenScan_1_CleanDir" `
              -Label "Șterge Metadate (Toate fișierele din director)" `
              -Icon "shell32.dll,240" `
              -CommandStr $CmdCleanDir

Add-MenuEntry -BaseRegPath "HKCU:\Software\Classes\Directory" `
              -KeyName "HiddenScan_2_ScanDir" `
              -Label "Scanează Metadate (Tot directorul)" `
              -Icon "shell32.dll,23" `
              -CommandStr $CmdScanDir

# 3. Pe fundalul unui Director deschis (HKCU:\Software\Classes\Directory\Background\shell)
$CmdCleanBg     = "powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$Launcher`" -Target `"%V`" -Mode clean"
$CmdScanBg      = "powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$Launcher`" -Target `"%V`" -Mode scan"

Add-MenuEntry -BaseRegPath "HKCU:\Software\Classes\Directory\Background" `
              -KeyName "HiddenScan_1_CleanBg" `
              -Label "Șterge Metadate (Tot directorul curent)" `
              -Icon "shell32.dll,240" `
              -CommandStr $CmdCleanBg

Add-MenuEntry -BaseRegPath "HKCU:\Software\Classes\Directory\Background" `
              -KeyName "HiddenScan_2_ScanBg" `
              -Label "Scanează Metadate (Tot directorul curent)" `
              -Icon "shell32.dll,23" `
              -CommandStr $CmdScanBg

# 4. Scurtătură în SendTo (vizibilă direct și pe Windows 11) + pe Desktop
$WshShell = New-Object -ComObject WScript.Shell
$SendToDir = [Environment]::GetFolderPath("SendTo")
if ($SendToDir) {
    $ShortcutSendTo = $WshShell.CreateShortcut((Join-Path $SendToDir "Șterge Metadate (hidden-scan).lnk"))
    $ShortcutSendTo.TargetPath = "powershell.exe"
    $ShortcutSendTo.Arguments = "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$Launcher`" -Mode clean -Target"
    $ShortcutSendTo.IconLocation = "shell32.dll,240"
    $ShortcutSendTo.Save()
}

$DesktopDir = [Environment]::GetFolderPath("Desktop")
if ($DesktopDir) {
    $ShortcutDesktop = $WshShell.CreateShortcut((Join-Path $DesktopDir "Scanare & Ștergere Metadate.lnk"))
    $ShortcutDesktop.TargetPath = "powershell.exe"
    $ShortcutDesktop.Arguments = "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -Command `"& { `$env:PYTHONPATH='$AppRoot'; pythonw.exe -m hidden_scan.gui }`""
    $ShortcutDesktop.WorkingDirectory = $AppRoot
    $ShortcutDesktop.IconLocation = "shell32.dll,240"
    $ShortcutDesktop.Save()
}

Write-Host "[OK] Meniul Clic-Dreapta și scurtătura Desktop au fost instalate cu succes!" -ForegroundColor Green
