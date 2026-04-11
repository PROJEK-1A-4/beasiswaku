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

def extract_beasiswa_info(item, category_name: str) -> Optional[Dict]:
    """
    Extract informasi beasiswa dari HTML element
    
    """
    try:
        # Verifikasi selector - SUDAH TESTED dengan HTML asli
        nama = item.select_one(".entry-title")  # VERIFIED: WordPress entry-title
        link = item.select_one("a")  # VERIFIED: First <a> tag contains link
        deskripsi = item.select_one(".entry-content")  # VERIFIED: Full description di sini
        
        # Deadline & Penyelenggara: extract dari title attribute dengan regex
        link_title = link.get("title") if link else ""
        
        # Ekstrak text
        nama_text = nama.get_text(strip=True) if nama else "Unknown"
        link_href = link.get("href") if link else ""
        deskripsi_text = deskripsi.get_text(strip=True) if deskripsi else ""
        
        # Extract deadline dari title attribute
        deadline_match = re.search(r'DEADLINE[:\s]+([^)]+)', link_title, re.IGNORECASE) if link_title else None
        deadline_text = deadline_match.group(1).strip() if deadline_match else "Tidak Diketahui"
        
        # TASK KEMAL: Extract penyelenggara dari deskripsi atau gunakan heuristic
        # Untuk sekarang: default "Unknown" — bisa di-improve dengan regex/heuristic
        penyelenggara_text = extract_penyelenggara(nama_text, deskripsi_text)
        
        # Normalisasi jenjang
        jenjang_map = {
            "s1": "S1",
            "s2": "S2",
            "diploma": "Diploma",
            "dalam_negeri": "Dalam Negeri",
            "luar_negeri": "Luar Negeri"
        }
        jenjang = jenjang_map.get(category_name, "Dalam Negeri")
        
        # Tentukan status (TASK KEMAL: adjust logic sesuai kebutuhan)
        status = determine_status(deadline_text)
        
        # Normalisasi deadline ke format YYYY-MM-DD (TASK KEMAL: adjust parsing)
        deadline_normalized = parse_deadline(deadline_text)
        
        beasiswa = {
            "nama": clean_text(nama_text),
            "penyelenggara": clean_text(penyelenggara_text),
            "jenjang": jenjang,
            "deadline": deadline_normalized,
            "status": status,
            "link": normalize_url(link_href),
            "deskripsi": clean_text(deskripsi_text),
            "timestamp_scraping": datetime.now().isoformat()
        }
        
        return beasiswa
    
    except Exception as e:
        logger.debug(f"Error extracting beasiswa: {str(e)}")
        return None
    
def determine_status(deadline_text: str) -> str:
    """
    menentukan status beasiswa (Buka / Segera Tutup / Tutup)
    
    Kriteria:
    - Buka: ≥ 8 hari lagi
    - Segera Tutup: 1-7 hari lagi
    - Tutup: sudah kedaluwarsa
    """
    # PLACEHOLDER — implementasi logic tahap lanjut
    return "Buka"

def extract_penyelenggara(nama_beasiswa: str, deskripsi: str) -> str:
    """
    Extract penyelenggara dari nama beasiswa atau deskripsi
    
    Heuristic:
    1. Cari kata kunci institusi di awal judul (sebelum 'BEASISWA')
    2. Cari di kalimat pertama deskripsi
    3. Default: "Tidak Diketahui"
    
    Contoh:
    - "BEASISWA DJARUM PLUS..." → "DJARUM"
    - "PROGRAM BSI SCHOLARSHIP..." → "BSI"
    """
    # Cari kata pertama yang bukan common words (case-insensitive)
    common_words = {'beasiswa', 'program', 'tahun', 'untuk', 'mahasiswa', 'the', 'a', 'an'}
    
    words = nama_beasiswa.lower().split()  # FIXED: lowercase untuk case-insensitive comparison
    for word in words:
        if len(word) > 3 and word not in common_words:
            return word.upper()  # Return uppercase hasil
    
    return "Tidak Diketahui"

def parse_deadline(deadline_text: str) -> str:
    
    text = deadline_text.lower()

    if text == "tidak diketahui" or "segera" in text or "dibuka" in text:
        return "0000-00-00"
    
    bulan_map = {
        'januari': '01', 'jan': '01',
        'februari': '02', 'feb': '02',
        'maret': '03', 'mar': '03',
        'april': '04', 'apr': '04',
        'mei': '05', 'may': '05',
        'juni': '06', 'jun': '06',
        'juli': '07', 'jul': '07',
        'agustus': '08', 'agu': '08', 'aug': '08',
        'september': '09', 'sep': '09',
        'oktober': '10', 'okt': '10', 'oct': '10',
        'november': '11', 'nov': '11',
        'desember': '12', 'des': '12', 'dec': '12'
    }

    try:
        # Ekstrak semua angka dan huruf menggunakan Regular Expression (Regex)
        # Contoh: dari "10 Juni 2026", kita dapat list: ['10', 'juni', '2026']
        parts = re.findall(r'[a-z]+|\d+', text)
        #Asumsi format umum adalah: Tanggal, Bulan(teks), Tahun
        if len(parts) >= 3:
            # Format tanggal menjadi 2 digit (misal: '5' menjadi '05')
            hari = parts[0].zfill(2)  # Pad dengan 0 jika hanya 1 digit 
            bulan_text = parts[1]
            tahun = parts[2]

            if len(tahun) == 2:  # Jika tahun hanya 2 digit, tambahkan prefix '20'
                tahun = '20' + tahun
            
            # FIXED: Check bulan_map di level yang sama (tidak nested)
            if bulan_text in bulan_map:
                bulan_angka = bulan_map[bulan_text]
                return f"{tahun}-{bulan_angka}-{hari}"
                
    except Exception as e:
        logger.debug(f"Gagal memproses deadline: {deadline_text}. Error: {e}")


    return "0000-00-00"