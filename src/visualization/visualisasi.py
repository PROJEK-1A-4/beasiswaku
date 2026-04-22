"""
Modul visualisasi Beasiswaku
Peran:
1. Mengambil data statistik/tracker dari CRUD.
2. Mengubah data menjadi chart.
3. Menampilkan chart di dashbord pengguna.
4. Mengembalikan Figure untuk dipasang ke PyQt6.
"""

from __future__ import annotations

import logging
from collections import Counter
from datetime import datetime
from typing import Dict, List, Tuple

import matplotlib
# Explicitly set the backend to PyQt6 (qtagg) before importing pyplot
matplotlib.use('qtagg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

# Import data layer (CRUD) sebagai sumber data yang resmi
from src.database.crud import (
    get_beasiswa_per_jenjang,
    get_top_penyelenggara,
    get_status_availability,
    get_lamaran_list,
)

logger = logging.getLogger(__name__)

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


def _apply_axis_style(ax: plt.Axes) -> None:
    """
    Fungsi helper internal untuk merapikan style sumbu chart.
    Agar semua chart memiliki style yang konsisten dan menghindari duplikasi.
    """
    ax.grid(axis="y", linestyle="--", alpha=0.35, color=COLOR_PALETTE["grid"])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def _style_chart_title(ax: plt.Axes, title: str) -> None:
    """Disimpan untuk kompatibilitas; judul ditampilkan di UI, bukan di dalam chart."""
    pass


def _render_empty_state(ax: plt.Axes, title: str, message: str = "Data tidak tersedia") -> None:
    """
    Menampilkan tampilan fallback apabila data kosong.
    Aplikasi tidak crash saat database belum ada data.
    """
    _style_chart_title(ax, title)
    ax.set_facecolor("#f8fafc")
    ax.text(
        0.5, 0.50, message,
        ha="center", va="center",
        fontsize=11, color="#5f6b7a",
        bbox={
            "boxstyle": "round,pad=0.35",
            "facecolor": "white",
            "edgecolor": "#d7dee8",
            "linewidth": 1.0,
        },
        transform=ax.transAxes
    )
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)


def create_bar_chart_beasiswa_per_jenjang(
    data: Dict[str, int],
    title: str = "Jumlah Beasiswa per Jenjang",
) -> Tuple[plt.Figure, plt.Axes]:
    """Membuat bar chart jumlah beasiswa per jenjang."""
    fig, ax = plt.subplots(figsize=(8, 4.5))

    if not data:
        _render_empty_state(ax, title)
        fig.tight_layout()
        return fig, ax

    labels = list(data.keys())
    values = [int(v) for v in data.values()]

    bars = ax.bar(labels, values, color=COLOR_PALETTE["bar_default"], alpha=0.9)
    _style_chart_title(ax, title)
    ax.set_xlabel("Jenjang")
    ax.set_ylabel("Jumlah Beasiswa")
    _apply_axis_style(ax)

    for bar, value in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            value + 0.05,
            str(value),
            ha="center",
            va="bottom",
            fontsize=10,
        )

    fig.tight_layout(rect=[0, 0.02, 1, 0.92])
    return fig, ax


def create_bar_chart_top_penyelenggara(
    data: List[Dict],
    title: str = "Top Penyelenggara Beasiswa",
    limit: int = 5,
) -> Tuple[plt.Figure, plt.Axes]:
    """Membuat bar horizontal untuk top penyelenggara."""
    fig, ax = plt.subplots(figsize=(9, 5))

    if not data:
        _render_empty_state(ax, title)
        fig.tight_layout()
        return fig, ax

    sliced = data[: max(1, limit)]
    names = [str(item.get("nama_penyelenggara", "Unknown")) for item in sliced]
    totals = [int(item.get("total_beasiswa", 0)) for item in sliced]

    bars = ax.barh(names, totals, color=COLOR_PALETTE["bar_secondary"], alpha=0.9)
    _style_chart_title(ax, title)
    ax.set_xlabel("Jumlah Beasiswa")
    ax.set_ylabel("Penyelenggara")
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
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

    fig.tight_layout(rect=[0, 0.02, 1, 0.92])
    return fig, ax


def create_pie_chart_status_ketersediaan(
    data: Dict[str, int],
    title: str = "Status Ketersediaan Beasiswa",
) -> Tuple[plt.Figure, plt.Axes]:
    """Membuat pie chart status ketersediaan beasiswa."""
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
    _style_chart_title(ax, title)
    ax.axis("equal")
    fig.tight_layout(rect=[0, 0.02, 1, 0.92])
    return fig, ax


def create_pie_chart_status_lamaran(
    data: Dict[str, int],
    title: str = "Distribusi Status Lamaran",
) -> Tuple[plt.Figure, plt.Axes]:
    """Membuat pie chart status lamaran user."""
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
    _style_chart_title(ax, title)
    ax.axis("equal")
    fig.tight_layout(rect=[0, 0.02, 1, 0.92])
    return fig, ax


def create_bar_chart_lamaran_per_bulan(
    data: Dict[str, int],
    title: str = "Jumlah Lamaran per Bulan",
) -> Tuple[plt.Figure, plt.Axes]:
    """Membuat bar chart jumlah lamaran per bulan."""
    fig, ax = plt.subplots(figsize=(10, 5.5))

    if not data:
        _render_empty_state(ax, title)
        fig.tight_layout()
        return fig, ax

    months = sorted(data.keys())
    values = [int(data[m]) for m in months]

    bars = ax.bar(months, values, color=COLOR_PALETTE["bar_default"], alpha=0.9)
    _style_chart_title(ax, title)
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
    fig.tight_layout(rect=[0, 0.02, 1, 0.90])
    return fig, ax


def load_statistik_data() -> Tuple[Dict[str, int], List[Dict], Dict[str, int]]:
    """Mengambil data statistik dari CRUD (data real database)."""
    jenjang_data = get_beasiswa_per_jenjang() or {}
    top_penyelenggara_data = get_top_penyelenggara(limit=5) or []
    status_data = get_status_availability() or {}

    return jenjang_data, top_penyelenggara_data, status_data


def load_tracker_data(user_id: int) -> Tuple[Dict[str, int], Dict[str, int]]:
    """Mengambil daftar lamaran user dari database, lalu mengelompokkan berdasarkan status dan bulan."""
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
    """Mengubah matplotlib figure menjadi canvas PyQt6."""
    return FigureCanvas(fig)


def build_statistik_canvases() -> Dict[str, FigureCanvas]:
    """Membuat paket canvas untuk Tab Statistik."""
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
    """Membuat paket canvas untuk Tab Tracker user tertentu."""
    status_counts, month_counts = load_tracker_data(user_id)

    fig_status, _ = create_pie_chart_status_lamaran(status_counts)
    fig_month, _ = create_bar_chart_lamaran_per_bulan(month_counts)

    return {
        "canvas_lamaran_status": figure_to_canvas(fig_status),
        "canvas_lamaran_bulanan": figure_to_canvas(fig_month),
    }


if __name__ == "__main__":
    """Demo lokal cepat untuk cek visual sebelum integrasi ke main.py."""
    statistik_canvases = build_statistik_canvases()

    # Preview figure statistik
    for canvas in statistik_canvases.values():
        canvas.figure.show()

    plt.show()
