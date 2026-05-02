@echo off
echo ============================================
echo  NGO Proposal Drafting Bot - Backend
echo  PRJ-032 | Yeshwanth Sai R
echo ============================================
echo.

REM Check if .env exists
if not exist .env (
    echo [WARNING] .env file not found!
    echo Please copy .env.example to .env and add your API key.
    echo.
    copy .env.example .env
    echo Created .env from template. Please edit it with your API key.
    pause
    exit /b 1
)

echo Starting FastAPI backend on http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
uvicorn backend.main:app --reload --port 8000
