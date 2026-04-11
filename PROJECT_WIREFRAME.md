# 🎨 BeasiswaKu - Project Structure Wireframe

## 📐 System Architecture Wireframe

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          BeasiswaKu Application                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      Presentation Layer (GUI)                       │   │
│  │                          PyQt6 Interface                            │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │                                                                     │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌────────────────────────┐   │   │
│  │  │ Login Window │  │Registration  │  │  Main Window (3 Tabs)  │   │   │
│  │  │              │  │   Window     │  │                        │   │   │
│  │  │ - Username   │→ │ - Username   │→ │ [Tab1] [Tab2] [Tab3]  │   │   │
│  │  │ - Password   │  │ - Email      │  │                        │   │   │
│  │  │ - Login Btn  │  │ - Password   │  │                        │   │   │
│  │  │ - Register   │  │ - Register   │  │                        │   │   │
│  │  │   Link       │  │   Button     │  │                        │   │   │
│  │  └──────────────┘  └──────────────┘  └────────────────────────┘   │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                   Business Logic Layer                              │   │
│  │              CRUD Operations & Validations                          │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │                                                                     │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐   │   │
│  │  │ Authentication  │  │  CRUD Modules   │  │  Aggregations  │   │   │
│  │  │                 │  │                 │  │                 │   │   │
│  │  │ - Register User │  │ - Beasiswa      │  │ - Per Jenjang   │   │   │
│  │  │ - Login User    │  │ - Lamaran       │  │ - Top Provider  │   │   │
│  │  │ - Verify Pwd    │  │ - Favorit       │  │ - Status Count  │   │   │
│  │  │ - Hash Bcrypt   │  │ - Catatan       │  │                 │   │   │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘   │   │
│  │                                                                     │   │
│  │              ↓ Validation & Error Handling ↓                        │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      Data Access Layer                              │   │
│  │                    SQLite3 Database                                 │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │                                                                     │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐              │   │
│  │  │   akun   │ │beasiswa  │ │riwayat   │ │favorit   │              │   │
│  │  │ (Users)  │ │          │ │lamaran   │ │          │              │   │
│  │  │          │ │          │ │(Apps)    │ │          │              │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘              │   │
│  │                                                                     │   │
│  │  ┌──────────┐ ┌──────────┐                                         │   │
│  │  │ catatan  │ │penyeleng │                                         │   │
│  │  │ (Notes)  │ │gara      │                                         │   │
│  │  │          │ │(Provider)│                                         │   │
│  │  └──────────┘ └──────────┘                                         │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🖥️ GUI Layout Wireframes

### 1️⃣ **Login Window**

```
┌──────────────────────────────────────────┐
│        BeasiswaKu - Login                │
├──────────────────────────────────────────┤
│                                          │
│  📊 BeasiswaKu Logo                      │
│                                          │
│  Username: [_____________________]       │
│                                          │
│  Password: [_____________________]       │
│                                          │
│  ┌──────────────┐  ┌──────────────┐    │
│  │   Login      │  │   Register   │    │
│  └──────────────┘  └──────────────┘    │
│                                          │
│  [✓] Remember me                         │
│                                          │
│  Status: Ready                           │
└──────────────────────────────────────────┘
```

### 2️⃣ **Registration Window**

```
┌──────────────────────────────────────────┐
│     BeasiswaKu - Register Account        │
├──────────────────────────────────────────┤
│                                          │
│  Username: [_____________________]       │
│           ⓘ Must be unique               │
│                                          │
│  Email:    [_____________________]       │
│           ⓘ Valid email required         │
│                                          │
│  Password: [_____________________]       │
│           ⓘ Min 6 characters             │
│                                          │
│  Confirm:  [_____________________]       │
│                                          │
│  Full Name:[_____________________]       │
│           ⓘ (Optional)                   │
│                                          │
│  Level:    [D3/D4/S1/S2 ▼]              │
│                                          │
│  ┌──────────────┐  ┌──────────────┐    │
│  │   Register   │  │   Cancel     │    │
│  └──────────────┘  └──────────────┘    │
│                                          │
└──────────────────────────────────────────┘
```

### 3️⃣ **Main Window (3 Tabs)**

```
┌──────────────────────────────────────────────────────────────────┐
│  BeasiswaKu - Scholarship Manager          [_] [□] [×]          │
├──────────────────────────────────────────────────────────────────┤
│  File  Help                                                       │
├──────────────────────────────────────────────────────────────────┤
│  [Beasiswa] [Lamaran] [Catatan]           User: john_doe         │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  TAB 1: BEASISWA MANAGEMENT                                      │
│  ───────────────────────────────────                             │
│                                                                  │
│  [🔍 Search] [+ Add] [Edit] [Delete] [❤ Favorit]               │
│                                                                  │
│  Filter: [Jenjang ▼] [Status ▼] [Deadline ▼]  [Apply]          │
│                                                                  │
│  ╔════════════════════════════════════════════════════════════╗ │
│  ║ # │ Judul           │ Penyelenggara │ Deadline  │ Applied ║ │
│  ╠════╪═════════════════╪═══════════════╪═══════════╪═════════╣ │
│  ║ 1 │ Beasiswa A      │ Org A         │ 2026-05-01│ ✓       ║ │
│  ║ 2 │ Beasiswa B      │ Org B         │ 2026-06-01│         ║ │
│  ║ 3 │ Beasiswa C      │ Org C         │ 2026-07-01│         ║ │
│  ║   │                 │               │           │         ║ │
│  ╚════╧═════════════════╧═══════════════╧═══════════╧═════════╝ │
│                                                                  │
│  Showing 1-3 of 100  [◄ Previous] [Next ►]                      │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### 4️⃣ **Tab 2: Application History**

```
├──────────────────────────────────────────────────────────────────┤
│  TAB 2: APPLICATION HISTORY                                      │
│  ──────────────────────────────                                  │
│                                                                  │
│  [➕ New Application] [Edit] [Delete]                            │
│                                                                  │
│  Filter: [Status ▼] [Date ▼]  [Apply]                           │
│                                                                  │
│  ╔════════════════════════════════════════════════════════════╗ │
│  ║ # │ Beasiswa        │ Status       │ Tanggal    │ Catatan ║ │
│  ╠════╪═════════════════╪══════════════╪════════════╪═════════╣ │
│  ║ 1 │ Beasiswa A      │ ✓ Approved   │ 2026-04-01 │ Review  ║ │
│  ║ 2 │ Beasiswa B      │ ⏳ Pending   │ 2026-04-05 │ Waiting ║ │
│  ║ 3 │ Beasiswa C      │ ✗ Rejected   │ 2026-04-10 │ -       ║ │
│  ║   │                 │              │            │         ║ │
│  ╚════╧═════════════════╧══════════════╧════════════╧═════════╝ │
│                                                                  │
│  Status Statistics:                                              │
│  Approved: 5 | Pending: 3 | Rejected: 2                         │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### 5️⃣ **Tab 3: Notes & Favorites**

```
├──────────────────────────────────────────────────────────────────┤
│  TAB 3: NOTES & FAVORITES                                        │
│  ──────────────────────────────                                  │
│                                                                  │
│  [➕ Add Note] [Edit] [Delete]                                   │
│                                                                  │
│  ╔════════════════════════════════════════════════════════════╗ │
│  ║ Beasiswa                │ ❤ Status  │ Notes Preview      ║ │
│  ╠═════════════════════════╪═══════════╪════════════════════╣ │
│  ║ Beasiswa A              │ ❤ Favorit │ Good opportunity...║ │
│  ║                         │           │                    ║ │
│  ║ Beasiswa B              │ 🤍 Not    │ High competition...║ │
│  ║                         │           │                    ║ │
│  ║ Beasiswa C              │ ❤ Favorit │ Need to prepare...║ │
│  ║                         │           │                    ║ │
│  ╚═════════════════════════╧═══════════╧════════════════════╝ │
│                                                                  │
│  Note Editor (Double-click to edit):                             │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ [Edit] [Save] [Cancel]                                  │   │
│  │                                                          │   │
│  │ ╔── Note for Beasiswa A ──────────────────────────────╗ │   │
│  │ ║ This is a great opportunity for financial aid.      ║ │   │
│  │ ║ Need to prepare good portfolio.                     ║ │   │
│  │ ║ Deadline: May 1st, 2026                             ║ │   │
│  │ ╚──────────────────────────────────────────────────────╝ │   │
│  │ Character count: 125 / 2000                             │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🗄️ Database Schema Wireframe

```
┌─────────────────────────────────────────────────────────────────┐
│                    SQLite Database Schema                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────┐         ┌──────────────────────┐    │
│  │      akun (Users)    │         │  penyelenggara       │    │
│  ├──────────────────────┤         ├──────────────────────┤    │
│  │ id (PK) ─────────────┼────────→│ id (PK)              │    │
│  │ username (UNIQUE)    │         │ nama                 │    │
│  │ email (UNIQUE)       │         │ description          │    │
│  │ password_hash        │         │ website              │    │
│  │ nama_lengkap         │         │ contact_email        │    │
│  │ jenjang              │         │ created_at           │    │
│  │ created_at           │         └──────────────────────┘    │
│  │ updated_at           │                  ▲                   │
│  └──────────────────────┘                  │ FK               │
│           ▲                                 │                   │
│           │ FK                              │                   │
│           │                                 │                   │
│  ┌────────┴─────────────────────┐     ┌────┴──────────────────┐│
│  │   beasiswa (Scholarships)     │     │                       ││
│  ├───────────────────────────────┤     │                       ││
│  │ id (PK)                       │     │  riwayat_lamaran     ││
│  │ judul                         │─────┤  (Applications)      ││
│  │ penyelenggara_id (FK)         │     │  ├────────────────┤  ││
│  │ jenjang                       │     │  │ id (PK)        │  ││
│  │ deadline (INDEX)              │     │  │ user_id (FK)───┘  ││
│  │ status (INDEX)                │     │  │ beasiswa_id (FK)  ││
│  │ deskripsi                     │     │  │ status      (UNIQUE
│  │ benefit                       │     │  │ tanggal_daftar    ││
│  │ persyaratan                   │     │  │ catatan           ││
│  │ minimal_ipk                   │     │  │ created_at        ││
│  │ coverage                      │     │  │ updated_at        ││
│  │ link_aplikasi                 │     │  └────────────────┘  ││
│  │ created_at                    │     │                       ││
│  │ updated_at                    │     │  ┌────────────────┐  ││
│  └───────────────────────────────┘     │  │ favorit        │  ││
│           ▲                             │  │ ├──────────┤   │  ││
│           │ FK                          │  │ id (PK)   │   │  ││
│           │                             │  │ user_id   │   │  ││
│           │                             │  │ beasiswa← ┘   │  ││
│  ┌────────┴─────────────────────────┐  │  │ UNIQUE()   │   │  ││
│  │  catatan (Personal Notes)         │  │  │ created_at│   │  ││
│  ├────────────────────────────────────┤ │  └────────────────┘  ││
│  │ id (PK)                            │ │                       ││
│  │ user_id (FK) ──────────────────┐  │ │                       ││
│  │ beasiswa_id (FK) ──────────────┼──┘ │                       ││
│  │ content (max 2000 chars)        │    │                       ││
│  │ created_at                      │    │                       ││
│  │ updated_at                      │    │                       ││
│  │ UNIQUE(user_id, beasiswa_id)    │    │                       ││
│  └────────────────────────────────────┘ └───────────────────────┘│
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

Legend:
  PK = Primary Key
  FK = Foreign Key
  UNIQUE = Unique Constraint
  INDEX = Indexed for performance
```

---

## 📂 File Structure Wireframe

```
beasiswaku/
│
├── 📄 Documentation (13 files)
│   ├── README.md                      ← Start here!
│   ├── QUICKSTART.md                  ← Installation
│   ├── DOCUMENTATION.md               ← API Reference
│   ├── PROJECT_SUMMARY.md             ← Executive Summary
│   ├── COMPLETION_SUMMARY.md          ← Detailed Completion
│   ├── PROJECT_STATUS_DASHBOARD.md    ← Status Overview
│   ├── TEST_RESULTS.md                ← Test Coverage
│   ├── ONBOARDING.md                  ← Developer Guide
│   ├── blueprint_beasiswaku.md        ← System Blueprint
│   ├── DOCUMENTATION_INDEX.md         ← Navigation
│   ├── TODAYS_WORK_SUMMARY.md         ← Session Summary
│   ├── PROJECT_INDEX.md               ← Project Index
│   └── PROJECT_WIREFRAME.md           ← This file
│
├── 🐍 Source Code
│   ├── main.py                        ← Entry point
│   ├── gui_beasiswa.py                ← Main GUI (Tab 1)
│   ├── gui_favorit.py                 ← Favorit Tab (Tab 3)
│   ├── gui_notes.py                   ← Notes UI (Tab 3)
│   └── crud.py                        ← 23 CRUD functions
│
├── 🧪 Test Suite (10 files)
│   ├── test_phase_1_1.py              ← Database tests
│   ├── test_auth_demo.py              ← Auth tests
│   ├── test_phase_2_2.py              ← Beasiswa CRUD
│   ├── test_phase_3_1.py              ← Application CRUD
│   ├── test_phase_3_2.py              ← Favorit CRUD
│   ├── test_phase_4_1.py              ← Aggregations
│   ├── test_phase_1_3.py              ← GUI tests
│   ├── test_phase_5_2.py              ← Status tests
│   ├── test_phase_5_3.py              ← Favorit UI tests
│   └── test_phase_5_4.py              ← Notes tests
│
├── 📊 Analysis & Tools
│   ├── comprehensive_analysis.py      ← Analysis tool
│   └── FINAL_TESTING_REPORT.py        ← Final report
│
├── 🗄️ Database
│   ├── database/
│   │   └── beasiswaku.db              ← SQLite (auto-created)
│   └── backup/                         ← Backups
│
└── ⚙️ Configuration
    ├── requirements.txt               ← Dependencies
    ├── setup.sh                       ← Linux setup
    ├── setup.bat                      ← Windows setup
    └── setup_and_run.sh              ← Interactive setup
```

---

## 🔄 Data Flow Wireframe

```
┌─────────────────────────────────────────────────────────────────┐
│                       Data Flow Diagram                         │
└─────────────────────────────────────────────────────────────────┘

USER INPUT
    │
    ▼
┌─────────────────────┐
│  GUI Layer (PyQt6)  │  ← User interactions
│  - Click buttons    │
│  - Enter text       │
│  - Select filters   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────────────┐
│  Business Logic (crud.py)           │  ← Process data
│  - Validate input                   │
│  - Execute operations               │
│  - Apply business rules             │
│  - Handle errors                    │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│  Database Access (SQLite)           │  ← CRUD operations
│  - Execute queries                  │
│  - Manage transactions              │
│  - Enforce constraints              │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│  Database (SQLite file)             │  ← Data storage
│  - 6 tables                         │
│  - Relationships (FK)               │
│  - Constraints (UNIQUE, CHECK)      │
└──────────┬──────────────────────────┘
           │
           ▼ (Return data)
┌─────────────────────────────────────┐
│  Business Logic (Process results)   │  ← Format for display
│  - Create lists/tables              │
│  - Calculate aggregations           │
│  - Filter/sort results              │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│  GUI Layer (Display)                │  ← Show results
│  - Update tables                    │
│  - Show messages                    │
│  - Refresh UI                       │
└──────────┬──────────────────────────┘
           │
           ▼
      USER SEES RESULT
```

---

## 🔐 Authentication Flow Wireframe

```
┌─────────────────────────────────────────────────────────────────┐
│                   Authentication Flow                           │
└─────────────────────────────────────────────────────────────────┘

REGISTER NEW USER:
  │
  ├─→ [Register Window]
  │   ├─ Input username, email, password, etc.
  │   │
  │   ├─→ [Validate Input]
  │   │   ├─ Check username not exists
  │   │   ├─ Verify email format
  │   │   └─ Check password strength
  │   │
  │   ├─→ [Hash Password with bcrypt]
  │   │   └─ Add salt + hash
  │   │
  │   ├─→ [Save to Database]
  │   │   └─ Insert into akun table
  │   │
  │   └─→ ✅ Account created → Go to Login

LOGIN EXISTING USER:
  │
  ├─→ [Login Window]
  │   ├─ Input username/email + password
  │   │
  │   ├─→ [Find User in Database]
  │   │   └─ Query: SELECT * FROM akun WHERE username = ?
  │   │
  │   ├─→ [Verify Password]
  │   │   ├─ Get stored password_hash
  │   │   ├─ Hash input password with same salt
  │   │   └─ Compare hashes
  │   │
  │   ├─→ ✅ Password matches?
  │   │   ├─ YES: Load user data
  │   │   │   └─→ [Main Window] (Logged in)
  │   │   │
  │   │   └─ NO: Show error
  │   │       └─→ [Login Window] (Try again)
```

---

## 📱 User Journey Wireframe

```
┌─────────────────────────────────────────────────────────────────┐
│              Typical User Journey in BeasiswaKu                 │
└─────────────────────────────────────────────────────────────────┘

START
  │
  ▼
┌─────────────────┐
│  Launch App     │
└────────┬────────┘
         │
         ▼
  ┌─────────────┐
  │ LoggedIn?   │  ──NO──→ [Login/Register Window]
  └────┬────────┘         │
       │ YES              ├─ Register new account
       │                  │
       │                  └─ Enter username, password, email
       │                     │
       │                  ┌──┴─────────────────┐
       │                  │ Validate & Save    │
       │                  └──┬─────────────────┘
       │                     │
       │                  [Login Window]
       │                     │
       │            ┌────────┴───────┐
       │            │ Login Success? │
       │            └────┬───────┬───┘
       │                 │       │
       │            YES  │       │ NO
       │                 │       └─→ [Show Error, Retry]
       │                 │
       └─────────┬───────┘
                 │
                 ▼
        ┌────────────────────┐
        │  MAIN WINDOW       │  ← User is now logged in
        │  (3 Tabs)          │
        └────────────────────┘
                 │
         ┌───────┼───────┐
         │       │       │
         ▼       ▼       ▼
    [TAB 1]  [TAB 2]  [TAB 3]
    (Search  (View    (Notes &
     & Manage Applied) Favorites)
     Scholas)
         │       │       │
    ┌────┴───┐┌──┴────┐┌─┴────┐
    │        ││       ││      │
    ▼        ▼│       │▼      │
  [View]  [View]   [Edit]  [Manage]
  [Filter][Status] [Notes] [Favorites]
  [Sort]  [Update] [Save]  [Toggle ❤]
  [Add]   [Delete] [Delete
  [Bookmark
  [Delete

         │       │       │
         └───────┼───────┘
                 │
                 ▼
        ┌──────────────────┐
        │ Update Database  │
        │ (All changes     │
        │  persisted)      │
        └────────┬─────────┘
                 │
         ┌───────┴────────┐
         │                │
         ▼                ▼
    [Continue]      [Logout]
    [Using App]     [Return to Login]
         │                │
         └────────┬───────┘
                  │
                  ▼
              [END]
```

---

## 🏗️ Module Interaction Wireframe

```
┌─────────────────────────────────────────────────────────────────┐
│           Module Interaction & Dependencies                     │
└─────────────────────────────────────────────────────────────────┘

main.py (Entry Point)
  │
  ├─→ Imports: gui_beasiswa, gui_favorit, gui_notes, crud
  │
  └─→ QApplication instance
      │
      ├─→ gui_beasiswa.LoginWindow()
      │   ├─ Signal: login_successful
      │   ├─ Calls: crud.login_user()
      │   └─ Calls: crud.register_user()
      │
      └─→ gui_beasiswa.MainWindow() [on successful login]
          ├─ gui_beasiswa.py (Main GUI + Tab 1)
          │  ├─ Calls: crud.get_beasiswa_list()
          │  ├─ Calls: crud.add_beasiswa()
          │  ├─ Calls: crud.edit_beasiswa()
          │  ├─ Calls: crud.delete_beasiswa()
          │  ├─ Calls: crud.add_favorit()
          │  └─ Calls: crud.check_user_applied()
          │
          ├─ gui_favorit.py (Tab 2 - Applications)
          │  ├─ Calls: crud.get_lamaran_list()
          │  ├─ Calls: crud.add_lamaran()
          │  ├─ Calls: crud.edit_lamaran()
          │  ├─ Calls: crud.delete_lamaran()
          │  └─ Calls: crud.get_beasiswa_per_jenjang()
          │
          └─ gui_notes.py (Tab 3 - Notes & Favorites)
             ├─ Calls: crud.get_favorit_list()
             ├─ Calls: crud.delete_favorit()
             ├─ Calls: crud.get_catatan()
             ├─ Calls: crud.add_catatan()
             ├─ Calls: crud.edit_catatan()
             ├─ Calls: crud.delete_catatan()
             └─ Calls: crud.get_catatan_list()

crud.py (Business Logic)
  │
  ├─→ Authentication Module
  │   ├─ register_user(username, email, password, etc.)
  │   └─ login_user(username, password)
  │
  ├─→ Beasiswa Module
  │   ├─ add_beasiswa(...)
  │   ├─ get_beasiswa_list(filters, sort, page)
  │   ├─ edit_beasiswa(id, ...)
  │   └─ delete_beasiswa(id)
  │
  ├─→ Application Module
  │   ├─ add_lamaran(user_id, beasiswa_id, ...)
  │   ├─ get_lamaran_list(user_id, filters)
  │   ├─ edit_lamaran(id, status, ...)
  │   └─ delete_lamaran(id)
  │
  ├─→ Favorit Module
  │   ├─ add_favorit(user_id, beasiswa_id)
  │   ├─ get_favorit_list(user_id)
  │   └─ delete_favorit(user_id, beasiswa_id)
  │
  ├─→ Notes Module
  │   ├─ add_catatan(user_id, beasiswa_id, content)
  │   ├─ get_catatan(user_id, beasiswa_id)
  │   ├─ edit_catatan(id, content)
  │   ├─ delete_catatan(id)
  │   └─ get_catatan_list(user_id)
  │
  ├─→ Aggregation Module
  │   ├─ get_beasiswa_per_jenjang()
  │   ├─ get_top_penyelenggara()
  │   └─ get_status_availability()
  │
  └─→ Database Layer
      │
      ├─→ SQLite Connection
      │   ├─ cursor.execute(query, params)
      │   ├─ conn.commit()
      │   └─ conn.rollback()
      │
      └─→ 6 Tables
          ├─ akun (users)
          ├─ beasiswa
          ├─ riwayat_lamaran
          ├─ favorit
          ├─ catatan
          └─ penyelenggara
```

---

## 🔄 CRUD Operations Wireframe

```
┌─────────────────────────────────────────────────────────────────┐
│              CRUD Operations Flow (Example: Beasiswa)           │
└─────────────────────────────────────────────────────────────────┘

CREATE (Add):
  User Input
    │
    ▼
  [Form] → Validate ─ YES → [Hash/Encrypt] → DB INSERT
           │                              ↓
          NO                        Log Success
           │                              ↓
           └──────→ [Show Error]       Refresh List

READ (Get):
  User Action
    │
    ▼
  [Query] ──→ Apply Filters
              Apply Sort
              Apply Pagination
              │
              ▼
         [Execute Query]
              │
              ▼
         ┌────────────────────┐
         │ Return Data List   │
         │ (Beasiswa objects) │
         └────────────────────┘
              │
              ▼
         [Display in Table]

UPDATE (Edit):
  User Edit Form
    │
    ▼
  [Modified Data] ──→ Validate
                        │
                        ├─ YES → [Update DB]
                        │           │
                        │           ▼
                        │      Log Change
                        │           │
                        │           ▼
                        │      Refresh View
                        │
                        └─ NO → [Show Error]

DELETE:
  User Click Delete
    │
    ▼
  [Confirm Dialog]
    │
    ├─ YES → [Remove from DB]
    │          │
    │          ▼
    │       Update References (FK)
    │          │
    │          ▼
    │       Log Deletion
    │          │
    │          ▼
    │       Refresh View
    │
    └─ NO → [Cancel]
```

---

## 📊 GUI Component Hierarchy

```
QApplication
│
└─ QMainWindow (main.py)
   │
   ├─ LoginWindow (gui_beasiswa.py)
   │  ├─ QLabel (logo)
   │  ├─ QLineEdit (username)
   │  ├─ QLineEdit (password)
   │  ├─ QPushButton (login_btn)
   │  ├─ QPushButton (register_btn)
   │  └─ QCheckBox (remember_me)
   │
   ├─ RegisterWindow (gui_beasiswa.py)
   │  ├─ QLineEdit (username)
   │  ├─ QLineEdit (email)
   │  ├─ QLineEdit (password)
   │  ├─ QLineEdit (confirm_password)
   │  ├─ QLineEdit (full_name)
   │  ├─ QComboBox (jenjang)
   │  ├─ QPushButton (register_btn)
   │  └─ QPushButton (cancel_btn)
   │
   └─ MainWindow (gui_beasiswa.py, gui_favorit.py, gui_notes.py)
      ├─ QMenuBar
      │  ├─ File Menu
      │  └─ Help Menu
      │
      ├─ QTabWidget
      │  │
      │  ├─ TAB 1: Beasiswa Management
      │  │  ├─ QLineEdit (search_box)
      │  │  ├─ QPushButton (add_btn, edit_btn, delete_btn)
      │  │  ├─ QComboBox (filter_jenjang, filter_status)
      │  │  ├─ QTableWidget
      │  │  │  └─ Columns: id, judul, penyelenggara, deadline, applied
      │  │  └─ QPushButton (pagination)
      │  │
      │  ├─ TAB 2: Applications
      │  │  ├─ QPushButton (new_app_btn, edit_btn, delete_btn)
      │  │  ├─ QComboBox (filter_status)
      │  │  ├─ QTableWidget
      │  │  │  └─ Columns: id, beasiswa, status, tanggal, catatan
      │  │  └─ QLabel (statistics)
      │  │
      │  └─ TAB 3: Notes & Favorites
      │     ├─ QPushButton (add_note_btn, edit_btn, delete_btn)
      │     ├─ QTableWidget
      │     │  └─ Columns: beasiswa, status (heart), notes_preview
      │     └─ QTextEdit (note_editor)
      │        └─ QLabel (char_count)
      │
      ├─ QStatusBar
      │  └─ QLabel (status_message)
      │
      └─ QToolBar (optional)
         └─ Shortcut buttons
```

---

## 🔗 Relationship Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│            Database Table Relationships                          │
└──────────────────────────────────────────────────────────────────┘

                    ┌─────────────────┐
                    │  penyelenggara  │
                    │  (Providers)    │
                    ├─────────────────┤
                    │ id (PK)         │
                    │ nama            │
                    │ description     │
                    └────────┬────────┘
                             │ 1
                             │
                      1 to Many
                             │
                             ▼
                    ┌─────────────────┐
                    │    beasiswa     │
                    │ (Scholarships)  │
                    ├─────────────────┤
                    │ id (PK)         │
                    │ penyelenggara..│◄─── FK
                    └────────┬─┬──────┘
                             │ │
                        1    │ │    1
                         to  │ │  to
                        Many │ │ Many
                             │ │
              ┌──────────────┘ └─────────────┐
              │                              │
              ▼                              ▼
    ┌──────────────────────┐    ┌──────────────────────┐
    │  riwayat_lamaran    │    │     favorit          │
    │ (Applications)      │    │  (Bookmarks)         │
    ├──────────────────────┤    ├──────────────────────┤
    │ id (PK)             │    │ id (PK)              │
    │ user_id (FK)        │    │ user_id (FK)         │
    │ beasiswa_id (FK)    │    │ beasiswa_id (FK)     │
    │ status             │    │ created_at           │
    │ tanggal_daftar     │    └──────────────────────┘
    │ UNIQUE(user, beas) │              ▲
    └──────────┬─────────┘              │
               │                 1      │
               │                 to     │
               │                Many    │
               │                        │
               △ 1                      │
               │                        │
         to Many                        │
               │                        │
    ┌──────────┴──────────┬─────────────┘
    │                     │
    │        N: Many      │
    │                     │
    ▼                     ▼
┌──────────────────┐  ┌──────────────────┐
│      akun        │  │     catatan      │
│    (Users)       │  │  (Personal Notes)│
├──────────────────┤  ├──────────────────┤
│ id (PK)          │  │ id (PK)          │
│ username (UQ)    │  │ user_id (FK)     │
│ email (UQ)       │  │ beasiswa_id (FK) │
│ password_hash    │  │ content          │
│ nama_lengkap     │  │ UNIQUE(user,be)  │
│ jenjang          │  └──────────────────┘
│ created_at       │
│ updated_at       │
└──────────────────┘

Legend:
  PK = Primary Key
  FK = Foreign Key
  UQ = Unique
  1 to Many = One User has Many Applications
  Many = Multiple records can reference same parent
```

---

## 🎯 Feature Implementation Wireframe

```
┌──────────────────────────────────────────────────────────────────┐
│         Feature Implementation & Testing Coverage               │
└──────────────────────────────────────────────────────────────────┘

PHASE 1: Foundation
  ├─ Database Design ────────────── ✅ 6 tables created
  ├─ Authentication ─────────────── ✅ Bcrypt hashing
  ├─ GUI Framework ──────────────── ✅ PyQt6 interface
  └─ Test Coverage ──────────────── ✅ Database tests

PHASE 2: Beasiswa Management
  ├─ Add Scholarship ────────────── ✅ With validation
  ├─ View List ──────────────────── ✅ With filtering
  ├─ Edit Details ───────────────── ✅ Update timestamps
  ├─ Delete Safely ──────────────── ✅ FK protection
  ├─ Advanced Filtering ─────────── ✅ 5 filter types
  ├─ Sorting ────────────────────── ✅ 4 directions
  ├─ Pagination ─────────────────── ✅ Limit/offset
  └─ Test Coverage ──────────────── ✅ 15 test scenarios

PHASE 3: Application Tracking
  ├─ Record Applications ────────── ✅ Status tracking
  ├─ View History ───────────────── ✅ Per-user history
  ├─ Update Status ──────────────── ✅ 3 statuses
  ├─ Delete Records ─────────────── ✅ Safe deletion
  ├─ Duplicate Prevention ────────── ✅ Unique constraint
  └─ Test Coverage ──────────────── ✅ 12 test scenarios

PHASE 4: Advanced Features
  ├─ Favorit System ─────────────── ✅ One-click bookmark
  ├─ Personal Notes ─────────────── ✅ 2000 char limit
  ├─ Statistics Dashboard ───────── ✅ Count per level
  ├─ Aggregation Queries ────────── ✅ Top providers
  └─ Test Coverage ──────────────── ✅ 27 test scenarios

PHASE 5: Polish & UI
  ├─ Applied Status Badge ───────── ✅ Visual indicator
  ├─ Favorite Heart Icon ────────── ✅ Toggle button
  ├─ Color-coded Status ─────────── ✅ Green/Yellow/Red
  ├─ Error Messages ─────────────── ✅ User-friendly
  ├─ Help Tooltips ──────────────── ✅ Informative
  └─ Test Coverage ──────────────── ✅ 13 test scenarios

ADDITIONAL: Quality
  ├─ Code Documentation ────────── ✅ Full docstrings
  ├─ Type Hints ────────────────── ✅ All functions
  ├─ Error Handling ────────────── ✅ Comprehensive
  ├─ Logging ───────────────────── ✅ All operations
  ├─ Security ──────────────────── ✅ Bcrypt, validation
  └─ Test Coverage ──────────────── ✅ 10 test suites
```

---

## 📈 Development Progress Wireframe

```
100%  │  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
      │  
75%   │  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
      │  
50%   │  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
      │  
25%   │  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
      │  
 0%   └──────────────────────────────────────────
      W1  W2  W3  W4  W5  W6  W7  W8

║ Week  │ Phase                    │ Status  ║
╠═══════╪══════════════════════════╪═════════╣
║ W1-2  │ Phase 1: Foundation      │ ✅ 100% ║
║ W3-4  │ Phase 2-3: CRUD          │ ✅ 100% ║
║ W5    │ Phase 4-5: Advanced      │ ✅ 100% ║
║ W6    │ Testing & Verification   │ ✅ 100% ║
║ W7    │ Documentation            │ ✅ 100% ║
║ W8    │ Final Analysis & Report  │ ✅ 100% ║
╚═══════╧══════════════════════════╧═════════╝

STATUS: ✅ 100% COMPLETE - PRODUCTION READY
```

---

**Generated:** 2026-04-11  
**Format:** Project Structure Wireframe  
**Status:** ✅ Complete

For interactive diagrams and code, please refer to actual project files.
