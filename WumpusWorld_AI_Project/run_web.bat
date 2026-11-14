@echo off
title Wumpus World AI Launcher
cls
echo ============================================================
echo         WUMPUS WORLD AI AGENT - PROJECT LAUNCHER
echo ============================================================
echo.
echo Choose how you would like to run the project:
echo.
echo [1] Open Standalone Web App (index.html) - RECOMMENDED (Zero-Dependency)
echo [2] Launch Streamlit Web Dashboard (http://localhost:8501)
echo [3] Run Console Terminal Simulation (main.py)
echo [4] Exit
echo.
set /p choice="Enter choice [1-4] (default is 1): "

if "%choice%"=="" set choice=1

if "%choice%"=="1" (
    echo Opening Standalone Web Page in default browser...
    start "" "%~dp0index.html"
    goto end
)

if "%choice%"=="2" (
    echo Starting Streamlit server...
    cd /d "%~dp0WumpusWorld_AI_Project"
    start http://localhost:8501
    ".\venv\Scripts\python.exe" -m streamlit run visualization.py
    goto end
)

if "%choice%"=="3" (
    echo Running Console Simulation...
    cd /d "%~dp0WumpusWorld_AI_Project"
    ".\venv\Scripts\python.exe" main.py
    pause
    goto end
)

:end
