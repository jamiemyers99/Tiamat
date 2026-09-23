@echo off
title Tiamat
cd /d "%~dp0dist"
where py >nul 2>nul && (set PY=py) || (set PY=python)
%PY% --version >nul 2>nul
if errorlevel 1 (
  echo Python 3 is needed to run the local game server.
  echo Get it from https://www.python.org/downloads/ and try again.
  pause
  exit /b 1
)
echo Starting Tiamat at http://localhost:8765 ...
echo Close this window to stop the game server.
start "" http://localhost:8765/
%PY% -m http.server 8765 --bind 127.0.0.1
