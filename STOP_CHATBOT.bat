@echo off
title CHATBOT BPS LAMPUNG SELATAN - SYSTEM STOP
color 0C

echo ========================================================
echo   MEMATIKAN CHATBOT BPS KABUPATEN LAMPUNG SELATAN
echo ========================================================
echo.

echo Mematikan proses Node.js (WA Bridge)...
taskkill /F /IM node.exe > nul 2>&1

echo Mematikan proses Python (Backend AI)...
taskkill /F /IM python.exe > nul 2>&1

echo.
echo ========================================================
echo   CHATBOT BERHASIL DIMATIKAN!
echo ========================================================
echo.
pause
