#!/usr/bin/env bash
#
# run_sidecar.sh
# Fork E: One-Click Offline Inference Sidecar & Packaging Script
#
# Starts (if available) a local llama-server GGUF inference sidecar on
# port 8080, then starts the main TETCP forensic server on port 8000,
# and opens the browser. Fully offline / air-gapped: no external calls.
#
# Usage:
#   chmod +x run_sidecar.sh
#   ./run_sidecar.sh
#
# Env overrides:
#   MODEL_PATH   path to a GGUF model (default: models/LFM2.5-8B-A1B-Q4_0.gguf)
#   LLM_PORT     port for llama-server (default: 8080)
#   APP_PORT     port for server.py (default: 8000)

set -uo pipefail

MODEL_PATH="${MODEL_PATH:-models/LFM2.5-8B-A1B-Q4_0.gguf}"
LLM_PORT="${LLM_PORT:-8080}"
APP_PORT="${APP_PORT:-8000}"

LLM_PID=""
APP_PID=""

# ---------------------------------------------------------------------------
# Cleanup: kill both child processes on Ctrl+C / exit
# ---------------------------------------------------------------------------
cleanup() {
    echo ""
    echo "[sidecar] Shutting down..."
    if [[ -n "${LLM_PID}" ]] && kill -0 "${LLM_PID}" 2>/dev/null; then
        kill "${LLM_PID}" 2>/dev/null
        wait "${LLM_PID}" 2>/dev/null
        echo "[sidecar] Stopped llama-server (pid ${LLM_PID})"
    fi
    if [[ -n "${APP_PID}" ]] && kill -0 "${APP_PID}" 2>/dev/null; then
        kill "${APP_PID}" 2>/dev/null
        wait "${APP_PID}" 2>/dev/null
        echo "[sidecar] Stopped server.py (pid ${APP_PID})"
    fi
    exit 0
}
trap cleanup INT TERM

# ---------------------------------------------------------------------------
# 1. Locate an inference backend (llama-server or ollama). Optional.
# ---------------------------------------------------------------------------
LLM_BACKEND=""
if command -v llama-server >/dev/null 2>&1; then
    LLM_BACKEND="llama-server"
elif command -v ollama >/dev/null 2>&1; then
    LLM_BACKEND="ollama"
fi

if [[ "${LLM_BACKEND}" == "llama-server" ]]; then
    if [[ -f "${MODEL_PATH}" ]]; then
        echo "[sidecar] Found llama-server. Launching with model: ${MODEL_PATH}"
        llama-server \
            -m "${MODEL_PATH}" \
            --port "${LLM_PORT}" \
            -ngl 99 \
            -c 4096 \
            --host 127.0.0.1 \
            > llama-server.log 2>&1 &
        LLM_PID=$!
        echo "[sidecar] llama-server started (pid ${LLM_PID}), logging to llama-server.log"
    else
        echo "[sidecar] llama-server found but model not present at: ${MODEL_PATH}"
        echo "[sidecar] Continuing without local inference (heuristic fallback will be used)."
    fi
elif [[ "${LLM_BACKEND}" == "ollama" ]]; then
    echo "[sidecar] Found ollama. Assuming it is already served on its default port."
    echo "[sidecar] (ollama typically self-manages; not auto-launched here.)"
else
    echo "[sidecar] No local inference backend (llama-server / ollama) found on PATH."
    echo "[sidecar] Continuing without local inference (heuristic fallback will be used)."
fi

# Give the inference server a moment to come up before the app pings it.
if [[ -n "${LLM_PID}" ]]; then
    echo "[sidecar] Waiting for llama-server to warm up..."
    for i in $(seq 1 20); do
        if curl -s "http://127.0.0.1:${LLM_PORT}/v1/models" >/dev/null 2>&1; then
            echo "[sidecar] llama-server is responding on port ${LLM_PORT}."
            break
        fi
        sleep 0.5
    done
fi

# ---------------------------------------------------------------------------
# 2. Launch the main forensic server (server.py)
# ---------------------------------------------------------------------------
if [[ ! -f "server.py" ]]; then
    echo "[sidecar] ERROR: server.py not found in current directory."
    echo "[sidecar] Run this script from the repository root."
    cleanup
fi

echo "[sidecar] Starting python3 server.py on port ${APP_PORT}..."
APP_PORT="${APP_PORT}" python3 server.py > server.log 2>&1 &
APP_PID=$!
echo "[sidecar] server.py started (pid ${APP_PID}), logging to server.log"

# Give it a moment to bind the port.
sleep 1
if ! kill -0 "${APP_PID}" 2>/dev/null; then
    echo "[sidecar] ERROR: server.py exited immediately. Check server.log:"
    tail -n 30 server.log
    cleanup
fi

# ---------------------------------------------------------------------------
# 3. Open the browser
# ---------------------------------------------------------------------------
URL="http://localhost:${APP_PORT}/"
echo "[sidecar] Platform is live at: ${URL}"

if command -v xdg-open >/dev/null 2>&1; then
    xdg-open "${URL}" >/dev/null 2>&1 &
elif command -v open >/dev/null 2>&1; then
    open "${URL}" >/dev/null 2>&1 &
else
    echo "[sidecar] Please open ${URL} manually in your browser."
fi

echo "[sidecar] Press Ctrl+C to stop all services."

# Wait on the app server; cleanup() runs on Ctrl+C via trap.
wait "${APP_PID}"
