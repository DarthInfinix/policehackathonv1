<#
.SYNOPSIS
    Chandigarh Police Cyber Crime Investigation Platform (PS3-DWID)
    Windows & NVIDIA CUDA Whisper ASR Environment Setup & Diagnostic Tool
.DESCRIPTION
    Verifies and configures:
    1. NVIDIA GPU & CUDA capability via nvidia-smi.
    2. Whisper executable (whisper-cli.exe with CUDA or CPU support).
    3. FFmpeg and FFprobe binaries for WhatsApp (.opus / .ogg) normalization.
    4. Whisper GGML models (ggml-medium.bin, ggml-small.bin, ggml-base.bin).
    5. Python virtual environment & optional faster-whisper CUDA fallback.
#>

[CmdletBinding()]
param(
    [switch]$DownloadModels,
    [switch]$TestAudio
)

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "🛡️  CHANDIGARH POLICE CYBER CRIME INVESTIGATION PLATFORM (PS3-DWID)" -ForegroundColor Cyan
Write-Host "🎙️  Windows Whisper ASR & GPU Hardware Acceleration Diagnostic" -ForegroundColor DarkCyan
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host ""

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $ScriptDir) { $ScriptDir = Get-Location }
Set-Location $ScriptDir

# 1. Check NVIDIA GPU & CUDA
Write-Host "🔍 [1/5] Probing Hardware Acceleration (NVIDIA GPU / CUDA)..." -ForegroundColor Yellow
$NvidiaFound = $false
$GpuName = "None"
$GpuVram = "0 MB"

if (Get-Command nvidia-smi -ErrorAction SilentlyContinue) {
    try {
        $gpuQuery = & nvidia-smi --query-gpu=name,memory.total --format=csv,noheader,nounits 2>&1
        if ($LASTEXITCODE -eq 0 -and $gpuQuery) {
            $parts = $gpuQuery[0] -split ","
            $GpuName = $parts[0].Trim()
            $GpuVram = "$($parts[1].Trim()) MB"
            $NvidiaFound = $true
            Write-Host "   ✅ Dedicated NVIDIA GPU Detected: $GpuName ($GpuVram VRAM)" -ForegroundColor Green
            Write-Host "      CUDA acceleration will enable ultra-fast transcription on larger models." -ForegroundColor DarkGray
        }
    } catch {}
}

if (-not $NvidiaFound) {
    Write-Host "   ℹ️  No NVIDIA GPU detected via nvidia-smi." -ForegroundColor DarkYellow
    Write-Host "      Whisper will operate using multi-threaded CPU mode (AVX2/AVX512)." -ForegroundColor DarkGray
}

# 2. Check FFmpeg / FFprobe
Write-Host "`n🔍 [2/5] Checking FFmpeg & FFprobe (Required for Opus/OGG WhatsApp Audio)..." -ForegroundColor Yellow
$FfmpegBin = $null
$FfmpegCandidates = @(
    "$ScriptDir\tools\ffmpeg\bin\ffmpeg.exe",
    "$ScriptDir\tools\ffmpeg\ffmpeg.exe",
    "C:\ffmpeg\bin\ffmpeg.exe",
    "C:\Program Files\ffmpeg\bin\ffmpeg.exe",
    "$env:LOCALAPPDATA\Programs\ffmpeg\bin\ffmpeg.exe"
)
foreach ($c in $FfmpegCandidates) {
    if (Test-Path $c) { $FfmpegBin = $c; break }
}
if (-not $FfmpegBin -and (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
    $FfmpegBin = (Get-Command ffmpeg).Source
}

if ($FfmpegBin) {
    Write-Host "   ✅ FFmpeg found: $FfmpegBin" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  FFmpeg is NOT found in PATH or standard locations." -ForegroundColor Red
    Write-Host "      Quick installation options:" -ForegroundColor DarkGray
    Write-Host "      Option A: Run in PowerShell: winget install Gyan.FFmpeg" -ForegroundColor White
    Write-Host "      Option B: Download ffmpeg-release-essentials.zip and extract to $ScriptDir\tools\ffmpeg\bin\ffmpeg.exe" -ForegroundColor White
}

# 3. Check Whisper Executable
Write-Host "`n🔍 [3/5] Checking Whisper CLI Executable..." -ForegroundColor Yellow
$WhisperBin = $null
$WhisperCandidates = @(
    "$ScriptDir\tools\whisper\whisper-cli.exe",
    "$ScriptDir\tools\whisper\whisper.exe",
    "C:\whisper-cpp\whisper-cli.exe",
    "C:\whisper-cpp\whisper.exe",
    "C:\whisper\whisper-cli.exe",
    "C:\whisper\whisper.exe",
    "$env:LOCALAPPDATA\Programs\whisper\whisper-cli.exe"
)
foreach ($wc in $WhisperCandidates) {
    if (Test-Path $wc) { $WhisperBin = $wc; break }
}
if (-not $WhisperBin) {
    if (Get-Command whisper-cli -ErrorAction SilentlyContinue) { $WhisperBin = (Get-Command whisper-cli).Source }
    elseif (Get-Command whisper-cpp -ErrorAction SilentlyContinue) { $WhisperBin = (Get-Command whisper).Source }
}

if ($WhisperBin) {
    Write-Host "   ✅ Whisper executable found: $WhisperBin" -ForegroundColor Green
} else {
    Write-Host "   ℹ️  Standalone whisper-cli.exe not found." -ForegroundColor DarkYellow
    Write-Host "      For maximum speed with your NVIDIA GPU on Windows:" -ForegroundColor DarkGray
    Write-Host "      1. Download whisper-cublas release from https://github.com/ggerganov/whisper.cpp/releases" -ForegroundColor White
    Write-Host "      2. Extract whisper-cli.exe into: $ScriptDir\tools\whisper\whisper-cli.exe" -ForegroundColor White
    Write-Host "      (The platform will also check for Python faster-whisper as a fallback)" -ForegroundColor DarkGray
}

# 4. Check Models in models/whisper/
Write-Host "`n🔍 [4/5] Checking Local Offline Whisper Models..." -ForegroundColor Yellow
$ModelDir = "$ScriptDir\models\whisper"
if (-not (Test-Path $ModelDir)) {
    New-Item -ItemType Directory -Path $ModelDir -Force | Out-Null
}

$AvailableModels = @()
$CheckTiers = @(
    @{ Name = "ggml-medium.bin"; Tier = "MEDIUM"; ExpectedSizeMB = 1530 },
    @{ Name = "ggml-small.bin";  Tier = "SMALL";  ExpectedSizeMB = 487 },
    @{ Name = "ggml-base.bin";   Tier = "BASE";   ExpectedSizeMB = 148 }
)

foreach ($item in $CheckTiers) {
    $p = "$ModelDir\$($item.Name)"
    if (Test-Path $p) {
        $sizeMB = [math]::Round((Get-Item $p).Length / 1MB, 1)
        Write-Host "   ✅ [$($item.Tier)] $($item.Name) ($sizeMB MB) is ready." -ForegroundColor Green
        $AvailableModels += $item
    } else {
        Write-Host "   ⚪ [$($item.Tier)] $($item.Name) is not downloaded." -ForegroundColor DarkGray
    }
}

if ($AvailableModels.Count -eq 0) {
    Write-Host "   ⚠️  No GGML models found in $ModelDir." -ForegroundColor Yellow
} else {
    $activeModel = $AvailableModels[0]
    Write-Host "   🎯 Active Selected Model: $($activeModel.Tier) ($($activeModel.Name))" -ForegroundColor Cyan
}

# 5. Check Python Fallback Packages
Write-Host "`n🔍 [5/5] Checking Python ASR Fallback Capabilities..." -ForegroundColor Yellow
$py = if (Test-Path "$ScriptDir\.venv\Scripts\python.exe") { "$ScriptDir\.venv\Scripts\python.exe" } else { "python" }
$pyHasFasterWhisper = & $py -c "import faster_whisper; print('OK')" 2>$null
$pyHasOpenAIWhisper = & $py -c "import whisper; print('OK')" 2>$null
$pyTorchCuda = & $py -c "import torch; print(f'CUDA:{torch.cuda.is_available()}')" 2>$null

if ($pyHasFasterWhisper -match "OK") {
    Write-Host "   ✓ faster-whisper package: Installed ($pyTorchCuda)" -ForegroundColor Green
} elseif ($pyHasOpenAIWhisper -match "OK") {
    Write-Host "   ✓ openai-whisper package: Installed ($pyTorchCuda)" -ForegroundColor Green
} else {
    Write-Host "   ℹ️  Python whisper packages not installed in virtualenv." -ForegroundColor DarkGray
    Write-Host "      (Optional: pip install faster-whisper for Python-level CUDA acceleration)" -ForegroundColor DarkGray
}

Write-Host ""
Write-Host "=================================================================" -ForegroundColor Green
Write-Host "🎯 DIAGNOSTIC SUMMARY" -ForegroundColor Green
Write-Host "   • NVIDIA GPU:        $(if ($NvidiaFound) {"$GpuName ($GpuVram)"} else {'None (CPU Mode)'})" -ForegroundColor $(if ($NvidiaFound) {'Green'} else {'DarkYellow'})
Write-Host "   • Whisper Binary:    $(if ($WhisperBin) {$WhisperBin} else {'Missing (Python fallback)'})" -ForegroundColor $(if ($WhisperBin) {'Green'} else {'DarkYellow'})
Write-Host "   • FFmpeg Normalizer: $(if ($FfmpegBin) {$FfmpegBin} else {'Missing'})" -ForegroundColor $(if ($FfmpegBin) {'Green'} else {'Red'})
Write-Host "   • Active Model:      $(if ($AvailableModels.Count -gt 0) {"$($AvailableModels[0].Tier) ($($AvailableModels[0].Name))"} else {'None'})" -ForegroundColor $(if ($AvailableModels.Count -gt 0) {'Green'} else {'Red'})
Write-Host "=================================================================" -ForegroundColor Green
Write-Host "Ready to launch: .\start.ps1`n" -ForegroundColor Cyan
