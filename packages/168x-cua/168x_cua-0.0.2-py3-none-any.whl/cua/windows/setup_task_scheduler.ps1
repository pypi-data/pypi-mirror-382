# ==========================================================
# setup_task_scheduler.ps1 - 168x-cua auto-start
# ==========================================================

$mgmt       = 'C:\168x-cua-management'
$scriptsDir = Join-Path $mgmt 'scripts'
$taskName   = '168x-cua'
$user       = 'azureadmin'
$runnerPs1  = Join-Path $scriptsDir 'run-168x-cua.ps1'

# Locate python.exe
$python = (Get-Command python.exe -ErrorAction SilentlyContinue).Source
if (-not $python) { $python = 'python.exe' }

Write-Host "Using Python at: $python"

# 1 ─────────────────────────────────────────────────────────
#   Remove old task if exists
# ───────────────────────────────────────────────────────────
Write-Host "`n*** Cleaning old task ..."
Import-Module ScheduledTasks -ErrorAction SilentlyContinue
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue

# 2 ─────────────────────────────────────────────────────────
#   Create scripts folder
# ───────────────────────────────────────────────────────────
Write-Host "*** Creating scripts folder ..."
New-Item -ItemType Directory -Path $scriptsDir -Force | Out-Null

# 3 ─────────────────────────────────────────────────────────
#   Write run-168x-cua.ps1 (upgrade + auto-restart loop)
# ───────────────────────────────────────────────────────────
Write-Host "*** Writing run-168x-cua.ps1 ..."
@"
# Upgrade 168x-cua
Write-Host "Upgrading 168x-cua..."
pip install --upgrade 168x-cua

# Run in infinite loop
while (`$true) {
    try {
        Write-Host "Starting 168x-cua..."
        & "168x-cua.exe"
    } catch {
        Write-Host "168x-cua crashed: `$(`$_.Exception.Message)"
    }
    Write-Host "Restarting in 5 seconds..."
    Start-Sleep -Seconds 5
}
"@ | Set-Content $runnerPs1 -Encoding UTF8

# 4 ─────────────────────────────────────────────────────────
#   Register task to run at startup
# ───────────────────────────────────────────────────────────
Write-Host "*** Creating '$taskName' task ..."

$action = New-ScheduledTaskAction `
            -Execute 'PowerShell.exe' `
            -Argument "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$runnerPs1`"" `
            -WorkingDirectory $mgmt

$settings = New-ScheduledTaskSettingsSet `
              -MultipleInstances IgnoreNew `
              -Hidden `
              -AllowStartIfOnBatteries `
              -DontStopIfGoingOnBatteries `
              -StartWhenAvailable `
              -ExecutionTimeLimit (New-TimeSpan -Seconds 0)

$principal = New-ScheduledTaskPrincipal `
              -UserId    $user `
              -LogonType Interactive `
              -RunLevel  Highest

$startupTrig = New-ScheduledTaskTrigger -AtStartup

Register-ScheduledTask -TaskName  $taskName `
                       -Action    $action `
                       -Trigger   $startupTrig `
                       -Settings  $settings `
                       -Principal $principal `
                       -Description '168x-cua auto-start at system startup with auto-upgrade and restart loop' `
                       -Force

if (-not $?) {
    Write-Host "ERROR: $($Error[0])"
} else {
    Write-Host "`n✔  Setup complete — 168x-cua will start automatically on system boot."
}
