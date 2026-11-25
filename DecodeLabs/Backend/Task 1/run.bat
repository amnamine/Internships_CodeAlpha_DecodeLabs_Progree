@echo off
title REST API Fundamentals Playground
cls
echo ====================================================
echo   REST API Fundamentals Playground Startup Script
echo ====================================================
echo.

rem Check for Node.js
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed or not in your PATH.
    echo Please install Node.js from https://nodejs.org/ to run this server.
    echo.
    pause
    exit /b 1
)

rem Install dependencies if node_modules folder does not exist
if not exist node_modules (
    echo [INFO] Installing required dependencies: express and cors...
    call npm install
    if %errorlevel% neq 0 (
        echo [ERROR] Dependency installation failed.
        pause
        exit /b 1
    )
    echo.
)

rem Launch browser in background
echo [INFO] Starting browser at http://localhost:3000...
start http://localhost:3000

rem Start server
echo [INFO] Starting Express REST Server...
node server.js

pause
