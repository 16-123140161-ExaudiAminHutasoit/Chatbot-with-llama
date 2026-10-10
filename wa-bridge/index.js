// WA Bridge - Chatbot BPS Kabupaten Lampung Selatan
// Menghubungkan WhatsApp via Baileys ke backend FastAPI

require("dotenv").config();
const fs = require("fs");
const path = require("path");
const axios = require("axios");
const qrcode = require("qrcode-terminal");
const pino = require("pino");
const {
  default: makeWASocket,
  useMultiFileAuthState,
  DisconnectReason,
  fetchLatestBaileysVersion,
} = require("@whiskeysockets/baileys");

const CHAT_BACKEND_URL = process.env.CHAT_BACKEND_URL || "http://localhost:8001/api/chat";
const BACKEND_TIMEOUT_MS = parseInt(process.env.BACKEND_TIMEOUT_MS || "120000", 10);
const FALLBACK_MESSAGE = [
  "Mohon maaf, sistem AI sedang tidak dapat memproses permintaan Anda saat ini.",
  "",
  "Untuk bantuan langsung, silakan hubungi kami:",
  "- Telepon : (0727) 322241",
  "- Email   : bps1803@bps.go.id",
  "- WA      : +62 858-1911-1803",
  "",
  "Website Resmi: https://lampungselatankab.bps.go.id",
  "",
  "Ketik 0 untuk kembali ke Menu Utama.",
].join("\n");
const ALLOWED_NUMBERS = (process.env.ALLOWED_NUMBERS || "")
  .split(",")
  .map((n) => n.trim())
  .filter(Boolean);

const userSessions = new Map();

function getSession(jid) {
  if (!userSessions.has(jid)) {
    userSessions.set(jid, {
      level: "init",
      menu: null,
      subItem: null,
      yearList: null,
      queryAll: null,
      queryYear: null,
      lastChartName: null,
      lastChartLabel: null,
      lastChartStyle: "bar",
    });
  }
  return userSessions.get(jid);
}

function setSession(jid, updates) {
  userSessions.set(jid, { ...getSession(jid), ...updates });
}

function resetToMain(jid) {
  userSessions.set(jid, {
    level: "main",
    menu: null,
    subItem: null,
    yearList: null,
    queryAll: null,
    queryYear: null,
  });
}

const MAX_HISTORY = 4;
const conversationHistory = new Map();

function getHistory(jid) {
  if (!conversationHistory.has(jid)) conversationHistory.set(jid, []);
  return conversationHistory.get(jid);
}

function pushHistory(jid, role, content) {
  const hist = getHistory(jid);
  hist.push({ role, content });
  while (hist.length > MAX_HISTORY) hist.shift();
}

function clearHistory(jid) {
  conversationHistory.set(jid, []);
}

const MENU_UTAMA = [
  "====================================",
  " *LAYANAN INFORMASI BPS LAMPUNG SELATAN*",
  "====================================",
  "",
  "Selamat datang di Layanan Informasi Resmi BPS Kabupaten Lampung Selatan.",
  "",
  " *Silakan Pilih Topik Data (Ketik Angkanya):*",
  "",
  "1. *Tentang BPS & Sensus Ekonomi*",
  "2. *Kependudukan (Demografi)*",
  "3. *Sosial, Pendidikan & Ketenagakerjaan*",
  "4. *Ekonomi & PDRB*",
  "5. *Tanya Jawab Bebas (Konsultasi AI)*",
  "",
  " _Ketik nomor pilihan Anda (1 - 5)._",
].join("\n");

const SUBMENU = {
  1: [
    "====================================",
    " *TENTANG BPS & SENSUS EKONOMI*",
    "====================================",
    "",
    "Pilih informasi yang Anda butuhkan:",
    "",
    "1. Profil & Kontak BPS Lampung Selatan",
    "2. Jam Layanan & Pelayanan Statistik (PST)",
    "3. FAQ & Cara Pengaduan",
    "4. Cara Verifikasi Petugas Sensus",
    "5. Informasi Sensus Ekonomi 2026 (SE2026)",
    "",
    " _Ketik 0 untuk kembali ke Menu Utama._",
  ].join("\n"),

  2: [
    "====================================",
    " *KEPENDUDUKAN (DEMOGRAFI)*",
    "====================================",
    "",
    "Pilih data statistik yang Anda butuhkan:",
    "",
    "1. Jumlah Penduduk",
    "2. Kepadatan Penduduk",
    "3. Laju Pertumbuhan Penduduk",
    "4. Persentase Penduduk per Kecamatan",
    "5. Piramida Penduduk (Kelompok Umur)",
    "6. Proyeksi Penduduk",
    "7. Rasio Jenis Kelamin (Sex Ratio)",
    "",
    " _Ketik 0 untuk kembali ke Menu Utama._",
  ].join("\n"),

  3: [
    "====================================",
    " *SOSIAL, PENDIDIKAN & KETENAGAKERJAAN*",
    "====================================",
    "",
    "Pilih data statistik yang Anda butuhkan:",
    "",
    "1. Angka Partisipasi Kasar (APK)",
    "2. Angka Partisipasi Murni (APM)",
    "3. Indeks Pembangunan Manusia (IPM)",
    "4. Indikator Kemiskinan",
    "5. Tingkat Partisipasi Angkatan Kerja (TPAK)",
    "6. Tingkat Pengangguran Terbuka (TPT)",
    "7. Gini Ratio (Rasio Gini)",
    "",
    " _Ketik 0 untuk kembali ke Menu Utama._",
  ].join("\n"),

  4: [
    "====================================",
    " *EKONOMI & PDRB*",
    "====================================",
    "",
    "Pilih data statistik yang Anda butuhkan:",
    "",
    "1. PDRB Lapangan Usaha - ADHB",
    "2. PDRB Lapangan Usaha - ADHK",
    "3. PDRB Pengeluaran - ADHB",
    "4. PDRB Pengeluaran - ADHK",
    "5. Laju Pertumbuhan PDRB",
    "6. Distribusi PDRB",
    "7. Gini Ratio",
    "",
    " _Ketik 0 untuk kembali ke Menu Utama._",
  ].join("\n"),
};

// ─────────────────────────────────────────────────────────────────────────────
// KONTEN STATIS MENU 1 (tanpa LLM)
// ─────────────────────────────────────────────────────────────────────────────
const STATIC_M1 = {
  1: [
    "====================================",
    " *PROFIL & KONTAK BPS LAMPUNG SELATAN*",
    "====================================",
    "",
    " *Instansi:* BPS Kabupaten Lampung Selatan",
    " *Alamat:* Jl. Mustafa Kemal No. 24, Kalianda, Lampung Selatan 35513",
    " *Telepon:* (0727) 322241",
    " *Email:* bps1803@bps.go.id",
    " *WhatsApp:* +62 858-1911-1803",
    " *Website:* lampungselatankab.bps.go.id",
    "",
    "─────────────",
    " *Tentang BPS Lamsel:*",
    "BPS Kabupaten Lampung Selatan adalah lembaga pemerintah non-kementerian yang bertanggung jawab dalam pengumpulan, pengolahan, dan penyebaran data statistik di wilayah Kabupaten Lampung Selatan.",
    "",
    " _Ketik 0 untuk kembali ke Menu Utama._",
  ].join("\n"),

  2: [
    "====================================",
    " *JAM LAYANAN & PST (PELAYANAN STATISTIK)*",
    "====================================",
    "",
    " *Jam Operasional Kantor:*",
    "• Senin - Kamis : 08.00 - 15.30 WIB",
    "• Jumat         : 08.00 - 15.00 WIB",
    "• Sabtu & Minggu: Tutup (Hari Libur)",
    "",
    "─────────────",
    " *Layanan PST Meliputi:*",
    "• Permintaan & konsultasi data statistik",
    "• Penjualan publikasi BPS",
    "• Rekomendasi kegiatan statistik",
    "",
    "─────────────",
    " *Hubungi Kami:*",
    "• Telepon : (0727) 322241",
    "• Email   : bps1803@bps.go.id",
    "• WA      : +62 858-1911-1803",
    "",
    " _Ketik 0 untuk kembali ke Menu Utama._",
  ].join("\n"),

  3: [
    "====================================",
    " *FAQ & CARA PENGAJUAN PENGADUAN*",
    "====================================",
    "",
    " *Pertanyaan Umum (FAQ):*",
    "",
    " *T: Bagaimana cara mendapatkan data BPS Lamsel?*",
    "   *J:* Kunjungi website lampungselatankab.bps.go.id, datang langsung ke kantor PST, atau hubungi kontak resmi kami.",
    "",
    " *T: Apakah publikasi BPS tersedia secara gratis?*",
    "   *J:* Sebagian besar publikasi tersedia gratis di website BPS. Beberapa publikasi khusus mungkin dikenakan biaya cetak.",
    "",
    " *T: Data apa saja yang tersedia di BPS Lamsel?*",
    "   *J:* Data kependudukan, ekonomi, sosial, pendidikan, ketenagakerjaan, kemiskinan, PDRB, IPM, dan indikator statistik lainnya.",
    "",
    "─────────────",
    " *Cara Menyampaikan Pengaduan:*",
    "• *Email*   : bps1803@bps.go.id",
    "• *Telepon* : (0727) 322241",
    "• *WhatsApp*: +62 858-1911-1803",
    "• *Alamat*  : Jl. Mustafa Kemal No. 24, Kalianda",
    "",
    " _Ketik 0 untuk kembali ke Menu Utama._",
  ].join("\n"),

  4: [
    "====================================",
    " *VERIFIKASI PETUGAS SENSUS BPS*",
    "====================================",
    "",
    " *Ciri-Ciri Petugas Resmi BPS:*",
    "• Membawa Surat Tugas Resmi BPS",
    "• Menggunakan Tanda Pengenal / ID Card BPS yang berlaku",
    "• Membawa dokumen / kuesioner resmi BPS",
    "",
    "─────────────",
    " *Langkah Verifikasi:*",
    "1. Minta petugas menunjukkan Surat Tugas & ID Card.",
    "2. Cocokkan nama petugas dengan dokumen.",
    "3. Konfirmasi ke kantor BPS via Telp: (0727) 322241 / WA: +62 858-1911-1803.",
    "",
    "─────────────",
    " *PENTING - Petugas BPS TIDAK PERNAH:*",
    "• Meminta uang / pembayaran dalam bentuk apapun.",
    "• Meminta data perbankan, PIN, atau kata sandi.",
    "",
    " _Ketik 0 untuk kembali ke Menu Utama._",
  ].join("\n"),

  5: [
    "-- Informasi Sensus Ekonomi 2026 (SE2026) --",
    "",
    "Apa itu Sensus Ekonomi?",
    "Sensus Ekonomi adalah pendataan seluruh usaha/perusahaan non-pertanian",
    "yang ada di Indonesia, dilaksanakan setiap 10 tahun sekali oleh BPS.",
    "",
    "Tujuan Sensus Ekonomi 2026:",
    "- Mendapatkan gambaran lengkap tentang populasi usaha di Indonesia",
    "- Menyediakan data dasar perkembangan ekonomi nasional dan daerah",
    "- Memperbarui kerangka sampel survei ekonomi",
    "",
    "Jadwal Pelaksanaan:",
    "- Listing (pendataan awal) SE2026 dilaksanakan pada tahun 2026",
    "",
    "Usaha yang dicacah dalam SE2026:",
    "Seluruh usaha/perusahaan di luar sektor pertanian, meliputi:",
    "perdagangan, industri pengolahan, jasa, konstruksi, dan sektor lainnya.",
    "",
    "Informasi lebih lanjut:",
    "- Telepon : (0727) 322241",
    "- Email   : bps1803@bps.go.id",
    "- WA      : +62 858-1911-1803",
    "",
    "Ketik 0 untuk kembali ke Menu Utama atau pilih nomor lain.",
  ].join("\n"),
};

// ─────────────────────────────────────────────────────────────────────────────
// KONFIGURASI SUB-MENU DATA (Menu 2, 3, 4)
//
// Setiap item memiliki:
//   label       : Nama topik yang ditampilkan
//   years       : null (query langsung) | string[] (daftar tahun untuk dipilih)
//   queryAll    : Query ke LLM untuk "Semua tahun" (digunakan jika years != null)
//   queryYear   : Template query per tahun, gunakan {YEAR} sebagai placeholder
//   directQuery : Query langsung ke LLM (digunakan jika years == null)
// ─────────────────────────────────────────────────────────────────────────────
const DATA_MENU = {
  2: {
    title: "Kependudukan (Demografi)",
    maxItem: 7,
    items: {
      1: {
        label: "Jumlah Penduduk",
        years: ["2024", "2023", "2022", "2021", "2020", "2019", "2018", "2017"],
        queryAll:  "Tampilkan seluruh data jumlah penduduk Kabupaten Lampung Selatan dari semua tahun yang tersedia secara lengkap",
        queryYear: "Berapa jumlah penduduk Kabupaten Lampung Selatan tahun {YEAR}? Tampilkan data lengkap termasuk per kecamatan jika tersedia.",
        chartName: "chart_penduduk",
      },
      2: {
        label: "Kepadatan Penduduk",
        years: null,
        directQuery: "Tampilkan data kepadatan penduduk per kecamatan di Kabupaten Lampung Selatan secara lengkap",
        chartName: "chart_kepadatan_penduduk",
      },
      3: {
        label: "Laju Pertumbuhan Penduduk",
        years: ["2024", "2023", "2022", "2021", "2020", "2019", "2018"],
        queryAll:  "Tampilkan seluruh data laju pertumbuhan penduduk Kabupaten Lampung Selatan dari semua tahun yang tersedia",
        queryYear: "Berapa laju pertumbuhan penduduk Kabupaten Lampung Selatan tahun {YEAR}?",
        chartName: "chart_laju_penduduk",
      },
      4: {
        label: "Persentase Penduduk per Kecamatan",
        years: null,
        directQuery: "Tampilkan data persentase penduduk per kecamatan di Kabupaten Lampung Selatan secara lengkap",
        chartName: "chart_persentase_penduduk",
      },
      5: {
        label: "Piramida Penduduk (Kelompok Umur)",
        years: null,
        directQuery: "Tampilkan data piramida penduduk berdasarkan kelompok umur di Kabupaten Lampung Selatan",
        chartName: "chart_piramida_penduduk",
      },
      6: {
        label: "Proyeksi Penduduk",
        years: null,
        directQuery: "Tampilkan data proyeksi penduduk per kecamatan di Kabupaten Lampung Selatan secara lengkap",
        chartName: "chart_proyeksi_penduduk",
      },
      7: {
        label: "Rasio Jenis Kelamin",
        years: null,
        directQuery: "Tampilkan data rasio jenis kelamin penduduk per kecamatan di Kabupaten Lampung Selatan",
        chartName: "chart_sex_ratio",
      },
    },
  },

  3: {
    title: "Sosial, Pendidikan, Ketenagakerjaan dan Gini Ratio",
    maxItem: 7,
    items: {
      1: {
        label: "Angka Partisipasi Kasar (APK)",
        years: null,
        directQuery: "Tampilkan rincian data Angka Partisipasi Kasar APK Menurut Jenjang Pendidikan BPS Kabupaten Lampung Selatan dari semua tahun",
        chartName: "chart_apk",
      },
      2: {
        label: "Angka Partisipasi Murni (APM)",
        years: null,
        directQuery: "Tampilkan rincian data Angka Partisipasi Murni APM Menurut Jenjang Pendidikan BPS Kabupaten Lampung Selatan dari semua tahun",
        chartName: "chart_apm",
      },
      3: {
        label: "Indeks Pembangunan Manusia (IPM)",
        years: ["2024", "2023", "2022", "2021", "2020", "2019", "2018", "2015", "2010"],
        queryAll:  "Tampilkan seluruh data Indeks Pembangunan Manusia IPM Kabupaten Lampung Selatan dari semua tahun yang tersedia",
        queryYear: "Berapa Indeks Pembangunan Manusia IPM Kabupaten Lampung Selatan tahun {YEAR}? Tampilkan komponen IPM jika tersedia.",
        chartName: "chart_ipm",
      },
      4: {
        label: "Indikator Kemiskinan",
        years: ["2025", "2024", "2023", "2022", "2021", "2020", "2015", "2010", "2005"],
        queryAll:  "Tampilkan seluruh data indikator kemiskinan Kabupaten Lampung Selatan dari semua tahun: jumlah penduduk miskin (ribu jiwa), persentase penduduk miskin (%), garis kemiskinan (rupiah), P1, dan P2",
        queryYear: "Tampilkan data indikator kemiskinan Kabupaten Lampung Selatan tahun {YEAR}: jumlah penduduk miskin dalam ribu jiwa, persentase penduduk miskin dalam persen, garis kemiskinan dalam rupiah per kapita per bulan, indeks kedalaman kemiskinan P1, dan indeks keparahan kemiskinan P2",
        chartName: "chart_kemiskinan",
      },
      5: {
        label: "Tingkat Partisipasi Angkatan Kerja (TPAK)",
        years: null,
        directQuery: "Tampilkan data Tingkat Partisipasi Angkatan Kerja TPAK Kabupaten Lampung Selatan dari semua tahun yang tersedia",
        chartName: "chart_ketenagakerjaan",
      },
      6: {
        label: "Tingkat Pengangguran Terbuka (TPT)",
        years: null,
        directQuery: "Tampilkan data Tingkat Pengangguran Terbuka TPT Kabupaten Lampung Selatan dari semua tahun yang tersedia",
        chartName: "chart_ketenagakerjaan",
      },
      7: {
        label: "Gini Ratio (Rasio Gini)",
        years: null,
        directQuery: "Tampilkan rincian data Gini Ratio Rasio Gini Ketimpangan Pendapatan BPS Kabupaten Lampung Selatan dari semua tahun",
        chartName: "chart_gini_ratio",
      },
    },
  },

  4: {
    title: "Ekonomi dan PDRB",
    maxItem: 7,
    items: {
      1: {
        label: "PDRB Lapangan Usaha - ADHB",
        years: ["2024", "2023", "2020", "2015", "2010"],
        queryAll:  "Tampilkan seluruh data PDRB lapangan usaha atas dasar harga berlaku ADHB Kabupaten Lampung Selatan dari semua tahun (2010 s.d. 2024)",
        queryYear: "Berapa nilai PDRB lapangan usaha atas dasar harga berlaku ADHB Kabupaten Lampung Selatan pada tahun {YEAR}? Tampilkan rincian sektor.",
        chartName: "chart_pdrb_adhb",
      },
      2: {
        label: "PDRB Lapangan Usaha - ADHK",
        years: ["2024", "2023", "2020", "2015", "2010"],
        queryAll:  "Tampilkan seluruh data PDRB lapangan usaha atas dasar harga konstan ADHK Kabupaten Lampung Selatan dari semua tahun (2010 s.d. 2024)",
        queryYear: "Berapa nilai PDRB lapangan usaha atas dasar harga konstan ADHK Kabupaten Lampung Selatan pada tahun {YEAR}? Tampilkan rincian sektor.",
        chartName: "chart_pdrb_adhk",
      },
      3: {
        label: "PDRB Pengeluaran - ADHB",
        years: ["2024", "2023", "2020", "2015", "2010"],
        queryAll:  "Tampilkan seluruh data PDRB pengeluaran atas dasar harga berlaku ADHB Kabupaten Lampung Selatan dari semua tahun (2010 s.d. 2024)",
        queryYear: "Berapa total nilai PDRB pengeluaran atas dasar harga berlaku ADHB Kabupaten Lampung Selatan pada tahun {YEAR} dalam Milyar Rupiah?",
        chartName: "chart_pdrb_pengeluaran_adhb",
      },
      4: {
        label: "PDRB Pengeluaran - ADHK",
        years: ["2024", "2023", "2020", "2015", "2010"],
        queryAll:  "Tampilkan seluruh data PDRB pengeluaran atas dasar harga konstan ADHK Kabupaten Lampung Selatan dari semua tahun (2010 s.d. 2024)",
        queryYear: "Berapa total nilai PDRB pengeluaran atas dasar harga konstan ADHK Kabupaten Lampung Selatan pada tahun {YEAR} dalam Milyar Rupiah?",
        chartName: "chart_pdrb_pengeluaran_adhk",
      },
      5: {
        label: "Laju Pertumbuhan PDRB",
        years: ["2024", "2023", "2022", "2021", "2020", "2019", "2018", "2017", "2016", "2015", "2014", "2013", "2012", "2011"],
        queryAll:  "Tampilkan seluruh data ringkasan laju pertumbuhan ekonomi PDRB Kabupaten Lampung Selatan dari semua tahun (2011 hingga 2024) secara lengkap dalam persen %",
        queryYear: "Berapa laju pertumbuhan ekonomi PDRB Kabupaten Lampung Selatan pada tahun {YEAR} (dalam persen %)? Tampilkan angka persen pertumbuhan ekonomi secara lengkap.",
        chartName: "chart_laju_ekonomi",
      },
      6: {
        label: "Distribusi PDRB",
        years: ["2024", "2023", "2020", "2015", "2010"],
        queryAll:  "Tampilkan data distribusi PDRB Kabupaten Lampung Selatan menurut lapangan usaha dan pengeluaran dari semua tahun",
        queryYear: "Tampilkan distribusi PDRB Kabupaten Lampung Selatan menurut lapangan usaha dan pengeluaran pada tahun {YEAR} secara lengkap",
        chartName: "chart_pdrb_adhb",
      },
      7: {
        label: "Gini Ratio",
        years: ["2024", "2023", "2022", "2021", "2020", "2019"],
        queryAll:  "Tampilkan seluruh data Gini Ratio Kabupaten Lampung Selatan dari semua tahun yang tersedia",
        queryYear: "Berapa Gini Ratio Kabupaten Lampung Selatan pada tahun {YEAR}?",
        chartName: "chart_gini_ratio",
      },
    },
  },
};

// ─────────────────────────────────────────────────────────────────────────────
// FUNGSI PEMBUAT TEKS MENU PILIHAN TAHUN
// ─────────────────────────────────────────────────────────────────────────────
function buildYearMenu(label, years) {
  const lines = [
    `-- ${label} --`,
    "",
    "Pilih tahun data yang Anda inginkan:",
    "",
  ];
  years.forEach((yr, idx) => {
    lines.push(`${idx + 1}. ${yr}`);
  });
  lines.push(`${years.length + 1}. Semua tahun (tampilkan data lengkap)`);
  lines.push("");
  lines.push("0. Kembali ke Menu Utama");
  return lines.join("\n");
}

// ─────────────────────────────────────────────────────────────────────────────
// FUNGSI KOMUNIKASI BACKEND (SSE Streaming)
// ─────────────────────────────────────────────────────────────────────────────
async function askBackend(jid, userText) {
  const messages = [
    ...getHistory(jid),
    { role: "user", content: userText },
  ];

  const response = await axios.post(
    CHAT_BACKEND_URL,
    { messages },
    {
      responseType: "stream",
      timeout: BACKEND_TIMEOUT_MS,
      headers: { "Content-Type": "application/json" },
    }
  );

  return new Promise((resolve, reject) => {
    let buffer = "";
    let answer = "";
    const timer = setTimeout(() => {
      response.data.destroy();
      reject(new Error("Timeout menunggu balasan backend"));
    }, BACKEND_TIMEOUT_MS);

    response.data.on("data", (chunk) => {
      buffer += chunk.toString("utf8");
      const events = buffer.split("\n\n");
      buffer = events.pop();
      for (const evt of events) {
        const line = evt.trim();
        if (!line.startsWith("data:")) continue;
        const raw = line.slice(5).trim();
        try {
          const parsed = JSON.parse(raw);
          if (typeof parsed === "string") answer += parsed;
        } catch {
          if (raw && !raw.startsWith("{")) answer += raw;
        }
      }
    });

    response.data.on("end",   () => { clearTimeout(timer); resolve(answer.trim()); });
    response.data.on("error", (e) => { clearTimeout(timer); reject(e); });
  });
}

// ─────────────────────────────────────────────────────────────────────────────
// EKSPANSI SINGKATAN BAHASA INDONESIA
// ─────────────────────────────────────────────────────────────────────────────
function expandAbbreviations(text) {
  const abbrevMap = {
    "dmn":     "dimana",  "dimna": "dimana",  "brp":  "berapa",
    "gmn":     "bagaimana","gimana":"bagaimana","knp": "kenapa",
    "kpn":     "kapan",   "apaan": "apa",     "sy":   "saya",
    "ak":      "aku",     "yg":    "yang",    "utk":  "untuk",
    "dg":      "dengan",  "dr":    "dari",    "dlm":  "dalam",
    "tsb":     "tersebut","dgn":   "dengan",  "sdh":  "sudah",
    "udh":     "sudah",   "blm":   "belum",   "tdk":  "tidak",
    "gak":     "tidak",   "gk":    "tidak",   "ga":   "tidak",
    "bsk":     "besok",   "skrg":  "sekarang","skrang":"sekarang",
    "ipm":     "Indeks Pembangunan Manusia (IPM)",
    "ipns":    "Indeks Pembangunan Manusia (IPM)",
    "pdrb":    "Produk Domestik Regional Bruto (PDRB)",
    "pdrd":    "Produk Domestik Regional Bruto (PDRB)",
    "prdb":    "Produk Domestik Regional Bruto (PDRB)",
    "adhb":    "Atas Dasar Harga Berlaku (ADHB)",
    "adhk":    "Atas Dasar Harga Konstan (ADHK)",
    "tpt":     "Tingkat Pengangguran Terbuka (TPT)",
    "tptk":    "Tingkat Pengangguran Terbuka (TPT)",
    "tpak":    "Tingkat Partisipasi Angkatan Kerja (TPAK)",
    "tpkt":    "Tingkat Partisipasi Angkatan Kerja (TPAK)",
    "apk":     "Angka Partisipasi Kasar (APK)",
    "apm":     "Angka Partisipasi Murni (APM)",
    "lpp":     "Laju Pertumbuhan Penduduk (LPP)",
    "lpps":    "Laju Pertumbuhan Penduduk (LPP)",
    "uhh":     "Usia Harapan Hidup (UHH)",
    "rls":     "Rata-rata Lama Sekolah (RLS)",
    "hls":     "Harapan Lama Sekolah (HLS)",
    "se2026":  "Sensus Ekonomi 2026 (SE2026)",
    "pst":     "Pelayanan Statistik Terpadu (PST)",
    "lda":     "Lampung Selatan Dalam Angka (LDA)",
    "info":    "informasi","jd":   "jadi",    "kl":   "kalau",
    "kalo":    "kalau",
  };
  let expanded = text;
  for (const [abbrev, full] of Object.entries(abbrevMap)) {
    const regex = new RegExp(`(?<![a-zA-Z])${abbrev}(?![a-zA-Z])`, "gi");
    expanded = expanded.replace(regex, full);
  }
  return expanded;
}

// ─────────────────────────────────────────────────────────────────────────────
// PEMBERSIHAN JAWABAN LLM
// ─────────────────────────────────────────────────────────────────────────────
const ENGLISH_REFUSALS = [
  "i'm sorry", "can't assist", "further questions",
  "i'd be happy", "provide more specific", "clear question",
  "i am sorry", "cannot assist", "i don't understand",
  "as an ai language model", "i cannot help",
];

function cleanLLMAnswer(raw) {
  if (!raw) return null;
  // Hapus semua bintang (*)
  let answer = raw.replace(/\*/g, "");
  // Hapus baris 'Penanggung Jawab Data: ...' jika terbawa
  answer = answer.replace(/Penanggung\s+Jawab\s+Data\s*:.*$/gmi, "").trim();

  // Jika jawaban sudah berisi data statistik (panjang > 50 / ada baris baru),
  // hapus kalimat apologetik palsu yang nempel di bagian paling bawah.
  if (answer.length > 50 || answer.includes("\n")) {
    answer = answer.replace(/Mohon\s+maaf,?\s+data\s+untuk\s+tahun\s+tersebut\s+belum\s+tersedia.*$/gmi, "").trim();
    answer = answer.replace(/Silakan\s+hubungi\s+kantor\s+BPS\s+Lampung\s+Selatan.*$/gmi, "").trim();
  }

  // Hapus emoji yang mungkin datang dari prompt lama
  answer = answer.replace(/[\u{1F600}-\u{1F64F}\u{1F300}-\u{1F5FF}\u{1F680}-\u{1F6FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/gu, "").trim();
  // Ganti jawaban Bahasa Inggris (match case-insensitive di awal kalimat)
  const lower = answer.toLowerCase();
  if (ENGLISH_REFUSALS.some((p) => lower.startsWith(p) || lower.includes(" " + p))) {
    return (
      "Mohon maaf, pesan Anda belum dapat kami pahami. " +
      "Silakan tanyakan informasi seputar data statistik, sensus, " +
      "atau layanan BPS Kabupaten Lampung Selatan."
    );
  }
  return answer.trim();
}

// ─────────────────────────────────────────────────────────────────────────────
// HANDLE PERTANYAAN KE LLM
// ─────────────────────────────────────────────────────────────────────────────
const CONTACT_INFO = [
  "Untuk informasi lebih lanjut, hubungi kami:",
  "- Telepon : (0727) 322241",
  "- Email   : bps1803@bps.go.id",
  "- WA      : +62 858-1911-1803",
  "- Alamat  : Jl. Mustafa Kemal No. 24, Kalianda, Lampung Selatan 35513",
  "",
  "Jam layanan: Senin-Jumat, 08.00-15.30 WIB.",
].join("\n");

function logUserQuestion(jid, question) {
  try {
    const logDir = path.join(__dirname, "..", "logs");
    if (!fs.existsSync(logDir)) fs.mkdirSync(logDir, { recursive: true });
    const logFile = path.join(logDir, "pertanyaan_warga.csv");
    if (!fs.existsSync(logFile)) {
      fs.writeFileSync(logFile, "Timestamp,WhatsApp_ID,Pertanyaan\n", "utf8");
    }
    const timestamp = new Date().toISOString();
    const cleanQ = `"${question.replace(/"/g, '""')}"`;
    fs.appendFileSync(logFile, `${timestamp},${jid},${cleanQ}\n`, "utf8");
  } catch (err) {
    console.error("[ANALYTICS] Gagal mencatat log pertanyaan:", err.message);
  }
}

async function handleLLMQuery(jid, question) {
  logUserQuestion(jid, question);
  const expanded = expandAbbreviations(question);
  if (expanded !== question) console.log(`[EXPAND] '${question}' -> '${expanded}'`);

  try {
    const raw    = await askBackend(jid, expanded);
    const answer = cleanLLMAnswer(raw);

    if (!answer || answer.trim().length < 5) {
      return [
        "Informasi Tidak Tersedia",
        "",
        "Mohon maaf, kami belum memiliki data spesifik untuk permintaan tersebut.",
        "",
        CONTACT_INFO,
        "",
        "Ketik 0 untuk kembali ke Menu Utama.",
      ].join("\n");
    }

    // Pastikan link referensi resmi selalu ada di akhir jawaban
    let finalAnswer = answer;
    if (!finalAnswer.includes("http://") && !finalAnswer.includes("https://")) {
      finalAnswer += "\n\nTautan Referensi Resmi BPS Lamsel:\nhttps://lampungselatankab.bps.go.id";
    }

    return finalAnswer + "\n\nKetik 0 untuk kembali ke Menu Utama.";
  } catch (err) {
    console.error("[LLM] Gagal memanggil backend:", err.message);
    return FALLBACK_MESSAGE;
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// LOGIKA UTAMA STATE MACHINE
// ─────────────────────────────────────────────────────────────────────────────
const GREETINGS = new Set([
  "p", "ping", "halo", "hallo", "hai", "hi", "hello",
  "halo kak", "hallo kak", "halo min", "hai min",
  "assalamu'alaikum", "assalamualaikum", "assalamualaikum wr wb",
  "assalamu'alaikum wr wb", "assalamu'alaikum wr. wb.",
  "selamat pagi", "selamat siang", "selamat sore", "selamat malam",
  "pagi", "siang", "sore", "malam",
  "mulai", "start", "menu", "help", "bantuan", "tes", "test",
]);

async function processMessage(jid, text) {
  const cleanText  = text.trim();
  const cleanLower = cleanText.toLowerCase();
  const session    = getSession(jid);

  // ── 1. GREETING -> Menu Utama ─────────────────────────────────────────────
  if (GREETINGS.has(cleanLower)) {
    clearHistory(jid);
    resetToMain(jid);
    return MENU_UTAMA;
  }

  // ── 2. Angka "0" -> Kembali ke Menu Utama dari level manapun ─────────────
  if (cleanText === "0") {
    resetToMain(jid);
    return MENU_UTAMA;
  }

  // ── 3. Deteksi permintaan diagram/grafik via kata kunci teks bebas ──────────
  const isDiagramRequest = /diagram|grafik|chart|gambar|grafis|visual/i.test(cleanLower);
  if (isDiagramRequest) {
    const CHART_KEYWORDS = [
      { keys: ["kemiskinan","miskin"],                       chartName: "chart_kemiskinan",           label: "Indikator Kemiskinan" },
      { keys: ["ipm","pembangunan manusia"],                 chartName: "chart_ipm",                  label: "Indeks Pembangunan Manusia (IPM)" },
      { keys: ["apk","partisipasi kasar"],                   chartName: "chart_apk",                  label: "Angka Partisipasi Kasar (APK)" },
      { keys: ["apm","partisipasi murni"],                   chartName: "chart_apm",                  label: "Angka Partisipasi Murni (APM)" },
      { keys: ["gini","ketimpangan","rasio gini"],           chartName: "chart_gini_ratio",           label: "Gini Ratio" },
      { keys: ["ketenagakerjaan","tpak","tpt","angkatan kerja","pengangguran"], chartName: "chart_ketenagakerjaan", label: "Ketenagakerjaan" },
      { keys: ["laju ekonomi","pertumbuhan ekonomi","laju pdrb","pertumbuhan pdrb"], chartName: "chart_laju_ekonomi", label: "Laju Pertumbuhan PDRB" },
      { keys: ["pengeluaran adhk","pdrb pengeluaran adhk","pengeluaran konstan"], chartName: "chart_pdrb_pengeluaran_adhk", label: "PDRB Pengeluaran ADHK" },
      { keys: ["pengeluaran adhb","pdrb pengeluaran adhb","pengeluaran berlaku"], chartName: "chart_pdrb_pengeluaran_adhb", label: "PDRB Pengeluaran ADHB" },
      { keys: ["pdrb adhb","harga berlaku"],                 chartName: "chart_pdrb_adhb",            label: "PDRB ADHB" },
      { keys: ["pdrb adhk","harga konstan"],                 chartName: "chart_pdrb_adhk",            label: "PDRB ADHK" },
      { keys: ["pdrb pengeluaran","pengeluaran"],            chartName: "chart_pdrb_pengeluaran_adhb", label: "PDRB Pengeluaran ADHB" },
      { keys: ["pdrb"],                                      chartName: "chart_pdrb_adhb",            label: "PDRB" },
      { keys: ["piramida","kelompok umur"],                  chartName: "chart_piramida_penduduk",    label: "Piramida Penduduk" },
      { keys: ["proyeksi penduduk"],                         chartName: "chart_proyeksi_penduduk",    label: "Proyeksi Penduduk" },
      { keys: ["kepadatan"],                                 chartName: "chart_kepadatan_penduduk",   label: "Kepadatan Penduduk" },
      { keys: ["sex ratio","rasio jenis kelamin"],           chartName: "chart_sex_ratio",            label: "Rasio Jenis Kelamin" },
      { keys: ["persentase penduduk"],                       chartName: "chart_persentase_penduduk",  label: "Persentase Penduduk per Kecamatan" },
      { keys: ["laju penduduk","pertumbuhan penduduk"],      chartName: "chart_laju_penduduk",        label: "Laju Pertumbuhan Penduduk" },
      { keys: ["penduduk","jumlah penduduk","demografi"],    chartName: "chart_penduduk",             label: "Jumlah Penduduk" },
    ];

    let requestedStyle = "bar";
    if (/garis|line|tren|trend|kurva/i.test(cleanLower)) {
      requestedStyle = "line";
    } else if (/pie|lingkaran|donat|donut|persen|distribusi/i.test(cleanLower)) {
      requestedStyle = "pie";
    } else if (/lain|variasi|opsi|beda/i.test(cleanLower)) {
      // Jika pengguna meminta 'diagram yang lain' tanpa sebut jenis, rotasi otomatis (bar -> line -> pie -> bar)
      const curStyle = session.lastChartStyle || "bar";
      if (curStyle === "bar") requestedStyle = "line";
      else if (curStyle === "line") requestedStyle = "pie";
      else requestedStyle = "bar";
    }

    // 1. Cek apakah ada kata kunci topik tertentu (kemiskinan, ipm, dll)
    for (const entry of CHART_KEYWORDS) {
      if (entry.keys.some((k) => cleanLower.includes(k))) {
        console.log(`[CHART-KEYWORD] Request diagram '${entry.label}' style='${requestedStyle}' via kata kunci.`);
        setSession(jid, {
          lastChartName: entry.chartName,
          lastChartLabel: entry.label,
          lastChartStyle: requestedStyle,
        });
        return {
          text: ` Berikut adalah diagram grafik statistik resmi BPS Kabupaten Lampung Selatan untuk *${entry.label}* (${requestedStyle.toUpperCase()}).\n\nKetik 0 untuk kembali ke Menu Utama.`,
          chartName: entry.chartName,
          chartStyle: requestedStyle,
        };
      }
    }

    // 2. Jika tidak sebut nama data tapi pengguna minta "diagram yang lain" dan ada riwayat diagram sebelumnya
    if (/lain|variasi|opsi|beda|garis|line|pie|lingkaran|batang|bar/i.test(cleanLower) && session.lastChartName) {
      console.log(`[CHART-CONTEXT] Mengganti gaya diagram '${session.lastChartLabel}' menjadi '${requestedStyle}' berdasarkan konteks terakhir.`);
      setSession(jid, { lastChartStyle: requestedStyle });
      return {
        text: ` Berikut adalah diagram variasi bentuk *${requestedStyle.toUpperCase()}* untuk *${session.lastChartLabel}* BPS Kabupaten Lampung Selatan.\n\nKetik 0 untuk kembali ke Menu Utama.`,
        chartName: session.lastChartName,
        chartStyle: requestedStyle,
      };
    }

    // 3. Jika benar-benar baru dan tidak ada kata kunci yang cocok — tampilkan daftar diagram yang tersedia
    return [
      "Diagram yang tersedia di sistem kami:",
      "",
      "• Diagram Kemiskinan        → ketik: diagram kemiskinan",
      "• Diagram IPM               → ketik: diagram ipm",
      "• Diagram APK               → ketik: diagram apk",
      "• Diagram APM               → ketik: diagram apm",
      "• Diagram PDRB ADHB         → ketik: diagram pdrb adhb",
      "• Diagram PDRB ADHK         → ketik: diagram pdrb adhk",
      "• Diagram Laju PDRB         → ketik: diagram laju pdrb",
      "• Diagram Ketenagakerjaan   → ketik: diagram ketenagakerjaan",
      "• Diagram Gini Ratio        → ketik: diagram gini",
      "• Diagram Jumlah Penduduk   → ketik: diagram penduduk",
      "• Diagram Kepadatan         → ketik: diagram kepadatan",
      "• Diagram Piramida Penduduk → ketik: diagram piramida",
      "",
      "Atau pilih dari menu terstruktur:",
      "Ketik 2 (Kependudukan) | 3 (Sosial) | 4 (Ekonomi)",
      "",
      "Ketik 0 untuk kembali ke Menu Utama.",
    ].join("\n");
  }

  // Helper: Cek apakah input adalah angka murni (tanpa huruf/titik/koma)
  // Mencegah input seperti "1abc" atau "1.5" dibaca sebagai angka valid.
  const isPureNumber = /^\d+$/.test(cleanText);

  // Fungsi parse integer yang ketat: hanya menerima string angka bulat murni (misal "1", "2")
  // parseInt("1abc") → 1 (salah), parseStrictInt("1abc") → NaN (benar)
  function parseStrictInt(str) {
    return /^\d+$/.test(str) ? parseInt(str, 10) : NaN;
  }

  // ── 3. Level MAIN (atau INIT) ─────────────────────────────────────────────
  if (session.level === "main" || session.level === "init") {
    switch (cleanText) {
      case "1": setSession(jid, { level: "submenu", menu: 1 }); return SUBMENU[1];
      case "2": setSession(jid, { level: "submenu", menu: 2 }); return SUBMENU[2];
      case "3": setSession(jid, { level: "submenu", menu: 3 }); return SUBMENU[3];
      case "4": setSession(jid, { level: "submenu", menu: 4 }); return SUBMENU[4];
      case "5":
        setSession(jid, { level: "freetext" });
        return [
          "-- Pertanyaan Bebas --",
          "",
          "Silakan ketik pertanyaan Anda tentang data statistik",
          "BPS Kabupaten Lampung Selatan.",
          "",
          "Contoh pertanyaan:",
          "- Berapa IPM Lampung Selatan tahun 2024?",
          "- Berapa laju pertumbuhan ekonomi Lampung Selatan?",
          "- Berapa jumlah penduduk miskin Lampung Selatan?",
          "",
          "Ketik 0 untuk kembali ke Menu Utama.",
        ].join("\n");
      default:
        // Jika berupa angka murni tetapi tidak ada di pilihan (seperti 95, 9, 88)
        if (isPureNumber) {
          return [
            "Mohon maaf, nomor pilihan yang Anda masukkan tidak tersedia pada daftar menu.",
            "",
            "Silakan masukkan kembali nomor pilihan yang benar (1 s.d. 5), atau ketik pertanyaan spesifik Anda secara langsung.",
            "",
            MENU_UTAMA,
          ].join("\n");
        }

        // Deteksi input tidak valid / acak (contoh: 'abcde123', karakter tanpa spasi yang tidak bermakna pertanyaan)
        const isAlphanumericGibberish =
          !cleanText.includes(" ") &&
          /[a-zA-Z]/.test(cleanText) &&
          /\d/.test(cleanText);

        if (isAlphanumericGibberish) {
          return [
            "Mohon maaf, format pesan yang Anda masukkan tidak dikenali.",
            "",
            "Silakan pilih nomor menu yang tersedia (1 s.d. 5), atau ketik pertanyaan seputar data statistik BPS secara lengkap.",
            "",
            MENU_UTAMA,
          ].join("\n");
        }

        // Jika berupa kalimat/teks pertanyaan bebas -> LLM
        setSession(jid, { level: "freetext" });
        return await handleLLMQuery(jid, cleanText);
    }
  }

  // ── 4. Level SUBMENU ──────────────────────────────────────────────────────
  if (session.level === "submenu") {
    const num = parseStrictInt(cleanText);

    // ── 4a. Menu 1: Konten statis ──────────────────────────────────────────
    if (session.menu === 1) {
      if (num >= 1 && num <= 5) return STATIC_M1[num];
      if (isPureNumber) {
        return [
          "Mohon maaf, nomor pilihan yang Anda masukkan tidak tersedia pada sub-menu.",
          "",
          "Silakan masukkan kembali nomor pilihan yang benar sesuai daftar berikut:",
          "",
          SUBMENU[1],
        ].join("\n");
      }
      return await handleLLMQuery(jid, cleanText);
    }

    // ── 4b. Menu 2, 3, 4: Sub-menu dinamis (Kembalikan DATA TEKS STATISTIK LENGKAP tanpa diagram)
    if ([2, 3, 4].includes(session.menu)) {
      const menuData = DATA_MENU[session.menu];

      if (!isNaN(num) && num >= 1 && num <= menuData.maxItem) {
        const item = menuData.items[num];
        const query = item.directQuery || item.queryAll || `Tampilkan seluruh data statistik lengkap resmi BPS Kabupaten Lampung Selatan untuk indikator ${item.label}`;

        console.log(`[DATA-EXEC] Mengambil data teks statistik RAG untuk: ${item.label}`);
        return await handleLLMQuery(jid, query);
      }

      // Jika angka murni tetapi di luar range pilihan sub-menu
      if (isPureNumber) {
        return [
          "Mohon maaf, nomor pilihan yang Anda masukkan tidak tersedia pada sub-menu.",
          "",
          "Silakan masukkan kembali nomor pilihan yang benar sesuai daftar berikut:",
          "",
          SUBMENU[session.menu],
        ].join("\n");
      }

      // Pertanyaan bebas -> LLM
      return await handleLLMQuery(jid, cleanText);
    }
  }

  // ── 5. Level YEAR_SELECT: Pengguna memilih tahun ──────────────────────────
  if (session.level === "year_select") {
    const num      = parseStrictInt(cleanText);
    const years    = session.yearList  || [];
    const maxYears = years.length;

    if (!isNaN(num) && num >= 1 && num <= maxYears) {
      // Pilihan tahun spesifik
      const selectedYear = years[num - 1];
      const query = session.queryYear.replace("{YEAR}", selectedYear);
      console.log(`[YEAR] Tahun dipilih: ${selectedYear} | Query: ${query}`);
      const activeItem = DATA_MENU[session.menu]?.items[session.subItem];
      const chart = activeItem?.chartName;
      const ans = await handleLLMQuery(jid, query);
      return chart ? { text: ans, chartName: chart } : ans;
    }

    if (!isNaN(num) && num === maxYears + 1) {
      // Pilihan "Semua tahun"
      console.log(`[YEAR] Semua tahun | Query: ${session.queryAll}`);
      const activeItem = DATA_MENU[session.menu]?.items[session.subItem];
      const chart = activeItem?.chartName;
      const ans = await handleLLMQuery(jid, session.queryAll);
      return chart ? { text: ans, chartName: chart } : ans;
    }

    // Jika angka murni tetapi di luar range pilihan tahun
    if (isPureNumber) {
      const activeItem = DATA_MENU[session.menu]?.items[session.subItem];
      const label = activeItem ? activeItem.label : "Pilihan Tahun";
      return [
        "Mohon maaf, nomor pilihan yang Anda masukkan tidak tersedia pada daftar tahun.",
        "",
        "Silakan masukkan kembali nomor pilihan yang benar sesuai daftar berikut:",
        "",
        buildYearMenu(label, years),
      ].join("\n");
    }

    // Input berupa teks pertanyaan bebas -> LLM
    return await handleLLMQuery(jid, cleanText);
  }

  // ── 6. Level FREETEXT ─────────────────────────────────────────────────────
  if (session.level === "freetext") {
    return await handleLLMQuery(jid, cleanText);
  }

  // ── 7. Fallback ───────────────────────────────────────────────────────────
  resetToMain(jid);
  return MENU_UTAMA;
}

// ─────────────────────────────────────────────────────────────────────────────
// FILTER NOMOR YANG DIIZINKAN
// ─────────────────────────────────────────────────────────────────────────────
function isAllowed(numberOnly) {
  if (ALLOWED_NUMBERS.length === 0) return true;
  return ALLOWED_NUMBERS.includes(numberOnly);
}

// ─────────────────────────────────────────────────────────────────────────────
// BRIDGE WhatsApp
// ─────────────────────────────────────────────────────────────────────────────
async function startBridge() {
  const { state, saveCreds } = await useMultiFileAuthState("./auth_state");
  const { version }          = await fetchLatestBaileysVersion();
  const fs                   = require("fs");

  const sock = makeWASocket({
    version,
    auth:              state,
    logger:            pino({ level: "silent" }),
    printQRInTerminal: false,
  });

  sock.ev.on("creds.update", saveCreds);

  sock.ev.on("connection.update", (update) => {
    const { connection, lastDisconnect, qr } = update;

    if (qr) {
      console.log("Scan QR ini dengan WhatsApp (Linked Devices):");
      qrcode.generate(qr, { small: true });
    }

    if (connection === "close") {
      const statusCode  = lastDisconnect?.error?.output?.statusCode;
      const isLoggedOut = statusCode === DisconnectReason.loggedOut;

      console.log(
        `Koneksi terputus (Status Code: ${statusCode}).`,
        isLoggedOut ? "Sesi berakhir. Menghapus cache..." : "Mencoba sambung ulang dalam 3 detik..."
      );

      if (isLoggedOut) {
        if (fs.existsSync("./auth_state")) {
          fs.rmSync("./auth_state", { recursive: true, force: true });
        }
        console.log("Sesi lama dihapus. Jalankan 'node index.js' untuk scan QR baru.");
      } else {
        setTimeout(startBridge, 3000);
      }
    } else if (connection === "open") {
      console.log("Terhubung ke WhatsApp.");
    }
  });

  sock.ev.on("messages.upsert", async ({ messages, type }) => {
    if (type !== "notify") return;

    for (const msg of messages) {
      try {
        if (!msg.message || msg.key.fromMe) continue;

        const jid = msg.key.remoteJid;
        if (!jid || jid.endsWith("@g.us")) continue;

        const numberOnly = jid.split("@")[0];
        if (!isAllowed(numberOnly)) continue;

        const text =
          msg.message.conversation ||
          msg.message.extendedTextMessage?.text || "";

        if (!text.trim()) {
          const isMedia =
            msg.message.imageMessage ||
            msg.message.videoMessage ||
            msg.message.audioMessage ||
            msg.message.stickerMessage ||
            msg.message.documentMessage;
          if (isMedia) {
            await sock.sendMessage(jid, {
              text: [
                "Mohon maaf, saat ini kami hanya dapat memproses pesan teks.",
                "",
                "Silakan ketik pertanyaan Anda, atau ketik *menu* untuk melihat pilihan layanan yang tersedia.",
              ].join("\n"),
            });
          }
          continue;
        }

        console.log(`[MSG] dari ${numberOnly}: ${text}`);
        await sock.sendPresenceUpdate("composing", jid);

        // Fitur khusus Admin: Reset Barcode via WA dengan perintah !reset / /reset
        const cleanText = text.trim().toLowerCase();
        if (cleanText === "!reset" || cleanText === "/reset" || cleanText === "reset barcode" || cleanText === "reset qr") {
          await sock.sendMessage(jid, {
            text: " *MENGHAPUS SESI & RESET BARCODE*\n\nSesi WhatsApp sedang dihapus. QR Code / Barcode baru akan segera muncul di terminal server...",
          });
          console.log("[RESET] Perintah reset diterima dari WhatsApp. Menghapus auth_state...");
          setTimeout(() => {
            if (fs.existsSync("./auth_state")) {
              fs.rmSync("./auth_state", { recursive: true, force: true });
            }
            try { sock.end(new Error("Reset requested")); } catch (e) {}
            startBridge();
          }, 1500);
          continue;
        }

        const res       = await processMessage(jid, text);
        const replyText = typeof res === "object" ? res.text : res;

        pushHistory(jid, "user",      text);
        pushHistory(jid, "assistant", replyText);

        // Kirim gambar diagram secara dinamis via API backend jika permintaan diagram
        if (typeof res === "object" && res.chartName) {
          const CHART_API = process.env.CHART_BACKEND_URL || "http://localhost:8001/api/chart";
          try {
            const style = res.chartStyle || "bar";
            console.log(`[CHART] Generate diagram on-demand: ${res.chartName} (style: ${style})`);
            const imgRes = await axios.get(`${CHART_API}/${res.chartName}?style=${style}`, {
              responseType: "arraybuffer",
              timeout: 30000,
            });
            const imgBuffer = Buffer.from(imgRes.data);
            await sock.sendMessage(jid, {
              image: imgBuffer,
              caption: replyText || " Diagram Grafik Data Statistik Resmi BPS Kabupaten Lampung Selatan",
            });
            console.log(`[CHART] Diagram '${res.chartName}' berhasil dikirim.`);
          } catch (chartErr) {
            console.error(`[CHART] Gagal generate diagram '${res.chartName}':`, chartErr.message);
            await sock.sendMessage(jid, { text: replyText });
          }
        } else {
          // Kirim balasan teks biasa jika bukan diagram
          await sock.sendMessage(jid, { text: replyText });
        }
        console.log(`[REPLY] ke ${numberOnly}: ${replyText.substring(0, 100)}...`);
      } catch (err) {
        console.error("[ERROR] Gagal memproses pesan:", err);
      }
    }
  });
}

// ─────────────────────────────────────────────────────────────────────────────
// PROMPT INTERAKTIF TERMINAL (Ketik 'reset' atau 'r' di Terminal untuk Scan QR Baru)
// ─────────────────────────────────────────────────────────────────────────────
const readline = require("readline");
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
});

rl.on("line", (line) => {
  const input = line.trim().toLowerCase();
  if (input === "r" || input === "reset" || input === "qr" || input === "reset barcode") {
    console.log("\n========================================================");
    console.log("  [PERINTAH TERMINAL] RESET SESI & GENERATE BARCODE BARU");
    console.log("========================================================");
    console.log("Menghapus folder sesi auth_state...");

    const fs = require("fs");
    if (fs.existsSync("./auth_state")) {
      fs.rmSync("./auth_state", { recursive: true, force: true });
      console.log(" Folder auth_state berhasil dihapus!");
    } else {
      console.log(" Folder auth_state tidak ditemukan (sudah bersih).");
    }

    console.log("Memulai ulang koneksi untuk memunculkan QR Code / Barcode baru...\n");
    startBridge().catch((err) => {
      console.error("Gagal restart bridge:", err);
    });
  }
});

console.log(" [PETUNJUK TERMINAL] Ketik 'reset' atau 'r' lalu tekan ENTER kapan saja untuk menghapus sesi & scan QR Code baru.");

startBridge().catch((err) => {
  console.error("Gagal memulai bridge:", err);
  process.exit(1);
});

