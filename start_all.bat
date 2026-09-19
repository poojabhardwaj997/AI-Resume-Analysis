@echo off
TITLE AI Resume Analysis - Launch System
color 0A

echo ===================================================================
echo     AI-Powered Resume Analysis & Skill Gap Detection System
echo ===================================================================
echo.
echo [1/3] Starting FastAPI Backend on http://localhost:8000 ...
start "AI Resume - Backend Server" cmd /k "cd backend && python -m uvicorn app.main:app --reload --port 8000"

echo [2/3] Starting React Frontend on http://localhost:5173 ...
start "AI Resume - Frontend Server" cmd /k "cd frontend && npm run dev"

echo.
echo [3/3] Waiting 4 seconds for servers to initialize...
timeout /t 4 /nobreak >nul

echo Opening browser at http://localhost:5173 ...
start http://localhost:5173

echo.
echo ===================================================================
echo   System running!
echo   - Frontend: http://localhost:5173
echo   - Backend:  http://localhost:8000
echo   - API Docs: http://localhost:8000/docs
echo ===================================================================
pause
