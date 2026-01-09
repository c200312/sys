# Education System Startup Script (PowerShell)
# Usage: .\start.ps1 [start|stop|restart|status]

param(
    [Parameter(Position=0)]
    [ValidateSet("start", "stop", "restart", "status")]
    [string]$Action = "start"
)

$ErrorActionPreference = "SilentlyContinue"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackendDir = Join-Path $ScriptDir "backend"
$FrontendDir = Join-Path $ScriptDir "frontend"
$LogDir = Join-Path $ScriptDir "logs"
$PythonExe = Join-Path $BackendDir ".venv\Scripts\python.exe"

$Services = @(
    @{Port=8080; Module="app.main:app"; Name="Main_API"},
    @{Port=8002; Module="aippt.main:app"; Name="AI_PPT"},
    @{Port=8003; Module="aiwriting.main:app"; Name="AI_Writing"},
    @{Port=8004; Module="airag.main:app"; Name="AI_RAG"}
)
$FrontendPort = 3000

if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir | Out-Null
}

function Write-Header($text) {
    Write-Host ""
    Write-Host "============================================================"
    Write-Host "  $text"
    Write-Host "============================================================"
    Write-Host ""
}

function Stop-PortProcess($port) {
    $netstatOutput = netstat -ano | Select-String ":$port\s+.*LISTENING"
    foreach ($line in $netstatOutput) {
        if ($line -match '\s+(\d+)\s*$') {
            $procId = $matches[1]
            if ($procId -and $procId -ne "0") {
                $result = taskkill /F /PID $procId 2>&1
                if ($LASTEXITCODE -eq 0) {
                    Write-Host "    Stopped PID: $procId (port $port)"
                }
            }
        }
    }
}

function Test-Port($port) {
    $result = netstat -ano | Select-String ":$port\s+.*LISTENING"
    return $null -ne $result
}

function Do-Stop {
    Write-Header "Education System - Stopping All Services"

    Write-Host "[*] Stopping frontend..."
    Stop-PortProcess $FrontendPort

    Write-Host "[*] Stopping backend services..."
    foreach ($svc in $Services) {
        Stop-PortProcess $svc.Port
    }

    Write-Host "[*] All services stopped"
    Write-Host ""
}

function Do-Start {
    Write-Header "Education System - Starting All Services"

    if (-not (Test-Path $PythonExe)) {
        Write-Host "[ERROR] Python not found: $PythonExe" -ForegroundColor Red
        return
    }

    $envFile = Join-Path $BackendDir ".env"
    if (Test-Path $envFile) {
        Get-Content $envFile | ForEach-Object {
            if ($_ -match '^\s*([^#][^=]+)=(.*)$') {
                $name = $matches[1].Trim()
                $value = $matches[2].Trim()
                [Environment]::SetEnvironmentVariable($name, $value, "Process")
            }
        }
    }

    Write-Host "[*] Starting backend services..."
    Push-Location $BackendDir
    foreach ($svc in $Services) {
        Stop-PortProcess $svc.Port
        Start-Sleep -Milliseconds 300

        $logFile = Join-Path $LogDir "$($svc.Name).log"
        $cmdArgs = "-m uvicorn $($svc.Module) --host 0.0.0.0 --port $($svc.Port)"

        Start-Process cmd.exe -ArgumentList "/c `"$PythonExe $cmdArgs > `"$logFile`" 2>&1`"" -WindowStyle Hidden

        Write-Host "    $($svc.Name) -> http://localhost:$($svc.Port)" -ForegroundColor Green
        Start-Sleep -Milliseconds 500
    }
    Pop-Location

    Write-Host "[*] Starting frontend..."
    Push-Location $FrontendDir
    Stop-PortProcess $FrontendPort

    $frontendLog = Join-Path $LogDir "frontend.log"
    Start-Process cmd.exe -ArgumentList "/c `"npm.cmd run dev > `"$frontendLog`" 2>&1`"" -WindowStyle Hidden

    Write-Host "    Frontend -> http://localhost:$FrontendPort" -ForegroundColor Green
    Pop-Location

    Write-Host ""
    Write-Host "[*] Waiting for services to start..."
    Start-Sleep -Seconds 5

    Write-Host "[*] Checking service status..."
    $allOk = $true

    foreach ($svc in $Services) {
        if (Test-Port $svc.Port) {
            Write-Host "    [OK] $($svc.Name) (port $($svc.Port))" -ForegroundColor Green
        } else {
            Write-Host "    [FAIL] $($svc.Name) (port $($svc.Port)) - check logs\$($svc.Name).log" -ForegroundColor Red
            $allOk = $false
        }
    }

    if (Test-Port $FrontendPort) {
        Write-Host "    [OK] Frontend (port $FrontendPort)" -ForegroundColor Green
    } else {
        Write-Host "    [FAIL] Frontend (port $FrontendPort) - check logs\frontend.log" -ForegroundColor Red
        $allOk = $false
    }

    Write-Host ""
    if ($allOk) {
        Write-Host "All services started successfully!" -ForegroundColor Green
    } else {
        Write-Host "Some services failed to start. Check log files." -ForegroundColor Yellow
    }

    Write-Host ""
    Write-Host "------------------------------------------------------------"
    Write-Host "  Logs: logs\"
    Write-Host "  Stop: .\start.ps1 stop"
    Write-Host "  Restart: .\start.ps1 restart"
    Write-Host "  Status: .\start.ps1 status"
    Write-Host "------------------------------------------------------------"
    Write-Host ""
}

function Do-Status {
    Write-Header "Education System - Service Status"

    foreach ($svc in $Services) {
        if (Test-Port $svc.Port) {
            Write-Host "[OK] $($svc.Name) (port $($svc.Port)) running" -ForegroundColor Green
        } else {
            Write-Host "[--] $($svc.Name) (port $($svc.Port)) not running" -ForegroundColor Red
        }
    }

    if (Test-Port $FrontendPort) {
        Write-Host "[OK] Frontend (port $FrontendPort) running" -ForegroundColor Green
    } else {
        Write-Host "[--] Frontend (port $FrontendPort) not running" -ForegroundColor Red
    }

    Write-Host ""
}

switch ($Action) {
    "start" { Do-Start }
    "stop" { Do-Stop }
    "restart" {
        Write-Header "Education System - Restarting All Services"
        Do-Stop
        Start-Sleep -Seconds 2
        Do-Start
    }
    "status" { Do-Status }
}
