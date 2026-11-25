@echo off
echo ==============================================
echo Installing Dependencies...
echo ==============================================
call npm install
echo.
echo ==============================================
echo Starting the Server...
echo ==============================================
node server.js
pause
