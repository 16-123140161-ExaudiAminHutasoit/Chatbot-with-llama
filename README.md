# 🤖 WhatsApp AI Chatbot — LlamaIndex + Ollama + Baileys

Chatbot berbasis WhatsApp dengan kemampuan AI lokal (offline), diagram statistik otomatis, dan sistem menu interaktif. Dibangun menggunakan **Node.js (Baileys)**, **Python (FastAPI + LlamaIndex)**, dan **Ollama** sebagai model AI lokal.

---

## 📦 Tech Stack

| Komponen | Teknologi |
|----------|-----------|
| WhatsApp Gateway | [Baileys](https://github.com/WhiskeySockets/Baileys) (Node.js) |
| Backend AI | FastAPI + LlamaIndex (Python 3.11) |
| Model AI | [Ollama](https://ollama.com) — `qwen2.5:1.5b` (lokal, offline) |
| Database Pengetahuan | File Markdown (`.md`) diindex via RAG |
| Diagram / Grafik | Matplotlib (Python) |

---

## 📁 Struktur Direktori

```text
Chatbot/
├── wa-bridge/                        # WhatsApp Bridge (Node.js)
│   ├── index.js                      # Logic utama chatbot & state machine
│   ├── charts/                       # Output diagram PNG (di-generate otomatis)
│   ├── .env.example                  # Template konfigurasi (salin jadi .env)
│   └── package.json
│
├── llamaindex-docs-agent/
│   └── backend/
│       ├── main.py                   # Server FastAPI (Port 8001)
│       ├── data/                     # ⚠️ FOLDER INI KOSONG DI GITHUB
│       │   ├── sensus/               # Letakkan file .md data utama di sini
│       │   └── docs/                 # Letakkan file .md dokumen pendukung di sini
│       ├── storage/                  # Di-generate otomatis saat pertama jalan
│       ├── .env.example              # Template konfigurasi backend
│       └── pyproject.toml
│
├── generate_charts.py                # Script generator diagram statistik
├── JALANKAN_CHATBOT.bat              # Starter otomatis (Windows)
├── STOP_CHATBOT.bat                  # Stop semua proses chatbot
├── RESET_SCAN_BARCODE.bat            # Reset sesi WhatsApp & scan QR ulang
└── BUAT_SHORTCUT_DESKTOP.bat         # Buat shortcut di Desktop
```

---

## ⚙️ Instalasi & Setup Awal

### Prasyarat
Pastikan software berikut sudah ter-install:
- [Node.js](https://nodejs.org) v18 atau v20 LTS
- [Python](https://python.org) 3.11+ *(centang "Add Python to PATH" saat install)*
- [Ollama](https://ollama.com)

### 1. Clone Repo

```bash
git clone https://github.com/16-123140161-ExaudiAminHutasoit/Chatbot-with-llama.git
cd Chatbot-with-llama
```

### 2. Install Library Node.js

```bash
cd wa-bridge
npm install
```

### 3. Install Library Python

```bash
cd llamaindex-docs-agent/backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Setup File Konfigurasi `.env`

**WhatsApp Bridge:**
```bash
cd wa-bridge
copy .env.example .env
```
Buka `.env` lalu isi `ALLOWED_NUMBERS` dengan nomor WhatsApp yang boleh menggunakan bot.

**Backend AI:**
```bash
cd llamaindex-docs-agent/backend
copy .env.example .env
```

### 5. Download Model AI (hanya 1x, butuh internet ~986 MB)

```bash
ollama run qwen2.5:1.5b
```
Tunggu hingga selesai, lalu ketik `/exit` untuk keluar.

---

## 📂 Cara Memasukkan Data ke Database AI

> ⚠️ **Folder `data/sensus/` dan `data/docs/` sengaja dikosongkan** di repository ini.
> Anda perlu mengisi sendiri dengan data Anda sebelum menjalankan chatbot.

### Format Data yang Didukung

Database AI membaca file **Markdown (`.md`)** yang diletakkan di:
```
llamaindex-docs-agent/backend/data/sensus/     ← Data utama / statistik
llamaindex-docs-agent/backend/data/docs/       ← Dokumen pendukung / referensi
```

### Contoh Format File `.md`

**`data/sensus/profil_wilayah.md`**
```markdown
# Profil Wilayah

## Luas Wilayah
Luas wilayah adalah 2.109,74 km².

## Jumlah Kecamatan
Terdiri dari 17 kecamatan dan 256 desa/kelurahan.

## Jumlah Penduduk 2025
Total penduduk: 1.146.070 jiwa
- Laki-laki : 581.200 jiwa
- Perempuan : 564.870 jiwa
```

**`data/sensus/data_ekonomi.md`**
```markdown
# Data Ekonomi

## PDRB 2024
Total PDRB Atas Dasar Harga Berlaku tahun 2024: Rp 57.234,50 Miliar.

## Laju Pertumbuhan Ekonomi
- 2022 : 5,14%
- 2023 : 4,98%
- 2024 : 5,02%
```

### Langkah-Langkah Memasukkan Data

```
1. Buat file .md baru di dalam folder:
   llamaindex-docs-agent/backend/data/sensus/

2. Isi dengan data/informasi yang ingin diketahui oleh AI

3. Hapus folder storage lama (wajib jika sudah pernah dijalankan):
   - llamaindex-docs-agent/backend/storage/
   - llamaindex-docs-agent/backend/pipeline_storage/

4. Jalankan chatbot kembali — AI akan otomatis membaca dan
   mengindeks semua file .md yang baru ditambahkan
```

> 💡 **Tips:** Semakin detail dan terstruktur isi file `.md`, semakin akurat jawaban AI.

---

## 🚀 Menjalankan Chatbot

**Cara mudah (Windows):**
1. Buka folder proyek
2. Klik 2x **`JALANKAN_CHATBOT.bat`**
3. Scan **QR Code** yang muncul menggunakan WhatsApp di HP (*Perangkat Tertaut*)

**Cara manual (CMD):**
```bash
# Terminal 1 — Backend AI
cd llamaindex-docs-agent/backend
venv\Scripts\activate
python main.py

# Terminal 2 — WhatsApp Bridge (setelah backend siap ~30 detik)
cd wa-bridge
node index.js
```

---

## 🔄 Perintah & Tips Berguna

| Aksi | Cara |
|------|------|
| Mematikan chatbot | Klik `STOP_CHATBOT.bat` |
| Reset sesi WhatsApp & scan QR baru | Klik `RESET_SCAN_BARCODE.bat` |
| Buat shortcut di Desktop | Klik `BUAT_SHORTCUT_DESKTOP.bat` |
| Reset via Terminal saat bot berjalan | Ketik `r` + Enter di jendela WhatsApp Bridge |
| Generate ulang semua diagram | `python generate_charts.py` |

---

## 🔒 Keamanan & Data Privat

File berikut **tidak ter-upload ke GitHub** (dilindungi `.gitignore`):

| File / Folder | Alasan |
|---|---|
| `wa-bridge/auth_state/` | Sesi & kunci enkripsi WhatsApp |
| `.env` | Konfigurasi & nomor HP privat |
| `data/sensus/`, `data/docs/` | Data internal |
| `storage/`, `pipeline_storage/` | Database vector (di-generate otomatis) |
| `node_modules/`, `venv/` | Library (di-install ulang via npm/pip) |

---

## 📄 Lisensi

MIT License — bebas digunakan dan dimodifikasi.
