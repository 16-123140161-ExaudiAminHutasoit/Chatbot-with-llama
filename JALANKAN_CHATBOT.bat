@echo off
title CHATBOT BPS LAMPUNG SELATAN - SYSTEM START
color 0A

echo ========================================================
echo   MENYALAKAN CHATBOT BPS KABUPATEN LAMPUNG SELATAN
echo ========================================================
echo.

echo [1/2] Menyalakan Backend AI (FastAPI + LlamaIndex)...
start "Backend Python AI (FastAPI Port 8001)" cmd /k "cd /d C:\Chatbot\llamaindex-docs-agent\backend && .\venv\Scripts\python.exe main.py"

echo [2/2] Menunggu Backend Siap (10 Detik)...
timeout /t 10 /nobreak > nul

echo.
echo Menyalakan WhatsApp Bridge...
start "WhatsApp Bridge (Baileys)" cmd /k "cd /d C:\Chatbot\wa-bridge && node index.js"

echo.
echo ========================================================
echo   CHATBOT BERHASIL DIJALANKAN!
echo   JANGAN TUTUP JENDELA TERMINAL YANG MUNCUL.
echo ========================================================
echo.
pause
