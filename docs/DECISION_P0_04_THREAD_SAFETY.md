# Decision P0-04: Thread-Safe Database Strategy

Tanggal: 2026-04-20  
Owner: Darva  
Status: P0-04.2 selesai diimplementasikan, lanjut P0-04.3

## 1. Tujuan
Menetapkan strategi thread safety untuk akses SQLite agar stabil saat aplikasi melakukan scraping async dan operasi UI/CRUD berjalan bersamaan.

## 2. Kondisi Saat Ini
- Koneksi dikelola oleh singleton `DatabaseManager` dengan satu koneksi global.
- Konfigurasi `DATABASE_CHECK_SAME_THREAD` saat ini bernilai `False`.
- Sinkronisasi web berjalan dengan thread scraper (QThread), lalu memicu proses persist ke database dari alur GUI.

Risiko utama dari kondisi ini:
- Potensi race condition pada koneksi bersama.
- Potensi lock contention dan perilaku nondeterministic saat write berdekatan.
- Debugging sulit karena state transaksi tercampur di koneksi yang sama.

## 3. Opsi yang Dievaluasi

### Opsi A: Tetap satu koneksi global + lock manual
Kelebihan:
- Perubahan paling kecil.

Kekurangan:
- Tetap menyisakan coupling tinggi pada shared connection.
- Lock manual mudah bocor dan sulit dipelihara seiring bertambah fitur.

### Opsi B: Dedicated DB worker (queue)
Kelebihan:
- Write path sangat terkontrol dan serial.
- Paling aman untuk skenario concurrency kompleks.

Kekurangan:
- Perubahan arsitektur besar (butuh wrapper command queue lintas CRUD/UI).
- Tidak cocok untuk target perbaikan cepat P0.

### Opsi C: Per-thread connection (thread-local) dengan API tetap
Kelebihan:
- Perubahan moderat namun signifikan secara safety.
- Cocok untuk arsitektur saat ini karena tidak memaksa refactor besar API CRUD.
- Setiap thread memakai koneksi sendiri, mengurangi konflik state transaksi.

Kekurangan:
- Tetap perlu konfigurasi SQLite yang tepat (WAL/busy timeout).
- Tetap perlu stress test untuk validasi lock scenario.

## 4. Keputusan Final
Dipilih Opsi C: Per-thread connection (thread-local) dengan API existing tetap.

Keputusan teknis inti:
1. `DatabaseManager` tetap singleton sebagai manager, tetapi bukan single-connection.
2. Setiap thread mendapatkan koneksi sendiri (thread-local map berbasis thread id).
3. `check_same_thread` diarahkan menjadi `True` untuk mencegah cross-thread misuse pada koneksi yang sama.
4. FK enforcement tetap di level koneksi (sudah dikerjakan pada P0-03).
5. Tambahkan PRAGMA koneksi yang mendukung concurrency SQLite:
- `journal_mode=WAL`
- `busy_timeout` (ms)

## 5. Dampak File (Implementasi P0-04.2)
Perubahan utama yang akan dikerjakan pada langkah berikutnya:
- `src/core/database.py`
  - Ubah penyimpanan koneksi dari single value menjadi per-thread.
  - Tambah utilitas close untuk koneksi thread aktif dan close-all.
  - Tambah PRAGMA WAL dan busy timeout saat create connection.
- `src/core/config.py`
  - Set default `DATABASE_CHECK_SAME_THREAD=True`.
  - Tambah konfigurasi timeout ms jika diperlukan (`DATABASE_BUSY_TIMEOUT_MS`).
- `tests/unit/` (file baru)
  - Tambah test thread safety (minimal 2 thread concurrent write/read).

Perubahan minor/opsional:
- `tests/unit/test_database.py`
  - Rapikan setup test agar tidak bergantung pada konfigurasi manual lintas test.

## 6. Kriteria Selesai P0-04
Checklist gate untuk menutup P0-04:
1. Multi-thread access tidak memunculkan `sqlite3.ProgrammingError` terkait thread affinity.
2. Operasi sync + UI CRUD tidak menghasilkan error random pada skenario uji dasar.
3. Stress test sederhana lulus konsisten.
4. Seluruh test database terkait tetap lulus.

## 7. Non-Goal (Bukan Cakupan Langkah Ini)
- Belum membangun full DB command queue architecture.
- Belum memindahkan semua write path menjadi async job queue.
- Belum refactor besar boundary GUI -> service -> repository.

## 8. Next Action
Lanjut ke P0-04.2: implementasi per-thread connection pada `DatabaseManager` secara minimal-invasif.
