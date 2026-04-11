import logging
from scraper import auto_scrape_on_startup, scrape_beasiswa_data, determine_status

# Setup logging khusus untuk testing
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MockCrudModule:
    """
    Ini adalah modul CRUD tiruan (Mock) untuk menirukan pekerjaan Darva.
    Fungsinya hanya untuk mencetak data ke terminal, membuktikan bahwa
    scraper milik Kemal berhasil mengirim data dengan struktur yang benar.
    """
    def __init__(self):
        self.database_palsu = []

    def get_beasiswa_list(self):
        # Kita pura-pura databasenya masih kosong agar auto-scrape berjalan
        return self.database_palsu

    def add_beasiswa(self, judul, jenjang, deadline, deskripsi, link_aplikasi, status):
        # Ini meniru fungsi add_beasiswa milik Darva
        data_baru = {
            "judul": judul,
            "jenjang": jenjang,
            "deadline": deadline,
            "status": status, # Status dinamis hasil penentuan fungsi Kemal
            # Deskripsi dan link kita potong sedikit saat diprint biar terminal ga penuh
            "deskripsi_singkat": deskripsi[:30] + "..." if deskripsi else "",
            "link": link_aplikasi
        }
        self.database_palsu.append(data_baru)
        
        # Cetak ke terminal setiap kali data berhasil "disimpan"
        print(f"✅ [MOCK DB] Tersimpan: {judul[:40]}... | {jenjang} | {deadline} | Status: {status}")
        return True

def run_test():
    print("=" * 60)
    print("🧪 MEMULAI TEST INTEGRASI SCRAPER -> DATABASE")
    print("=" * 60)
    
    # Inisialisasi CRUD tiruan
    mock_crud = MockCrudModule()
    
    # Jalankan fungsi auto-scrape milikmu dan lemparkan CRUD tiruan ke dalamnya
    # CATATAN: Karena proses scrape utuh bisa memakan waktu lama, 
    # test ini akan menjalankan flow penuhmu.
    berhasil = auto_scrape_on_startup(mock_crud)
    
    print("\n" + "=" * 60)
    print("📊 HASIL AKHIR TEST")
    print("=" * 60)
    
    if berhasil:
        print(f"✅ Test SUKSES! Scraper berhasil mengisi {len(mock_crud.database_palsu)} data ke Mock Database.")
        print("\nContoh 1 data pertama yang berhasil di-parsing untuk Darva:")
        if mock_crud.database_palsu:
            import json
            print(json.dumps(mock_crud.database_palsu[0], indent=2))
    else:
        print("❌ Test GAGAL! Auto-scrape mengembalikan nilai False atau error.")

if __name__ == "__main__":
    run_test()