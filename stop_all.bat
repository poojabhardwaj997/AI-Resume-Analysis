@echo off
TITLE AI Resume Analysis - Stop System
color 0C

echo ===================================================================
echo     Stopping AI Resume Analysis Local Dev Servers
echo ===================================================================
echo.
echo Terminating running Uvicorn and Node / Vite processes...
taskkill /F /IM uvicorn.exe /T 2>nul
taskkill /F /FI "WINDOWTITLE eq AI Resume*" /T 2>nul

echo.
echo Processes stopped cleanly.
echo ===================================================================
pause
