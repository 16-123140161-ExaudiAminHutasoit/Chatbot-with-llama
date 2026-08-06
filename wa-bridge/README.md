# WA Bridge — Prototipe Chatbot Sensus BPS

Menghubungkan WhatsApp ke backend FastAPI + LlamaIndex (`/api/chat`) menggunakan
[Baileys](https://github.com/WhiskeySockets/Baileys) — library WhatsApp Web
**tidak resmi**. Cocok untuk uji coba internal, bukan solusi produksi jangka panjang.

## ⚠️ Sebelum mulai

- Gunakan nomor WA **test/cadangan** dulu, jangan langsung nomor utama kantor,
  untuk menghindari risiko banned saat masih tahap uji coba.
- Backend FastAPI (`python main.py`) harus sudah berjalan lebih dulu di
  `http://localhost:8000` (atau alamat lain sesuai `.env`).

## 1. Install dependency

```bash
cd wa-bridge
npm install
```

## 2. Konfigurasi

```bash
cp .env.example .env
```

Edit `.env` sesuai kebutuhan, minimal pastikan `CHAT_BACKEND_URL` mengarah ke
backend yang benar, misalnya:

```
CHAT_BACKEND_URL=http://localhost:8000/api/chat
```

Kalau backend dan bridge nanti dijalankan di server yang sama (VPS), biarkan
`localhost`. Kalau beda container/mesin, ganti ke IP/hostname backend.

## 3. Jalankan bridge

```bash
npm start
```

Akan muncul **QR code di terminal**. Scan pakai WhatsApp di HP:
**Setelan → Perangkat Tertaut → Tautkan Perangkat**.

Setelah tersambung, akan muncul:
```
✅ Terhubung ke WhatsApp.
```

Sesi login tersimpan di folder `auth_state/` — jangan dihapus atau
di-commit ke git (tambahkan ke `.gitignore`), supaya tidak perlu scan QR
ulang setiap kali restart.

## 4. Tes

Kirim pesan WhatsApp ke nomor yang baru discan tadi dari HP lain. Bridge akan
meneruskan pertanyaan ke backend dan membalas otomatis dengan jawaban dari
chatbot.

## Menjalankan di VPS kantor (agar selalu aktif)

Supaya proses tidak mati saat SSH ditutup, pakai `pm2`:

```bash
npm install -g pm2
pm2 start index.js --name wa-bridge-bps
pm2 start /path/ke/backend/main.py --interpreter python3 --name backend-fastapi
pm2 save
pm2 startup   # ikuti instruksi yang muncul agar auto-start saat server reboot
```

Cek status & log:
```bash
pm2 status
pm2 logs wa-bridge-bps
```

## Catatan keamanan & operasional

- **Nomor terbatas dulu**: isi `ALLOWED_NUMBERS` di `.env` untuk membatasi
  siapa saja yang bisa mengetes selama tahap prototipe.
- **Riwayat percakapan** disimpan sementara di memori (RAM) bridge, hilang
  saat proses direstart — cukup untuk prototipe, bukan untuk audit jangka
  panjang. Untuk kebutuhan resmi, sebaiknya log ke database.
- **Migrasi ke WhatsApp Cloud API resmi** disarankan sebelum dipakai untuk
  nomor resmi kantor / diumumkan ke publik untuk sensus, karena Baileys
  melanggar Terms of Service WhatsApp dan berisiko nomor diblokir.
