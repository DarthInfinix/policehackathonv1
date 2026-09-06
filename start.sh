#!/usr/bin/env bash
# ==============================================================================
# Chandigarh Police Cyber Crime Investigation Platform (PS3-DWID)
# Air-Gapped Local Inference & Forensic Orchestration Startup Script
# ==============================================================================

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

mkdir -p logs

# Configuration & Paths
LLAMA_SERVER="${LLAMA_SERVER:-/Users/darthinfinix/llama.cpp/build/bin/llama-server}"
LIQUID_MODEL="${LIQUID_MODEL:-/Volumes/Offshore3/LlamaCpp/models/liquidai/LFM2.5-8B-A1B-Q4_0.gguf}"
DOTS_MODEL="${DOTS_MODEL:-/Volumes/Offshore3/LlamaCpp/models/dotsocr4bit/dots.ocr.Q4_K_M.gguf}"
DOTS_MMPROJ="${DOTS_MMPROJ:-/Volumes/Offshore3/LlamaCpp/models/dotsocr4bit/dots.ocr.mmproj-Q8_0.gguf}"

LIQUID_PORT="${LIQUID_PORT:-8012}"
DOTS_PORT="${DOTS_PORT:-8015}"
WEB_PORT="${WEB_PORT:-8000}"

# Detect Python interpreter
if [ -x "/Users/darthinfinix/chirag/policehackathonv1/.venv/bin/python3" ]; then
    PYTHON_BIN="/Users/darthinfinix/chirag/policehackathonv1/.venv/bin/python3"
elif [ -x "$DIR/.venv/bin/python3" ]; then
    PYTHON_BIN="$DIR/.venv/bin/python3"
else
    PYTHON_BIN="python3"
fi

echo "================================================================="
echo "🛡️  CHANDIGARH POLICE CYBER CRIME INVESTIGATION PLATFORM"
echo "🔒 Section 63(4) BSA Compliant Forensic Triage & Offline SLM"
echo "================================================================="

SPAWNED_PIDS=()

cleanup() {
    echo ""
    echo "Shutting down platform processes..."
    for pid in "${SPAWNED_PIDS[@]}"; do
        if kill -0 "$pid" 2>/dev/null; then
            echo "Stopping process $pid..."
            kill "$pid" 2>/dev/null || true
        fi
    done
    echo "✓ All processes stopped cleanly."
    exit 0
}

trap cleanup SIGINT SIGTERM

# 1. Check & Start LiquidAI Inference Server (Port 8012)
if lsof -i :"$LIQUID_PORT" >/dev/null 2>&1; then
    echo "✓ LiquidAI LFM2.5 is already running on port $LIQUID_PORT."
else
    if [ -f "$LIQUID_MODEL" ] && [ -x "$LLAMA_SERVER" ]; then
        echo "🚀 Starting LiquidAI LFM2.5 on port $LIQUID_PORT (Apple M4 Metal)..."
        "$LLAMA_SERVER" \
            -m "$LIQUID_MODEL" \
            --port "$LIQUID_PORT" \
            -ngl 99 \
            -c 4096 \
            --host 127.0.0.1 \
            > logs/liquid_server.log 2>&1 &
        LIQUID_PID=$!
        SPAWNED_PIDS+=("$LIQUID_PID")
        echo "✓ LiquidAI server started (PID: $LIQUID_PID) -> logs/liquid_server.log"
    else
        echo "⚠️  LiquidAI model not found or llama-server not executable. Skipping."
    fi
fi

# 2. Check & Start dots.ocr Multimodal VLM Server (Port 8015)
if lsof -i :"$DOTS_PORT" >/dev/null 2>&1; then
    echo "✓ dots.ocr VLM is already running on port $DOTS_PORT."
else
    if [ -f "$DOTS_MODEL" ] && [ -f "$DOTS_MMPROJ" ] && [ -x "$LLAMA_SERVER" ]; then
        echo "🚀 Starting dots.ocr (Qwen2-1.7B ViT) on port $DOTS_PORT..."
        "$LLAMA_SERVER" \
            -m "$DOTS_MODEL" \
            --mmproj "$DOTS_MMPROJ" \
            --port "$DOTS_PORT" \
            -ngl 99 \
            -c 2048 \
            --host 127.0.0.1 \
            > logs/dots_server.log 2>&1 &
        DOTS_PID=$!
        SPAWNED_PIDS+=("$DOTS_PID")
        echo "✓ dots.ocr server started (PID: $DOTS_PID) -> logs/dots_server.log"
    else
        echo "ℹ️  dots.ocr server not launched; ocr_worker will use native llama-mtmd-cli / Tesseract."
    fi
fi

# 3. Check & Start Forensic Web Application (Port 8000)
if lsof -i :"$WEB_PORT" >/dev/null 2>&1; then
    echo "✓ Forensic Web App is already active on http://localhost:$WEB_PORT"
else
    echo "🌐 Starting Forensic Web Server on http://localhost:$WEB_PORT..."
    "$PYTHON_BIN" server.py > logs/web_server.log 2>&1 &
    WEB_PID=$!
    SPAWNED_PIDS+=("$WEB_PID")
    echo "✓ Web server started (PID: $WEB_PID) -> logs/web_server.log"
fi

# Wait for Web Server readiness
echo "⏳ Verifying service availability..."
for i in {1..15}; do
    if curl -s "http://127.0.0.1:$WEB_PORT/api/health" >/dev/null 2>&1 || curl -s "http://127.0.0.1:$WEB_PORT/" >/dev/null 2>&1; then
        echo "✅ Platform is fully online and ready!"
        break
    fi
    sleep 1
done

# Auto-open browser on macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "🖥️  Opening http://localhost:$WEB_PORT in default browser..."
    open "http://localhost:$WEB_PORT"
elif command -v xdg-open >/dev/null 2>&1; then
    xdg-open "http://localhost:$WEB_PORT"
fi

echo ""
echo "================================================================="
echo "🟢 CHANDIGARH POLICE INVESTIGATION PLATFORM RUNNING"
echo "   - Web UI:           http://localhost:$WEB_PORT"
echo "   - LiquidAI (SLM):   http://localhost:$LIQUID_PORT"
echo "   - dots.ocr (VLM):   http://localhost:$DOTS_PORT (or native CLI)"
echo "   - Logs:             tail -f logs/*.log"
echo "================================================================="
echo "Press Ctrl+C to safely terminate all platform processes."

# Keep alive to catch Ctrl+C
wait
