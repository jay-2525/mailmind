@echo off
title InboxGuard Launcher
echo ==========================================================
echo  Starting InboxGuard (MailMind Agentic Email Intelligence)
echo ==========================================================

cd /d "%~dp0"

echo.
echo [1/2] Starting FastAPI Backend on http://localhost:8000...
start "InboxGuard Backend" cmd /k "cd /d backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

timeout /t 3 /nobreak >nul

echo [2/2] Starting React Vite Frontend on http://localhost:5173...
start "InboxGuard Frontend" cmd /k "cd /d frontend && npm.cmd run dev"

echo.
echo ==========================================================
echo  InboxGuard launched successfully!
echo   - Frontend UI:  http://localhost:5173
echo   - Backend API:  http://localhost:8000
echo   - Swagger Docs: http://localhost:8000/docs
echo ==========================================================
