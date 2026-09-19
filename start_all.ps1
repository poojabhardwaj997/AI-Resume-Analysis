# ===================================================================
# PowerShell 1-Click Launch Script for AI Resume Analysis System
# ===================================================================

Write-Host "===================================================================" -ForegroundColor Cyan
Write-Host "    AI-Powered Resume Analysis & Skill Gap Detection System" -ForegroundColor Green
Write-Host "===================================================================" -ForegroundColor Cyan

$workspace = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "`n[1/3] Launching FastAPI Backend Server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$workspace\backend'; python -m uvicorn app.main:app --reload --port 8000"

Write-Host "[2/3] Launching React Vite Frontend Server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$workspace\frontend'; npm run dev"

Write-Host "[3/3] Waiting for servers to spin up..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

Write-Host "`nOpening http://localhost:5173 in default browser..." -ForegroundColor Green
Start-Process "http://localhost:5173"

Write-Host "`n===================================================================" -ForegroundColor Cyan
Write-Host " System running successfully!" -ForegroundColor Green
Write-Host " - Frontend: http://localhost:5173" -ForegroundColor White
Write-Host " - Backend:  http://localhost:8000" -ForegroundColor White
Write-Host " - API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "===================================================================" -ForegroundColor Cyan
