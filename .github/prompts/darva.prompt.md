---
name: darva-development-context
description: >-
  Darva's development context for BeasiswaKu. Use when: working on CRUD operations, database schema, authentication, session management, or data operations. Focuses Copilot on database-first approaches and DARVA's responsibilities as PIC for crud.py and session management in main.py.

---

# Darva's Development Context

You are **Darva**, the **Database & Authentication Specialist** for BeasiswaKu.

## Your Responsibilities

- **PIC (Primary):** `crud.py` — All database CRUD operations & authentication
- **Supporting:** `main.py` — Session management & login/register screens (with Kyla for UI)
- **Blueprint Reference:** Section 0 (Team assignments), Section 6 (Database schema)

## FASE 1 Prerequisites (Your Critical Path)

You are the **blocker releaser** for others! Your tasks unblock everyone else:

```
PHASE 1 CRITICAL:
- [ ] Database schema (all 5 tables)
- [ ] Authentication: hash_password(), verify_password(), register_user(), login_user()
- [ ] Session management in main.py
- [ ] Basic CRUD: get_beasiswa_list(), add_beasiswa(), edit_beasiswa(), delete_beasiswa()
- [ ] Lamaran CRUD: add_lamaran(), edit_lamaran(), delete_lamaran(), get_lamaran_list()
```

**Until this is done, Kyla (UI), Aulia (charts), and others are BLOCKED.**

## Your First Task Sequence

1. **FASE 1.1** (Must do FIRST): Create database schema in `init_db()` function
   - Tables: akun, beasiswa, penyelenggara, riwayat_lamaran, favorit
   - Run: `python -c "from crud import init_db; init_db()"`
   - Verify: `sqlite3 database/beasiswaku.db ".schema"`

2. **FASE 1.2**: Implement authentication functions
   - Use `bcrypt` (see copilot-instructions.md Section 6)
   - Test with: `python -c "from crud import hash_password, verify_password; ..."`

3. **FASE 1.3**: Implement basic CRUD for beasiswa
   - Must have parameters checked
   - All queries parameterized (no SQL injection)
   - Add to schema: timestamps, creation dates

4. **FASE 2.2**: Implement CRUD for lamaran (after FASE 1.3 done)
   - Dependency: Kyla will use this to build Tab Tracker UI

## Before Starting Any Task

Always ask Copilot:
```
"Darva: Saya mau implementasikan [task]. 
Cek FASE di Section 0 — apakah prerequisitenya sudah selesai? 
Atau ada blocker dari orang lain?"
```

## Code Style Reminders

- Use **parameterized queries** ALWAYS: `cursor.execute(query, (param1, param2))`
- **bcrypt** for passwords: `bcrypt.hashpw()`, `bcrypt.checkpw()`
- **Docstrings** in all functions
- **Error handling** with try/except + messagebox
- **Logging** for debug: `logging.info()`, `logging.error()`

See: copilot-instructions.md Section 5, 6, 11

## Blockers & Dependencies

**You can start:** FASE 1.1 (no dependencies)

**You ARE:**
- Unblocking Kyla (Tab Beasiswa UI waits for CRUD functions)
- Unblocking Aulia (Statistik waits for data aggregation queries)

## Communication Points

**Sync with:**
- **Kyla**: CRUD functions → UI integration (discuss parameter names, return types)
- **Aulia**: Aggregation queries for charts (discuss data structure)

**Daily Standup Report Format:**
```
Darva: [Database & CRUD]
  - Yesterday: [what you accomplished]
  - Today: [what you're working on]
  - Blocker: [if any]
  - ETA unblock: [when Kyla/Aulia can start depending tasks]
```

**Example:**
```
Darva: [CRUD Beasiswa]
  - Yesterday: ✅ DB schema + authentication done
  - Today: 🟡 Implementing CRUD functions (add/edit/delete)
  - Blocker: None
  - ETA unblock: Today 4 PM → Kyla can start Tab Beasiswa UI
```

## First Command to Copilot

After setup complete:
```
"Darva: Buatkan init_db() function untuk initialize database schema beasiswa.
Gunakan blueprint Section 6.2 dan instructions Section 5 untuk CRUD pattern.
Tabel yang diperlukan: akun, beasiswa, penyelenggara, riwayat_lamaran, favorit"
```

---

*Last updated: April 2026*  
*For questions: refer to copilot-instructions.md or ask in group chat*
