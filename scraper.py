"""
Tim: KEMAL (Scraping & Search Specialist)
"""

import requests
from bs4 import BeautifulSoup
import json
import os
import re
import time
from datetime import datetime
from typing import List, Dict, Optional
import logging

# PyQt6 untuk background threading
try:
    from PyQt6.QtCore import QThread, pyqtSignal
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False

# Konfigurasi logging untuk debugging dan monitoring
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Konfigurasi folder
BACKUP_DIR = "backup"
os.makedirs(BACKUP_DIR, exist_ok=True)

# URL website sumber scraping
BASE_URL = "https://indbeasiswa.com"
CATEGORIES = {
    "s1": "beasiswa-s1",
    "s2": "beasiswa-s2",
    "diploma": "beasiswa-diploma",
    "dalam_negeri": "beasiswa-indonesia",
    "luar_negeri": "beasiswa-luar-negeri"
}

# Headers untuk menghindari 403 Forbidden
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# Konfigurasi pagination - Smart Hybrid (10 pages per kategori)
# NOTE: Consistent 10 pages untuk semua kategori untuk dapat maksimal beasiswa
MAX_PAGES_CONFIG = {
    "s1": 10,              # Top 10 pages
    "s2": 10,              # Top 10 pages
    "diploma": 10,         # Top 10 pages
    "dalam_negeri": 10,    # Top 10 pages
    "luar_negeri": 10      # Top 10 pages
}

# Rate limiting
REQUEST_DELAY = 1  # 1 second antara requests untuk polite scraping


def scrape_beasiswa_data() -> Dict[str, List[Dict]]:
    """
    Main function untuk scrape semua kategori beasiswa dari indbeasiswa.com
    
    Return:
        Dict dengan struktur:
        {
            "beasiswa": [list of beasiswa dicts],
            "penyelenggara": [list of penyelenggara dicts]
        }
    
    Catatan:
        - Function ini INDEPENDENT dari database
        - Bisa dijalankan standalone untuk testing
        - Generate JSON backup otomatis
    """
    all_beasiswa = []
    all_penyelenggara = set()  # Set untuk avoid duplicate penyelenggara
    
    logger.info("🔄 Memulai proses scraping indbeasiswa.com (dengan pagination)...")
    
    for category_name, category_slug in CATEGORIES.items():
        logger.info(f"  → Scraping kategori: {category_name}")
        try:
            beasiswa_list = scrape_category(category_slug, category_name)
            logger.info(f"     ✅ Berhasil scrape {len(beasiswa_list)} beasiswa")
            
            # Ekstrak penyelenggara unik
            for b in beasiswa_list:
                if b.get("penyelenggara"):
                    all_penyelenggara.add(b["penyelenggara"])
            
            all_beasiswa.extend(beasiswa_list)
        except Exception as e:
            logger.error(f"     ❌ Error scraping {category_name}: {str(e)}")
            continue
    
    logger.info(f"✅ Total beasiswa scraped: {len(all_beasiswa)}")
    logger.info(f"✅ Total penyelenggara unik: {len(all_penyelenggara)}")
    
    # Format penyelenggara untuk database
    penyelenggara_list = [
        {
            "nama": nama,
            "jenis": detect_penyelenggara_type(nama),
            "jumlah_beasiswa": sum(1 for b in all_beasiswa if b.get("penyelenggara") == nama),
            "website": None,
            "kontak": None,
            "keterangan": None
        }
        for nama in all_penyelenggara
    ]
    
    # Generate JSON backup
    backup_data = {
        "beasiswa": all_beasiswa,
        "penyelenggara": penyelenggara_list,
        "timestamp": datetime.now().isoformat(),
        "total_beasiswa": len(all_beasiswa),
        "total_penyelenggara": len(penyelenggara_list)
    }
    
    save_backup(backup_data)
    
    return {
        "beasiswa": all_beasiswa,
        "penyelenggara": penyelenggara_list
    }