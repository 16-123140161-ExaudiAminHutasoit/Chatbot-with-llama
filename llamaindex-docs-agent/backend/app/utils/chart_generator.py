"""
chart_generator.py
Menghasilkan diagram statistik BPS secara dinamis (on-demand) dengan berbagai variasi bentuk (Bar, Line, Pie/Donut Chart).
Setiap fungsi mengembalikan BytesIO (bytes gambar PNG) — tidak menyimpan ke file.
"""

import io
import matplotlib
matplotlib.use("Agg")   # Backend non-GUI untuk server
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

# ─── Konstanta Tampilan ──────────────────────────────────────────────────────
FIG_SIZE     = (9.5, 5.2)
DPI          = 150

EXCEL_BLUE   = "#4472C4"
EXCEL_ORANGE = "#ED7D31"
EXCEL_GRAY   = "#A5A5A5"
EXCEL_GREEN  = "#70AD47"
EXCEL_YELLOW = "#FFC000"
EXCEL_PURPLE = "#7030A0"
EXCEL_TEAL   = "#002060"

PALETTE      = [EXCEL_BLUE, EXCEL_ORANGE, EXCEL_GREEN, EXCEL_YELLOW, EXCEL_PURPLE, EXCEL_TEAL, EXCEL_GRAY, "#ED553B", "#3CAEA3", "#F6D55C"]
BG_COLOR     = "#FFFFFF"
GRID_COLOR   = "#D9D9D9"

plt.rcParams["font.sans-serif"] = ["Calibri", "Arial", "DejaVu Sans"]
plt.rcParams["font.family"]     = "sans-serif"


# ─── Helper Style & Output ───────────────────────────────────────────────────
def _style(fig, ax, title=""):
    ax.set_facecolor(BG_COLOR)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(GRID_COLOR)
    ax.spines["bottom"].set_color(GRID_COLOR)
    ax.spines["left"].set_linewidth(0.8)
    ax.spines["bottom"].set_linewidth(0.8)
    ax.grid(True, axis="y", linestyle="-", alpha=0.7, color=GRID_COLOR, linewidth=0.75)
    ax.set_axisbelow(True)
    if title:
        ax.set_title(title, fontsize=11, fontweight="bold", color="#333333", pad=10)


def _to_buf(fig) -> io.BytesIO:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf


# ─── 1. KEMISKINAN ───────────────────────────────────────────────────────────
def chart_kemiskinan(style: str = "bar") -> io.BytesIO:
    years = ["2005","2010","2015","2020","2021","2022","2023","2024","2025"]
    pct   = [26.28, 20.61, 16.27, 14.08, 14.19, 13.14, 12.79, 12.57, 12.05]
    jiwa  = [329200,188000,157700,143330,145850,136210,133670,132380,127740]

    if style in ["pie", "lingkaran", "donut", "donat"]:
        fig, ax = plt.subplots(figsize=FIG_SIZE, dpi=DPI)
        fig.patch.set_facecolor(BG_COLOR)
        recent_years = ["2020", "2021", "2022", "2023", "2024", "2025"]
        recent_jiwa  = [143330, 145850, 136210, 133670, 132380, 127740]
        plt.suptitle("Proporsi Penduduk Miskin per Tahun (2020–2025) [Diagram Lingkaran]",
                     fontsize=12, fontweight="bold", color="#262626", y=0.97)
        wedges, texts, autotexts = ax.pie(
            recent_jiwa, labels=[f"Thn {y}" for y in recent_years], autopct="%1.1f%%", startangle=140,
            colors=PALETTE[:len(recent_years)], wedgeprops=dict(width=0.45, edgecolor="white")
        )
        plt.setp(autotexts, size=9, weight="bold", color="white")
        plt.setp(texts, size=9.5)
        plt.figtext(0.5, 0.01, "Sumber: BPS Kabupaten Lampung Selatan", ha="center", fontsize=8.5, color="#595959")
        plt.tight_layout(rect=[0, 0.04, 1, 0.95])
        return _to_buf(fig)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=FIG_SIZE, dpi=DPI, sharex=True)
    fig.patch.set_facecolor(BG_COLOR)

    if style in ["line", "garis"]:
        plt.suptitle("Tren Indikator Kemiskinan Lampung Selatan (2005–2025) [Grafik Garis]",
                     fontsize=12, fontweight="bold", color="#262626", y=0.98)
        _style(fig, ax1, "Tingkat Kemiskinan (%)")
        ax1.plot(years, pct, color=EXCEL_BLUE, marker="o", linewidth=2.5, markersize=6, zorder=4)
        ax1.set_ylim(0, 32)
        for i, v in enumerate(pct):
            ax1.annotate(f"{v:.2f}%".replace(".",","), (years[i], pct[i]),
                        textcoords="offset points", xytext=(0,8), ha="center", fontsize=8.5)

        _style(fig, ax2, "Jumlah Penduduk Miskin (Jiwa)")
        ax2.plot(years, jiwa, color=EXCEL_ORANGE, marker="s", linewidth=2.5, markersize=6, zorder=4)
        ax2.set_ylim(0, 380000)
        ax2.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x,p: f"{int(x):,}".replace(",",".")))
        for i, v in enumerate(jiwa):
            ax2.annotate(f"{v:,}".replace(",","."), (years[i], jiwa[i]),
                        textcoords="offset points", xytext=(0,8), ha="center", fontsize=8.5)
    else:
        plt.suptitle("Indikator Kemiskinan Kabupaten Lampung Selatan (2005–2025)",
                     fontsize=12, fontweight="bold", color="#262626", y=0.98)
        _style(fig, ax1, "Tingkat Kemiskinan (%)")
        bars1 = ax1.bar(years, pct, color=EXCEL_BLUE, width=0.55, zorder=3)
        ax1.set_ylim(0, 32)
        ax1.tick_params(labelsize=9, colors="#595959")
        for b, v in zip(bars1, pct):
            ax1.text(b.get_x()+b.get_width()/2, b.get_height()+0.8,
                     f"{v:.2f}%".replace(".",","), ha="center", fontsize=8.5, color="#262626")

        _style(fig, ax2, "Jumlah Penduduk Miskin (Jiwa)")
        bars2 = ax2.bar(years, jiwa, color=EXCEL_ORANGE, width=0.55, zorder=3)
        ax2.set_ylim(0, 380000)
        ax2.tick_params(labelsize=9, colors="#595959")
        ax2.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x,p: f"{int(x):,}".replace(",",".")))
        for b, v in zip(bars2, jiwa):
            ax2.text(b.get_x()+b.get_width()/2, b.get_height()+8000,
                     f"{v:,}".replace(",","."), ha="center", fontsize=8.5, color="#262626")

    plt.figtext(0.5, 0.01, "Sumber: BPS Kabupaten Lampung Selatan", ha="center", fontsize=8.5, color="#595959")
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    return _to_buf(fig)


# ─── 2. PENDUDUK ─────────────────────────────────────────────────────────────
def chart_penduduk(style: str = "bar") -> io.BytesIO:
    years    = ["2017","2018","2020","2021","2022","2023","2024","2025"]
    pop_jiwa = [992760,1002290,1064300,1071700,1081100,1101400,1124680,1146070]

    fig, ax = plt.subplots(figsize=FIG_SIZE, dpi=DPI)
    fig.patch.set_facecolor(BG_COLOR)

    if style in ["pie", "lingkaran", "donut", "donat"]:
        recent_years = ["2020", "2021", "2022", "2023", "2024", "2025"]
        recent_pop   = [1064300, 1071700, 1081100, 1101400, 1124680, 1146070]
        plt.suptitle("Proporsi Penduduk Lampung Selatan per Tahun (2020–2025) [Diagram Lingkaran]",
                     fontsize=12, fontweight="bold", color="#262626", y=0.97)
        wedges, texts, autotexts = ax.pie(
            recent_pop, labels=[f"Thn {y}" for y in recent_years], autopct="%1.1f%%", startangle=140,
            colors=PALETTE[:len(recent_years)], wedgeprops=dict(width=0.45, edgecolor="white")
        )
        plt.setp(autotexts, size=9, weight="bold", color="white")
        plt.setp(texts, size=9.5)
    elif style in ["line", "garis"]:
        _style(fig, ax)
        plt.suptitle("Tren Pertumbuhan Penduduk Lampung Selatan (2017–2025) [Grafik Garis]",
                     fontsize=12, fontweight="bold", color="#262626", y=0.97)
        ax.plot(years, pop_jiwa, color=EXCEL_BLUE, marker="o", linewidth=2.5, markersize=7, zorder=4)
        ax.fill_between(years, pop_jiwa, color=EXCEL_BLUE, alpha=0.15)
        ax.set_ylim(800000, 1220000)
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x,p: f"{int(x):,}".replace(",",".")))
        for i, v in enumerate(pop_jiwa):
            ax.annotate(f"{v:,}".replace(",","."), (years[i], pop_jiwa[i]),
                        textcoords="offset points", xytext=(0,8), ha="center", fontsize=8.5)
        ax.legend(["Jumlah Penduduk (Jiwa)"], loc="upper center", bbox_to_anchor=(0.5,-0.12), frameon=False, fontsize=9.5)
    else:
        _style(fig, ax)
        plt.suptitle("Jumlah Penduduk Kabupaten Lampung Selatan (2017–2025)",
                     fontsize=12, fontweight="bold", color="#262626", y=0.97)
        bars = ax.bar(years, pop_jiwa, color=EXCEL_BLUE, width=0.55, zorder=3)
        ax.set_ylim(800000, 1220000)
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x,p: f"{int(x):,}".replace(",",".")))
        for b, v in zip(bars, pop_jiwa):
            ax.text(b.get_x()+b.get_width()/2, b.get_height()+7000,
                    f"{v:,}".replace(",","."), ha="center", fontsize=8.5, color="#262626")
        ax.legend(["Jumlah Penduduk (Jiwa)"], loc="upper center", bbox_to_anchor=(0.5,-0.12), frameon=False, fontsize=9.5)

    plt.figtext(0.5, 0.01, "Sumber: BPS & Disdukcapil Kabupaten Lampung Selatan", ha="center", fontsize=8.5, color="#595959")
    plt.tight_layout(rect=[0, 0.04, 1, 0.95])
    return _to_buf(fig)


# ─── 3. LAJU EKONOMI ─────────────────────────────────────────────────────────
def chart_laju_ekonomi(style: str = "bar") -> io.BytesIO:
    years  = ["2011","2012","2013","2014","2015","2016","2017","2018","2019","2020","2021","2022","2023","2024"]
    growth = [5.81, 5.96, 6.41, 5.80, 5.38, 5.22, 5.46, 5.23, 5.13, -1.73, 2.60, 4.81, 4.82, 4.62]

    fig, ax = plt.subplots(figsize=FIG_SIZE, dpi=DPI)
    fig.patch.set_facecolor(BG_COLOR)

    if style in ["pie", "lingkaran", "donut", "donat"]:
        recent_years = ["2019", "2020", "2021", "2022", "2023", "2024"]
        recent_g     = [5.13, 1.73, 2.60, 4.81, 4.82, 4.62]  # Gunakan nilai absolut untuk pie
        plt.suptitle("Perbandingan Pertumbuhan Ekonomi 6 Tahun Terakhir [Diagram Lingkaran]",
                     fontsize=12, fontweight="bold", color="#262626", y=0.97)
        wedges, texts, autotexts = ax.pie(
            recent_g, labels=[f"Thn {y}" for y in recent_years], autopct="%1.1f%%", startangle=140,
            colors=PALETTE[:len(recent_years)], wedgeprops=dict(width=0.45, edgecolor="white")
        )
        plt.setp(autotexts, size=9, weight="bold", color="white")
        plt.setp(texts, size=9.5)
    elif style in ["line", "garis"]:
        _style(fig, ax)
        plt.suptitle("Tren Laju Pertumbuhan Ekonomi PDRB Lampung Selatan [Grafik Garis]",
                     fontsize=12, fontweight="bold", color="#262626", y=0.97)
        ax.plot(years, growth, color=EXCEL_BLUE, marker="o", linewidth=2.5, markersize=6, zorder=4)
        ax.axhline(0, color=GRID_COLOR, linewidth=1.0, zorder=2)
        ax.set_ylim(-3.5, 8.5)
        for i, v in enumerate(growth):
            offset = 8 if v >= 0 else -14
            ax.annotate(f"{v:.2f}%".replace(".",","), (years[i], growth[i]),
                        textcoords="offset points", xytext=(0,offset), ha="center", fontsize=8)
        ax.legend(["Laju Pertumbuhan Ekonomi (%)"], loc="upper center", bbox_to_anchor=(0.5,-0.12), frameon=False, fontsize=9.5)
    else:
        _style(fig, ax)
        plt.suptitle("Laju Pertumbuhan Ekonomi PDRB Lampung Selatan (2011–2024)",
                     fontsize=12, fontweight="bold", color="#262626", y=0.97)
        colors = [EXCEL_ORANGE if g < 0 else EXCEL_BLUE for g in growth]
        bars = ax.bar(years, growth, color=colors, width=0.55, zorder=3)
        ax.axhline(0, color=GRID_COLOR, linewidth=1.0, zorder=2)
        ax.set_ylim(-3.5, 8.5)
        for b, v in zip(bars, growth):
            offset = 0.3 if v >= 0 else -0.6
            ax.text(b.get_x()+b.get_width()/2, v+offset,
                    f"{v:.2f}%".replace(".",","), ha="center", fontsize=8, color="#262626")
        ax.legend(["Laju Pertumbuhan Ekonomi (%)"], loc="upper center", bbox_to_anchor=(0.5,-0.12), frameon=False, fontsize=9.5)

    plt.figtext(0.5, 0.01, "Sumber: BPS Kabupaten Lampung Selatan", ha="center", fontsize=8.5, color="#595959")
    plt.tight_layout(rect=[0, 0.04, 1, 0.95])
    return _to_buf(fig)


# ─── 4. IPM ──────────────────────────────────────────────────────────────────
def chart_ipm(style: str = "bar") -> io.BytesIO:
    years = ["2010","2015","2018","2019","2020","2021","2022","2023","2024"]
    ipm   = [63.14, 66.21, 67.89, 68.34, 68.39, 68.61, 69.41, 70.82, 71.60]

    fig, ax = plt.subplots(figsize=FIG_SIZE, dpi=DPI)
    fig.patch.set_facecolor(BG_COLOR)

    if style in ["pie", "lingkaran", "donut", "donat"]:
        recent_years = ["2019","2020","2021","2022","2023","2024"]
        recent_ipm   = [68.34, 68.39, 68.61, 69.41, 70.82, 71.60]
        plt.suptitle("Proporsi IPM Lampung Selatan (2019–2024) [Diagram Lingkaran]",
                     fontsize=12, fontweight="bold", color="#262626", y=0.97)
        wedges, texts, autotexts = ax.pie(
            recent_ipm, labels=[f"Thn {y}" for y in recent_years], autopct="%1.1f%%", startangle=140,
            colors=PALETTE[:len(recent_years)], wedgeprops=dict(width=0.45, edgecolor="white")
        )
        plt.setp(autotexts, size=9, weight="bold", color="white")
        plt.setp(texts, size=9.5)
    elif style in ["bar", "batang"]:
        _style(fig, ax)
        plt.suptitle("Indeks Pembangunan Manusia (IPM) Lampung Selatan [Diagram Batang]",
                     fontsize=12, fontweight="bold", color="#262626", y=0.97)
        bars = ax.bar(years, ipm, color=EXCEL_BLUE, width=0.55, zorder=3)
        ax.set_ylim(50, 78)
        for b, v in zip(bars, ipm):
            ax.text(b.get_x()+b.get_width()/2, b.get_height()+0.8,
                    f"{v:.2f}".replace(".",","), ha="center", fontsize=8.5, color="#262626")
        ax.legend(["IPM Kabupaten Lampung Selatan"], loc="upper center", bbox_to_anchor=(0.5,-0.12), frameon=False, fontsize=9.5)
    else:
        _style(fig, ax)
        plt.suptitle("Indeks Pembangunan Manusia (IPM) Lampung Selatan (2010–2024)",
                     fontsize=12, fontweight="bold", color="#262626", y=0.97)
        ax.plot(years, ipm, color=EXCEL_BLUE, marker="o", linewidth=2.5, markersize=7, zorder=4)
        ax.fill_between(years, ipm, color=EXCEL_BLUE, alpha=0.12)
        ax.set_ylim(60, 75)
        for i, v in enumerate(ipm):
            ax.annotate(f"{v:.2f}".replace(".",","), (years[i], v),
                        textcoords="offset points", xytext=(0,8), ha="center", fontsize=8.5)
        ax.legend(["IPM Kabupaten Lampung Selatan"], loc="upper center", bbox_to_anchor=(0.5,-0.12), frameon=False, fontsize=9.5)

    plt.figtext(0.5, 0.01, "Sumber: BPS Kabupaten Lampung Selatan", ha="center", fontsize=8.5, color="#595959")
    plt.tight_layout(rect=[0, 0.04, 1, 0.95])
    return _to_buf(fig)


# ─── 5. KETENAGAKERJAAN ──────────────────────────────────────────────────────
def chart_ketenagakerjaan(style: str = "bar") -> io.BytesIO:
    years = ["2015","2018","2020","2021","2022","2023","2024"]
    tpak  = [67.8, 69.2, 69.5, 70.1, 70.8, 71.4, 72.1]
    tpt   = [5.82, 5.12, 5.41, 5.25, 4.89, 4.62, 4.38]

    if style in ["pie", "lingkaran", "donut", "donat"]:
        fig, ax = plt.subplots(figsize=FIG_SIZE, dpi=DPI)
        fig.patch.set_facecolor(BG_COLOR)
        # Diagram lingkaran untuk komposisi angkatan kerja vs bukan angkatan kerja 2024
        vals   = [72.1, 27.9]
        labels = ["Bekerja / Cari Kerja (TPAK 72,1%)", "Bukan Angkatan Kerja (27,9%)"]
        plt.suptitle("Komposisi Angkatan Kerja Lampung Selatan (2024) [Diagram Lingkaran]",
                     fontsize=12, fontweight="bold", color="#262626", y=0.97)
        wedges, texts, autotexts = ax.pie(
            vals, labels=labels, autopct="%1.1f%%", startangle=140,
            colors=[EXCEL_BLUE, EXCEL_ORANGE], wedgeprops=dict(width=0.45, edgecolor="white")
        )
        plt.setp(autotexts, size=10, weight="bold", color="white")
        plt.setp(texts, size=9.5)
        plt.figtext(0.5, 0.01, "Sumber: BPS Kabupaten Lampung Selatan", ha="center", fontsize=8.5, color="#595959")
        plt.tight_layout(rect=[0, 0.04, 1, 0.95])
        return _to_buf(fig)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=FIG_SIZE, dpi=DPI, sharex=True)
    fig.patch.set_facecolor(BG_COLOR)

    if style in ["line", "garis"]:
        plt.suptitle("Tren Ketenagakerjaan Lampung Selatan (2015–2024) [Grafik Garis]",
                     fontsize=12, fontweight="bold", color="#262626", y=0.98)
        _style(fig, ax1, "Tingkat Partisipasi Angkatan Kerja (TPAK %)")
        ax1.plot(years, tpak, color=EXCEL_BLUE, marker="o", linewidth=2.5, zorder=4)
        ax1.set_ylim(60, 78)
        for i, v in enumerate(tpak):
            ax1.annotate(f"{v:.1f}%".replace(".",","), (years[i], tpak[i]), textcoords="offset points", xytext=(0,6), ha="center", fontsize=8.5)

        _style(fig, ax2, "Tingkat Pengangguran Terbuka (TPT %)")
        ax2.plot(years, tpt, color=EXCEL_ORANGE, marker="s", linewidth=2.5, zorder=4)
        ax2.set_ylim(3, 7)
        for i, v in enumerate(tpt):
            ax2.annotate(f"{v:.2f}%".replace(".",","), (years[i], tpt[i]), textcoords="offset points", xytext=(0,6), ha="center", fontsize=8.5)
    else:
        plt.suptitle("Indikator Ketenagakerjaan Lampung Selatan (2015–2024)",
                     fontsize=12, fontweight="bold", color="#262626", y=0.98)
        _style(fig, ax1, "Tingkat Partisipasi Angkatan Kerja (TPAK %)")
        bars1 = ax1.bar(years, tpak, color=EXCEL_BLUE, width=0.55, zorder=3)
        ax1.set_ylim(0, 85)
        for b, v in zip(bars1, tpak):
            ax1.text(b.get_x()+b.get_width()/2, b.get_height()+1.8, f"{v:.1f}%".replace(".",","), ha="center", fontsize=8.5, color="#262626")

        _style(fig, ax2, "Tingkat Pengangguran Terbuka (TPT %)")
        bars2 = ax2.bar(years, tpt, color=EXCEL_ORANGE, width=0.55, zorder=3)
        ax2.set_ylim(0, 8)
        for b, v in zip(bars2, tpt):
            ax2.text(b.get_x()+b.get_width()/2, b.get_height()+0.25, f"{v:.2f}%".replace(".",","), ha="center", fontsize=8.5, color="#262626")

    plt.figtext(0.5, 0.01, "Sumber: BPS Kabupaten Lampung Selatan", ha="center", fontsize=8.5, color="#595959")
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    return _to_buf(fig)


# ─── 6. PERSENTASE PENDUDUK ──────────────────────────────────────────────────
def chart_persentase_penduduk(style: str = "bar") -> io.BytesIO:
    kec = ["Natar","Jati Agung","Kalianda","Tanjung Bintang","Katibung","Sidomulyo","Candipuro","Lainnya"]
    pct = [18.12, 11.60, 8.89, 7.98, 6.79, 6.18, 5.42, 35.02]

    fig, ax = plt.subplots(figsize=FIG_SIZE, dpi=DPI)
    fig.patch.set_facecolor(BG_COLOR)

    if style in ["pie", "lingkaran", "donut", "donat"] or True:  # Default terbaik persentase
        if style not in ["bar", "batang", "line", "garis"]:
            plt.suptitle("Persentase Distribusi Penduduk per Kecamatan (2025) [Diagram Lingkaran]",
                         fontsize=12, fontweight="bold", color="#262626", y=0.97)
            wedges, texts, autotexts = ax.pie(
                pct, labels=kec, autopct="%1.1f%%", startangle=140,
                colors=PALETTE[:len(kec)], wedgeprops=dict(width=0.45, edgecolor="white")
            )
            plt.setp(autotexts, size=8.5, weight="bold", color="white")
            plt.setp(texts, size=9)
            plt.figtext(0.5, 0.01, "Sumber: Disdukcapil & BPS Kabupaten Lampung Selatan", ha="center", fontsize=8.5, color="#595959")
            plt.tight_layout(rect=[0, 0.04, 1, 0.95])
            return _to_buf(fig)

    _style(fig, ax)
    plt.suptitle("Persentase Distribusi Penduduk per Kecamatan (2025)",
                 fontsize=12, fontweight="bold", color="#262626", y=0.97)
    bars = ax.bar(kec, pct, color=EXCEL_BLUE, width=0.55, zorder=3)
    ax.set_ylim(0, 42)
    ax.tick_params(labelsize=9, colors="#595959")
    for b, v in zip(bars, pct):
        ax.text(b.get_x()+b.get_width()/2, b.get_height()+0.8,
                f"{v:.2f}%".replace(".",","), ha="center", fontsize=8.5, color="#262626")

    plt.figtext(0.5, 0.01, "Sumber: Disdukcapil & BPS Kabupaten Lampung Selatan", ha="center", fontsize=8.5, color="#595959")
    plt.tight_layout(rect=[0, 0.04, 1, 0.95])
    return _to_buf(fig)


# Fallback generator universal pendukung Bar, Line, dan Pie
def _generic_chart(title: str, labels: list, values: list, style: str = "bar") -> io.BytesIO:
    fig, ax = plt.subplots(figsize=FIG_SIZE, dpi=DPI)
    fig.patch.set_facecolor(BG_COLOR)

    if style in ["pie", "lingkaran", "donut", "donat"]:
        plt.suptitle(f"{title} [Diagram Lingkaran]", fontsize=12, fontweight="bold", color="#262626", y=0.97)
        # Ambil max 6 data teratas untuk pie chart agar tidak sesak
        use_labels = labels[-6:] if len(labels) > 6 else labels
        use_values = values[-6:] if len(values) > 6 else values
        wedges, texts, autotexts = ax.pie(
            use_values, labels=[str(l) for l in use_labels], autopct="%1.1f%%", startangle=140,
            colors=PALETTE[:len(use_labels)], wedgeprops=dict(width=0.45, edgecolor="white")
        )
        plt.setp(autotexts, size=8.5, weight="bold", color="white")
        plt.setp(texts, size=9)
    elif style in ["line", "garis"]:
        _style(fig, ax)
        plt.suptitle(f"{title} [Grafik Garis]", fontsize=12, fontweight="bold", color="#262626", y=0.97)
        ax.plot(labels, values, color=EXCEL_BLUE, marker="o", linewidth=2.5, markersize=6, zorder=4)
        for i, v in enumerate(values):
            ax.annotate(str(v), (labels[i], values[i]), textcoords="offset points", xytext=(0,6), ha="center", fontsize=8.5)
    else:
        _style(fig, ax)
        plt.suptitle(title, fontsize=12, fontweight="bold", color="#262626", y=0.97)
        bars = ax.bar(labels, values, color=EXCEL_BLUE, width=0.55, zorder=3)
        for b, v in zip(bars, values):
            ax.text(b.get_x()+b.get_width()/2, b.get_height()+0.02*max(values), str(v), ha="center", fontsize=8.5)

    plt.figtext(0.5, 0.01, "Sumber: BPS Kabupaten Lampung Selatan", ha="center", fontsize=8.5, color="#595959")
    plt.tight_layout(rect=[0, 0.04, 1, 0.95])
    return _to_buf(fig)


def chart_apk(style: str = "bar") -> io.BytesIO:
    return _generic_chart("Angka Partisipasi Kasar (APK) Pendidikan (2015–2024)",
                          ["2015","2019","2020","2021","2022","2023","2024"],
                          [117.14,104.86,102.92,102.17,102.85,103.48,107.79], style=style)

def chart_apm(style: str = "bar") -> io.BytesIO:
    return _generic_chart("Angka Partisipasi Murni (APM) Pendidikan (2015–2024)",
                          ["2015","2019","2020","2021","2022","2023","2024"],
                          [97.85,98.12,98.45,98.67,98.90,99.12,99.35], style=style)

def chart_gini_ratio(style: str = "bar") -> io.BytesIO:
    return _generic_chart("Gini Ratio Kabupaten Lampung Selatan (2011–2025)",
                          ["2011","2013","2015","2017","2019","2020","2021","2022","2023","2024","2025"],
                          [0.302, 0.350, 0.348, 0.300, 0.331, 0.299, 0.268, 0.260, 0.257, 0.253, 0.239], style=style)

def chart_pdrb_adhb(style: str = "bar") -> io.BytesIO:
    return _generic_chart("Total PDRB ADHB Lampung Selatan (2010–2025)",
                          ["2010","2015","2020","2023","2024","2025"],
                          [18535.51, 31412.78, 44293.00, 55994.57, 60320.74, 65658.66], style=style)

def chart_pdrb_adhk(style: str = "bar") -> io.BytesIO:
    return _generic_chart("Total PDRB ADHK Riil Lampung Selatan (2010–2025)",
                          ["2010","2015","2020","2023","2024","2025"],
                          [18535.51, 24012.30, 29850.40, 34210.15, 35790.80, 37540.20], style=style)

def chart_kepadatan_penduduk(style: str = "bar") -> io.BytesIO:
    return _generic_chart("Kepadatan Penduduk per Kecamatan (Tahun 2025)",
                          ["Natar","Jati Agung","Candipuro","Tanjung Bintang","Kalianda","Sidomulyo","Katibung","Lainnya"],
                          [972, 808, 734, 705, 631, 578, 443, 420], style=style)

def chart_laju_penduduk(style: str = "bar") -> io.BytesIO:
    return _generic_chart("Laju Pertumbuhan Penduduk Lampung Selatan (2018–2025)",
                          ["2018","2020","2021","2022","2023","2024","2025"],
                          [0.96, 1.25, 0.69, 0.88, 1.88, 2.11, 1.90], style=style)

def chart_piramida_penduduk(style: str = "bar") -> io.BytesIO:
    return _generic_chart("Struktur Kelompok Umur Penduduk (Tahun 2025)",
                          ["0-4","5-9","10-14","15-19","20-24","25-29","30-34","35-39","40-44","45-49","50-54","55-59","60-64","65+"],
                          [76857,100826,103825,90683,88670,89237,83847,83634,89567,83321,69296,54834,46342,85135], style=style)

def chart_proyeksi_penduduk(style: str = "bar") -> io.BytesIO:
    return _generic_chart("Proyeksi Penduduk Kabupaten Lampung Selatan (2020–2025)",
                          ["2020","2021","2022","2023","2024","2025"],
                          [1064300,1071700,1081100,1101400,1124680,1146070], style=style)

def chart_sex_ratio(style: str = "bar") -> io.BytesIO:
    return _generic_chart("Rasio Jenis Kelamin (Sex Ratio) Lampung Selatan (2017–2024)",
                          ["2017","2018","2020","2021","2022","2023","2024"],
                          [104.2, 104.1, 103.8, 103.9, 104.0, 104.3, 104.5], style=style)

def chart_pdrb_pengeluaran_adhb(style: str = "bar") -> io.BytesIO:
    return _generic_chart("PDRB Pengeluaran ADHB Lampung Selatan (2010–2025)",
                          ["2010","2015","2020","2023","2024","2025"],
                          [18535.51, 31412.78, 44293.00, 55994.57, 60320.74, 65658.66], style=style)

def chart_pdrb_pengeluaran_adhk(style: str = "bar") -> io.BytesIO:
    return _generic_chart("PDRB Pengeluaran ADHK Riil Lampung Selatan (2010–2025)",
                          ["2010","2015","2020","2023","2024","2025"],
                          [18535.51, 24654.68, 29743.30, 33528.67, 35077.05, 37081.66], style=style)

def chart_pdrb_pengeluaran(style: str = "bar") -> io.BytesIO:
    return chart_pdrb_pengeluaran_adhb(style=style)


# Dispatcher Map
CHART_MAP = {
    "chart_kemiskinan":            chart_kemiskinan,
    "chart_penduduk":              chart_penduduk,
    "chart_laju_ekonomi":          chart_laju_ekonomi,
    "chart_ipm":                   chart_ipm,
    "chart_ketenagakerjaan":       chart_ketenagakerjaan,
    "chart_apk":                   chart_apk,
    "chart_apm":                   chart_apm,
    "chart_gini_ratio":            chart_gini_ratio,
    "chart_pdrb_adhb":             chart_pdrb_adhb,
    "chart_pdrb_adhk":             chart_pdrb_adhk,
    "chart_kepadatan_penduduk":    chart_kepadatan_penduduk,
    "chart_laju_penduduk":         chart_laju_penduduk,
    "chart_persentase_penduduk":   chart_persentase_penduduk,
    "chart_piramida_penduduk":     chart_piramida_penduduk,
    "chart_proyeksi_penduduk":     chart_proyeksi_penduduk,
    "chart_sex_ratio":             chart_sex_ratio,
    "chart_pdrb_pengeluaran":      chart_pdrb_pengeluaran,
    "chart_pdrb_pengeluaran_adhb": chart_pdrb_pengeluaran_adhb,
    "chart_pdrb_pengeluaran_adhk": chart_pdrb_pengeluaran_adhk,
}


def generate_chart(name: str, style: str = "bar") -> io.BytesIO | None:
    fn = CHART_MAP.get(name)
    if fn is None:
        return None
    return fn(style=style)
