@echo off
REM ai-security-lab launcher (Windows).
REM Double-click this file or run `launch.bat` from a terminal.

cd /d "%~dp0"
set PY=python
set PORT=8000
REM Default to all interfaces so the app is reachable from other devices on the LAN.
set HOST=0.0.0.0

%PY% -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)" 2>nul
if errorlevel 1 (
    echo [launch] Need Python 3.11 or newer.
    pause
    exit /b 1
)

%PY% -c "import fastapi, uvicorn" 2>nul
if errorlevel 1 (
    echo [launch] Installing dependencies first time...
    %PY% -m pip install -r requirements.txt
)

echo [launch] Server starting at http://%HOST%:%PORT%
start "" http://%HOST%:%PORT%
%PY% -m uvicorn webapp.server:app --host %HOST% --port %PORT%
