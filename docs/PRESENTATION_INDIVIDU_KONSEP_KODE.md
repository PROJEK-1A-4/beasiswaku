# BeasiswaKu - Penjelasan Konsep + Kodingan per Individu

Dokumen ini berisi materi presentasi per individu: konsep dasar yang digunakan, keterkaitannya dengan fitur, dan contoh kode yang benar-benar diterapkan di project.

## 1. Darva

Peran utama: Core system, database, CRUD, dan agregasi data backend.

Konsep dasar yang dijelaskan:
- Fungsi (`def`) untuk modularisasi operasi database per fitur.
- Class/Object dengan `DatabaseManager` (singleton) untuk pengelolaan koneksi.
- Struktur data `tuple`, `list`, `dict` untuk return value dan payload data.
- Integrasi data storage melalui SQLite file-based.

Keterkaitan konsep dengan fitur:
- Login/register, tambah lamaran, favorit, statistik status semuanya bergantung pada fungsi CRUD modular.
- Koneksi database yang stabil dipakai semua fitur GUI melalui singleton manager.

Nama file dan contoh kodingan:

File: `src/core/database.py`

```python
class DatabaseManager:
    _instance: Optional['DatabaseManager'] = None
    _connection: Optional[sqlite3.Connection] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def get_connection(self) -> sqlite3.Connection:
        if self._connection is None:
            self._connection = self._create_connection()
        return self._connection
```

File: `src/database/crud.py`

```python
def register_user(username: str, email: str, password: str,
                 nama_lengkap: str = "", jenjang: str = "") -> Tuple[bool, str]:
    if not username or not username.strip():
        return False, "Username tidak boleh kosong"

    password_hash = hash_password(password)
    cursor.execute("""
        INSERT INTO akun (username, email, password_hash, nama_lengkap, jenjang)
        VALUES (?, ?, ?, ?, ?)
    """, (username, email, password_hash, nama_lengkap, jenjang))
```

File: `src/database/crud.py`

```python
def add_lamaran(user_id: int, beasiswa_id: int, tanggal_daftar: Optional[str] = None,
               status: str = "Pending", catatan: str = "") -> Tuple[bool, str, Optional[int]]:
    if tanggal_daftar is None or tanggal_daftar.strip() == "":
        tanggal_daftar = datetime.now().strftime('%Y-%m-%d')

    cursor.execute("""
        INSERT INTO riwayat_lamaran (user_id, beasiswa_id, tanggal_daftar, status, catatan)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, beasiswa_id, tanggal_daftar, status, catatan.strip()))
```

File: `src/database/crud.py`

```python
def get_status_availability() -> Dict[str, int]:
    cursor.execute("""
        SELECT status, COUNT(*) as total
        FROM beasiswa
        WHERE status IS NOT NULL
        GROUP BY status
    """)
    results = cursor.fetchall()
    status_dict = {row['status']: row['total'] for row in results}
    return status_dict
```

## 2. Kemal

Peran utama: Web scraping, parsing data eksternal, backup data, sinkronisasi async.

Konsep dasar yang dijelaskan:
- Fungsi (`def`) sebagai pipeline scraping bertahap.
- Class/Object (`ScraperThread`) untuk proses background agar UI tidak freeze.
- Struktur data `list`, `set`, `dict` untuk hasil scraping dan deduplikasi.
- File handling (`open`, `json.dump`) untuk backup data scraping.

Keterkaitan konsep dengan fitur:
- Tombol "Sync Web" di Beranda/Beasiswa memicu scraping ini.
- Data hasil scraping dipakai untuk memperbarui daftar beasiswa pada aplikasi.

Nama file dan contoh kodingan:

File: `src/scraper/scraper.py`

```python
def scrape_beasiswa_data() -> Dict[str, List[Dict]]:
    all_beasiswa = []
    all_penyelenggara = set()

    for category_name, category_slug in CATEGORIES.items():
        beasiswa_list = scrape_category(category_slug, category_name)
        for b in beasiswa_list:
            if b.get("penyelenggara"):
                all_penyelenggara.add(b["penyelenggara"])
        all_beasiswa.extend(beasiswa_list)
```

File: `src/scraper/scraper.py`

```python
def save_backup(data: Dict) -> Dict[str, str]:
    beasiswa_file = os.path.join(BACKUP_DIR, "beasiswa.json")
    with open(beasiswa_file, "w", encoding="utf-8") as f:
        json.dump(data["beasiswa"], f, ensure_ascii=False, indent=2)

    metadata_file = os.path.join(BACKUP_DIR, "_metadata.json")
    metadata = {
        "timestamp": data.get("timestamp"),
        "total_beasiswa": data.get("total_beasiswa"),
        "total_penyelenggara": data.get("total_penyelenggara"),
        "categories": list(CATEGORIES.keys())
    }
    with open(metadata_file, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
```

File: `src/scraper/scraper.py`

```python
class ScraperThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(object)
    error = pyqtSignal(str)

    def run(self):
        beasiswa_data = scrape_beasiswa_data()
        self.finished.emit(beasiswa_data)
```

## 3. Aulia

Peran utama: Entry point aplikasi, autentikasi, main window orchestration, pengaturan akun.

Konsep dasar yang dijelaskan:
- Fungsi (`def`) sebagai event handler untuk aksi user (login, register).
- Class/Object (`LoginWindow`, `RegisterWindow`, `MainWindow`) untuk pengelompokan logika tiap layar.
- Struktur data tuple dari backend (`success, message, user_data`) untuk kontrol alur UI.
- Integrasi dengan database backend untuk autentikasi dan update akun.

Keterkaitan konsep dengan fitur:
- Seluruh perjalanan user dari aplikasi dibuka sampai masuk dashboard utama dikontrol dari modul ini.

Nama file dan contoh kodingan:

File: `main.py`

```python
class LoginWindow(QDialog):
    login_success = pyqtSignal(int, str)

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        success, message, user_data = login_user(username, password)
        if success:
            self.current_user_id = user_data['id']
            self.login_success.emit(user_data['id'], username)
            self.accept()
```

File: `main.py`

```python
class RegisterWindow(QDialog):
    def handle_register(self):
        username = self.username_input.text().strip()
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()
        success, message = register_user(username, email, password)
        if success:
            self.accept()
```

File: `main.py`

```python
class MainWindow(QMainWindow):
    def __init__(self, user_id: int, username: str):
        super().__init__()
        self.user_id = user_id
        self.username = username
        self.init_ui()
```

## 4. Kyla

Peran utama: Implementasi antarmuka tab dan interaksi user (Beasiswa, Beranda, Tracker, Profil).

Konsep dasar yang dijelaskan:
- Fungsi (`def`) untuk filter data, apply lamaran, refresh tampilan.
- Class/Object (`BeasiswaTab`, `TrackerTab`) untuk pemisahan fitur UI.
- Struktur data `list` dan `dict` untuk data tabel/filter.
- File handling pada fitur export CSV.
- Chart pada tracker untuk menjelaskan progres lamaran user.

Keterkaitan konsep dengan fitur:
- Interaksi user di UI langsung memanggil backend dan update tab lain agar data sinkron.

Nama file dan contoh kodingan:

File: `src/gui/tab_beasiswa.py`

```python
def _get_filtered_data(self) -> List[Dict[str, Any]]:
    search_text = self.search_input.text().lower()
    status_filter = self.status_filter.currentText()
    jenjang_filter = self.jenjang_filter.currentText()

    return [
        item for item in self.beasiswa_data
        if (search_text in item["nama"].lower() or
            search_text in item["penyelenggara"].lower()) and
           (status_filter == "Semua" or item["status"] == status_filter) and
           (jenjang_filter == "Semua" or item["jenjang"] == jenjang_filter)
    ]
```

File: `src/gui/tab_beasiswa.py`

```python
def export_to_csv(self):
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['NO', 'NAMA BEASISWA', 'PENYELENGGARA', 'JENJANG', 'DEADLINE', 'STATUS']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for idx, item in enumerate(rows_to_export, 1):
            writer.writerow({
                'NO': idx,
                'NAMA BEASISWA': item['nama'],
                'PENYELENGGARA': item['penyelenggara'],
                'JENJANG': item['jenjang'],
                'DEADLINE': item['deadline'],
                'STATUS': item['status']
            })
```

File: `src/gui/tab_beasiswa.py`

```python
def apply_beasiswa(self, beasiswa_id: int):
    if check_user_applied(self.user_id, beasiswa_id):
        return

    success, message, _ = add_lamaran(
        user_id=self.user_id,
        beasiswa_id=beasiswa_id,
        status="Pending",
    )
```

File: `src/gui/tab_tracker.py`

```python
def _create_donut_chart(self) -> FigureCanvas:
    status_counts = self._get_status_counts()
    labels = list(APPLICATION_STATUS_ORDER)
    sizes = [status_counts[label] for label in labels]
    ax.pie(sizes, colors=colors, autopct=lambda pct: f"{pct:.0f}%")
```

## 5. Richard

Peran utama: Dashboard statistik dan visualisasi data (chart-based insights).

Konsep dasar yang dijelaskan:
- Fungsi (`def`) untuk generate masing-masing chart.
- Class/Object (`StatistikTab`) untuk mengelola komponen visualisasi secara terstruktur.
- Struktur data `dict` dan `list` untuk mapping data agregasi ke chart.
- Keterkaitan langsung antara query agregasi dan visual chart (bar/donut).

Keterkaitan konsep dengan fitur:
- User dapat melihat pola data beasiswa secara visual: distribusi jenjang, status ketersediaan, top penyelenggara.

Nama file dan contoh kodingan:

File: `src/gui/tab_statistik.py`

```python
class StatistikTab(QWidget):
    def _get_status_count_map(self) -> Dict[str, int]:
        status_map = {label: 0 for label in SCHOLARSHIP_STATUS_ORDER}
        for key, count in self.stat_data.get("status_counts", {}).items():
            if key in status_map:
                status_map[key] = int(count or 0)
        return status_map
```

File: `src/gui/tab_statistik.py`

```python
def _create_bar_chart(self) -> FigureCanvas:
    jenjang_map = self._get_jenjang_count_map()
    jenjang = [k for k in ["D3", "D4", "S1", "S2"] if k in jenjang_map]
    values = [jenjang_map.get(k, 0) for k in jenjang]
    ax.bar(jenjang, values, color=colors)
```

File: `src/gui/tab_statistik.py`

```python
def _create_donut_chart(self) -> FigureCanvas:
    status_map = self._get_status_count_map()
    statuses = ['Buka', 'Segera Tutup', 'Tutup']
    values = [status_map.get(s, 0) for s in statuses]
    ax.pie(values, colors=colors, wedgeprops=dict(width=0.36))
```

File: `src/services/dashboard_service.py`

```python
def get_statistik_snapshot(top_limit: int = 5) -> Dict[str, Any]:
    raw_status_counts = get_status_availability()
    normalized_status_counter: Counter = Counter()
    for key, value in raw_status_counts.items():
        normalized_status_counter[normalize_scholarship_status(key)] += int(value or 0)

    jenjang_counts = {str(key): int(value) for key, value in get_beasiswa_per_jenjang().items() if key}
    return {
        "status_counts": ordered_counts(normalized_status_counter, SCHOLARSHIP_STATUS_ORDER),
        "jenjang_counts": jenjang_counts,
    }
```

## 6. Catatan Penggunaan Saat Presentasi

Saran alur penjelasan per orang agar konsisten:
1. Tunjukkan fitur yang didemo dulu.
2. Jelaskan konsep dasarnya (def/class/struktur data/file handling/chart).
3. Tunjukkan potongan kode + nama file.
4. Tutup dengan dampak ke fitur (mengapa solusi itu dipilih).
