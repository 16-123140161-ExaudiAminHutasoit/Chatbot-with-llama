@echo off
title BUAT SHORTCUT DESKTOP - CHATBOT BPS
color 0A

echo ========================================================
echo   MEMBUAT SHORTCUT CHATBOT DI DESKTOP
echo ========================================================
echo.

set "SCRIPT_DIR=C:\Chatbot"
set "DESKTOP_DIR=%USERPROFILE%\Desktop"

echo Membuat shortcut 'JALANKAN CHATBOT BPS'...
powershell -Command "$s=(New-Object -COM WScript.Shell).CreateShortcut('%DESKTOP_DIR%\JALANKAN CHATBOT BPS.lnk'); $s.TargetPath='%SCRIPT_DIR%\JALANKAN_CHATBOT.bat'; $s.WorkingDirectory='%SCRIPT_DIR%'; $s.IconLocation='%SCRIPT_DIR%\app_icon.ico'; $s.Save()"

echo Membuat shortcut 'HENTIKAN CHATBOT BPS'...
powershell -Command "$s=(New-Object -COM WScript.Shell).CreateShortcut('%DESKTOP_DIR%\HENTIKAN CHATBOT BPS.lnk'); $s.TargetPath='%SCRIPT_DIR%\STOP_CHATBOT.bat'; $s.WorkingDirectory='%SCRIPT_DIR%'; $s.IconLocation='%SCRIPT_DIR%\stop_icon.ico'; $s.Save()"

echo.
echo ========================================================
echo   BERHASIL! Shortcut telah dibuat di Desktop:
echo   1. JALANKAN CHATBOT BPS (Lengkap dengan Logo BPS)
echo   2. HENTIKAN CHATBOT BPS (Lengkap dengan Logo Stop)
echo ========================================================
echo.
pause
