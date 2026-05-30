#!/usr/bin/env bash
# ai-security-lab launcher: zero-command setup.
# Usage:  ./launch.sh
#
# Checks Python, installs missing deps, starts the FastAPI server, opens browser.

set -e
cd "$(dirname "$0")"

PY=${PY:-python3}
PORT=${PORT:-8000}
# Default to all interfaces so the app is reachable from other devices on the LAN.
# Override with HOST=127.0.0.1 ./launch.sh to restrict to localhost.
HOST=${HOST:-0.0.0.0}

if ! command -v "$PY" >/dev/null 2>&1; then
    echo "[launch] Python 3 not found. Install python 3.11+ and re-run."
    exit 1
fi

# Verify version >= 3.11
"$PY" -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)" || {
    echo "[launch] Need Python 3.11 or newer. Current: $($PY --version)"
    exit 1
}

# Check that fastapi + uvicorn are importable; install requirements.txt if not.
if ! "$PY" -c "import fastapi, uvicorn" >/dev/null 2>&1; then
    echo "[launch] Installing dependencies (first run only)…"
    if "$PY" -m pip install --user --break-system-packages -r requirements.txt >/tmp/aisl-pip.log 2>&1; then
        echo "[launch] Dependencies installed."
    else
        echo "[launch] pip install failed. Output:"
        cat /tmp/aisl-pip.log
        exit 1
    fi
fi

# Pick a browser-open command (best-effort, never fatal).
open_browser() {
    local url="$1"
    if command -v xdg-open >/dev/null 2>&1; then xdg-open "$url" >/dev/null 2>&1 &
    elif command -v open >/dev/null 2>&1; then open "$url" >/dev/null 2>&1 &
    elif command -v start >/dev/null 2>&1; then start "$url" >/dev/null 2>&1 &
    fi
}

URL="http://${HOST}:${PORT}"
echo "[launch] Server starting at ${URL}"
( sleep 1.5 && open_browser "$URL" ) &

exec "$PY" -m uvicorn webapp.server:app --host "$HOST" --port "$PORT"
