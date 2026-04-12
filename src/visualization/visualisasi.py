# Modul visualisasi Beasiswaku 
# Peran:
# 1. Mengambil data statistik/tracker dari CRUD.
# 2. Mengubah data menjadi chart.
# 3. Menampilkan chart di dashbord pengguna.
# 4. Mengembalikan Figure untuk dipasang ke PyQt6.

from __future__ import annotations

from collections import Counter
from datetime import datetime
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt

# FigureCanvas untuk integrasi Matplotlib ke PyQt6
try:
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
except Exception:
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

# Import data layer (CRUD) sebagai sumber data yang resmi
from src.database.crud import (
    get_beasiswa_per_jenjang,
    get_top_penyelenggara,
    get_status_availability,
    get_lamaran_list,
)
# Menyusun variasi warna untuk chart agar tampilan seragam dan menarik.
COLOR_PALETTE = {
    # Status beasiswa
    "Buka": "#2E7D32",
    "Segera Tutup": "#F9A825",
    "Tutup": "#C62828",
    # Status lamaran
    "Pending": "#546E7A",
    "Submitted": "#1E88E5",
    "Accepted": "#2E7D32",
    "Rejected": "#C62828",
    "Withdrawn": "#8E24AA",
    # Utility
    "bar_default": "#1E88E5",
    "bar_secondary": "#26A69A",
    "grid": "#D9D9D9",
    "empty_text": "#777777",
}

def _apply_axis_style(ax) -> None:
    """
    Fungsi helper internal untuk merapikan style sumbu chart.

    Alasan:
    - Agar semua chart memiliki style yang konsisten.
    - Menghindari duplikasi kode styling di setiap fungsi chart.
    """
    ax.grid(axis="y", linestyle="--", alpha=0.35, color=COLOR_PALETTE["grid"])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

def _render_empty_state(ax, title: str, message: str = "Data tidak tersedia") -> None:
    """
    Menampilkan tampilan fallback apabila data kosong.

    Alasan:
    - Aplikasi tidak crash saat database belum ada data.
    - User tetap dapat feedback visual yang jelas.
    """
    ax.set_title(title)
    ax.text(
        0.5, 0.5, message,
        ha="center", va="center",
        fontsize=11, color=COLOR_PALETTE["empty_text"],
        transform=ax.transAxes
    )
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_visible(False)

def create_bar_chart_beasiswa_per_jenjang(
        data: Dict[str, int],
        title: str = "Jumlah Beasiswa per Jenjang",
    ) -> Tuple[plt.Figure, plt.Axes]:
        """
        Membuat bar chart jumlah beasiswa per jenjang.

        Input:
        - data: dict, contoh {"D3": 4, "D4": 5, "S1": 14, "S2": 9}

        Return:
        - (figure, axes) dari matplotlib

        Alasan chart ini:
        - Menjawab pertanyaan: jenjang mana yang paling banyak peluang beasiswanya?
        """
        fig, ax = plt.subplots(figsize=(8, 4.5))

        if not data:
            _render_empty_state(ax, title)
            fig.tight_layout()
            return fig, ax

        labels = list(data.keys())
        values = [int(v) for v in data.values()]

        bars = ax.bar(labels, values, color=COLOR_PALETTE["bar_default"], alpha=0.9)
        ax.set_title(title)
        ax.set_xlabel("Jenjang")
        ax.set_ylabel("Jumlah Beasiswa")
        _apply_axis_style(ax)

        # Label angka di atas bar agar nilai mudah dibaca saat presentasi
        for bar, value in zip(bars, values):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                value + 0.05,
                str(value),
                ha="center",
                va="bottom",
                fontsize=10,
            )

        fig.tight_layout()
        return fig, ax

def create_bar_chart_top_penyelenggara(
        data: List[Dict],
        title: str = "Top Penyelenggara Beasiswa",
        limit: int = 5,
    ) -> Tuple[plt.Figure, plt.Axes]:
        """
        Membuat bar horizontal untuk top penyelenggara.

        Input:
        - data: list of dict, contoh:
          [{"nama_penyelenggara": "LPDP", "total_beasiswa": 12}, ...]
        - limit: jumlah top data yang ditampilkan (default 5)

        Return:
        - (figure, axes)

        Alasan chart ini:
        - Menunjukkan institusi penyedia beasiswa paling dominan.
        """
        fig, ax = plt.subplots(figsize=(9, 5))

        if not data:
            _render_empty_state(ax, title)
            fig.tight_layout()
            return fig, ax

        sliced = data[: max(1, limit)]
        names = [str(item.get("nama_penyelenggara", "Unknown")) for item in sliced]
        totals = [int(item.get("total_beasiswa", 0)) for item in sliced]

        bars = ax.barh(names, totals, color=COLOR_PALETTE["bar_secondary"], alpha=0.9)
        ax.set_title(title)
        ax.set_xlabel("Jumlah Beasiswa")
        ax.set_ylabel("Penyelenggara")
        _apply_axis_style(ax)
        ax.invert_yaxis()  # Nilai tertinggi di atas

        for bar, total in zip(bars, totals):
            ax.text(
                total + 0.05,
                bar.get_y() + bar.get_height() / 2,
                str(total),
                va="center",
                fontsize=10,
            )

        fig.tight_layout()
        return fig, ax

def create_pie_chart_status_ketersediaan(
        data: Dict[str, int],
        title: str = "Status Ketersediaan Beasiswa",
    ) -> Tuple[plt.Figure, plt.Axes]:
        """
        Membuat pie chart status ketersediaan beasiswa.

        Input:
        - data: dict, contoh {"Buka": 18, "Segera Tutup": 7, "Tutup": 3}

        Return:
        - (figure, axes)

        Alasan chart ini:
        - Mempermudah melihat proporsi beasiswa yang masih buka atau hampir tutup atau sudah tutup.
        """
        fig, ax = plt.subplots(figsize=(6.5, 6.5))

        if not data:
            _render_empty_state(ax, title)
            fig.tight_layout()
            return fig, ax

        labels = list(data.keys())
        values = [int(v) for v in data.values()]
        colors = [COLOR_PALETTE.get(label, "#90A4AE") for label in labels]

        ax.pie(
            values,
            labels=labels,
            colors=colors,
            autopct="%1.1f%%",
            startangle=90,
            wedgeprops={"edgecolor": "white", "linewidth": 1.0},
            textprops={"fontsize": 10},
        )
        ax.set_title(title)
        ax.axis("equal")
        fig.tight_layout()
        return fig, ax

def create_pie_chart_status_lamaran(
        data: Dict[str, int],
        title: str = "Distribusi Status Lamaran",
    ) -> Tuple[plt.Figure, plt.Axes]:
        """
        Membuat pie chart status lamaran user.

        Input:
        - data: dict, contoh {"Pending": 4, "Submitted": 2, "Accepted": 1}

        Return:
        - (figure, axes)

        Alasan chart ini:
        - Menjelaskan progres lamaran user secara cepat dalam bentuk proporsi.
        """
        fig, ax = plt.subplots(figsize=(6.5, 6.5))

        if not data:
            _render_empty_state(ax, title)
            fig.tight_layout()
            return fig, ax

        labels = list(data.keys())
        values = [int(v) for v in data.values()]
        colors = [COLOR_PALETTE.get(label, "#90A4AE") for label in labels]

        ax.pie(
            values,
            labels=labels,
            colors=colors,
            autopct="%1.1f%%",
            startangle=90,
            wedgeprops={"edgecolor": "white", "linewidth": 1.0},
            textprops={"fontsize": 10},
        )
        ax.set_title(title)
        ax.axis("equal")
        fig.tight_layout()
        return fig, ax

def create_bar_chart_lamaran_per_bulan(
        data: Dict[str, int],
        title: str = "Jumlah Lamaran per Bulan",
    ) -> Tuple[plt.Figure, plt.Axes]:
        """
        Membuat bar chart jumlah lamaran per bulan.

        Input:
        - data: dict dengan key format YYYY-MM, contoh {"2026-01": 2, "2026-02": 5}

        Return:
        - (figure, axes)

        Alasan chart ini:
        - Menunjukkan tren aktivitas pendaftaran user dari waktu ke waktu.
        """
        fig, ax = plt.subplots(figsize=(10, 5.5))

        if not data:
            _render_empty_state(ax, title)
            fig.tight_layout()
            return fig, ax

        months = sorted(data.keys())
        values = [int(data[m]) for m in months]

        bars = ax.bar(months, values, color=COLOR_PALETTE["bar_default"], alpha=0.9)
        ax.set_title(title)
        ax.set_xlabel("Bulan")
        ax.set_ylabel("Jumlah Lamaran")
        _apply_axis_style(ax)

        for bar, value in zip(bars, values):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                value + 0.05,
                str(value),
                ha="center",
                va="bottom",
                fontsize=9,
            )

        plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
        fig.subplots_adjust(bottom=0.25)
        fig.tight_layout()
        return fig, ax

def load_statistik_data() -> Tuple[Dict[str, int], List[Dict], Dict[str, int]]:
        """
        Mengambil data statistik dari CRUD (data real database).

        Return:
        - jenjang_data: dict jumlah beasiswa per jenjang
        - top_penyelenggara_data: list top penyelenggara
        - status_data: dict status ketersediaan beasiswa

        Alasan fungsi ini:
        - Memisahkan proses ambil data dari proses render chart.
        """
        jenjang_data = get_beasiswa_per_jenjang() or {}
        top_penyelenggara_data = get_top_penyelenggara(limit=5) or []
        status_data = get_status_availability() or {}

        return jenjang_data, top_penyelenggara_data, status_data

def load_tracker_data(user_id: int) -> Tuple[Dict[str, int], Dict[str, int]]:
        """
        Mengambil daftar lamaran user dari database, lalu mengelompokkan berdasarkan status dan bulan.

        Input:
        - user_id: id user aktif

        Return:
        - status_counts: dict jumlah status lamaran
        - month_counts: dict jumlah lamaran per bulan (YYYY-MM)

        Alasan:
        - get_lamaran_list memberi data detail per baris.
        - Fungsi ini merangkum detail itu menjadi format siap-chart.
        """
        lamaran_list, _ = get_lamaran_list(filter_user_id=user_id)

        if not lamaran_list:
            return {}, {}

        status_counter: Counter = Counter()
        month_counter: Counter = Counter()

        for item in lamaran_list:
            status = str(item.get("status", "Pending"))
            status_counter[status] += 1

            tanggal = str(item.get("tanggal_daftar", "")).strip()
            month_key = "Unknown"

            if tanggal:
                try:
                    dt = datetime.strptime(tanggal, "%Y-%m-%d")
                    month_key = dt.strftime("%Y-%m")
                except ValueError:
                    if len(tanggal) >= 7:
                        month_key = tanggal[:7]

            month_counter[month_key] += 1

        month_dict = dict(sorted(month_counter.items(), key=lambda x: (x[0] == "Unknown", x[0])))
        return dict(status_counter), month_dict

def figure_to_canvas(fig: plt.Figure) -> FigureCanvas:
        """
        Mengubah matplotlib figure menjadi canvas PyQt6.

        Alasan:
        - UI PyQt6 membutuhkan widget canvas agar figure bisa ditaruh di layout.
        """
        return FigureCanvas(fig)

def build_statistik_canvases() -> Dict[str, FigureCanvas]:
        """
        Membuat paket canvas untuk Tab Statistik.

        Return keys:
        - canvas_jenjang
        - canvas_penyelenggara
        - canvas_status

        Alasan:
        - Mempermudah main.py dengan memanggil sekali untuk dapat 3 chart.
        """
        jenjang_data, top_org_data, status_data = load_statistik_data()

        fig_jenjang, _ = create_bar_chart_beasiswa_per_jenjang(jenjang_data)
        fig_org, _ = create_bar_chart_top_penyelenggara(top_org_data)
        fig_status, _ = create_pie_chart_status_ketersediaan(status_data)

        return {
            "canvas_jenjang": figure_to_canvas(fig_jenjang),
            "canvas_penyelenggara": figure_to_canvas(fig_org),
            "canvas_status": figure_to_canvas(fig_status),
        }

def build_tracker_canvases(user_id: int) -> Dict[str, FigureCanvas]:
        """
        Membuat paket canvas untuk Tab Tracker user tertentu.

        Input:
        - user_id: user aktif

        Return keys:
        - canvas_lamaran_status
        - canvas_lamaran_bulanan
        """
        status_counts, month_counts = load_tracker_data(user_id)

        fig_status, _ = create_pie_chart_status_lamaran(status_counts)
        fig_month, _ = create_bar_chart_lamaran_per_bulan(month_counts)

        return {
            "canvas_lamaran_status": figure_to_canvas(fig_status),
            "canvas_lamaran_bulanan": figure_to_canvas(fig_month),
        }

if __name__ == "__main__":
        """
        Demo lokal cepat:
        - Menjalankan chart statistik dari data real database.
        - Berguna untuk cek visual sebelum integrasi ke main.py.
        """
        statistik_canvases = build_statistik_canvases()

        # Preview figure statistik
        for canvas in statistik_canvases.values():
            canvas.figure.show()

        plt.show()
