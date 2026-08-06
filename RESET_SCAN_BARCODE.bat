@echo off
title CHATBOT BPS - RESET SCAN BARCODE
color 0C

echo ========================================================
echo   RESET SESI WHATSAPP / ULANG SCAN BARCODE
echo ========================================================
echo.
echo Mematikan proses chatbot yang sedang berjalan...
taskkill /FI "WINDOWTITLE eq WhatsApp Bridge*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Backend Python AI*" /F >nul 2>&1

echo.
echo Menghapus sesi login lama (folder auth_state)...
if exist "C:\Chatbot\wa-bridge\auth_state" (
    rmdir /s /q "C:\Chatbot\wa-bridge\auth_state"
    echo Sesi lama BERHASIL dihapus!
) else (
    echo Sesi lama tidak ditemukan / sudah bersih.
)

echo.
echo ========================================================
echo   SELESAI! Sesi WhatsApp telah di-reset.
echo   Silakan klik 2x JALANKAN_CHATBOT.bat untuk munculkan
echo   QR Code / Barcode yang baru.
echo ========================================================
echo.
pause
