# 🎓 Blueprint Aplikasi BeasiswaKu
### Dokumen Cetak Biru Komprehensif — Versi 1.0

> **Disusun oleh:** Kelompok A4 | D4 Sarjana Terapan Teknik Informatika | POLBAN | 2025/2026
> **Status Dokumen:** Draft Aktif — diperbarui seiring progres pengerjaan
> **Tanggal:** Maret 2026

---

## Daftar Isi

1. [Ringkasan Eksekutif](#1-ringkasan-eksekutif)
2. [Target Pengguna & Konteks](#2-target-pengguna--konteks)
3. [Daftar Fitur](#3-daftar-fitur)
4. [Alur Pengguna (User Flow)](#4-alur-pengguna-user-flow)
5. [Kebutuhan Layar (UI Requirements)](#5-kebutuhan-layar-ui-requirements)
6. [Arsitektur Data & Sistem](#6-arsitektur-data--sistem)
7. [Rekomendasi Tech Stack](#7-rekomendasi-tech-stack)
8. [Strategi Pembeda dari Kompetitor](#8-strategi-pembeda-dari-kompetitor)
9. [Risiko & Mitigasi](#9-risiko--mitigasi)
10. [Catatan Teknis Penting](#10-catatan-teknis-penting)
11. [Timeline & Milestone](#11-timeline--milestone)
12. [Pembagian Tugas Tim](#12-pembagian-tugas-tim)

---

## 1. Ringkasan Eksekutif

### Konsep Utama
BeasiswaKu adalah **aplikasi desktop personal scholarship manager** berbasis Python yang dirancang untuk menjadi satu-satunya alat yang dibutuhkan mahasiswa dalam perjalanan mencari dan mendaftar beasiswa — mulai dari menemukan beasiswa yang sesuai, mencatat setiap lamaran, hingga mengevaluasi progres secara visual.

### Problem Statement
Mahasiswa Indonesia menghadapi tiga masalah nyata dalam proses pencarian beasiswa:

| # | Masalah | Dampak |
|---|---|---|
| 1 | Informasi beasiswa sulit diakses dan tidak dapat difilter sesuai kebutuhan karena tidak tersedia dalam satu platform yang terorganisir | Mahasiswa melewatkan peluang beasiswa yang sebenarnya sesuai |
| 2 | Tidak ada pengingat terpusat untuk deadline pendaftaran | Mahasiswa gagal daftar bukan karena tidak memenuhi syarat, tapi karena terlambat |
| 3 | Tidak ada tools untuk mencatat dan melacak status lamaran secara pribadi | Mahasiswa kehilangan jejak lamarannya sendiri dan tidak bisa evaluasi progres |

Kondisi ini diperparah oleh ketidaksetaraan akses informasi yang terbukti menurunkan partisipasi pendaftaran meskipun mahasiswa sebenarnya memenuhi syarat *(Herber, 2018)*.

### Solusi
Platform desktop **offline-first** yang mengotomatisasi pengambilan data beasiswa via web scraping, dilengkapi sistem autentikasi multi-user, manajemen lamaran personal, dan visualisasi grafik progres — semua dalam satu tampilan terintegrasi.

### Nilai Unik (Unique Value Proposition)
> *"BeasiswaKu bukan sekadar agregator beasiswa. Ini adalah personal scholarship manager — dari menemukan, menandai, mendaftar, hingga mengevaluasi, semua dalam satu aplikasi desktop yang bekerja offline."*

---

## 2. Target Pengguna & Konteks

### Profil Pengguna Utama
- **Siapa:** Mahasiswa aktif jenjang D3, D4, S1, dan S2
- **Usia:** 18–27 tahun
- **Konteks penggunaan:** Digunakan di laptop/PC pribadi, baik di kos, kampus, maupun rumah
- **Tingkat literasi teknologi:** Menengah — familiar dengan aplikasi desktop, tidak perlu dokumentasi teknis yang rumit
- **Frekuensi penggunaan:** Mingguan saat musim beasiswa, harian saat mendekati deadline

### Kebutuhan Utama Pengguna
- Ingin tahu beasiswa apa saja yang tersedia untuk jenjangnya **tanpa harus membuka banyak tab browser**
- Ingin diingatkan deadline secara otomatis **tanpa harus mengingat sendiri**
- Ingin mencatat beasiswa mana yang sudah didaftar dan apa statusnya **dalam satu tempat**
- Ingin tahu seberapa aktif dirinya mendaftar beasiswa **secara visual**

### Skenario Penggunaan Nyata
```
Skenario 1 — Pencarian Rutin:
Budi, mahasiswa D4 semester 3, membuka BeasiswaKu setiap Senin pagi.
Ia langsung filter "Diploma" dan "Buka" → lihat 12 beasiswa yang relevan →
tandai 3 sebagai favorit → lihat 1 beasiswa deadline 5 hari lagi (highlight merah) →
langsung catat di Tracker sebagai "Pending".

Skenario 2 — Evaluasi Bulanan:
Di akhir bulan, Siti membuka Tab Statistik → lihat pie chart lamarannya:
6 Pending, 2 Diterima, 1 Ditolak → motivasi untuk lebih aktif bulan depan.
```

---

## 3. Daftar Fitur

### 3.1 Fitur MVP (Minimum Viable Product) — Target UTS

#### 🔐 Autentikasi & Akun
- [ ] Halaman Register (username, email, password)
- [ ] Halaman Login
- [ ] Logout
- [ ] Password di-hash menggunakan `bcrypt`
- [ ] CRUD manajemen akun pengguna

#### 📋 Tab Beasiswa
- [ ] Tabel data beasiswa hasil scraping otomatis
- [ ] Filter & search real-time (jenjang, status)
- [ ] Sort kolom ascending/descending (klik header)
- [ ] CRUD manual (tambah, edit, hapus) + validasi form + dialog konfirmasi
- [ ] Warning ⚠️ untuk beasiswa deadline ≤ 7 hari
- [ ] Export data ke CSV
- [ ] Timestamp waktu scraping terakhir
- [ ] Auto-scraping saat pertama buka (jika database kosong)

#### 📝 Tab Tracker Lamaran
- [ ] CRUD riwayat lamaran pribadi per akun
- [ ] Validasi input + dialog konfirmasi hapus
- [ ] Pie chart: proporsi status (Pending / Diterima / Ditolak)
- [ ] Bar chart: jumlah lamaran per bulan

### 3.2 Fitur Lanjutan — Target UAS

#### 📊 Tab Statistik
- [ ] Bar chart: jumlah beasiswa per jenjang pendidikan
- [ ] Bar chart: top 5 penyelenggara beasiswa terbanyak
- [ ] Pie chart: proporsi ketersediaan beasiswa (Buka / Segera Tutup / Tutup)
- [ ] Warna grafik dinamis mengikuti data real

### 3.3 Fitur Tambahan — Nilai Plus

| Prioritas | Fitur | Kesulitan | PIC |
|---|---|---|---|
| ⭐ Tinggi | Highlight baris deadline (kuning/merah) | 🟢 Mudah | Kyla |
| ⭐ Tinggi | Kolom "Sudah Daftar?" di Tab Beasiswa | 🟡 Sedang | Kyla + Darva |
| ⭐ Tinggi | Detail popup beasiswa (dobel klik) | 🟡 Sedang | Kyla |
| ⭐ Tinggi | Fitur Favorit / Bookmark | 🟡 Sedang | Kyla + Darva |
| 🔵 Sedang | Counter jumlah data di judul tab | 🟢 Mudah | Aulia |
| 🔵 Sedang | Tombol Refresh manual | 🟢 Mudah | Kyla + Kemal |
| 🔵 Sedang | Filter deadline otomatis (sekali klik) | 🟢 Mudah | Kyla |
| 🔵 Sedang | Dark / Light Mode | 🟢 Mudah | Aulia |
| 🔵 Sedang | Catatan pribadi per beasiswa | 🟡 Sedang | Darva + Kyla |
| 🔵 Sedang | Halaman profil pengguna | 🟡 Sedang | Darva |
| ⚪ Opsional | Notifikasi desktop OS (`plyer`) | 🔴 Kompleks | Aulia |
| ⚪ Opsional | Pengingat deadline terjadwal | 🔴 Kompleks | Darva + Aulia |
| ⚪ Opsional | Audit log perubahan data | 🔴 Kompleks | Darva |
| ⚪ Opsional | Full-text search deskripsi beasiswa | 🔴 Kompleks | Kyla + Kemal |
| ⚪ Opsional | Grafik tren beasiswa per bulan/tahun | 🔴 Kompleks | Richard |

---

## 4. Alur Pengguna (User Flow)

### 4.1 Flow Pertama Kali Membuka Aplikasi (New User)

```
[Buka Aplikasi]
       │
       ▼
[Cek database SQLite]
       │
   Belum ada ──────────────────────────────────────────┐
       │                                               │
       ▼                                               ▼
[Tampil Screen Login]                    [Jalankan Auto-Scraping]
       │                                    (background thread)
       ▼                                               │
[Pilih: Login / Register]                [Simpan ke SQLite]
       │                                               │
  Register ──► [Isi Form Register]                     │
       │              │                                │
       │         [Validasi Input]                      │
       │              │                                │
       │       [Simpan ke tabel akun]                  │
       │              │                                │
       └──────────────┘                                │
       │                                               │
       ▼                                               │
[Login berhasil] ◄─────────────────────────────────────┘
       │
       ▼
[Tampil Main Window — Tab Beasiswa aktif]
```

### 4.2 Flow Pengguna yang Sudah Punya Akun

```
[Buka Aplikasi]
       │
       ▼
[Cek database SQLite — sudah ada]
       │
       ▼
[Tampil Screen Login]
       │
[Isi username + password] ──► [Verifikasi bcrypt hash]
       │                               │
       │                        Gagal ─┘─► [Tampil pesan error]
       │                                        │
       │                                   [Coba lagi]
       │
   Berhasil
       │
       ▼
[Main Window terbuka]
       │
       ├──► [Tab Beasiswa] ─────────────────────────────────────────────┐
       │         │                                                       │
       │    [Lihat tabel beasiswa]                                       │
       │         │                                                       │
       │    [Filter/Search/Sort] ──► [Tabel terupdate real-time]        │
       │         │                                                       │
       │    [Klik 2x baris] ──► [Popup detail beasiswa]                 │
       │         │                                                       │
       │    [Klik Favorit] ──► [Tersimpan ke tabel favorit]             │
       │         │                                                       │
       │    [CRUD manual] ──► [Validasi] ──► [Dialog konfirmasi] ──► [Simpan] │
       │         │                                                       │
       │    [Export CSV] ──► [Pilih lokasi simpan] ──► [File .csv]      │
       │         │                                                       │
       │    [Refresh] ──► [Jalankan ulang scraping]                     │
       │                                                                 │
       ├──► [Tab Tracker Lamaran] ──────────────────────────────────────┤
       │         │                                                       │
       │    [Lihat daftar lamaran pribadi]                               │
       │         │                                                       │
       │    [Tambah lamaran] ──► [Isi form] ──► [Validasi] ──► [Simpan]│
       │         │                                                       │
       │    [Edit/Hapus] ──► [Dialog konfirmasi] ──► [Update DB]        │
       │         │                                                       │
       │    [Lihat grafik] ──► [Pie chart status + Bar chart per bulan] │
       │                                                                 │
       ├──► [Tab Statistik] ────────────────────────────────────────────┤
       │         │                                                       │
       │    [Bar chart per jenjang]                                      │
       │    [Bar chart top 5 penyelenggara]                              │
       │    [Pie chart status ketersediaan]                              │
       │                                                                 │
       └──► [Logout] ──► [Kembali ke Screen Login] ────────────────────┘
```

### 4.3 Flow Notifikasi Deadline

```
[Aplikasi dibuka / Tab Beasiswa aktif]
       │
       ▼
[Sistem cek semua deadline di database]
       │
       ├──► deadline ≤ 3 hari ──► [Highlight baris MERAH] + [Warning popup]
       │
       ├──► deadline ≤ 7 hari ──► [Highlight baris KUNING] + [Ikon ⚠️]
       │
       └──► deadline > 7 hari ──► [Tampil normal]
```

---

## 5. Kebutuhan Layar (UI Requirements)

### Layar 1 — Screen Login

| Elemen | Detail |
|---|---|
| Logo & nama aplikasi | "BeasiswaKu" + tagline singkat |
| Field username | Input text, placeholder "Masukkan username" |
| Field password | Input password (tersembunyi), ikon show/hide |
| Tombol Login | Primary button |
| Link Register | "Belum punya akun? Daftar di sini" |
| Pesan error | Muncul di bawah form jika login gagal |

---

### Layar 2 — Screen Register

| Elemen | Detail |
|---|---|
| Field nama lengkap | Input text |
| Field username | Input text + validasi unik |
| Field email | Input text + validasi format email |
| Field password | Input password + konfirmasi password |
| Indikator kekuatan password | Weak / Medium / Strong |
| Tombol Daftar | Primary button |
| Link Login | "Sudah punya akun? Login" |

---

### Layar 3 — Main Window (Tab Beasiswa)

| Area | Elemen |
|---|---|
| **Toolbar atas** | Nama aplikasi, nama user yang login, tombol Logout |
| **Tab bar** | Tab Beasiswa (aktif) \| Tab Tracker \| Tab Statistik |
| **Bar kontrol** | Search box, dropdown filter Jenjang, dropdown filter Status, tombol Filter Aktif, tombol Refresh, tombol Export CSV |
| **Tabel utama** | Kolom: No, Nama Beasiswa, Penyelenggara, Jenjang, Deadline, Status, Sudah Daftar?, Aksi |
| **Highlight** | Baris merah (≤3 hari), baris kuning (≤7 hari) |
| **Footer tabel** | Timestamp scraping terakhir, jumlah data ditampilkan |
| **Panel CRUD** | Tombol Tambah, Edit (aktif jika baris dipilih), Hapus (aktif jika baris dipilih) |

---

### Layar 4 — Popup Detail Beasiswa

| Elemen | Detail |
|---|---|
| Nama beasiswa | Heading besar |
| Penyelenggara | Dengan link website resmi (klik buka browser) |
| Jenjang & deadline | Ditampilkan dengan warna status |
| Deskripsi | Teks lengkap hasil scraping |
| Tombol Favorit | Toggle ⭐ bookmark |
| Tombol Tambah ke Tracker | Langsung isi form Tracker dari popup ini |
| Tombol Tutup | Menutup popup |

---

### Layar 5 — Main Window (Tab Tracker Lamaran)

| Area | Elemen |
|---|---|
| **Panel kiri (40%)** | Tabel riwayat lamaran: Nama Beasiswa, Tanggal Daftar, Status, Catatan — tombol Tambah, Edit, Hapus |
| **Panel kanan atas (30%)** | Pie chart: proporsi status lamaran (Pending / Diterima / Ditolak) |
| **Panel kanan bawah (30%)** | Bar chart: jumlah lamaran per bulan |

---

### Layar 6 — Form Tambah/Edit Lamaran

| Elemen | Detail |
|---|---|
| Dropdown nama beasiswa | Pilih dari daftar beasiswa yang ada di database |
| Field tanggal daftar | Date picker |
| Dropdown status | Pending / Diterima / Ditolak |
| Field catatan | Text area bebas, opsional |
| Tombol Simpan | Primary button |
| Tombol Batal | Secondary button |
| Pesan validasi | Muncul inline di bawah field yang salah |

---

### Layar 7 — Main Window (Tab Statistik)

| Area | Elemen |
|---|---|
| **Panel kiri atas** | Bar chart: jumlah beasiswa per jenjang pendidikan |
| **Panel kanan atas** | Bar chart: top 5 penyelenggara terbanyak |
| **Panel bawah tengah** | Pie chart: proporsi status ketersediaan (Buka / Segera Tutup / Tutup) |
| **Keterangan** | Legenda warna dinamis di setiap grafik |

---

### Layar 8 — Halaman Profil Pengguna

| Elemen | Detail |
|---|---|
| Avatar/inisial nama | Ditampilkan sebagai lingkaran dengan inisial |
| Field nama lengkap | Editable |
| Field email | Editable + validasi format |
| Field username | Read-only |
| Ganti password | Form terpisah: password lama, password baru, konfirmasi |
| Tombol Simpan Perubahan | Primary button |
| Tombol Hapus Akun | Danger button + konfirmasi berlapis |

---

## 6. Arsitektur Data & Sistem

### 6.1 Struktur Folder Proyek

```
beasiswaku/
│
├── main.py                    # Entry point, main window, screen login, notifikasi
├── scraper.py                 # Web scraping + auto-scraping + generate JSON backup
├── crud.py                    # CRUD semua tabel + autentikasi + UI Tab Tracker
├── gui_beasiswa.py            # UI Tab Beasiswa
├── visualisasi.py             # Semua grafik (Tab Tracker & Tab Statistik)
│
├── database/
│   └── beasiswaku.db          # SQLite database utama (dibuat otomatis saat pertama run)
│
├── backup/
│   ├── beasiswa.json          # Ekspor/backup data beasiswa (memenuhi requirement)
│   ├── penyelenggara.json     # Ekspor/backup data penyelenggara
│   └── riwayat_lamaran.json   # Ekspor/backup riwayat lamaran
│
├── assets/
│   └── icon.png               # Ikon aplikasi (opsional)
│
├── requirements.txt           # Daftar library yang dibutuhkan
└── README.md                  # Dokumentasi lengkap
```

---

### 6.2 Skema Database SQLite

#### Tabel `akun`
```sql
CREATE TABLE akun (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    nama_lengkap    TEXT NOT NULL,
    username        TEXT NOT NULL UNIQUE,
    email           TEXT NOT NULL UNIQUE,
    password_hash   TEXT NOT NULL,        -- bcrypt hash
    created_at      TEXT DEFAULT (datetime('now', 'localtime'))
);
```

#### Tabel `beasiswa`
```sql
CREATE TABLE beasiswa (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    nama                TEXT NOT NULL,
    penyelenggara       TEXT,
    jenjang             TEXT,             -- S1 / S2 / Diploma / Umum
    deadline            TEXT,             -- Format: YYYY-MM-DD
    status              TEXT,             -- Buka / Segera Tutup / Tutup
    link                TEXT,
    deskripsi           TEXT,
    timestamp_scraping  TEXT              -- Waktu data terakhir diambil
);
```

#### Tabel `penyelenggara`
```sql
CREATE TABLE penyelenggara (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    nama            TEXT NOT NULL,
    jenis           TEXT,                 -- Pemerintah / Swasta / Internasional
    jumlah_beasiswa INTEGER DEFAULT 0,
    website         TEXT,
    kontak          TEXT,
    keterangan      TEXT
);
```

#### Tabel `riwayat_lamaran`
```sql
CREATE TABLE riwayat_lamaran (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL,
    nama_beasiswa   TEXT NOT NULL,
    tanggal_daftar  TEXT NOT NULL,        -- Format: YYYY-MM-DD
    status          TEXT DEFAULT 'Pending', -- Pending / Diterima / Ditolak
    catatan         TEXT,
    created_at      TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (user_id) REFERENCES akun(id) ON DELETE CASCADE
);
```

#### Tabel `favorit` *(fitur tambahan)*
```sql
CREATE TABLE favorit (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL,
    beasiswa_id INTEGER NOT NULL,
    added_at    TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (user_id) REFERENCES akun(id) ON DELETE CASCADE,
    FOREIGN KEY (beasiswa_id) REFERENCES beasiswa(id) ON DELETE CASCADE,
    UNIQUE (user_id, beasiswa_id)          -- Satu user tidak bisa favorit beasiswa yang sama 2x
);
```

#### Tabel `catatan` *(fitur tambahan)*
```sql
CREATE TABLE catatan (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL,
    beasiswa_id INTEGER NOT NULL,
    isi         TEXT,
    updated_at  TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (user_id) REFERENCES akun(id) ON DELETE CASCADE,
    FOREIGN KEY (beasiswa_id) REFERENCES beasiswa(id) ON DELETE CASCADE,
    UNIQUE (user_id, beasiswa_id)
);
```

#### Tabel `log_aktivitas` *(fitur opsional — audit log)*
```sql
CREATE TABLE log_aktivitas (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER,
    aksi        TEXT,                     -- CREATE / UPDATE / DELETE
    tabel       TEXT,                     -- Nama tabel yang diubah
    data_lama   TEXT,                     -- JSON string data sebelum diubah
    data_baru   TEXT,                     -- JSON string data sesudah diubah
    timestamp   TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (user_id) REFERENCES akun(id)
);
```

---

### 6.3 Diagram Relasi Antar Tabel (ERD Sederhana)

```
akun (1) ──────────── (N) riwayat_lamaran
  │                           │
  │                           └── beasiswa_id (referensi ke beasiswa)
  │
  ├── (1) ──── (N) favorit ──────── beasiswa (1)
  │
  ├── (1) ──── (N) catatan ─────── beasiswa (1)
  │
  └── (1) ──── (N) log_aktivitas

beasiswa (N) ──────── (1) penyelenggara
```

---

### 6.4 Alur Data Scraping

```
[indbeasiswa.com]
       │
       │  HTTP GET (requests)
       ▼
[HTML Response]
       │
       │  Parsing (BeautifulSoup4 + lxml)
       ▼
[Data mentah: nama, penyelenggara, deadline, jenjang, link]
       │
       ├──► [Simpan ke SQLite — tabel beasiswa & penyelenggara]
       │           + update timestamp_scraping
       │
       └──► [Generate JSON backup — beasiswa.json, penyelenggara.json]
                   (memenuhi requirement 3 file JSON)
```

---

## 7. Rekomendasi Tech Stack

### 7.1 Tabel Lengkap Tech Stack

| Kategori | Library/Tool | Versi | Alasan Pemilihan |
|---|---|---|---|
| Bahasa | Python | 3.10+ | Requirement mata kuliah, ekosistem library lengkap |
| GUI | PyQt6 | Latest | Powerful, native look, support layout manager & stylesheet |
| Visualisasi | Matplotlib | Latest | Integrasi mulus ke PyQt6 via `FigureCanvasQTAgg` |
| Web Scraping | requests | Latest | HTTP request ringan dan cepat |
| HTML Parsing | BeautifulSoup4 + lxml | Latest | Mudah digunakan, efisien untuk HTML statis |
| Database | sqlite3 | Built-in | Tidak perlu install terpisah, cocok untuk aplikasi lokal |
| Hash Password | bcrypt | Latest | Standar industri untuk hash password |
| Export | csv | Built-in | Tidak perlu install terpisah |
| Notifikasi OS | plyer | Latest | Cross-platform (Windows, Linux, macOS) — opsional |
| Kolaborasi | Git & GitHub | Latest | Version control, branch per anggota |

### 7.2 Kenapa Tidak Perlu Selenium?

> Website sumber scraping `indbeasiswa.com` berbasis **WordPress dengan HTML statis** — seluruh data beasiswa sudah ada di dalam HTML response saat pertama di-request. Tidak ada JavaScript rendering yang perlu ditunggu. Selenium hanya diperlukan untuk website yang kontennya dirender oleh JavaScript (React, Vue, Angular) setelah halaman dibuka.

**Cara memverifikasi:** Buka indbeasiswa.com → klik kanan → *View Page Source* → cari nama beasiswa. Jika data sudah ada di source, `requests + BeautifulSoup4` sudah cukup.

### 7.3 File `requirements.txt`

```
PyQt6
matplotlib
requests
beautifulsoup4
lxml
bcrypt
plyer
```

---

## 8. Strategi Pembeda dari Kompetitor

> Mengantisipasi adanya kelompok lain dengan tema scraping beasiswa yang serupa.

### Argumen Utama
Bagi BeasiswaKu, **web scraping hanyalah cara mendapatkan data — bukan fitur utama**. Yang membedakan adalah ekosistem fitur yang dibangun di atasnya:

| Dimensi | Kelompok Lain (Kemungkinan) | BeasiswaKu |
|---|---|---|
| Output scraping | Tampilkan daftar beasiswa | Tampilkan + filter + sort + highlight deadline |
| Manajemen data | Hanya lihat | CRUD + favorit + catatan pribadi |
| Personalisasi | Tidak ada | Sistem login per akun — data tracker terpisah per user |
| Visualisasi | Mungkin ada | 4+ grafik dinamis di 2 tab berbeda |
| Penyimpanan | JSON / tidak ada DB | SQLite dengan relasi antar tabel |
| Pengalaman user | Viewer beasiswa | Personal scholarship manager |

### Kalimat Pembeda untuk Presentasi
> *"Kalau kelompok lain fokus pada pengumpulan data beasiswa, kami fokus pada apa yang mahasiswa lakukan setelah menemukan beasiswa — yaitu melacak, mengelola, dan mengevaluasi lamarannya secara personal. Fitur Tracker Lamaran, sistem login multi-user, dan visualisasi progres itulah yang menjadi keunggulan utama kami."*

---

## 9. Risiko & Mitigasi

| # | Risiko | Dampak | Mitigasi |
|---|---|---|---|
| 1 | Struktur HTML `indbeasiswa.com` berubah | Scraper gagal ekstrak data | Tangani dengan `try-except` di setiap selector; buat fallback selector alternatif |
| 2 | Website target down / timeout | Auto-scraping gagal saat pertama buka | Tampilkan pesan error yang jelas; load data dari database lama jika ada |
| 3 | Integrasi antar modul tidak kompatibel | Bug saat semua file digabung | Tentukan interface/kontrak antar modul sejak awal; integrasi bertahap tiap minggu |
| 4 | Data beasiswa scraped tidak lengkap/kotor | Grafik tidak akurat | Tambahkan data cleaning di `scraper.py` sebelum simpan ke SQLite |
| 5 | PyQt6 versi tidak kompatibel antar anggota | Aplikasi tidak bisa jalan di laptop tertentu | Tentukan versi di `requirements.txt`; semua pakai virtual environment |
| 6 | Anggota tidak familiar dengan SQLite | CRUD tidak berjalan benar | Darva (PIC crud.py) buat fungsi helper CRUD yang bisa dipakai semua anggota |
| 7 | Requirement dosen: 3 file JSON tidak terpenuhi | Nilai berkurang | JSON tetap di-generate sebagai backup/ekspor — SQLite hanya penyimpanan utama |

---

## 10. Catatan Teknis Penting

### Autentikasi & Keamanan
- **Jangan** simpan password dalam bentuk plain text — selalu hash dengan `bcrypt`
- Session user aktif disimpan di variabel memori selama aplikasi berjalan, tidak perlu token/cookie
- Implementasi `user_id` di setiap tabel yang berhubungan dengan data personal agar data antar user tidak tercampur

### Integrasi Modul
- `crud.py` berperan sebagai **data access layer** — semua modul lain (gui, visualisasi) harus memanggil fungsi dari `crud.py` untuk akses database, tidak boleh query SQLite langsung dari file lain
- `scraper.py` hanya bertanggung jawab mengambil data dan menyimpan ke database — tidak boleh ada logika UI di dalamnya
- `visualisasi.py` hanya menerima data (list/dict) sebagai parameter fungsi — tidak boleh query database sendiri

### Threading untuk Scraping
- Proses scraping harus dijalankan di **background thread** (QThread) agar UI tidak freeze saat scraping berlangsung
- Tampilkan loading indicator / progress bar saat scraping berjalan

### Konvensi Kode
- Gunakan **snake_case** untuk nama variabel dan fungsi
- Setiap fungsi wajib punya docstring singkat
- Commit ke GitHub minimal **1x per sesi kerja** dengan pesan commit yang deskriptif

---

## 11. Timeline & Milestone

### Fase 1 — MVP (Target: UTS 13–18 April 2026)

| Minggu | Periode | Target | PIC Utama |
|---|---|---|---|
| 1 | 9–15 Mar 2026 | Setup GitHub, struktur folder, README awal, skema SQLite dummy | Semua |
| 2–3 | 16–28 Mar 2026 | *(Libur Idul Fitri)* scraping awal, UI dasar, skema database final | Kemal, Aulia |
| 4 | 30 Mar–5 Apr 2026 | `scraper.py` selesai + Tab Beasiswa UI dasar | Kemal, Kyla |
| 5 | 6–12 Apr 2026 | CRUD + autentikasi + validasi + integrasi awal | Darva, Aulia |
| **🎯 UTS** | **13–18 Apr 2026** | **MVP: Tab Beasiswa + CRUD + Login + filter + notifikasi deadline berjalan** | **Semua** |

### Fase 2 — Aplikasi Lengkap (Target: UAS 15–22 Juni 2026)

| Minggu | Periode | Target | PIC Utama |
|---|---|---|---|
| 6 | 20–26 Apr 2026 | Tab Tracker + pie chart + bar chart | Darva, Richard |
| 7 | 27 Apr–3 Mei 2026 | Tab Statistik + export CSV + integrasi penuh | Richard, Aulia |
| 8 | 4–10 Mei 2026 | Testing & bug fix seluruh fitur | Semua |
| 9–11 | 11 Mei–7 Jun 2026 | Polishing UI + fitur tambahan prioritas tinggi + README lengkap | Semua |
| **🎯 UAS** | **15–22 Jun 2026** | **Aplikasi selesai, lengkap, dan siap dipresentasikan** | **Semua** |

---

## 12. Pembagian Tugas Tim

| Anggota | NIM | File | Tanggung Jawab Detail |
|---|---|---|---|
| **Kemal Melvin Ibrahim** | 251524017 | `scraper.py` | Web scraping 5 kategori indbeasiswa.com → simpan ke SQLite + generate JSON backup + auto-scraping + QThread untuk background scraping |
| **Aulia Rahmi Taufik** | 251524003 | `main.py` | Entry point aplikasi + Main Window PyQt6 + screen login/register + tab bar + notifikasi deadline + dark/light mode toggle + counter jumlah data di tab |
| **Kyla Khansa** | 251524018 | `gui_beasiswa.py` | UI Tab Beasiswa: tabel, filter real-time, sort, highlight baris deadline, export CSV, tombol refresh, filter deadline otomatis, popup detail beasiswa, kolom "Sudah Daftar?", favorit/bookmark |
| **Darva Aryasatya P.H.** | 251524005 | `crud.py` | Data access layer: semua fungsi CRUD untuk tabel beasiswa, akun, lamaran, favorit, catatan + autentikasi (hash/verify bcrypt) + UI Tab Tracker + form tambah/edit lamaran + halaman profil pengguna |
| **Richard Fadhilah** | 251524028 | `visualisasi.py` | Semua grafik: pie chart & bar chart di Tab Tracker + bar chart per jenjang + bar chart top 5 penyelenggara + pie chart status ketersediaan di Tab Statistik + sistem warna dinamis |

---

## Checklist Minimum Requirement Dosen

- [x] Berkelompok 5–6 orang
- [x] Repository GitHub + branch per anggota
- [x] 1 file Python utama per anggota
- [x] Data dari web scraping
- [x] Format JSON (sebagai ekspor/backup)
- [x] 3 file JSON (beasiswa.json, penyelenggara.json, riwayat_lamaran.json)
- [x] Minimal 50 baris × 4 kolom data
- [x] CRUD lengkap
- [x] Minimal 1 grafik *(sudah 4+ grafik)*

---

> **Catatan Akhir:** Dokumen ini adalah living document — perbarui setiap ada perubahan keputusan teknis, penambahan fitur, atau perubahan pembagian tugas. Simpan di root folder repository GitHub agar semua anggota tim selalu memiliki akses ke versi terbaru.

---
*BeasiswaKu · Kelompok A4 · POLBAN · 2025/2026*
