---
name: aulia-development-context
description: >-
  Aulia's development context for BeasiswaKu. Use when: working on charts, visualization, analytics, dark mode, or UI themes. Focuses Copilot on data visualization approaches and AULIA's responsibilities as PIC for visualisasi.py and UI theming.

---

# Aulia's Development Context

You are **Aulia**, the **Analytics & Visualization Specialist** for BeasiswaKu.

## Your Responsibilities

- **PIC (Primary):** `visualisasi.py` — All charts (Matplotlib/Plotly), data visualization
- **Supporting:** `main.py` (UI theming) — Dark/Light mode, theme consistency, badges
- **Blueprint Reference:** Section 0 (Team assignments), Section 3.2 & 3.3 (Statistics features)

## FASE 3 & 4 Critical Path (Your Main Focus)

Visualization is what makes app **special**:

```
PHASE 3 (Tab Tracker Charts):
- [ ] Pie chart: Lamaran status (Pending/Diterima/Ditolak)
- [ ] Bar chart: Lamaran per bulan

PHASE 4 (Tab Statistik):
- [ ] Bar chart: Beasiswa per jenjang
- [ ] Bar chart: Top 5 penyelenggara terbanyak
- [ ] Pie chart: Status ketersediaan (Buka/Segera Tutup/Tutup)

BONUS FEATURES:
- [ ] Dark/Light mode toggle
- [ ] Color palette consistency
- [ ] Data badges (counter di tab)
```

## Dependency Status (You ARE BLOCKED)

**Tab Statistik CANNOT START until:**
1. ✅ FASE 1 Foundation → **DONE**
2. ⏳ FASE 2 Tab Beasiswa → Kyla **in-progress (ETA: 3 days)**
3. ⏳ FASE 3 Tab Tracker → Darva **in-progress (ETA: 2 days)**

**Status:** 
- ❌ Tab Statistik BLOCKED (need data from FASE 2 & 3)
- ✅ Prep work available NOW

## Your First Task Sequence (While Waiting)

1. **Prep Phase** (weeks 1-2, while Tab Beasiswa & Tracker being done):
   - Setup `visualisasi.py` file with proper imports
   - Install matplotlib/plotly and test
   - Design color palette (see copilot-instructions.md Section 8)
   - Create dummy data for testing chart structure
   - Prepare chart function templates

2. **Data Aggregation Phase** (week 2):
   - Work with Darva to create data aggregation queries
   - Queries: beasiswa per jenjang, top penyelenggara, status summary
   - Test queries with dummy data

3. **Implementation Phase** (week 3, after FASE 2 & 3 done):
   - Implement pie charts (Tracker status, Statistik status)
   - Implement bar charts (Tracker per-month, Statistik per-category)
   - Test with real data
   - Polish styling & colors

## Before You Get Stuck (Parallel Work)

**You CANNOT fully implement charts until FASE 2 & 3 done, BUT:**

✅ **You CAN do NOW:**
```
1. Setup visualisasi.py structure
   - Import matplotlib/plotly
   - Define function templates
   
2. Design color palette
   - Create COLOR_PALETTE dictionary
   - Test with dummy data
   
3. Create dummy data
   - Mock beasiswa dataset (10-20 rows)
   - Mock lamaran dataset (5-15 rows)
   - Use for testing chart rendering
   
4. Prep data aggregation queries (with Darva)
   - Query structure for beasiswa per jenjang
   - Query structure for top penyelenggara
   - Query structure for status counts
```

## Blockers & Dependencies

**You are blocked by:**
- Darva (Tab Tracker CRUD) → ETA 2 days
- Kyla (Tab Beasiswa data) → ETA 3 days

**Alternative:** Start PREP work! (see above)

**You will unblock:**
- No one (charts are independent)

## Communication with Darva (Critical!)

You need **data aggregation queries** from Darva:

```
Aulia → Darva:
"Darva, saya perlu data aggregation queries untuk charts:
1. Query: Hitung lamaran per bulan (group by month)
2. Query: Hitung beasiswa per jenjang
3. Query: Hitung top 5 penyelenggara terbanyak

Bisa Anda buat di crud.py sebagai helper functions?"
```

This way, when FASE 3 done, you can directly use functions untuk query data.

## Code Style Reminders

- **Matplotlib integration:** FigureCanvasTkAgg (see copilot-instructions.md Section 8)
- **Color consistency:** Use COLOR_PALETTE dictionary
- **Function naming:** `create_pie_chart_lamaran()`, `create_bar_chart_beasiswa_per_jenjang()`
- **Docstrings** in all functions
- **Error handling** with try/except

See: copilot-instructions.md Section 8

## Blueprint Reference

See `blueprint_beasiswaku.md`:
- **Section 3.2** — Tab Statistik features
- **Section 5 Layar 5 & 7** — Tab Tracker & Statistik chart layout
- **Section 4** — When charts are displayed (Tab Statistik, Tab Tracker)

## Daily Standup Report Format

```
Aulia: [Analytics & Visualization]
  - Yesterday: [what you prepared/practiced]
  - Today: [what you're working on (prep work)]
  - Blocker: [Darva/Kyla queries? Dependency?]
  - ETA for implementation: [when FASE 2 & 3 will be done]
```

**Example (week 1):**
```
Aulia: [Charts & Visualization]
  - Yesterday: ✅ Setup visualisasi.py + tested matplotlib
  - Today: 🟡 Designing color palette + creating dummy data
  - Blocker: ⏳ Waiting Darva/Kyla to finish FASE 2 & 3 (ETA: 3 days)
  - ETA implementation: 3 days from now (when data available)
```

**Example (week 2, when data available):**
```
Aulia: [Charts & Visualization]
  - Yesterday: ✅ Data aggregation queries ready, dummy charts working
  - Today: 🟡 Implementing pie chart status lamaran + bar chart per month
  - Blocker: None
  - ETA complete: Day after tomorrow
```

## First Command to Copilot (Now - Prep Work)

```
"Aulia: Buatkan visualisasi.py structure dengan:
1. Import matplotlib + FigureCanvasTkAgg
2. COLOR_PALETTE dictionary (warna untuk: pending, accepted, rejected, dst)
3. Function templates untuk pie chart & bar chart
4. Dummy data untuk test chart rendering

Sesuai blueprint Section 5 & instructions Section 8"
```

## Second Command (After FASE 2 & 3 Done)

```
"Aulia + Darva: Koordinasi aggregation queries untuk charts.
Aulia implementasikan:
1. Pie chart: Lamaran status distribution
2. Bar chart: Lamaran per bulan

Gunakan data dari database melalui Darva queries"
```

---

*Last updated: April 2026*  
*For questions: refer to copilot-instructions.md or ask in group chat*
