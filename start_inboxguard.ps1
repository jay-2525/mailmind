# ==============================================================================
# InboxGuard (MailMind) - Quick Launcher Script
# ==============================================================================

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Starting InboxGuard (MailMind Agentic Email Intelligence) " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
$backendDir = Join-Path $projectRoot "backend"
$frontendDir = Join-Path $projectRoot "frontend"

Write-Host "`n[1/2] Starting FastAPI Backend on http://localhost:8000..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backendDir'; python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

Start-Sleep -Seconds 3

Write-Host "[2/2] Starting React Vite Frontend on http://localhost:5173..." -ForegroundColor Green
Start-Process cmd.exe -ArgumentList "/k cd /d `"$frontendDir`" && npx.cmd vite --host 0.0.0.0 --port 5173"

Write-Host "`nAll services launched!" -ForegroundColor Yellow
Write-Host "  - Frontend UI:  http://localhost:5173" -ForegroundColor Cyan
Write-Host "  - Backend API:  http://localhost:8000" -ForegroundColor Cyan
Write-Host "  - Swagger Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
