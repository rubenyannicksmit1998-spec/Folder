# Windows (PowerShell): installeert alles voor de lokale aanbiedingen-run en plant hem elke maandag 08:30.
# Gebruik, vanuit de Folder-map:  powershell -ExecutionPolicy Bypass -File scripts\install-local.ps1
$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)
if (-not (Get-Command python -ErrorAction SilentlyContinue)) { throw "Installeer eerst Python 3.11+" }
if (-not (Get-Command claude -ErrorAction SilentlyContinue)) { throw "Installeer eerst Claude Code en log in" }
python -m venv .venv
& .\.venv\Scripts\pip install -q -r requirements.txt
& .\.venv\Scripts\playwright install chromium
$hook = Read-Host "Plak je Discord-webhook-URL" -AsSecureString
$plain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($hook))
[Environment]::SetEnvironmentVariable("DISCORD_WEBHOOK_URL", $plain, "User")
$py = Join-Path (Get-Location) ".venv\Scripts\python.exe"
$action = New-ScheduledTaskAction -Execute $py -Argument "-m bot.local_run" -WorkingDirectory (Get-Location)
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At 8:30am
Register-ScheduledTask -TaskName "Aanbiedingen-bot" -Action $action -Trigger $trigger -Force | Out-Null
Write-Host "Klaar. Test nu: .\.venv\Scripts\python -m bot.local_run --headed --dry-run"
