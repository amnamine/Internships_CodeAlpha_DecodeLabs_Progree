@echo off
title DecodeLabs - Run All 4 Backend Projects
cls
echo =======================================================
echo    DecodeLabs Backend Track - Launching All Projects   
echo =======================================================
echo.

rem Task 1: REST API Fundamentals
echo [1/4] Starting Task 1 (REST API Fundamentals)...
start "Task 1 - REST API Fundamentals" cmd /k "cd /d "%~dp0Task 1" && node server.js"

rem Task 2: Database Integration (CRUD) - Backend & Frontend
echo [2/4] Starting Task 2 (Database Integration CRUD)...
start "Task 2 - Backend" cmd /k "cd /d "%~dp0Task 2\backend" && node server.js"
start "Task 2 - Frontend" cmd /k "cd /d "%~dp0Task 2\frontend" && npm run dev"

rem Task 3: Secure Authentication System
echo [3/4] Starting Task 3 (Secure Authentication System)...
start "Task 3 - Auth System" cmd /k "cd /d "%~dp0Task 3" && node server.js"

rem Task 4: Third-Party API Integration
echo [4/4] Starting Task 4 (Third-Party API Integration)...
start "Task 4 - 3rd Party API" cmd /k "cd /d "%~dp0Task 4" && node server.js"

echo.
echo =======================================================
echo  All project servers have been launched!               
echo                                                       
echo  Task 1 (REST API):        http://localhost:3000       
echo  Task 2 (Backend API):     http://localhost:5000       
echo  Task 2 (Frontend App):    http://localhost:5173       
echo  Task 3 (Auth System):     http://localhost:3003       
echo  Task 4 (Weather 3rd Party):http://localhost:4000       
echo =======================================================
pause
