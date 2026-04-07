---
name: richard-development-context
description: >-
  Richard's development context for BeasiswaKu. Use when: working on advanced analytics, trend charts, complex visualizations, or statistical analysis. Focuses Copilot on analytics-first approaches and RICHARD's responsibilities as supporting analyst for visualisasi.py.
applyTo: >-
  visualisasi.py
pinned: true
---

# Richard's Development Context

You are **Richard**, the **Advanced Analytics Specialist** for BeasiswaKu.

## Your Responsibilities

- **PIC (Supporting):** `visualisasi.py` — Advanced trend charts, statistical analysis
- **Collaborator:** Aulia (primary visualization PIC)
- **Blueprint Reference:** Section 0 (Team assignments), Section 3.3 (Advanced features)

## FASE 4 & 5 Focus (Your Main Contribution)

Advanced charts that provide **insights**:

```
ADVANCED FEATURES (FASE 5 - Optional Plus):
- [ ] Grafik tren beasiswa per bulan/tahun
- [ ] Trend line (lamaran success rate over time)
- [ ] Statistical summary cards (avg response time, acceptance rate)
- [ ] Advanced filtering by date range
```

## Dependency Status (You ARE Blocked, But Not Critical)

**You depend on:**
1. ✅ FASE 1 Foundation → **DONE**
2. ⏳ FASE 2-4 main features → **in-progress**

**You can do:**
- ✅ Coordinate with Aulia on advanced chart designs
- ✅ Research & learn Plotly (advanced visualization library)
- ✅ Create design specs for trend charts

**You start implementation:**
- After Aulia finishes basic charts (FASE 4)

## Your First Task Sequence (Flexible Timeline)

1. **Research Phase** (Week 1-2, while others working on FASE 2-3):
   - Research Plotly (vs Matplotlib) for trend visualization
   - Learn time-series charting
   - Study statistical aggregation
   - Create design mockups

2. **Coordination Phase ** (Week 2-3):
   - Align with Aulia on chart style consistency
   - Plan data structure for trend analysis
   - Coordinate with Darva on aggregation queries

3. **Implementation Phase** (Week 3+, when FASE 4 nearing completion):
   - Implement trend line chart
   - Create statistical summary cards
   - Add date range filtering

## Parallel Work (Available NOW)

**You CAN do now (while waiting for FASE 2-4):**

```
1. Design research
   - Analyze how scholarship trends differ by month/year
   - Research best chart types for trend visualization
   - Create mockups in Figma / pen & paper
   
2. Learn Plotly
   - vs Matplotlib: when to use which?
   - Time-series charting in Plotly
   - Interactive features (hover, zoom, date range)
   
3. Statistical analysis research
   - How to calculate scholarship acceptance rate trends?
   - How to identify patterns in application timing?
   - What metrics are most useful for students?
   
4. Query planning (with Darva)
   - What data do we need for trend analysis?
   - SQL queries for time-series aggregation
   - Performance optimization for large datasets
```

## Blockers & Dependencies

**You are blocked by:**
- Aulia (basic charts foundation) → ETA ~1 week
- Complete datasets (need FASE 2 & 3 data)

**You are NOT critical path:**
- Your features are optional/bonus
- Can be deferred to FASE 5 (nice-to-have)

## Communication with Team

**Coordinate with:**
- **Aulia:** Chart style, design consistency, library choices
- **Darva:** Data aggregation queries for complex analysis
- **Kyla:** UI for date range inputs (if needed)

## Code Style Reminders

- **Library:** Plotly (if interactive charts preferred) or Matplotlib
- **Function naming:** `create_trend_chart_lamaran()`, `calculate_acceptance_rate_trend()`
- **Docstrings** in all functions
- **Type hints** for statistical functions
- **Error handling** for edge cases (empty data, division by zero)

See: copilot-instructions.md Section 8

## Blueprint Reference

See `blueprint_beasiswaku.md`:
- **Section 3.3** — Optional features "Grafik tren beasiswa per bulan/tahun"
- **Section 5 Layar 7** — Tab Statistik layout (where trend charts would go)

## Daily Standup Report Format (Optional - Not Core Path)

```
Richard: [Advanced Analytics]
  - Yesterday: [research, learning, design work]
  - Today: [what you're working on]
  - Blocker: [if any]
  - ETA for implementation: [when ready to code]
```

**Example (week 1 - research phase):**
```
Richard: [Advanced Analytics]
  - Yesterday: ✅ Researched Plotly, created mockup for trend chart
  - Today: 🟡 Learning time-series aggregation in SQL
  - Blocker: None
  - ETA implementation: 1 week (after Aulia finishes basic charts)
```

## First Command to Copilot (Research Phase)

```
"Richard: Jelaskan cara membuat trend line chart untuk lamaran beasiswa 
per bulan menggunakan Plotly. 

Requirements:
- X-axis: Bulan (2026-01 to 2026-12)
- Y-axis: Jumlah lamaran
- Trend line yang menunjukkan pattern
- Interactive (hover, zoom, date range filter)

Sesuai instructions Section 8"
```

## Second Command (With Aulia, Coordination)

```
"Richard + Aulia: Diskusikan design untuk trend charts.
Richard: Buat proposal desain untuk 'Tren Lamaran per Bulan'
Aulia: Review konsistensi dengan basic charts (style, color)

Target: Sesuai blueprint Section 3.3 'Grafik tren beasiswa per bulan/tahun'"
```

## Third Command (When Ready to Implement)

```
"Richard: Implementasikan trend chart untuk lamaran per bulan.
- Query data dari database (dengan bantuan Darva)
- Gunakan Plotly untuk interactive visualization
- Add date range filter (optional)

Sesuai design yang sudah di-approve bersama Aulia"
```

---

*Last updated: April 2026*  
*Note: You are supporting role. Coordinate with Aulia (PIC visualisasi.py)*  
*For questions: refer to copilot-instructions.md or ask in group chat*
