---
name: kemal-development-context
description: >-
  Kemal's development context for BeasiswaKu. Use when: working on web scraping, data fetching, search functionality, or data validation. Focuses Copilot on data-first approaches and KEMAL's responsibilities as PIC for scraper.py and search features.
applyTo: >-
  scraper.py,gui_beasiswa.py
pinned: true
---

# Kemal's Development Context

You are **Kemal**, the **Data & Search Specialist** for BeasiswaKu.

## Your Responsibilities

- **PIC (Primary):** `scraper.py` — Web scraping, auto-scraping, data validation, JSON backups
- **Supporting:** `gui_beasiswa.py` — Full-text search features, data filtering
- **Blueprint Reference:** Section 0 (Team assignments), Section 6 (Scraping), Section 3.3 (Features)

## FASE 2 Critical Path (Your Fastest Track)

Web scraping is a **foundation feature** that unblocks everyone:

```
PHASE 2 (Scraping & Data):
- [ ] Web scraper: scrape_beasiswa_data() function
- [ ] Data validation: validate_beasiswa_data()
- [ ] Database integration: save scraped data to beasiswa table
- [ ] JSON backup: backup_to_json()
- [ ] Auto-scraping on startup (threads)
- [ ] Refresh mechanism (manual trigger from UI)
- [ ] Test scraper with sample data
```

## Dependency Status (MINIMAL - You Can Start Now!)

**Tab Beasiswa scraper prerequisites:**
1. ✅ Database schema (beasiswa, penyelenggara) → Darva **DONE**
2. ✅ Database insert functions → Darva **can do in parallel**
3. ✅ No dependency on Kyla (UI can come later)

**You are NOT BLOCKED** — You can start NOW!

## Your First Task Sequence

1. **FASE 2.1** (START IMMEDIATELY):
   - Analyze target website(s) to scrape
   - Write `scrape_beasiswa_data()` function
   - Include error handling (timeout, network issues)
   - Test with sample scrape

2. **FASE 2.2** (After scraper works):
   - Implement `validate_beasiswa_data()` function
   - Check required fields (nama, deadline, jenjang, etc)
   - Clean & normalize data

3. **FASE 2.3** (Integration with Darva):
   - Implement database save in `scraper.py`
   - Call Darva's `add_beasiswa()` for each record
   - Or bulk insert

4. **FASE 2.4** (Backup & auto-scrape):
   - Implement `backup_to_json()` function
   - Setup auto-scrape thread in `main.py`
   - Test on app startup

5. **FASE 3.x** (Advanced - Full-text search):
   - Implement full-text search in `gui_beasiswa.py`
   - Enhanced filtering by deskripsi beasiswa

## Before Starting Scraper

**Check:**
```
"Kemal: Saya mau mulai scraper. 
Apa prerequisite? Darva sudah siap database schema?"
```

**Expected response:**
- ✅ Database schema → Darva **DONE** (can proceed NOW)
- ✅ No blockers

## Code Style Reminders

- **imports:** `requests`, `BeautifulSoup`, `json`
- **User-Agent:** Always set (avoid blocking)
- **timeout:** Specify (avoid forever hanging): `timeout=10`
- **error handling:** try/except RequestException, (see copilot-instructions.md Section 11)
- **logging:** `logging.info()`, `logging.error()`
- **Docstrings** in all functions
- **Data validation** BEFORE inserting to database

See: copilot-instructions.md Section 9

## Blueprint Scraping Reference

See `blueprint_beasiswaku.md`:
- **Section 6.3** — Scraping architecture
- **Section 4.1** — Auto-scraping on first open (flowchart)
- **Section 3.1** — Scraping as part of MVP

## Blockers & Dependencies

**You are NOT blocked** — Start NOW!

**You unblock:**
- Kyla (can build UI while you scrape)
- Everyone (data is critical)

## Communication with Darva

You need database integration:

```
Kemal → Darva:
"Darva, bisa siapkan function untuk insert beasiswa ke database?
Signature: insert_beasiswa(nama, penyelenggara, jenjang, deadline, deskripsi, link)

Saya scraper sudah siap menghasilkan data berbentuk: 
[{nama, penyelenggara, jenjang, deadline, deskripsi, link}, ...]"
```

## Daily Standup Report Format

```
Kemal: [Web Scraper & Data]
  - Yesterday: [what you accomplished]
  - Today: [what you're working on]
  - Blocker: [if any]
  - ETA complete: [when scraper stable]
```

**Example (week 1):**
```
Kemal: [Web Scraper]
  - Yesterday: ✅ Analyzed target website, wrote scraper function
  - Today: 🟡 Testing scraper with live data + data validation
  - Blocker: None
  - ETA complete: Tomorrow (scraper stable + tested)
```

## First Command to Copilot

```
"Kemal: Buatkan scraper.py dengan fungsi scrape_beasiswa_data() untuk 
mengambil beasiswa dari [source URL/website].

Requirements:
- Return list of dictionaries: [nama, penyelenggara, jenjang, deadline, deskripsi, link]
- Handle timeout & network errors gracefully
- Set User-Agent header
- Validate data sebelum return

Gunakan requests + beautifulsoup4, sesuai instructions Section 9"
```

## Second Command (After Scraper Works)

```
"Kemal: Implementasikan auto-scraping di main.py.
Saat app pertama kali buka:
1. Cek apakah database kosong
2. Jika kosong, jalankan scraper di background thread
3. Simpan data ke database via Darva CRUD functions
4. Show progress notification

Sesuai blueprint Section 4.1 & instructions Section 9"
```

---

*Last updated: April 2026*  
*For questions: refer to copilot-instructions.md or ask in group chat*
