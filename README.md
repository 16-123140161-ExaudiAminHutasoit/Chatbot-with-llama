# SYSTEM CHATBOT STATISTIK RESMI BPS KABUPATEN LAMPUNG SELATAN

Sistem Layanan Informasi dan Pelayanan Statistik Terpadu (PST) berbasis AI dan WhatsApp Gateway resmi untuk BPS Kabupaten Lampung Selatan.

---

##  Fitur Utama Sistem

1. **Infografis & Diagram Otomatis (100% Microsoft Excel Style)**
   - Meng-generate 17 jenis diagram indikator statistik resmi (Demografi, Kemiskinan, IPM, PDRB, Ketenagakerjaan, Gini Ratio, dll.).
   - Standar publikasi HD `300 DPI` dengan warna resmi Microsoft Excel (`#4472C4` Blue, `#ED7D31` Orange, `#70AD47` Green).

2. **Respon Super Cepat (1 - 2 Detik)**
   - Menu navigasi 1 s.d. 4 langsung mengembalikan gambar diagram dan teks rekapitulasi secara instan tanpa menunggu komputasi AI.

3. **Kecerdasan AI RAG Lokal (Offline & Privacy-Preserving)**
   - Menggunakan Ollama (`qwen2.5:1.5b`) dan LlamaIndex RAG untuk menjawab pertanyaan bebas masyarakat (Menu 5).
   - 100% lokal di PC kantor BPS, tanpa biaya API berlangganan, dan data sensus terjamin kerahasiaannya.

4. **Tampilan Pesan WhatsApp Modern Aesthetic**
   - Dilengkapi banner header, icon bullet point, dan pemisah visual yang rapi.

---

##  Struktur Direktori Proyek

```text
C:\Chatbot\
├── wa-bridge\               # Service Client WhatsApp (Node.js & Baileys)
│   ├── index.js             # Logic State Machine Chatbot & Layout WhatsApp
│   ├── charts\              # Direktori Output 17 Diagram PNG HD
│   └── package.json
├── llamaindex-docs-agent\   # Backend FastAPI & RAG Ollama Engine (Python)
│   ├── main.py              # Server FastAPI Port 8001
│   ├── data\sensus\         # Database Dokumen Markdown Sensus BPS
│   └── venv\                # Environment Python
├── generate_charts.py       # Engine Generator 17 Diagram Infografis
├── JALANKAN_CHATBOT.bat     # Launcher Otomatis 1-Klik
└── README.md                # Dokumentasi Operasional
```

---

##  Cara Menjalankan Sistem (1-Klik)

1. Buka folder `C:\Chatbot\`.
2. Klik ganda pada file **`JALANKAN_CHATBOT.bat`**.
3. Sistem akan otomatis membuka terminal backend Python dan WhatsApp Bridge.
4. Jika diminta, scan **QR Code** yang muncul di layar menggunakan aplikasi WhatsApp HP Kantor (*Perangkat Tertaut*).

---
