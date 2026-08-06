import os
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

CHART_DIR = r"C:\Chatbot\wa-bridge\charts"
os.makedirs(CHART_DIR, exist_ok=True)

FIG_SIZE = (9.5, 5.2)
DPI = 300

EXCEL_BLUE = "#4472C4"
EXCEL_ORANGE = "#ED7D31"
EXCEL_GRAY = "#A5A5A5"
EXCEL_GREEN = "#70AD47"
EXCEL_YELLOW = "#FFC000"

BG_COLOR = "#FFFFFF"
GRID_COLOR = "#D9D9D9"

plt.rcParams['font.sans-serif'] = ['Calibri', 'Aptos', 'Arial']
plt.rcParams['font.family'] = 'sans-serif'


def set_chart_style(fig, ax, title=""):
    ax.set_facecolor(BG_COLOR)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#D9D9D9')
    ax.spines['bottom'].set_color('#D9D9D9')
    ax.spines['left'].set_linewidth(0.8)
    ax.spines['bottom'].set_linewidth(0.8)
    ax.grid(True, axis='y', linestyle='-', alpha=0.7, color=GRID_COLOR, linewidth=0.75)
    ax.set_axisbelow(True)
    if title:
        ax.set_title(title, fontsize=11, fontweight='bold', color='#333333', loc='center', pad=10)


def create_kemiskinan_chart():
    years = ['2005', '2010', '2015', '2020', '2021', '2022', '2023', '2024', '2025']
    pct = [26.28, 20.61, 16.27, 14.08, 14.19, 13.14, 12.79, 12.57, 12.05]
    jiwa = [329200, 188000, 157700, 143330, 145850, 136210, 133670, 132380, 127740]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=FIG_SIZE, dpi=DPI, sharex=True)
    fig.patch.set_facecolor(BG_COLOR)

    plt.suptitle("Indikator Kemiskinan Kabupaten Lampung Selatan (2005 - 2025)", fontsize=12, fontweight='bold', color='#262626', y=0.98)

    set_chart_style(fig, ax1, "Tingkat Kemiskinan (%)")
    bars1 = ax1.bar(years, pct, color=EXCEL_BLUE, width=0.55, zorder=3)
    ax1.set_ylim(0, 32)
    ax1.tick_params(axis='both', labelsize=9, colors='#595959')

    for bar, val in zip(bars1, pct):
        yval = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width() / 2.0, yval + 0.8, f"{str(val).replace('.', ',')}%", ha='center', va='bottom', fontsize=8.5, color='#262626')

    set_chart_style(fig, ax2, "Jumlah Penduduk Miskin (Jiwa)")
    bars2 = ax2.bar(years, jiwa, color=EXCEL_ORANGE, width=0.55, zorder=3)
    ax2.set_ylim(0, 380000)
    ax2.tick_params(axis='both', labelsize=9, colors='#595959')
    ax2.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"{int(x):,}".replace(',', '.')))

    for bar, val in zip(bars2, jiwa):
        yval = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width() / 2.0, yval + 8000, f"{val:,}".replace(',', '.'), ha='center', va='bottom', fontsize=8.5, color='#262626')

    plt.figtext(0.5, 0.01, "Sumber: BPS Kabupaten Lampung Selatan", ha="center", fontsize=8.5, color='#595959')
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig(os.path.join(CHART_DIR, "chart_kemiskinan.png"))
    plt.close()


def create_penduduk_chart():
    years = ['2017', '2018', '2020', '2021', '2022', '2023', '2024', '2025']
    pop_jiwa = [992760, 1002290, 1064300, 1071700, 1081100, 1101400, 1124680, 1146070]

    fig, ax = plt.subplots(figsize=FIG_SIZE, dpi=DPI)
    fig.patch.set_facecolor(BG_COLOR)
    set_chart_style(fig, ax)

    plt.suptitle("Jumlah Penduduk Kabupaten Lampung Selatan (2017 - 2025)", fontsize=12, fontweight='bold', color='#262626', y=0.97)

    bars = ax.bar(years, pop_jiwa, color=EXCEL_BLUE, width=0.55, zorder=3, label='Jumlah Penduduk (Jiwa)')
    ax.tick_params(axis='both', labelsize=9, colors='#595959')
    ax.set_ylim(800000, 1220000)
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"{int(x):,}".replace(',', '.')))

    for bar, val in zip(bars, pop_jiwa):
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2.0, yval + 7000, f"{val:,}".replace(',', '.'), ha='center', va='bottom', fontsize=8.5, color='#262626')

    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.12), ncol=1, frameon=False, fontsize=9.5)
    plt.figtext(0.5, 0.01, "Sumber: BPS & Disdukcapil Kabupaten Lampung Selatan", ha="center", fontsize=8.5, color='#595959')

    plt.tight_layout(rect=[0, 0.04, 1, 0.95])
    plt.savefig(os.path.join(CHART_DIR, "chart_penduduk.png"))
    plt.close()


def create_laju_ekonomi_chart():
    years = ['2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019', '2020', '2021', '2022', '2023', '2024']
    growth = [5.81, 5.96, 6.41, 5.80, 5.38, 5.22, 5.46, 5.23, 5.13, -1.73, 2.60, 4.81, 4.82, 4.62]

    fig, ax = plt.subplots(figsize=FIG_SIZE, dpi=DPI)
    fig.patch.set_facecolor(BG_COLOR)
    set_chart_style(fig, ax)

    plt.suptitle("Laju Pertumbuhan Ekonomi PDRB Kabupaten Lampung Selatan (2011 - 2024)", fontsize=12, fontweight='bold', color='#262626', y=0.97)

    colors = [EXCEL_ORANGE if g < 0 else EXCEL_BLUE for g in growth]
    bars = ax.bar(years, growth, color=colors, width=0.55, zorder=3, label='Laju Pertumbuhan Ekonomi (%)')

    ax.axhline(0, color='#D9D9D9', linewidth=1.0, zorder=2)
    ax.tick_params(axis='both', labelsize=9, colors='#595959')
    ax.set_ylim(-3.5, 8.5)

    for bar, val in zip(bars, growth):
        yval = bar.get_height()
        va_val = 'bottom' if yval >= 0 else 'top'
        offset = 0.3 if yval >= 0 else -0.6
        ax.text(bar.get_x() + bar.get_width() / 2.0, yval + offset, f"{val:.2f}".replace('.', ',') + "%", ha='center', va=va_val, fontsize=8, color='#262626')

    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.12), ncol=1, frameon=False, fontsize=9.5)
    plt.figtext(0.5, 0.01, "Sumber: BPS Kabupaten Lampung Selatan", ha="center", fontsize=8.5, color='#595959')

    plt.tight_layout(rect=[0, 0.04, 1, 0.95])
    plt.savefig(os.path.join(CHART_DIR, "chart_laju_ekonomi.png"))
    plt.close()


def create_ipm_chart():
    years = ['2010', '2015', '2018', '2019', '2020', '2021', '2022', '2023', '2024']
    ipm = [63.14, 66.21, 67.89, 68.34, 68.39, 68.61, 69.41, 70.82, 71.60]

    fig, ax = plt.subplots(figsize=FIG_SIZE, dpi=DPI)
    fig.patch.set_facecolor(BG_COLOR)
    set_chart_style(fig, ax)

    plt.suptitle("Indeks Pembangunan Manusia (IPM) Kabupaten Lampung Selatan (2010 - 2024)", fontsize=12, fontweight='bold', color='#262626', y=0.97)

    ax.plot(years, ipm, color=EXCEL_BLUE, marker='o', linewidth=2.2, markersize=6, label='IPM Kabupaten Lampung Selatan', zorder=4)
    ax.tick_params(axis='both', labelsize=9, colors='#595959')
    ax.set_ylim(60, 75)

    for i, txt in enumerate(ipm):
        ax.annotate(f"{txt:.2f}".replace('.', ','), (years[i], ipm[i]), textcoords="offset points", xytext=(0, 8), ha='center', va='bottom', fontsize=8.5, color='#262626', zorder=10)

    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.12), ncol=1, frameon=False, fontsize=9.5)
    plt.figtext(0.5, 0.01, "Sumber: BPS Kabupaten Lampung Selatan", ha="center", fontsize=8.5, color='#595959')

    plt.tight_layout(rect=[0, 0.04, 1, 0.95])
    plt.savefig(os.path.join(CHART_DIR, "chart_ipm.png"))
    plt.close()


def create_ketenagakerjaan_chart():
    years = ['2015', '2018', '2020', '2021', '2022', '2023', '2024']
    tpak = [67.8, 69.2, 69.5, 70.1, 70.8, 71.4, 72.1]
    tpt = [5.82, 5.12, 5.41, 5.25, 4.89, 4.62, 4.38]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=FIG_SIZE, dpi=DPI, sharex=True)
    fig.patch.set_facecolor(BG_COLOR)

    plt.suptitle("Indikator Ketenagakerjaan Kabupaten Lampung Selatan (2015 - 2024)", fontsize=12, fontweight='bold', color='#262626', y=0.98)

    set_chart_style(fig, ax1, "Tingkat Partisipasi Angkatan Kerja (TPAK %)")
    bars1 = ax1.bar(years, tpak, color=EXCEL_BLUE, width=0.55, zorder=3)
    ax1.set_ylim(0, 85)
    ax1.tick_params(axis='both', labelsize=9, colors='#595959')

    for bar, val in zip(bars1, tpak):
        yval = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width() / 2.0, yval + 1.8, f"{val:.1f}".replace('.', ',') + "%", ha='center', va='bottom', fontsize=8.5, color='#262626')

    set_chart_style(fig, ax2, "Tingkat Pengangguran Terbuka (TPT %)")
    bars2 = ax2.bar(years, tpt, color=EXCEL_ORANGE, width=0.55, zorder=3)
    ax2.set_ylim(0, 8)
    ax2.tick_params(axis='both', labelsize=9, colors='#595959')

    for bar, val in zip(bars2, tpt):
        yval = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width() / 2.0, yval + 0.25, f"{val:.2f}".replace('.', ',') + "%", ha='center', va='bottom', fontsize=8.5, color='#262626')

    plt.figtext(0.5, 0.01, "Sumber: BPS Kabupaten Lampung Selatan", ha="center", fontsize=8.5, color='#595959')
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig(os.path.join(CHART_DIR, "chart_ketenagakerjaan.png"))
    plt.close()


def create_apk_chart():
    years = ['2015', '2019', '2020', '2021', '2022', '2023', '2024']
    sd = [117.14, 104.86, 102.92, 102.17, 102.85, 103.48, 107.79]
    smp = [101.07, 93.54, 93.01, 95.34, 83.74, 91.82, 89.12]
    sma = [67.98, 74.80, 76.17, 79.50, 78.81, 81.61, 87.69]

    fig, ax = plt.subplots(figsize=FIG_SIZE, dpi=DPI)
    fig.patch.set_facecolor(BG_COLOR)
    set_chart_style(fig, ax)

    plt.suptitle("Angka Partisipasi Kasar (APK) Pendidikan (2015 - 2024)", fontsize=12, fontweight='bold', color='#262626', y=0.97)

    ax.plot(years, sd, color=EXCEL_BLUE, marker='o', linewidth=2.2, label='SD / MI / Sederajat', zorder=3)
    ax.plot(years, smp, color=EXCEL_ORANGE, marker='s', linewidth=2.2, label='SMP / MTs / Sederajat', zorder=3)
    ax.plot(years, sma, color=EXCEL_GREEN, marker='^', linewidth=2.2, label='SMA / SMK / MA / Sederajat', zorder=3)

    ax.tick_params(axis='both', labelsize=9, colors='#595959')
    ax.set_ylim(60, 125)

    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.12), ncol=3, frameon=False, fontsize=9)
    plt.figtext(0.5, 0.01, "Sumber: BPS Kabupaten Lampung Selatan", ha="center", fontsize=8.5, color='#595959')

    plt.tight_layout(rect=[0, 0.04, 1, 0.95])
    plt.savefig(os.path.join(CHART_DIR, "chart_apk.png"))
    plt.close()


def create_apm_chart():
    years = ['2015', '2019', '2020', '2021', '2022', '2023', '2024']
    sd = [97.85, 98.12, 98.45, 98.67, 98.90, 99.12, 99.35]
    smp = [78.45, 80.12, 81.34, 82.50, 81.90, 83.45, 84.12]
    sma = [55.20, 58.90, 60.15, 61.80, 61.25, 63.40, 64.85]

    fig, ax = plt.subplots(figsize=FIG_SIZE, dpi=DPI)
    fig.patch.set_facecolor(BG_COLOR)
    set_chart_style(fig, ax)

    plt.suptitle("Angka Partisipasi Murni (APM) Pendidikan (2015 - 2024)", fontsize=12, fontweight='bold', color='#262626', y=0.97)

    ax.plot(years, sd, color=EXCEL_BLUE, marker='o', linewidth=2.2, label='SD / MI / Sederajat', zorder=3)
    ax.plot(years, smp, color=EXCEL_ORANGE, marker='s', linewidth=2.2, label='SMP / MTs / Sederajat', zorder=3)
    ax.plot(years, sma, color=EXCEL_GREEN, marker='^', linewidth=2.2, label='SMA / SMK / MA / Sederajat', zorder=3)

    ax.tick_params(axis='both', labelsize=9, colors='#595959')
    ax.set_ylim(50, 105)

    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.12), ncol=3, frameon=False, fontsize=9)
    plt.figtext(0.5, 0.01, "Sumber: BPS Kabupaten Lampung Selatan", ha="center", fontsize=8.5, color='#595959')

    plt.tight_layout(rect=[0, 0.04, 1, 0.95])
    plt.savefig(os.path.join(CHART_DIR, "chart_apm.png"))
    plt.close()


def create_gini_ratio_chart():
    years = ['2011', '2013', '2015', '2017', '2019', '2020', '2021', '2022', '2023', '2024', '2025']
    gini = [0.302, 0.350, 0.348, 0.300, 0.331, 0.299, 0.268, 0.260, 0.257, 0.253, 0.239]

    fig, ax = plt.subplots(figsize=FIG_SIZE, dpi=DPI)
    fig.patch.set_facecolor(BG_COLOR)
    set_chart_style(fig, ax)

    plt.suptitle("Gini Ratio Kabupaten Lampung Selatan (2011 - 2025)", fontsize=12, fontweight='bold', color='#262626', y=0.97)

    bars = ax.bar(years, gini, color=EXCEL_BLUE, width=0.55, zorder=3, label='Gini Ratio (Skala 0 - 1)')
    ax.tick_params(axis='both', labelsize=9, colors='#595959')
    ax.set_ylim(0, 0.45)

    for bar, val in zip(bars, gini):
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2.0, yval + 0.008, f"{val:.3f}".replace('.', ','), ha='center', va='bottom', fontsize=8.5, color='#262626')

    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.12), ncol=1, frameon=False, fontsize=9.5)
    plt.figtext(0.5, 0.01, "Sumber: BPS Kabupaten Lampung Selatan", ha="center", fontsize=8.5, color='#595959')

    plt.tight_layout(rect=[0, 0.04, 1, 0.95])
    plt.savefig(os.path.join(CHART_DIR, "chart_gini_ratio.png"))
    plt.close()


def create_pdrb_adhb_chart():
    years = ['2010', '2015', '2020', '2023', '2024', '2025']
    pdrb_m = [18535.51, 31412.78, 44293.00, 55994.57, 60320.74, 65658.66]

    fig, ax = plt.subplots(figsize=FIG_SIZE, dpi=DPI)
    fig.patch.set_facecolor(BG_COLOR)
    set_chart_style(fig, ax)

    plt.suptitle("Total PDRB ADHB Kabupaten Lampung Selatan (2010 - 2025)", fontsize=12, fontweight='bold', color='#262626', y=0.97)

    bars = ax.bar(years, pdrb_m, color=EXCEL_BLUE, width=0.55, zorder=3, label='PDRB ADHB (Milyar Rupiah)')
    ax.tick_params(axis='both', labelsize=9, colors='#595959')
    ax.set_ylim(0, 75000)
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"{int(x):,}".replace(',', '.')))

    for bar, val in zip(bars, pdrb_m):
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2.0, yval + 1500, f"{val:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'), ha='center', va='bottom', fontsize=8.5, color='#262626')

    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.12), ncol=1, frameon=False, fontsize=9.5)
    plt.figtext(0.5, 0.01, "Sumber: BPS Kabupaten Lampung Selatan", ha="center", fontsize=8.5, color='#595959')

    plt.tight_layout(rect=[0, 0.04, 1, 0.95])
    plt.savefig(os.path.join(CHART_DIR, "chart_pdrb_adhb.png"))
    plt.close()


def create_pdrb_adhk_chart():
    years = ['2010', '2015', '2020', '2023', '2024', '2025']
    pdrb_m = [18535.51, 24012.30, 29850.40, 34210.15, 35790.80, 37540.20]

    fig, ax = plt.subplots(figsize=FIG_SIZE, dpi=DPI)
    fig.patch.set_facecolor(BG_COLOR)
    set_chart_style(fig, ax)

    plt.suptitle("Total PDRB ADHK Riil Kabupaten Lampung Selatan (2010 - 2025)", fontsize=12, fontweight='bold', color='#262626', y=0.97)

    bars = ax.bar(years, pdrb_m, color=EXCEL_BLUE, width=0.55, zorder=3, label='PDRB ADHK (Milyar Rupiah)')
    ax.tick_params(axis='both', labelsize=9, colors='#595959')
    ax.set_ylim(0, 45000)
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"{int(x):,}".replace(',', '.')))

    for bar, val in zip(bars, pdrb_m):
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2.0, yval + 900, f"{val:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'), ha='center', va='bottom', fontsize=8.5, color='#262626')

    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.12), ncol=1, frameon=False, fontsize=9.5)
    plt.figtext(0.5, 0.01, "Sumber: BPS Kabupaten Lampung Selatan", ha="center", fontsize=8.5, color='#595959')

    plt.tight_layout(rect=[0, 0.04, 1, 0.95])
    plt.savefig(os.path.join(CHART_DIR, "chart_pdrb_adhk.png"))
    plt.close()


def create_kepadatan_penduduk_chart():
    kec = ['Natar', 'Jati Agung', 'Candipuro', 'Tanjung Bintang', 'Kalianda', 'Sidomulyo', 'Katibung', 'Lainnya']
    density = [972, 808, 734, 705, 631, 578, 443, 420]

    fig, ax = plt.subplots(figsize=FIG_SIZE, dpi=DPI)
    fig.patch.set_facecolor(BG_COLOR)
    set_chart_style(fig, ax)

    plt.suptitle("Kepadatan Penduduk per Kecamatan (Tahun 2025)", fontsize=12, fontweight='bold', color='#262626', y=0.97)

    colors = EXCEL_BLUE
    bars = ax.bar(kec, density, color=colors, width=0.55, zorder=3, label='Kepadatan Penduduk (Jiwa / km²)')

    ax.tick_params(axis='both', labelsize=9, colors='#595959')
    ax.set_ylim(0, 1150)
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"{int(x):,}".replace(',', '.')))

    for bar, val in zip(bars, density):
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2.0, yval + 20, f"{val:,}".replace(',', '.') + " Jiwa/km²", ha='center', va='bottom', fontsize=8, color='#262626')

    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.12), ncol=1, frameon=False, fontsize=9.5)
    plt.figtext(0.5, 0.01, "Sumber: Disdukcapil & BPS Kabupaten Lampung Selatan", ha="center", fontsize=8.5, color='#595959')

    plt.tight_layout(rect=[0, 0.04, 1, 0.95])
    plt.savefig(os.path.join(CHART_DIR, "chart_kepadatan_penduduk.png"))
    plt.close()


def create_laju_penduduk_chart():
    years = ['2018', '2020', '2021', '2022', '2023', '2024', '2025']
    growth = [0.96, 1.25, 0.69, 0.88, 1.88, 2.11, 1.90]

    fig, ax = plt.subplots(figsize=FIG_SIZE, dpi=DPI)
    fig.patch.set_facecolor(BG_COLOR)
    set_chart_style(fig, ax)

    plt.suptitle("Laju Pertumbuhan Penduduk Kabupaten Lampung Selatan (2018 - 2025)", fontsize=12, fontweight='bold', color='#262626', y=0.97)

    bars = ax.bar(years, growth, color=EXCEL_BLUE, width=0.55, zorder=3, label='Laju Pertumbuhan Penduduk (%)')
    ax.tick_params(axis='both', labelsize=9, colors='#595959')
    ax.set_ylim(0, 3.0)

    for bar, val in zip(bars, growth):
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2.0, yval + 0.08, f"{val:.2f}".replace('.', ',') + "%", ha='center', va='bottom', fontsize=8.5, color='#262626')

    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.12), ncol=1, frameon=False, fontsize=9.5)
    plt.figtext(0.5, 0.01, "Sumber: Disdukcapil & BPS Kabupaten Lampung Selatan", ha="center", fontsize=8.5, color='#595959')

    plt.tight_layout(rect=[0, 0.04, 1, 0.95])
    plt.savefig(os.path.join(CHART_DIR, "chart_laju_penduduk.png"))
    plt.close()


def create_persentase_penduduk_chart():
    kec = ['Natar', 'Jati Agung', 'Kalianda', 'Tanjung Bintang', 'Katibung', 'Sidomulyo', 'Candipuro', 'Lainnya']
    pct = [18.12, 11.60, 8.89, 7.98, 6.79, 6.18, 5.42, 35.02]

    fig, ax = plt.subplots(figsize=FIG_SIZE, dpi=DPI)
    fig.patch.set_facecolor(BG_COLOR)
    set_chart_style(fig, ax)

    plt.suptitle("Persentase Distribusi Penduduk per Kecamatan (Tahun 2025)", fontsize=12, fontweight='bold', color='#262626', y=0.97)

    bars = ax.bar(kec, pct, color=EXCEL_BLUE, width=0.55, zorder=3, label='Persentase Penduduk (%)')
    ax.tick_params(axis='both', labelsize=9, colors='#595959')
    ax.set_ylim(0, 42)

    for bar, val in zip(bars, pct):
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2.0, yval + 0.8, f"{val:.2f}".replace('.', ',') + "%", ha='center', va='bottom', fontsize=8.5, color='#262626')

    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.12), ncol=1, frameon=False, fontsize=9.5)
    plt.figtext(0.5, 0.01, "Sumber: Disdukcapil & BPS Kabupaten Lampung Selatan", ha="center", fontsize=8.5, color='#595959')

    plt.tight_layout(rect=[0, 0.04, 1, 0.95])
    plt.savefig(os.path.join(CHART_DIR, "chart_persentase_penduduk.png"))
    plt.close()


def create_piramida_penduduk_chart():
    groups = ['0-4', '5-9', '10-14', '15-19', '20-24', '25-29', '30-34', '35-39', '40-44', '45-49', '50-54', '55-59', '60-64', '65+']
    jiwa = [76857, 100826, 103825, 90683, 88670, 89237, 83847, 83634, 89567, 83321, 69296, 54834, 46342, 85135]

    fig, ax = plt.subplots(figsize=FIG_SIZE, dpi=DPI)
    fig.patch.set_facecolor(BG_COLOR)
    set_chart_style(fig, ax)

    plt.suptitle("Struktur Kelompok Umur Penduduk (Tahun 2025)", fontsize=12, fontweight='bold', color='#262626', y=0.97)

    bars = ax.bar(groups, jiwa, color=EXCEL_BLUE, width=0.55, zorder=3, label='Jumlah Penduduk (Jiwa)')
    ax.tick_params(axis='both', labelsize=9, colors='#595959')
    ax.set_ylim(0, 125000)
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"{int(x):,}".replace(',', '.')))

    for bar, val in zip(bars, jiwa):
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2.0, yval + 2500, f"{val:,}".replace(',', '.'), ha='center', va='bottom', fontsize=8, color='#262626')

    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.12), ncol=1, frameon=False, fontsize=9.5)
    plt.figtext(0.5, 0.01, "Sumber: Disdukcapil & BPS Kabupaten Lampung Selatan", ha="center", fontsize=8.5, color='#595959')

    plt.tight_layout(rect=[0, 0.04, 1, 0.95])
    plt.savefig(os.path.join(CHART_DIR, "chart_piramida_penduduk.png"))
    plt.close()


def create_proyeksi_penduduk_chart():
    years = ['2020', '2021', '2022', '2023', '2024', '2025']
    pop_jiwa = [1064300, 1071700, 1081100, 1101400, 1124680, 1146070]

    fig, ax = plt.subplots(figsize=FIG_SIZE, dpi=DPI)
    fig.patch.set_facecolor(BG_COLOR)
    set_chart_style(fig, ax)

    plt.suptitle("Proyeksi Penduduk Kabupaten Lampung Selatan (2020 - 2025)", fontsize=12, fontweight='bold', color='#262626', y=0.97)

    bars = ax.bar(years, pop_jiwa, color=EXCEL_BLUE, width=0.55, zorder=3, label='Proyeksi Penduduk (Jiwa)')
    ax.tick_params(axis='both', labelsize=9, colors='#595959')
    ax.set_ylim(800000, 1250000)
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"{int(x):,}".replace(',', '.')))

    for bar, val in zip(bars, pop_jiwa):
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2.0, yval + 7000, f"{val:,}".replace(',', '.'), ha='center', va='bottom', fontsize=8.5, color='#262626')

    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.12), ncol=1, frameon=False, fontsize=9.5)
    plt.figtext(0.5, 0.01, "Sumber: BPS Kabupaten Lampung Selatan", ha="center", fontsize=8.5, color='#595959')

    plt.tight_layout(rect=[0, 0.04, 1, 0.95])
    plt.savefig(os.path.join(CHART_DIR, "chart_proyeksi_penduduk.png"))
    plt.close()


def create_sex_ratio_chart():
    years = ['2017', '2018', '2020', '2021', '2022', '2023', '2024']
    ratio = [104.2, 104.1, 103.8, 103.9, 104.0, 104.3, 104.5]

    fig, ax = plt.subplots(figsize=FIG_SIZE, dpi=DPI)
    fig.patch.set_facecolor(BG_COLOR)
    set_chart_style(fig, ax)

    plt.suptitle("Rasio Jenis Kelamin (Sex Ratio) Lampung Selatan (2017 - 2024)", fontsize=12, fontweight='bold', color='#262626', y=0.97)

    bars = ax.bar(years, ratio, color=EXCEL_BLUE, width=0.55, zorder=3, label='Sex Ratio (Laki-laki per 100 Perempuan)')
    ax.tick_params(axis='both', labelsize=9, colors='#595959')
    ax.set_ylim(90, 112)

    for bar, val in zip(bars, ratio):
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2.0, yval + 0.8, f"{val:.1f}".replace('.', ','), ha='center', va='bottom', fontsize=8.5, color='#262626')

    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.12), ncol=1, frameon=False, fontsize=9.5)
    plt.figtext(0.5, 0.01, "Sumber: Disdukcapil & BPS Kabupaten Lampung Selatan", ha="center", fontsize=8.5, color='#595959')

    plt.tight_layout(rect=[0, 0.04, 1, 0.95])
    plt.savefig(os.path.join(CHART_DIR, "chart_sex_ratio.png"))
    plt.close()


def create_pdrb_pengeluaran_chart():
    years = ['2010', '2015', '2020', '2023', '2024']
    adhb = [18535.51, 31412.78, 44293.00, 55994.57, 60320.74]
    adhk = [18535.51, 24012.30, 29850.40, 34210.15, 35790.80]

    fig, ax = plt.subplots(figsize=FIG_SIZE, dpi=DPI)
    fig.patch.set_facecolor(BG_COLOR)
    set_chart_style(fig, ax)

    plt.suptitle("PDRB Pengeluaran ADHB dan ADHK (2010 - 2024)", fontsize=12, fontweight='bold', color='#262626', y=0.97)

    x = np.arange(len(years))
    width = 0.35

    ax.bar(x - width / 2, adhb, width, color=EXCEL_BLUE, label='ADHB (Harga Berlaku)', zorder=3)
    ax.bar(x + width / 2, adhk, width, color=EXCEL_ORANGE, label='ADHK (Harga Konstan)', zorder=3)

    ax.set_xticks(x)
    ax.set_xticklabels(years)
    ax.tick_params(axis='both', labelsize=9, colors='#595959')
    ax.set_ylim(0, 75000)

    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.12), ncol=2, frameon=False, fontsize=9.5)
    plt.figtext(0.5, 0.01, "Sumber: BPS Kabupaten Lampung Selatan", ha="center", fontsize=8.5, color='#595959')

    plt.tight_layout(rect=[0, 0.04, 1, 0.95])
    plt.savefig(os.path.join(CHART_DIR, "chart_pdrb_pengeluaran.png"))
    plt.close()


def generate_all_charts():
    create_kemiskinan_chart()
    create_laju_ekonomi_chart()
    create_ipm_chart()
    create_ketenagakerjaan_chart()
    create_penduduk_chart()
    create_apk_chart()
    create_apm_chart()
    create_gini_ratio_chart()
    create_pdrb_adhb_chart()
    create_pdrb_adhk_chart()
    create_kepadatan_penduduk_chart()
    create_laju_penduduk_chart()
    create_persentase_penduduk_chart()
    create_piramida_penduduk_chart()
    create_proyeksi_penduduk_chart()
    create_sex_ratio_chart()
    create_pdrb_pengeluaran_chart()


if __name__ == "__main__":
    generate_all_charts()
