# Context Document - BeasiswaKu

## 0. Tujuan Dokumen
Dokumen ini adalah ringkasan konteks menyeluruh proyek BeasiswaKu untuk dipakai AI lain (contoh: Gemini) sebagai sumber utama saat melakukan redesign GUI dan/atau redesign sistem.

Dokumen ini disusun dari kondisi kode aktual di repository (bukan hanya dokumentasi lama), lalu ditambah catatan risiko teknis dan arah redesign yang paling relevan.

## 1. Snapshot Proyek
- Nama aplikasi: BeasiswaKu
- Jenis aplikasi: Desktop app (PyQt6)
- Bahasa utama: Python
- Data storage: SQLite (file lokal)
- Versi tertera: 2.0.0
- Tanggal snapshot konteks: 2026-04-12
- Entry point aplikasi: main.py

## 2. Ringkasan Produk
BeasiswaKu adalah aplikasi manajemen beasiswa personal dengan fokus:
- Autentikasi user
- Browsing beasiswa
- Tracking lamaran
- Favorit beasiswa
- Catatan pribadi
- Statistik/visualisasi

Target utama penggunaan saat ini adalah desktop lokal/offline dengan database SQLite dalam proyek.

## 3. Sumber Kebenaran (Source of Truth)
Urutan sumber kebenaran yang dipakai di dokumen ini:
1. Kode aktual di main.py dan src/
2. Kontrak fungsi di src/database/crud.py
3. Struktur test di tests/
4. Dokumen markdown (README/docs) sebagai referensi sekunder

Catatan penting: Beberapa dokumentasi di repo masih merujuk file lama yang sudah tidak ada (misalnya src/gui/main_window.py, src/gui/login_window.py, src/gui/dialogs.py), sementara implementasi aktual dipusatkan di main.py dan modul tab di src/gui/.

## 4. Arsitektur Runtime Aktual

### 4.1 Alur Startup
1. main.main() membuat QApplication
2. init_db() dipanggil (delegasi ke DatabaseManager.init_schema)
3. LoginWindow tampil
4. Jika login sukses, MainWindow dibuat dengan user_id + username
5. MainWindow menampilkan sidebar + tab content

### 4.2 Komponen Utama
- main.py
  - LoginWindow
  - RegisterWindow
  - MainWindow
  - SettingsWindow
- src/core/
  - config.py: konfigurasi global via env
  - database.py: DatabaseManager singleton + init schema
- src/database/
  - crud.py: autentikasi, CRUD, agregasi
- src/gui/
  - sidebar.py
  - gui_beasiswa.py (dipakai oleh main.py)
  - tab_beranda.py
  - tab_tracker.py
  - tab_statistik.py
  - tab_profil.py
  - tab_favorit.py
  - tab_notes.py
  - components.py
  - design_tokens.py
  - styles.py
- src/scraper/scraper.py
- src/visualization/visualisasi.py

### 4.3 Navigasi UI
Sidebar mengontrol index tab:
- 0: Beranda
- 1: Beasiswa
- 2: Tracker Lamaran
- 3: Statistik
- 4: Profil

Tab bar disembunyikan, jadi navigasi utama lewat sidebar.

## 5. Struktur Direktori Aktual (Ringkas)
- main.py
- src/core/
- src/database/
- src/gui/
- src/scraper/
- src/visualization/
- tests/unit/
- tests/integration/
- docs/
- database/
- data/
- backup/
- logs/

## 6. Model Data dan Skema Database
Database manager membuat 6 tabel utama:

1. akun
- id
- username (unique)
- email (unique)
- password_hash
- nama_lengkap
- jenjang
- created_at
- updated_at

2. penyelenggara
- id
- nama
- description
- website
- contact_email
- created_at

3. beasiswa
- id
- judul
- penyelenggara_id (FK)
- jenjang
- deadline
- deskripsi
- benefit
- persyaratan
- minimal_ipk
- coverage
- status (default: Buka)
- link_aplikasi
- scrape_date
- created_at
- updated_at

4. riwayat_lamaran
- id
- user_id (FK)
- beasiswa_id (FK)
- status (default: Pending)
- tanggal_daftar
- catatan
- created_at
- updated_at
- unique(user_id, beasiswa_id)

5. favorit
- id
- user_id (FK)
- beasiswa_id (FK)
- created_at
- unique(user_id, beasiswa_id)

6. catatan
- id
- user_id (FK)
- beasiswa_id (FK)
- content
- created_at
- updated_at
- unique(user_id, beasiswa_id)

## 7. Kontrak API Backend (src/database/crud.py)

### 7.1 Authentication
- register_user(username, email, password, nama_lengkap="", jenjang="") -> (bool, str)
- login_user(username, password) -> (bool, str, user_data|None)
- hash_password(password) -> str
- verify_password(password, hashed_password) -> bool

### 7.2 Beasiswa
- add_beasiswa(...) -> (bool, str, beasiswa_id|None)
- get_beasiswa_list(filter_jenjang=None, filter_status=None, search_judul=None, sort_by='deadline', sort_order='ASC') -> (list[dict], int)
- edit_beasiswa(beasiswa_id, **kwargs) -> (bool, str)
- delete_beasiswa(beasiswa_id) -> (bool, str)

### 7.3 Lamaran
- add_lamaran(user_id, beasiswa_id, tanggal_daftar=None, status='Pending', catatan='') -> (bool, str, lamaran_id|None)
- get_lamaran_list(filter_user_id=None, filter_beasiswa_id=None, filter_status=None, sort_by='tanggal_daftar', sort_order='DESC') -> (list[dict], int)
- edit_lamaran(lamaran_id, **kwargs) -> (bool, str)
- delete_lamaran(lamaran_id) -> (bool, str)

### 7.4 Favorit
- add_favorit(user_id, beasiswa_id) -> (bool, str, favorit_id|None)
- get_favorit_list(user_id, sort_by='created_at', sort_order='DESC') -> (list[dict], int)
- delete_favorit(user_id, beasiswa_id) -> (bool, str)

### 7.5 Catatan
- add_catatan(user_id, beasiswa_id, content) -> (bool, str, catatan_id|None)
- get_catatan(user_id, beasiswa_id) -> (catatan_dict|None, str)
- edit_catatan(user_id, beasiswa_id, content) -> (bool, str)
- delete_catatan(user_id, beasiswa_id) -> (bool, str)
- get_catatan_list(user_id, filter_jenjang=None, search_judul=None) -> (list[dict], int)

### 7.6 Aggregation
- get_beasiswa_per_jenjang() -> dict[str, int]
- get_top_penyelenggara(limit=10) -> list[dict]
- get_status_availability() -> dict[str, int]
- check_user_applied(user_id, beasiswa_id) -> bool
- get_beasiswa_list_for_user(...) -> (list[dict], int)

## 8. Detail GUI Saat Ini

### 8.1 main.py
- Menangani autentikasi, main shell window, tab mounting, sidebar wiring.
- Login dan register sudah terhubung ke CRUD.
- SettingsWindow ada, namun implementasi ganti password saat ini tidak sinkron dengan schema terbaru (lihat bagian risiko).

### 8.2 Tab Beranda (src/gui/tab_beranda.py)
- Menampilkan stat card, deadline card, activity timeline.
- Ada query total beasiswa dari database.
- Banyak konten masih statis/hardcoded untuk activity/teks.

### 8.3 Tab Beasiswa (src/gui/gui_beasiswa.py)
- Search, filter status, filter jenjang, filter deadline, refresh, export CSV.
- Tabel data beasiswa dengan aksi view/bookmark/apply (aksi masih TODO di sebagian fungsi).
- Mengambil data dari tabel beasiswa + join penyelenggara.

### 8.4 Tab Tracker (src/gui/tab_tracker.py)
- Menampilkan riwayat lamaran + chart donut/bar.
- Data tabel saat ini masih sample data hardcoded (belum full mengambil data real CRUD untuk daftar lamaran user aktif).

### 8.5 Tab Statistik (src/gui/tab_statistik.py)
- Menampilkan stat cards + 3 chart.
- Ada query ke database, tapi banyak nilai visual/angka awal masih berbasis konfigurasi statis pada UI.

### 8.6 Tab Profil (src/gui/tab_profil.py)
- Layout profil lengkap (avatar, informasi, keamanan, preferensi, aktivitas).
- Fungsi load_user_data() saat ini query ke tabel users, padahal schema memakai tabel akun.

### 8.7 Modul Favorit dan Notes
- src/gui/tab_favorit.py
  - Toggle favorit, list favorit, stats favorit.
  - Sudah memakai fungsi CRUD favorit.
- src/gui/tab_notes.py
  - Notes editor dialog, quick notes button, list notes.
  - Sudah memakai CRUD catatan.

### 8.8 Design System
- design_tokens.py: token warna, typo, spacing, border radius, dll.
- styles.py: stylesheet global + helper button/banner/badge/dialog.
- Theme dominan saat ini: Navy + Orange.

## 9. Modul Scraper (src/scraper/scraper.py)
- Source target: indbeasiswa.com
- Kategori utama: s1, s2, diploma, dalam_negeri, luar_negeri
- Mendukung pagination (default 10 halaman per kategori)
- Helper utama: parse_deadline, determine_status, extract_penyelenggara, normalize_url, clean_text
- Menyimpan backup JSON ke folder backup/
- Ada dukungan QThread jika PyQt tersedia
- Integrasi langsung ke alur utama aplikasi belum aktif secara default

## 10. Modul Visualization (src/visualization/visualisasi.py)
- Menyediakan chart builder berbasis matplotlib:
  - Bar beasiswa per jenjang
  - Bar top penyelenggara
  - Pie status ketersediaan
  - Pie status lamaran
  - Bar lamaran per bulan
- Menyediakan data loader dari CRUD:
  - load_statistik_data()
  - load_tracker_data(user_id)
- Menyediakan converter Figure -> FigureCanvas
- Modul ini secara konsep bisa dijadikan single source chart engine, namun tab GUI saat ini masih punya implementasi chart sendiri.

## 11. Testing dan Kualitas

### 11.1 Struktur Test Aktual
File unit test inti:
- tests/unit/test_database.py
- tests/unit/test_gui.py
- tests/unit/test_scraper.py
- tests/unit/test_visualization.py
- tests/unit/test_init.py

Ada folder backup test phase lama di tests/unit/backup/.

### 11.2 Fakta Cepat dari Struktur Test
- test_database.py: 8 fungsi test
- test_gui.py: 31 fungsi test
- test_scraper.py: 33 fungsi test
- test_visualization.py: 61 fungsi test (terdapat duplikasi blok class test dalam file)

### 11.3 Status yang Dilaporkan Dokumentasi
TESTING_REPORT.md menyatakan:
- 107/107 test pass
- coverage inti 100%

Catatan: angka ini berasal dari laporan proyek, bukan verifikasi eksekusi ulang pada snapshot dokumen ini.

## 12. Dependensi, Build, dan Run

### 12.1 requirements.txt
- PyQt6
- matplotlib
- requests
- beautifulsoup4
- lxml
- bcrypt
- plyer

### 12.2 Command utama (Makefile)
- make setup
- make run
- make test
- make test-cov
- make lint
- make format
- make type-check

## 13. Risiko dan Inconsistency Penting (Wajib Diketahui untuk Redesign)

### 13.1 Mismatch schema vs query (tinggi)
- main.py SettingsWindow memakai kolom id_akun/password, padahal schema memakai id/password_hash.
- src/gui/tab_profil.py query tabel users, padahal tabel aktual adalah akun.

Dampak: fitur profile/security bisa gagal runtime atau tidak update data yang benar.

### 13.2 Singleton DB connection vs manual conn.close (tinggi)
Beberapa tab memanggil conn.close() langsung setelah get_connection() dari singleton manager.

Dampak potensial:
- DatabaseManager menyimpan object connection yang sudah ditutup.
- Operasi berikutnya dapat memicu error "Cannot operate on a closed database".

### 13.3 Duplikasi modul beasiswa (sedang)
- src/gui/gui_beasiswa.py
- src/gui/tab_beasiswa.py

Keduanya sangat mirip. main.py saat ini memakai gui_beasiswa.py.

Dampak: biaya maintenance tinggi, potensi drift fitur.

### 13.4 Kontrak export package tidak sinkron (sedang)
src/database/__init__.py mengekspor nama create_* yang tidak sesuai fungsi aktual (add_*/edit_*).

Dampak: import dari package level rawan gagal/menyesatkan.

### 13.5 Dokumentasi dan script setup sebagian usang (sedang)
- Banyak docs masih refer ke file GUI lama yang tidak ada.
- setup.sh dan setup_and_run.sh memakai import/path lama (mis. from crud import ...).

Dampak: onboarding baru berpotensi gagal atau bingung.

### 13.6 Integrasi scraper/visualization ke main flow belum penuh (sedang)
- Scraper belum jadi bagian startup flow utama.
- Statistik/tracker di GUI belum sepenuhnya memakai engine visualization terpusat.

## 14. Redesign Opportunities

### 14.1 Prioritas Redesign GUI
1. Satukan source UI per tab (hapus duplikasi gui_beasiswa vs tab_beasiswa).
2. Terapkan satu data pipeline untuk semua tab (hindari sample data hardcoded di tab production).
3. Standardisasi status dan label di UI:
   - Beasiswa: Buka, Segera Tutup, Tutup
   - Lamaran: Pending, Submitted, Accepted, Rejected, Withdrawn
4. Refactor form validasi dan feedback error jadi reusable component.
5. Rapikan style system agar semua komponen pakai helper styles.py (kurangi inline stylesheet besar).

### 14.2 Prioritas Redesign Sistem
1. Tambah service layer di antara GUI dan CRUD mentah.
2. Pisahkan query SQL dari widget code (pattern repository/service).
3. Benahi manajemen koneksi singleton:
   - Hindari conn.close() di consumer layer
   - Tambah safe reconnect check pada DatabaseManager
4. Satukan modul chart:
   - GUI memanggil src/visualization/visualisasi.py, bukan chart custom per tab.
5. Satukan status enum/constant di satu tempat (misalnya src/utils/constants).

### 14.3 Prioritas Data dan Integrasi
1. Pastikan scraper output map konsisten ke kolom beasiswa.
2. Buat pipeline ingest resmi (scrape -> validate -> upsert database).
3. Tambah migration script sederhana untuk perubahan schema di masa depan.

## 15. Rekomendasi Strategi Implementasi Redesign

### Opsi A - Stabilize dulu, lalu redesign visual
- Fase 1: Fix mismatch schema/query + connection lifecycle
- Fase 2: Unifikasi data source tracker/statistik/favorit/notes
- Fase 3: Redesign visual dan interaction flow

### Opsi B - Parallel redesign GUI + refactor backend tipis
- Buat branch redesign terpisah
- Bangun presenter/service baru tanpa langsung menghapus modul lama
- Migrasi tab satu per satu

Untuk tim kecil dan risiko runtime saat ini, Opsi A biasanya lebih aman.

## 16. Prompt Starter untuk Gemini
Gunakan prompt awal berikut jika ingin Gemini langsung bekerja dengan konteks ini:

"Saya lampirkan Context Document BeasiswaKu. Tolong lakukan audit redesign menyeluruh dalam 3 bagian: (1) quick wins bugfix kritis, (2) redesign arsitektur sistem yang realistis untuk PyQt6 + SQLite, (3) redesign GUI modern dengan prioritas usability mahasiswa. Berikan output berupa roadmap 4 fase, daftar perubahan per file, dan draft struktur modul baru yang kompatibel dengan codebase saat ini."

## 17. Checklist Validasi Setelah Redesign (Disarankan)
- Login/register bekerja dengan password_hash bcrypt
- Settings/Profile update bekerja ke tabel akun
- Tidak ada penggunaan conn.close() langsung dari layer GUI
- Tracker dan Statistik mengambil data real dari CRUD/service
- Satu sumber file BeasiswaTab saja
- Test otomatis berjalan konsisten dan laporan test diperbarui

## 18. Catatan Penutup
Project ini punya fondasi yang cukup kuat (struktur modul, CRUD lengkap, design tokens, test suite cukup besar), tetapi perlu sinkronisasi antar lapisan agar redesign tidak hanya cantik secara UI, tapi juga stabil secara runtime dan maintainable untuk jangka panjang.
