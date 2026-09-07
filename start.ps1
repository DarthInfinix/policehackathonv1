<#
.SYNOPSIS
    Chandigarh Police Cyber Crime Investigation Platform (PS3-DWID)
    Air-Gapped Windows / PowerShell Startup & Dependency Verification Script
.DESCRIPTION
    Checks Python 3, SQLite3, Tesseract OCR, and probes offline model servers
    running on localhost:8012 (LiquidAI SLM) and localhost:8015 (dots.ocr VLM),
    then launches the Forensic Web Platform on port 8000.
#>

[CmdletBinding()]
param(
    [int]$LiquidPort = 8012,
    [int]$DotsPort = 8015,
    [int]$WebPort = 8000,
    [switch]$NoBrowser,
    [switch]$SkipCheck
)

$ErrorActionPreference = "Continue"

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "🛡️  CHANDIGARH POLICE CYBER CRIME INVESTIGATION PLATFORM (PS3-DWID)" -ForegroundColor Cyan
Write-Host "🔒 Section 63(4) BSA Compliant Forensic Triage & Offline SLM" -ForegroundColor DarkCyan
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host ""

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $ScriptDir) { $ScriptDir = Get-Location }
Set-Location $ScriptDir

# Ensure logs directory exists
if (-not (Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" | Out-Null
}

$AllDepsMet = $true

# -----------------------------------------------------------------------------
# 1. Dependency Check: Python & Virtual Environment
# -----------------------------------------------------------------------------
Write-Host "🔍 [1/4] Checking Python Environment..." -ForegroundColor Yellow

$PythonCmd = $null
if (Test-Path "$ScriptDir\.venv\Scripts\python.exe") {
    $PythonCmd = "$ScriptDir\.venv\Scripts\python.exe"
    Write-Host "   ✓ Using local virtualenv Python: $PythonCmd" -ForegroundColor Green
} elseif (Test-Path "$ScriptDir\venv\Scripts\python.exe") {
    $PythonCmd = "$ScriptDir\venv\Scripts\python.exe"
    Write-Host "   ✓ Using local virtualenv Python: $PythonCmd" -ForegroundColor Green
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    $PythonCmd = "python"
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    $PythonCmd = "py -3"
} elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
    $PythonCmd = "python3"
}

if (-not $PythonCmd) {
    Write-Host "   ❌ CRITICAL: Python 3 was not found in PATH or virtual environments!" -ForegroundColor Red
    Write-Host "      Please install Python 3.9+ from https://www.python.org/downloads/ (check 'Add Python to PATH')" -ForegroundColor Red
    $AllDepsMet = $false
} else {
    try {
        $pyVer = & $PythonCmd --version 2>&1
        Write-Host "   ✓ Detected: $pyVer" -ForegroundColor Green

        # Verify SQLite3 availability
        $sqlCheck = & $PythonCmd -c "import sqlite3; print('SQLITE_OK')" 2>&1
        if ($sqlCheck -match "SQLITE_OK") {
            Write-Host "   ✓ SQLite3 module: Available & Functional" -ForegroundColor Green
        } else {
            Write-Host "   ⚠️  SQLite3 module verification warning: $sqlCheck" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "   ❌ Failed to execute Python: $_" -ForegroundColor Red
        $AllDepsMet = $false
    }
}

# -----------------------------------------------------------------------------
# 2. Dependency Check: Tesseract OCR
# -----------------------------------------------------------------------------
Write-Host "`n🔍 [2/4] Checking Tesseract OCR Engine..." -ForegroundColor Yellow

$TesseractBin = $null
if (Get-Command tesseract -ErrorAction SilentlyContinue) {
    $TesseractBin = "tesseract"
} else {
    $Candidates = @(
        "C:\Program Files\Tesseract-OCR\tesseract.exe",
        "C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        "$env:LOCALAPPDATA\Programs\Tesseract-OCR\tesseract.exe"
    )
    foreach ($c in $Candidates) {
        if (Test-Path $c) {
            $TesseractBin = $c
            # Add containing folder to PATH for child processes
            $tDir = Split-Path -Parent $c
            $env:PATH = "$tDir;$env:PATH"
            break
        }
    }
}

if ($TesseractBin) {
    try {
        $tVer = (& $TesseractBin --version 2>&1)[0]
        Write-Host "   ✓ Detected: $tVer ($TesseractBin)" -ForegroundColor Green
    } catch {
        Write-Host "   ✓ Tesseract found at $TesseractBin" -ForegroundColor Green
    }
} else {
    Write-Host "   ℹ️  Tesseract binary not found in standard paths." -ForegroundColor DarkYellow
    Write-Host "      Tesseract installer: https://github.com/UB-Mannheim/tesseract/wiki" -ForegroundColor DarkGray
    Write-Host "      (System will still operate using plain text, CSV, and remote/dots.ocr)" -ForegroundColor DarkGray
}

# -----------------------------------------------------------------------------
# 3. Probe Offline Model Servers (Localhost 8012 & 8015)
# -----------------------------------------------------------------------------
Write-Host "`n🔍 [3/4] Probing Offline Neural Model Servers..." -ForegroundColor Yellow

# Helper function to query local llama endpoints
function Test-ModelEndpoint {
    param([string]$Url, [string]$Label, [int]$Port)
    try {
        $req = [System.Net.WebRequest]::Create($Url)
        $req.Timeout = 1500
        $resp = $req.GetResponse()
        $reader = New-Object System.IO.StreamReader($resp.GetResponseStream())
        $content = $reader.ReadToEnd()
        $reader.Close()
        $resp.Close()

        $modelId = "Active Model"
        if ($content -match '"id":\s*"([^"]+)"') {
            $modelId = $matches[1]
        }
        return @{ Online = $true; Model = $modelId; Error = $null }
    } catch {
        return @{ Online = $false; Model = $null; Error = $_.Exception.Message }
    }
}

# A. Probe LiquidAI SLM (Port 8012)
$liquidResult = Test-ModelEndpoint -Url "http://127.0.0.1:$LiquidPort/v1/models" -Label "LiquidAI" -Port $LiquidPort
if ($liquidResult.Online) {
    Write-Host "   ✅ [ONLINE] LiquidAI LFM2.5 SLM responding on port $LiquidPort (Model: $($liquidResult.Model))" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  [OFFLINE] LiquidAI server not detected on http://127.0.0.1:$LiquidPort" -ForegroundColor DarkYellow
    Write-Host "      Command to start LiquidAI: llama-server.exe -m <model.gguf> --port $LiquidPort -ngl 99 -c 4096" -ForegroundColor DarkGray
    Write-Host "      Platform will operate in fallback mode using deterministic pattern matching." -ForegroundColor DarkGray
}

# B. Probe dots.ocr VLM (Port 8015)
$dotsResult = Test-ModelEndpoint -Url "http://127.0.0.1:$DotsPort/v1/models" -Label "dots.ocr" -Port $DotsPort
if ($dotsResult.Online) {
    Write-Host "   ✅ [ONLINE] dots.ocr Multimodal VLM responding on port $DotsPort (Model: $($dotsResult.Model))" -ForegroundColor Green
} else {
    Write-Host "   ℹ️  [STANDBY] dots.ocr server not active on http://127.0.0.1:$DotsPort" -ForegroundColor DarkCyan
    Write-Host "      Command to start dots.ocr: llama-server.exe -m <dots.gguf> --mmproj <mmproj.gguf> --port $DotsPort" -ForegroundColor DarkGray
    Write-Host "      OCR worker will automatically use Tesseract or native CLI engine." -ForegroundColor DarkGray
}

# -----------------------------------------------------------------------------
# 4. Launch Forensic Web Application (Port 8000)
# -----------------------------------------------------------------------------
Write-Host "`n🚀 [4/4] Starting Forensic Web Workbench..." -ForegroundColor Yellow

if (-not $PythonCmd) {
    Write-Host "❌ Cannot start server: Python is missing. Aborting." -ForegroundColor Red
    exit 1
}

# Check if WebPort is already occupied
$portOccupied = $false
try {
    $tcp = New-Object System.Net.Sockets.TcpClient
    $tcp.Connect("127.0.0.1", $WebPort)
    $tcp.Close()
    $portOccupied = $true
} catch {
    $portOccupied = $false
}

$ServerProcess = $null
if ($portOccupied) {
    Write-Host "   ✓ Forensic Web Server is already active on http://localhost:$WebPort" -ForegroundColor Green
} else {
    Write-Host "   🌐 Starting server.py on http://127.0.0.1:$WebPort..." -ForegroundColor Cyan
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $PythonCmd
    $psi.Arguments = "server.py"
    $psi.WorkingDirectory = $ScriptDir
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.UseShellExecute = $false
    $psi.CreateNoWindow = $true

    $ServerProcess = [System.Diagnostics.Process]::Start($psi)

    # Log reader background script
    $logStream = [System.IO.File]::AppendText("$ScriptDir\logs\web_server.log")
    $logStream.WriteLine("=== Server started at $(Get-Date) (PID: $($ServerProcess.Id)) ===")
    $logStream.Close()

    Write-Host "   ✓ Web Server process spawned (PID: $($ServerProcess.Id)) -> logs/web_server.log" -ForegroundColor Green

    # Wait up to 12s for readiness
    Write-Host "   ⏳ Waiting for service readiness..." -NoNewline
    $ready = $false
    for ($i = 0; $i -lt 12; $i++) {
        Start-Sleep -Milliseconds 800
        try {
            $testReq = [System.Net.WebRequest]::Create("http://127.0.0.1:$WebPort/api/health")
            $testReq.Timeout = 800
            $testResp = $testReq.GetResponse()
            $testResp.Close()
            $ready = $true
            break
        } catch {
            Write-Host "." -NoNewline
        }
    }
    Write-Host ""

    if ($ready) {
        Write-Host "   ✅ Forensic Server is online and responsive!" -ForegroundColor Green
    } else {
        Write-Host "   ℹ️  Server launched. If first startup, FTS5 index initialization may take a few seconds." -ForegroundColor DarkYellow
    }
}

# Auto-launch browser
$WebUrl = "http://localhost:$WebPort"
if (-not $NoBrowser) {
    Write-Host "`n🖥️  Opening $WebUrl in default browser..." -ForegroundColor Cyan
    Start-Process $WebUrl
}

Write-Host ""
Write-Host "=================================================================" -ForegroundColor Green
Write-Host "🟢 CHANDIGARH POLICE FORENSIC BENCHMARK OPERATIONAL" -ForegroundColor Green
Write-Host "   • Web Dashboard:     $WebUrl" -ForegroundColor White
Write-Host "   • LiquidAI (SLM):    http://localhost:$LiquidPort $(if ($liquidResult.Online) {'[ONLINE]'} else {'[OFFLINE]'})" -ForegroundColor $(if ($liquidResult.Online) {'Green'} else {'DarkYellow'})
Write-Host "   • dots.ocr (VLM):    http://localhost:$DotsPort $(if ($dotsResult.Online) {'[ONLINE]'} else {'[STANDBY]'})" -ForegroundColor $(if ($dotsResult.Online) {'Green'} else {'DarkCyan'})
Write-Host "   • Logs:              Get-Content logs\web_server.log -Wait" -ForegroundColor DarkGray
Write-Host "=================================================================" -ForegroundColor Green
Write-Host "Press Ctrl+C to terminate the forensic server process.`n" -ForegroundColor Yellow

# Clean shutdown handler
try {
    while ($true) {
        if ($ServerProcess -and $ServerProcess.HasExited) {
            Write-Host "`n⚠️  Server process terminated with exit code $($ServerProcess.ExitCode)." -ForegroundColor Red
            break
        }
        Start-Sleep -Seconds 1
    }
} finally {
    if ($ServerProcess -and (-not $ServerProcess.HasExited)) {
        Write-Host "`nStopping forensic web server (PID: $($ServerProcess.Id))..." -ForegroundColor Yellow
        $ServerProcess.Kill()
        Write-Host "✓ Server stopped cleanly." -ForegroundColor Green
    }
}
