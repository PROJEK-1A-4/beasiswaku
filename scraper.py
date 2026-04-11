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

def scrape_category(category_slug: str, category_name: str) -> List[Dict]:
    """
    Scrape satu kategori beasiswa dari indbeasiswa.com dengan PAGINATION
    
    Args:
        category_slug: URL slug kategori (e.g., "beasiswa-s1")
        category_name: Nama kategori untuk jenjang field (e.g., "s1", "diploma")
    
    Return:
        List of beasiswa dicts (termasuk duplikasi - penting untuk UI filtering per jenjang)
        NOTE: Duplikasi di-keep karena beasiswa bisa berlaku di multiple jenjang
    """
    beasiswa_list = []
    max_pages = MAX_PAGES_CONFIG.get(category_name, 1)
    
    for page_num in range(1, max_pages + 1):
        try:
            # Construct URL dengan pagination
            if page_num == 1:
                url = f"{BASE_URL}/{category_slug}"
            else:
                url = f"{BASE_URL}/{category_slug}/page/{page_num}/"
            
            logger.debug(f"    Fetching page {page_num}/{max_pages}: {url}")
            
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, "html.parser")  # Built-in parser
            
            # Parse beasiswa items dari halaman
            beasiswa_items = soup.select(".type-post")
            
            if not beasiswa_items and page_num == 1:
                logger.warning(f"  ⚠️  Tidak ada item ditemukan untuk {category_slug} page 1. Cek selector HTML.")
            
            # Extract beasiswa dari tiap item
            page_beasiswa_count = 0
            for item in beasiswa_items:
                try:
                    beasiswa = extract_beasiswa_info(item, category_name)
                    if beasiswa:
                        beasiswa_list.append(beasiswa)
                        page_beasiswa_count += 1
                except Exception as e:
                    logger.warning(f"  ⚠️  Error extract item: {str(e)}")
                    continue
            
            logger.debug(f"    Page {page_num}: {page_beasiswa_count} items, total so far: {len(beasiswa_list)}")
            
            # Rate limiting: delay sebelum request berikutnya (kecuali last page)
            if page_num < max_pages:
                time.sleep(REQUEST_DELAY)
        
        except requests.exceptions.Timeout:
            logger.warning(f"  ⚠️  Timeout page {page_num}: {url}")
            continue
        except requests.exceptions.RequestException as e:
            logger.warning(f"  ⚠️  Error page {page_num}: {url} - {str(e)}")
            continue
        except Exception as e:
            logger.warning(f"  ⚠️  Unexpected error page {page_num}: {str(e)}")
            continue
    
    return beasiswa_list