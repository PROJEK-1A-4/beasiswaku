# BeasiswaKu Improvement Masterplan

Dokumen ini merangkum area yang wajib di-improve berdasarkan audit kode aktual, lengkap dengan prioritas, dampak, dan langkah implementasi yang bisa langsung dieksekusi.

## 1. Ringkasan Cepat

Kondisi saat ini:
- Fitur inti jalan, dan unit test yang ada lulus.
- Namun ada technical debt struktural yang cukup besar pada boundary antarlayer, konsistensi error handling, integritas data lintas thread, dan akurasi dokumentasi.

Dampak jika tidak diperbaiki:
- Biaya maintenance akan naik cepat.
- Risiko bug regressions tinggi saat fitur baru ditambahkan.
- Onboarding anggota tim baru jadi lambat karena docs tidak sinkron.

Target utama:
1. Stabilkan reliability dan data integrity.
2. Rapikan struktur arsitektur (GUI -> Service -> Repository/CRUD).
3. Naikkan kualitas testing dan dokumentasi agar scalable.

## 2. Prioritas Eksekusi

- P0 (Wajib segera, 1-3 hari): bug fungsional, integritas data, error masking.
- P1 (Minggu ini): refactor boundary layer, performa query/listing, UX handler yang belum fungsional.
- P2 (1-2 sprint): standardisasi error contract, test architecture, observability.
- P3 (Backlog): clean-up style system, konsolidasi modul historis, hardening lanjutan.

## 3. Daftar Improvement Detail

## P0 - Critical Fixes

### P0-01: Perbaiki filter deadline yang saat ini misleading
- Area: GUI Beasiswa.
- Kondisi saat ini:
  - Fungsi "deadline dekat" hanya memfilter `status != Tutup`, bukan menghitung deadline dalam 7 hari.
  - Bukti: `src/gui/tab_beasiswa.py` fungsi `filter_by_deadline`.
- Dampak:
  - User mengira melihat beasiswa paling urgent, padahal masih campur semua yang "Buka".
- Implementasi:
  1. Parse field `deadline` ke date object.
  2. Filter hanya item dengan `0 <= days_left <= 7`.
  3. Tangani format tanggal invalid dengan fallback aman.
  4. Tambahkan label jumlah hasil (misal: "3 deadline dekat").
- Acceptance criteria:
  - Tombol "Deadline Dekat" hanya menampilkan item deadline <= 7 hari.

### P0-02: Hilangkan bare except yang menutupi error nyata
- Area: GUI Notes/Favorit, Service Sync.
- Kondisi saat ini:
  - Ada `except:` tanpa tipe exception.
  - Bukti:
    - `src/gui/tab_notes.py` (helper notes).
    - `src/gui/tab_favorit.py` (`is_beasiswa_favorited`).
    - `src/services/dashboard_service.py` (inner dan outer sync loop).
- Dampak:
  - Error nyata tersembunyi, sulit debug, data bisa silent fail.
- Implementasi:
  1. Ganti ke exception spesifik (mis. `sqlite3.Error`, `ValueError`).
  2. Logging wajib menyertakan context (`user_id`, `beasiswa_id`, operation).
  3. Untuk service sync, kumpulkan error detail per item (judul + alasan).
- Acceptance criteria:
  - Tidak ada lagi `except:` kosong di code path produksi.

### P0-03: Aktifkan foreign key enforcement di level connection, bukan per fungsi
- Area: Core database.
- Kondisi saat ini:
  - FK enforcement sering diaktifkan manual per operasi (`PRAGMA foreign_keys = ON`).
  - Connection global belum menjamin FK selalu aktif.
  - Bukti: `src/core/database.py` dan beberapa fungsi di `src/database/crud.py`.
- Dampak:
  - Potensi inkonsistensi jika ada operasi yang lupa set PRAGMA.
- Implementasi:
  1. Di `_create_connection()`, jalankan `PRAGMA foreign_keys = ON` sekali saat koneksi dibuat.
  2. Hapus PRAGMA manual yang redundant di fungsi CRUD.
  3. Tambah test yang memastikan FK selalu aktif pada koneksi baru.
- Acceptance criteria:
  - Semua insert/update FK invalid selalu gagal konsisten tanpa setup tambahan.

### P0-04: Validasi safety singleton connection lintas thread
- Area: Core database + scraper thread.
- Kondisi saat ini:
  - `DATABASE_CHECK_SAME_THREAD=False` dengan singleton connection.
  - Ada operasi scraping async yang juga bisa menyentuh DB.
  - Bukti: `src/core/config.py`, `src/core/database.py`, flow sync di GUI.
- Dampak:
  - Risiko race condition / lock contention / perilaku nondeterministic.
- Implementasi:
  1. Pilih strategi: single-thread DB worker ATAU per-thread connection.
  2. Jika per-thread connection: simpan connection per thread-local.
  3. Jika single worker: semua write DB via queue.
  4. Tambah stress test sederhana multi-write.
- Acceptance criteria:
  - Tidak ada deadlock atau error random saat sync + interaksi UI bersamaan.

## P1 - Struktur dan Alur Kode

### P1-01: Rapikan arsitektur layer (GUI jangan langsung ke CRUD)
- Area: GUI tabs.
- Kondisi saat ini:
  - Beberapa tab import fungsi CRUD langsung.
  - Bukti:
    - `src/gui/tab_beasiswa.py`
    - `src/gui/tab_tracker.py`
    - `src/gui/tab_profil.py`
- Dampak:
  - Coupling tinggi, sulit mock/test UI, perubahan schema mudah merembet ke UI.
- Implementasi:
  1. Definisikan service interface per domain: `BeasiswaService`, `TrackerService`, `ProfileService`.
  2. Semua tab hanya panggil service, bukan query/CRUD langsung.
  3. Pindahkan data-shaping ke service layer.
- Acceptance criteria:
  - Tidak ada import CRUD langsung dari modul GUI produksi.

### P1-02: Benahi koordinasi antar-tab yang masih rapuh
- Area: cross-tab refresh.
- Kondisi saat ini:
  - Refresh tab dilakukan via `self.window()` + `getattr(...)`.
  - Bukti: `src/gui/tab_beasiswa.py`, `src/gui/tab_tracker.py`.
- Dampak:
  - Mudah pecah saat struktur window berubah, sulit diuji.
- Implementasi:
  1. Gunakan event bus berbasis signal Qt terpusat (mis. `data_changed(topic)`), atau mediator.
  2. Tab subscribe topic yang relevan (`lamaran.updated`, `favorit.updated`).
  3. Hindari introspeksi atribut window secara dinamis.
- Acceptance criteria:
  - Cross-tab update tetap jalan tanpa akses atribut tab lain secara langsung.

### P1-03: Aktivasi handler pada tombol profil yang saat ini belum fungsional
- Area: Profil tab.
- Kondisi saat ini:
  - Banyak tombol belum dihubungkan ke handler (`clicked.connect` tidak ada di file profil).
  - Field juga masih mostly read-only dengan data campuran hardcoded.
  - Bukti: `src/gui/tab_profil.py`.
- Dampak:
  - UX terlihat siap dipakai tapi aksi tidak benar-benar terjadi.
- Implementasi:
  1. Tambah handler untuk edit profil, simpan perubahan, ubah password.
  2. Lepas nilai hardcoded (NIM/instansi/semester/statistik dummy) atau tandai sebagai placeholder eksplisit.
  3. Persist preferensi user (jika toggle memang ingin aktif).
- Acceptance criteria:
  - Semua tombol profil punya aksi nyata dan teruji.

### P1-04: Putuskan status modul Favorit/Notes (integrasi atau deprecate)
- Area: struktur fitur.
- Kondisi saat ini:
  - `tab_favorit.py` dan `tab_notes.py` ada, tapi tidak jadi tab utama di `main.py`.
- Dampak:
  - Dead code risk, kebingungan tim, duplicative maintenance.
- Implementasi:
  1. Pilih salah satu:
     - Integrasikan sebagai tab resmi; atau
     - Jadikan modul internal reusable; atau
     - Deprecate dan hapus bertahap.
  2. Sinkronkan navigasi sidebar dan beranda sesuai keputusan.
- Acceptance criteria:
  - Tidak ada modul fitur "setengah hidup".

### P1-05: Perbaiki deadline color logic yang hardcoded tanggal absolut
- Area: Favorit list UI.
- Kondisi saat ini:
  - Warna deadline dibandingkan ke tanggal literal seperti `2026-07-31`.
  - Bukti: `src/gui/tab_favorit.py`.
- Dampak:
  - Setelah tanggal lewat, seluruh indikator jadi tidak relevan.
- Implementasi:
  1. Bandingkan terhadap `today` dan selisih hari.
  2. Definisikan threshold dari config (mis. warning <= 14 hari, critical <= 7 hari).
- Acceptance criteria:
  - Warna deadline adaptif terhadap tanggal saat ini.

### P1-06: Kurangi N+1 query pada beasiswa list per user
- Area: CRUD.
- Kondisi saat ini:
  - `get_beasiswa_list_for_user` memanggil `check_user_applied` per row.
  - Bukti: `src/database/crud.py`.
- Dampak:
  - Performa turun drastis saat data besar.
- Implementasi:
  1. Gunakan single query dengan `LEFT JOIN riwayat_lamaran` dan computed field `sudah_daftar`.
  2. Hapus loop query per item.
- Acceptance criteria:
  - Satu request list user hanya memakai satu query utama.

### P1-07: Tambah pagination/lazy loading tabel beasiswa
- Area: Beasiswa listing.
- Kondisi saat ini:
  - Query render mengambil semua row sekaligus.
- Dampak:
  - UI melambat saat data bertambah besar.
- Implementasi:
  1. Tambah parameter `limit`/`offset` di service.
  2. Tambah kontrol paging di UI.
  3. Pertimbangkan sort/filter tetap di SQL.
- Acceptance criteria:
  - Waktu render stabil pada dataset besar.

## P2 - Standardisasi dan Kualitas Engineering

### P2-01: Samakan error contract seluruh backend
- Area: CRUD + services.
- Kondisi saat ini:
  - Return shape campuran: `(bool, msg)`, `(bool, msg, data)`, list+count, dll.
- Dampak:
  - Caller rumit, handling error tidak seragam.
- Implementasi:
  1. Definisikan `Result` object standar (success, code, message, payload).
  2. Terapkan bertahap per domain (auth, beasiswa, lamaran).
  3. Tambah mapper di UI agar transisi mulus.
- Acceptance criteria:
  - Kontrak return konsisten lintas modul.

### P2-02: Standardisasi status enum lintas layer
- Area: DB, service, UI.
- Kondisi saat ini:
  - Ada mapping dari status backend Inggris ke label Indonesia di UI.
- Dampak:
  - Risiko mismatch status saat fitur berkembang.
- Implementasi:
  1. Definisikan enum tunggal untuk storage + display mapping.
  2. Simpan canonical value di DB, translasi hanya di UI layer.
- Acceptance criteria:
  - Tidak ada literal status tersebar bebas di banyak file.

### P2-03: Rapikan konfigurasi logging
- Area: seluruh modul.
- Kondisi saat ini:
  - `logging.basicConfig(...)` dipanggil di banyak file.
- Dampak:
  - Handler ganda, format log tidak konsisten.
- Implementasi:
  1. Centralize setup logging di satu bootstrap module.
  2. Modul lain hanya `logger = logging.getLogger(__name__)`.
- Acceptance criteria:
  - Konfigurasi logger hanya dari satu entry point.

### P2-04: Perkuat test architecture (isolasi DB + assertion yang kuat)
- Area: tests.
- Kondisi saat ini:
  - Ada test script-style berbasis print/return bool.
  - Fixture DB belum fully isolated dari DB aplikasi utama.
- Dampak:
  - False confidence, flaky test, sulit dijalankan paralel.
- Implementasi:
  1. Migrasi script-style test menjadi `pytest` assertion murni.
  2. Gunakan test DB dedicated (mis. temp file per test session atau in-memory dengan setup schema).
  3. Tambah test untuk kasus race/sync failure/error propagation.
- Acceptance criteria:
  - Test tidak menyentuh DB produksi, assertion eksplisit, dan reproducible.

### P2-05: Tambah test untuk alur UI kritis
- Area: GUI integration.
- Kondisi saat ini:
  - Banyak test fokus CRUD, belum banyak validasi alur UI event.
- Dampak:
  - Handler UI rusak tidak cepat terdeteksi.
- Implementasi:
  1. Tambah test flow: apply lamaran, toggle favorit, sync web, update profil/password.
  2. Pastikan state antar-tab update sesuai event.
- Acceptance criteria:
  - Alur user utama punya test otomatis minimal smoke level.

## P3 - Dokumentasi dan Maintainability

### P3-01: Sinkronkan dokumen arsitektur dengan kode aktual
- Area: docs.
- Kondisi saat ini:
  - Beberapa dokumen masih menyebut file/fungsi yang sudah tidak ada atau rename.
  - Contoh: `main_window.py`, `login_window.py`, dan nama API CRUD lama di docs.
- Dampak:
  - Onboarding salah arah, developer buang waktu mencari file/function yang tidak ada.
- Implementasi:
  1. Audit docs terhadap source of truth (`main.py`, `src/*`).
  2. Perbarui semua contoh import/function ke API aktual.
  3. Tambahkan tanggal update dan owner dokumen.
- Acceptance criteria:
  - Tidak ada referensi path/function yang invalid pada docs utama.

### P3-02: Tetapkan kebijakan deprecate/compat wrapper
- Area: struktur modul.
- Kondisi saat ini:
  - Ada wrapper kompatibilitas (`src/gui/gui_beasiswa.py`) yang valid tapi perlu policy jelas.
- Dampak:
  - Potensi duplicate entry point jangka panjang.
- Implementasi:
  1. Dokumentasikan mana wrapper sementara, mana canonical path.
  2. Tetapkan timeline deprecate jika memang tidak dibutuhkan.
- Acceptance criteria:
  - Struktur import canonical jelas untuk semua developer.

## 4. Roadmap Implementasi (Disarankan)

## Sprint 1 (Stabilization)
- P0-01 sampai P0-04.
- P1-03.
- Output:
  - bug kritis selesai,
  - integritas data lebih aman,
  - profil action mulai nyata.

## Sprint 2 (Architecture Cleanup)
- P1-01, P1-02, P1-04, P1-05, P1-06, P1-07.
- Output:
  - boundary layer rapi,
  - cross-tab sinkron berbasis event,
  - performa listing meningkat.

## Sprint 3 (Engineering Quality)
- P2-01 sampai P2-05.
- P3-01.
- Output:
  - test lebih solid,
  - error contract seragam,
  - docs sinkron dengan code.

## 5. Pembagian Penugasan 5 Orang

Pembagian ini mengikuti domain ownership tim agar eksekusi cepat dan minim context switching.

### Person 1 - Darva (Core, Database, Backend Contract)
- Owner task:
  - P0-03 (FK enforcement di level connection).
  - P0-04 (strategi thread-safe DB: keputusan arsitektur + implementasi awal).
  - P1-06 (hilangkan N+1 query di beasiswa per user).
  - P2-01 (standarisasi result/error contract backend).
  - P2-04 (isolasi test DB dan migrasi test script-style utama).
- Status audit aktual (2026-04-22): PARTIAL.
  - P0-03 dan P0-04 belum konsisten di kode sekarang: `src/core/database.py` masih memakai pola singleton connection lama dan `src/core/config.py` masih belum menunjukkan strategi koneksi per-thread yang final.
  - P1-06 belum terverifikasi di tree sekarang: `src/database/crud.py` masih memperlihatkan pola lama yang mengarah ke N+1.
  - P2-01 dan P2-04 belum terverifikasi di tree sekarang: kontrak backend dan fixture test masih belum sinkron dengan versi yang direncanakan.
- Reviewer pendamping: Kemal.
- Deliverable:
  - PR backend stability.
  - PR query/performance.
  - PR test architecture database.

### Person 2 - Kemal (Scraper, Sync Robustness, Logging Reliability)
- Owner task:
  - P0-02 untuk area sync/scraper (hapus bare except, detail error per item scrape).
  - Hardening alur sinkronisasi scraper -> DB (error summary yang actionable).
  - P2-03 untuk konsolidasi logging pada scraper + sinkronisasi.
  - Dukungan stress test untuk skenario sync paralel (bagian dari P0-04/P2-04).
- Status audit aktual (2026-04-22): PARTIAL.
  - `src/scraper/scraper.py` sudah punya logging dan error summary yang lebih kaya, tetapi masih ada broad exception handling di beberapa jalur.
  - `src/services/dashboard_service.py` masih menyerap error dengan `except Exception` tanpa detail context pada loop sinkronisasi.
  - `src/gui/tab_notes.py` dan `src/gui/tab_favorit.py` masih menyimpan bare except, jadi target P0-02 belum selesai penuh.
- Reviewer pendamping: Darva.
- Deliverable:
  - PR scraper reliability.
  - PR observability/logging sync.

### Person 3 - Aulia (App Orchestration, Profile, Event Wiring)
- Owner task:
  - P1-02 (event bus/signal mediator untuk refresh antar-tab).
  - P1-03 (aktifkan handler tombol profil + alur simpan profile/password).
  - Integrasi perubahan arsitektur ke `main.py` dan flow window/tab.
  - P2-05 (smoke test UI flow: login/logout/profile update).
- Status audit aktual (2026-04-22): BELUM DIKERJAKAN.
  - Belum ada bukti pada tree sekarang bahwa event mediator antar-tab sudah dipasang secara terpusat.
  - Handler profil dan alur simpan profile/password belum terverifikasi di kode yang sekarang.
  - Smoke test UI flow juga belum terlihat sebagai implementasi yang stabil di test suite saat ini.
- Reviewer pendamping: Kyla.
- Deliverable:
  - PR app orchestration refactor.
  - PR profile functionalization.

### Person 4 - Kyla (GUI Beasiswa/Favorit UX & Scalability)
- Owner task:
  - P0-01 (deadline dekat benar-benar berbasis selisih hari).
  - P1-05 (deadline coloring adaptif, bukan tanggal hardcoded).
  - P1-07 (pagination/lazy loading tabel beasiswa).
  - P1-04 (putusan final integrasi/deprecate modul Favorit/Notes dari sisi UI).
- Status audit aktual (2026-04-22): BELUM DIKERJAKAN.
  - Audit cepat belum menemukan bukti bahwa filter deadline benar-benar berbasis selisih hari.
  - Deadline coloring adaptif dan pagination/lazy loading belum terverifikasi di UI current tree.
  - Keputusan final integrasi/deprecate Favorit/Notes belum dituangkan sebagai perubahan struktur yang final.
- Reviewer pendamping: Aulia.
- Deliverable:
  - PR UX correctness beasiswa/favorit.
  - PR performance UI listing.

### Person 5 - Richard (Statistik, Konsistensi Status, Dokumentasi Teknis)
- Owner task:
  - P2-02 (standardisasi enum/status mapping lintas service-UI chart).
  - P2-05 (test alur statistik/tracker setelah standardisasi status).
  - P3-01 (sinkronisasi dokumen arsitektur/API terhadap kode aktual).
  - P3-02 (policy compat wrapper + canonical import path).
- Status audit aktual (2026-04-22): BELUM DIKERJAKAN.
  - Belum ada bukti audit bahwa enum/status mapping sudah diseragamkan lintas layer.
  - Dokumentasi arsitektur dan API masih perlu diselaraskan ke source of truth yang sekarang.
  - Kebijakan compat wrapper vs canonical import path belum dinyatakan sebagai keputusan final di dokumen aktif.
- Reviewer pendamping: Darva.
- Deliverable:
  - PR status consistency + chart validation.
  - PR docs synchronization.

### Mode Eksekusi Non-Paralel (Fokus Per Orang)
Eksekusi dilakukan berantai (serial), bukan paralel. Pada satu waktu hanya ada satu owner yang aktif mengerjakan task implementasi utama, anggota lain fokus review, test regresi, dan persiapan fase berikutnya.

### Urutan Fase Kerja (Serial 5 Orang)
- Fase 1 - Darva:
  - P0-03 (FK enforcement di level connection).
  - P0-04 (strategi thread-safe DB, minimal keputusan arsitektur + implementasi awal).
  - Gate lanjut fase: seluruh test DB lulus dan validasi FK konsisten.
  - Status audit aktual (2026-04-22): PARTIAL.
    - Gate fase belum bisa dianggap tertutup karena tree sekarang masih menunjukkan implementasi database lama dan test suite lama.
- Fase 2 - Kemal:
  - P0-02 untuk area sync/scraper (hapus bare except, error detail per item).
  - P2-03 untuk logging reliability di alur sync.
  - Gate lanjut fase: sync gagal menampilkan error yang jelas dan tidak ada bare except pada path sync.
- Fase 3 - Kyla:
  - P0-01 (deadline dekat berbasis selisih hari).
  - P1-05 (deadline color adaptif).
  - P1-07 (pagination/lazy loading listing).
  - Gate lanjut fase: filter deadline benar dan performa listing membaik pada data besar.
- Fase 4 - Aulia:
  - P1-02 (event mediator/signal antar-tab).
  - P1-03 (handler profil: edit/simpan/password).
  - P2-05 (smoke test alur UI utama).
  - Gate lanjut fase: update antar-tab stabil dan aksi profil benar-benar fungsional.
- Fase 5 - Richard:
  - P2-02 (standardisasi enum/status lintas layer).
  - P3-01 (sinkronisasi dokumentasi arsitektur/API).
  - P3-02 (policy compat wrapper + canonical import path).
  - Gate selesai: docs sinkron dengan implementasi final dan status mapping konsisten.

### Rule Eksekusi Tim (Revisi Non-Paralel)
1. Hanya satu PR implementasi utama yang aktif pada satu waktu.
2. Fase berikutnya dimulai setelah gate fase sebelumnya terpenuhi.
3. Anggota non-owner di fase berjalan wajib mengerjakan review, regression test, dan verifikasi acceptance criteria.
4. Jika blocker fase > 1 hari kerja, owner boleh dipindahkan sementara atas keputusan tim.
5. Semua PR wajib mencantumkan ID task (contoh: P1-03) dan label fase (Fase-1 s.d. Fase-5).

## 6. KPI Keberhasilan

KPI teknis:
- 0 bare except di production path.
- 0 import CRUD langsung dari GUI (kecuali transitional adaptor yang terdokumentasi).
- Waktu render tab Beasiswa tetap responsif pada data >= 3.000 row.
- Semua test berjalan tanpa menyentuh database produksi.

KPI kualitas:
- Docs utama bebas referensi file/fungsi obsolete.
- Onboarding dev baru dapat menjalankan app + memahami struktur dalam <= 60 menit.

## 7. Catatan Eksekusi

Agar perubahan aman:
1. Mulai dari bug fungsional dan integritas data (P0).
2. Lakukan refactor arsitektur per modul kecil, jangan big-bang.
3. Setiap refactor wajib dibarengi test untuk mencegah regressions.
4. Update docs pada PR yang sama dengan perubahan kode.
