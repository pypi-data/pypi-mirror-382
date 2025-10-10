# ==========================================================
# install_and_run_cua.ps1 - 168x-cua installer and runner
# ==========================================================
# This script:
# - Installs/upgrades the 168x-cua package
# - Runs 168x-cua in an infinite loop (auto-restarts on crash)
#
# Usage: Add this script to Task Scheduler to run at startup
# ==========================================================

# Locate python.exe
$python = (Get-Command python.exe -ErrorAction SilentlyContinue).Source
if (-not $python) { 
    $python = 'python.exe' 
}

Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host "168x-cua Installer and Runner" -ForegroundColor Cyan
Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host "Using Python at: $python" -ForegroundColor Yellow
Write-Host ""

# Install/Upgrade 168x-cua
Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Installing/upgrading 168x-cua..." -ForegroundColor Green
try {
    & $python -m pip install --upgrade 168x-cua
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] ERROR: pip install failed with exit code $LASTEXITCODE" -ForegroundColor Red
        Write-Host "Press any key to exit..."
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        exit 1
    }
    Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Successfully installed/upgraded 168x-cua" -ForegroundColor Green
} catch {
    Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] ERROR: Failed to install 168x-cua: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

Write-Host ""
Write-Host "Starting infinite loop (press Ctrl+C to stop)..." -ForegroundColor Yellow
Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host ""

# Run in infinite loop with auto-restart
$restartCount = 0
while ($true) {
    try {
        if ($restartCount -gt 0) {
            Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Restart #$restartCount" -ForegroundColor Cyan
        }
        Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Starting 168x-cua..." -ForegroundColor Green
        
        # Run 168x-cua and capture exit code
        & "168x-cua.exe"
        $exitCode = $LASTEXITCODE
        
        Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] 168x-cua exited with code: $exitCode" -ForegroundColor Yellow
        
    } catch {
        Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] ERROR: 168x-cua crashed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    $restartCount++
    Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Restarting in 5 seconds..." -ForegroundColor Yellow
    Write-Host ""
    Start-Sleep -Seconds 5
}

