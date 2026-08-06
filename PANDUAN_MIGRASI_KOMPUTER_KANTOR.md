# PANDUAN MIGRASI / PEMINDAHAN CHATBOT KE KOMPUTER KANTOR BPS

Dokumen panduan langkah demi langkah untuk memindahkan seluruh sistem Chatbot BPS Lampung Selatan dari komputer saat ini ke Komputer Kantor BPS.

---

##  LANGKAH 1: SALIN (COPY) FOLDER PROYEK

1. Siapkan **Flashdisk** / **Harddisk Eksternal** / **Google Drive**.
2. Salin (Copy) **seluruh folder `C:\Chatbot`** dari komputer ini.
3. Paste (Tempel) folder tersebut di Komputer Kantor BPS pada lokasi yang persis sama:
   ```text
   C:\Chatbot\
   ```

---

##  LANGKAH 2: INSTALL PRASYARAT APLIKASI DI KOMPUTER KANTOR

Di Komputer Kantor BPS, pastikan 3 aplikasi pendukung gratis ini sudah ter-install:

1. **Node.js (LTS Version)**
   - Download: https://nodejs.org/
   - Jalankan installer dan klik *Next* sampai selesai.

2. **Python (Versi 3.10 atau 3.11)**
   - Download: https://www.python.org/
   - **PENTING**: Saat instalasi, centang kotak **"Add Python to PATH"** di bagian bawah installer sebelum mengeklik *Install Now*.

3. **Ollama (Mesin AI Offline)**
   - Download: https://ollama.com/
   - Jalankan installer Ollama.
   - Buka Command Prompt (CMD) di komputer kantor, lalu ketik:
     ```cmd
     ollama run qwen2.5:1.5b
     ```
   - Tunggu hingga unduhan model AI selesai 100%.

---

##  LANGKAH 3: BUAT SHORTCUT APLIKASI DI DESKTOP KOMPUTER KANTOR

1. Buka folder `C:\Chatbot\` di Komputer Kantor BPS.
2. Cari file **`JALANKAN_CHATBOT.bat`**.
3. **Klik kanan** pada file `JALANKAN_CHATBOT.bat` -> pilih **Send to** -> **Desktop (create shortcut)**.
4. Di layar Desktop Komputer Kantor, ubah nama (Rename) shortcut tersebut menjadi:
   ```text
   JALANKAN CHATBOT BPS
   ```
5. **Mengubah Logo Ikon Chatbot di Desktop**:
   - Klik kanan pada shortcut **JALANKAN CHATBOT BPS** di Desktop -> pilih **Properties**.
   - Klik tombol **Change Icon...** -> klik **Browse...** -> arahkan ke file `C:\Chatbot\app_icon.ico` -> klik **OK**.

---

##  LANGKAH 4: LOGIN WHATSAPP DI KOMPUTER KANTOR

1. Klik ganda shortcut **`JALANKAN CHATBOT BPS`** di Desktop Komputer Kantor.
2. Tunggu hingga gambar **QR Code** muncul di jendela terminal.
3. Buka aplikasi WhatsApp di HP Kantor -> **Perangkat Tertaut (Linked Devices)** -> **Tautkan Perangkat (Link a Device)**.
4. Scan QR Code tersebut menggunakan kamera HP.
5. Setelah muncul tulisan `Terhubung ke WhatsApp`, Chatbot BPS di komputer kantor sudah **100% Aktif & Siap Digunakan!** 
