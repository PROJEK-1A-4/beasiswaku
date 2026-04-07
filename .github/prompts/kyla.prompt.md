---
name: kyla-development-context
description: >-
  Kyla's development context for BeasiswaKu. Use when: working on Tab Beasiswa, Tkinter UI, widget design, filtering/searching, or any GUI component. Focuses Copilot on UI-first approaches and KYLA's responsibilities as PIC for gui_beasiswa.py and main window layout.
applyTo: >-
  gui_beasiswa.py,main.py
pinned: true
---

# Kyla's Development Context

You are **Kyla**, the **UI/UX Specialist** for BeasiswaKu (Beasiswa Tab).

## Your Responsibilities

- **PIC (Primary):** `gui_beasiswa.py` — Beasiswa tab UI, filtering, searching, CRUD panel
- **Supporting:** `main.py` (with Darva) — Main window layout, app structure
- **Blueprint Reference:** Section 0 (Team assignments), Section 5 (UI requirements), Section 4 (User flow)

## FASE 2 Critical Path (Your Main Focus)

Tab Beasiswa is a **core feature** user see first:

```
PHASE 2 (Tab Beasiswa):
- [ ] Tabel display (Treeview)
- [ ] Filter jenjang (dropdown: Semua, D3, D4, S1, S2)
- [ ] Filter status (dropdown: Buka, Segera Tutup, Tutup)
- [ ] Search real-time (text entry with KeyRelease binding)
- [ ] Sort by column (click header)
- [ ] CRUD Panel: Tambah, Edit, Hapus buttons
- [ ] Detail popup (dobel klik baris)
- [ ] Highlight deadline: Merah (≤3 hari), Kuning (≤7 hari)
- [ ] Export CSV
- [ ] Timestamp scraping terakhir
```

## FASE 2 Dependency Status

**You are BLOCKED until:**
1. ✅ Main window layout done (Darva) → **DONE**
2. ⏳ Database schema → Darva **doing now**
3. ⏳ CRUD functions (get, add, edit, delete) → Darva **in progress**
4. ✅ Auto-scraper & database save → Kemal **DONE**

**When Darva finishes CRUD:** You can start Tab Beasiswa UI implementation

## Your First Task Sequence

1. **Prep Phase** (while CRUD is being done):
   - Create `gui_beasiswa.py` file structure
   - Define BeasiswaTab class
   - Setup Treeview widget with column definitions
   - Create filter/search input widgets

2. **Integration Phase** (after Darva CRUD OK):
   - Integrate get_beasiswa_list() for data display
   - Connect CRUD buttons to Darva's functions
   - Test add/edit/delete sync with database

3. **Polish Phase**:
   - Highlight deadline logic
   - Detail popup (dobel klik)
   - Export CSV

## Before Starting Tab Beasiswa UI

**Always check:**
```
"Kyla: Saya mau mulai Tab Beasiswa UI.
Cek Section 0 prerequisite untuk Tab Beasiswa — 
sudah selesai atau ada blocker?"
```

**Expected response pattern:**
- ✅ Main window → DONE
- ✅ DB schema → DONE
- ⏳ CRUD functions → in-progress (ETA: X waktu)
- ✅ Scraper → DONE

**Action:** If CRUD in-progress, start with PREP (widget structure)

## Code Style Reminders

- **Grid layout** ALWAYS (see copilot-instructions.md Section 4)
- **Widget naming:** `btn_refresh`, `entry_search`, `combo_filter`, `tbl_beasiswa`
- **Variable naming:** `filter_jenjang_var = tk.StringVar()`
- **Bind events:** `.bind('<KeyRelease>', ...)`, `.bind('<<ComboboxSelected>>', ...)`
- **Docstrings** in all functions
- **Error handling** with messagebox dialogs

See: copilot-instructions.md Section 3, 4

## Blueprint UI Reference

See `blueprint_beasiswaku.md`:
- **Section 5 Layar 3** — Tab Beasiswa layout details
- **Section 4.2** — User flow (filter → search → CRUD operations)
- **Section 3.1** — Feature checklist for Tab Beasiswa

## Blockers & Dependencies

**You unblock:**
- Yourself (start UI prep now, integration after CRUD)

**You are blocked by:**
- Darva (CRUD functions)

**You unblock others:**
- No one (Tab Beasiswa is independent)

## Communication Points

**Sync with:**
- **Darva**: CRUD integration → function signatures, error handling, parameter names
- Discuss: "Darva, tunggu berapa lama CRUD selesai? Saya mau mulai prep UI sekarang"

**Daily Standup Report Format:**
```
Kyla: [Tab Beasiswa UI]
  - Yesterday: [what you prepared/accomplished]
  - Today: [what you're working on]
  - Blocker: [Darva CRUD? Other?]
  - ETA complete: [when Tab Beasiswa fully done]
```

**Example:**
```
Kyla: [Tab Beasiswa UI]
  - Yesterday: ✅ Treeview structure + filter widgets setup
  - Today: 🟡 Waiting Darva CRUD final test, will integrate add/edit/delete functions
  - Blocker: ⏳ Darva CRUD (ETA: 2 hours)
  - ETA complete: Tomorrow 12 PM (after Darva integration test)
```

## First Command to Copilot

After Darva finishes CRUD (or in parallel):
```
"Kyla: Buatkan Tab Beasiswa di gui_beasiswa.py dengan:
- Treeview dengan kolom: No, Nama, Penyelenggara, Jenjang, Deadline, Status
- Filter dropdown untuk jenjang (Semua, D3, D4, S1, S2)
- Search entry dengan real-time filtering
- Buttons: Tambah, Edit, Hapus
- Highlight deadline: merah ≤3 hari, kuning ≤7 hari

Sesuai blueprint Section 5 Layar 3 dan instructions Section 4"
```

---

*Last updated: April 2026*  
*For questions: refer to copilot-instructions.md or ask in group chat*
