@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (set "PY=py -3") else (set "PY=python")
echo [1/3] Installing Python dependencies...
%PY% -m pip install -r requirements.txt || goto :fail
echo [2/3] Downloading complete original source lessons and building the LMS...
%PY% scripts\build.py --sync || goto :fail
echo [3/3] Starting the Learning Hub at http://localhost:8000
start "" http://localhost:8000
%PY% -m http.server 8000
exit /b 0
:fail
echo.
echo Setup failed. Check internet connection, Python installation, and README.md.
pause
exit /b 1
