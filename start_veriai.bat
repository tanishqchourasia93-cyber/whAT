@echo off
title VeriAI - Launching Multi-LLM Platform
echo ===================================================
echo             Starting VeriAI Platform
echo ===================================================
echo.

set PROJECT_DIR=C:\Users\Tanishq\.gemini\antigravity\scratch\veriai

echo [1/2] Starting Backend Server (FastAPI on Port 8000)...
start "VeriAI Backend" cmd /k "cd /d %PROJECT_DIR%\backend && .venv\Scripts\activate && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

echo [2/2] Starting Frontend Server (React on Port 5173)...
start "VeriAI Frontend" cmd /k "cd /d %PROJECT_DIR%\frontend && npm run dev -- --host"

echo.
echo Both servers are starting up!
echo Waiting 4 seconds before opening your browser...
timeout /t 4 /nobreak > nul

echo Opening VeriAI in your default web browser...
start http://localhost:5173

echo.
echo ===================================================
echo VeriAI is running!
echo URL: http://localhost:5173
echo API Docs: http://127.0.0.1:8000/docs
echo (Keep the two black terminal windows open while using the app)
echo ===================================================
pause
