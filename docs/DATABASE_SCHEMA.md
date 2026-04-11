# Database Schema - BeasiswaKu

## Overview

BeasiswaKu uses SQLite3 with 6 tables implementing a relational schema for scholarship management.

**File Location:** `database/beasiswaku.db`  
**Initialization:** Automatic on first run via `src.core.database.DatabaseManager.init_schema()`

---

## Table 1: akun (User Accounts)

Stores user authentication information and profiles.

```sql
CREATE TABLE akun (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    username            TEXT UNIQUE NOT NULL,
    email               TEXT UNIQUE NOT NULL,
    password_hash       TEXT NOT NULL,
    nama_lengkap        TEXT,
    jenjang             TEXT,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

**Fields:**
| Field | Type | Notes |
|-------|------|-------|
| id | INTEGER | Primary key, auto-incrementing |
| username | TEXT | Unique identifier, required |
| email | TEXT | Email address, unique, required |
| password_hash | TEXT | bcrypt hashed password, required |
| nama_lengkap | TEXT | Full name |
| jenjang | TEXT | Education level (S1, S2, S3) |
| created_at | TIMESTAMP | Auto-set on creation |
| updated_at | TIMESTAMP | Auto-update on modification |

**Constraints:**
- PRIMARY KEY (id)
- UNIQUE (username)
- UNIQUE (email)
- NOT NULL (username, email, password_hash)

**Related Tables:**
- riwayat_lamaran (foreign key: user_id)
- favorit (foreign key: user_id)
- catatan (foreign key: user_id)

---

## Table 2: penyelenggara (Scholarship Providers)

Information about scholarship-providing organizations.

```sql
CREATE TABLE penyelenggara (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    nama            TEXT NOT NULL,
    description     TEXT,
    website         TEXT,
    contact_email   TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

**Fields:**
| Field | Type | Notes |
|-------|------|-------|
| id | INTEGER | Primary key |
| nama | TEXT | Organization name, required |
| description | TEXT | Detailed description |
| website | TEXT | Official website URL |
| contact_email | TEXT | Contact email address |
| created_at | TIMESTAMP | Creation timestamp |

**Related Tables:**
- beasiswa (foreign key: penyelenggara_id)

---

## Table 3: beasiswa (Scholarships)

Core scholarship database with details and requirements.

```sql
CREATE TABLE beasiswa (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    judul           TEXT NOT NULL,
    penyelenggara_id INTEGER,
    jenjang         TEXT,
    deadline        DATE NOT NULL,
    deskripsi       TEXT,
    benefit         TEXT,
    persyaratan     TEXT,
    minimal_ipk     REAL,
    coverage        TEXT,
    status          TEXT DEFAULT 'Buka',
    link_aplikasi   TEXT,
    scrape_date     TIMESTAMP,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (penyelenggara_id) REFERENCES penyelenggara(id)
)
```

**Fields:**
| Field | Type | Notes |
|-------|------|-------|
| id | INTEGER | Primary key |
| judul | TEXT | Scholarship title, required |
| penyelenggara_id | INTEGER | Foreign key to penyelenggara |
| jenjang | TEXT | Target education level |
| deadline | DATE | Application deadline, required |
| deskripsi | TEXT | Full description |
| benefit | TEXT | Benefits/prizes offered |
| persyaratan | TEXT | Requirements and conditions |
| minimal_ipk | REAL | Minimum GPA requirement |
| coverage | TEXT | Coverage details |
| status | TEXT | Status (Buka/Ditutup/Dibatalkan) |
| link_aplikasi | TEXT | Application URL |
| scrape_date | TIMESTAMP | Last updated from scraper |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last modification timestamp |

**Indexes (Recommended):**
```sql
CREATE INDEX idx_beasiswa_status ON beasiswa(status);
CREATE INDEX idx_beasiswa_deadline ON beasiswa(deadline);
CREATE INDEX idx_beasiswa_jenjang ON beasiswa(jenjang);
CREATE INDEX idx_beasiswa_penyelenggara ON beasiswa(penyelenggara_id);
```

**Related Tables:**
- riwayat_lamaran (foreign key: beasiswa_id)
- favorit (foreign key: beasiswa_id)
- catatan (foreign key: beasiswa_id)

---

## Table 4: riwayat_lamaran (Application History)

Tracks user applications to scholarships.

```sql
CREATE TABLE riwayat_lamaran (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL,
    beasiswa_id     INTEGER NOT NULL,
    status          TEXT DEFAULT 'Pending',
    tanggal_daftar  DATE,
    catatan         TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES akun(id),
    FOREIGN KEY (beasiswa_id) REFERENCES beasiswa(id),
    UNIQUE(user_id, beasiswa_id)
)
```

**Fields:**
| Field | Type | Notes |
|-------|------|-------|
| id | INTEGER | Primary key |
| user_id | INTEGER | Foreign key to akun, required |
| beasiswa_id | INTEGER | Foreign key to beasiswa, required |
| status | TEXT | Application status |
| tanggal_daftar | DATE | Application date |
| catatan | TEXT | Internal notes |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Update timestamp |

**Status Values:**
- `Pending` - Initial application status
- `Submitted` - Successfully submitted
- `Under Review` - Being reviewed
- `Accepted` - Application accepted
- `Rejected` - Application rejected

**Constraints:**
- UNIQUE (user_id, beasiswa_id) - User can apply to each beasiswa only once
- NOT NULL (user_id, beasiswa_id)

---

## Table 5: favorit (Favorite Scholarships)

User's favorited scholarships for quick access.

```sql
CREATE TABLE favorit (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL,
    beasiswa_id     INTEGER NOT NULL,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES akun(id),
    FOREIGN KEY (beasiswa_id) REFERENCES beasiswa(id),
    UNIQUE(user_id, beasiswa_id)
)
```

**Fields:**
| Field | Type | Notes |
|-------|------|-------|
| id | INTEGER | Primary key |
| user_id | INTEGER | Foreign key to akun, required |
| beasiswa_id | INTEGER | Foreign key to beasiswa, required |
| created_at | TIMESTAMP | When bookmarked |

**Constraints:**
- UNIQUE (user_id, beasiswa_id) - Each user can favorite each beasiswa once
- NOT NULL (user_id, beasiswa_id)

---

## Table 6: catatan (Personal Notes)

User's personal notes on scholarships.

```sql
CREATE TABLE catatan (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL,
    beasiswa_id     INTEGER NOT NULL,
    content         TEXT NOT NULL,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES akun(id),
    FOREIGN KEY (beasiswa_id) REFERENCES beasiswa(id),
    UNIQUE(user_id, beasiswa_id)
)
```

**Fields:**
| Field | Type | Notes |
|-------|------|-------|
| id | INTEGER | Primary key |
| user_id | INTEGER | Foreign key to akun, required |
| beasiswa_id | INTEGER | Foreign key to beasiswa, required |
| content | TEXT | Note content, required |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last modification timestamp |

**Constraints:**
- UNIQUE (user_id, beasiswa_id) - One note per user per beasiswa
- NOT NULL (user_id, beasiswa_id, content)

---

## Entity Relationship Diagram

```
┌──────────────┐
│   akun       │
│ (User Acc.)  │
├──────────────┤
│ id (PK)      │ ◄─────────────────────────────────────┐
│ username     │ ◄──────────┐                          │
│ email        │            │                          │
│ password_hash│            │                 ┌────────┴────────┐
│ nama_lengkap │            │                 │                 │
│ jenjang      │            │                 ▼                 ▼
└──────────────┘            │            riwayat_lamaran   favorit
       │                    │            (Application)     (Favorites)
       │                    │            ┌─────────────┐  ┌──────────┐
       │                    │            │ id (PK)     │  │ id (PK)  │
       │                    ├────────────┤ user_id (FK)│  │ user_id (FK)
       │                    │            │ beasiswa_id │  │ beasiswa_id
       │                    │            │ status      │  │ created_at
       │                    │            │ tanggal_..  │  └──────────┘
       │                    │            │ catatan     │        ▲
       │                    │            │ created_at  │        │
       │                    │            │ updated_at  │        │
       │                    │            └─────────────┘        │
       │                    │                    ▲               │
       │                    └────────────────────┼───────────────┘
       │                                         │
       │                    ┌────────────────────┴─────┐
       │                    │                          │
       │                    ▼                          ▼
       │             ┌──────────────┐          ┌──────────────┐
       │             │   catatan    │          │  beasiswa    │
       │             │  (Notes)     │          │              │
       ├─────────────┤ id (PK)      │          ├──────────────┤
       │             │ user_id (FK) │◄─────────┤ id (PK)      │
       │             │ beasiswa_id  │          │ judul        │
       │             │ content      │          │ penyelenggara│
       │             │ created_at   │          │ jenjang      │
       │             │ updated_at   │          │ deadline     │
       │             └──────────────┘          │ deskripsi    │
       │                                       │ benefit      │
       │             ┌──────────────┐          │ persyaratan  │
       │             │penyelenggara │          │ minimal_ipk  │
       │             │ (Provider)   │          │ coverage     │
       └─────────────┤ id (PK)      │◄─────────┤ status       │
                     │ nama         │          │ link_aplikasi│
                     │ description  │          │ scrape_date  │
                     │ website      │          │ created_at   │
                     │ contact_email│          │ updated_at   │
                     └──────────────┘          └──────────────┘

FK = Foreign Key
PK = Primary Key
```

---

## Data Integrity Constraints

### Primary Keys
All tables have `id INTEGER PRIMARY KEY AUTOINCREMENT` for unique identification.

### Foreign Keys
All foreign key relationships reference `id` field of related tables.

### Unique Constraints
- `akun.username` - Each user must have unique username
- `akun.email` - Each user must have unique email
- `riwayat_lamaran(user_id, beasiswa_id)` - User can apply to each beasiswa only once
- `favorit(user_id, beasiswa_id)` - User can favorite each beasiswa only once
- `catatan(user_id, beasiswa_id)` - User can have only one note per beasiswa

### Not Null Constraints
- `akun`: username, email, password_hash
- `beasiswa`: judul, deadline
- `penyelenggara`: nama
- `riwayat_lamaran`: user_id, beasiswa_id
- `catatan`: user_id, beasiswa_id, content

---

## Sample Queries

### Get user's applications with beasiswa details
```sql
SELECT 
    l.id, u.username, b.judul, b.deadline,
    l.status, l.tanggal_daftar, l.catatan
FROM riwayat_lamaran l
JOIN akun u ON l.user_id = u.id
JOIN beasiswa b ON l.beasiswa_id = b.id
WHERE u.id = ?
ORDER BY l.tanggal_daftar DESC;
```

### Get user's favorites with provider info
```sql
SELECT 
    b.id, b.judul, p.nama as penyelenggara,
    b.deadline, b.minimal_ipk, b.status
FROM favorit f
JOIN beasiswa b ON f.beasiswa_id = b.id
LEFT JOIN penyelenggara p ON b.penyelenggara_id = p.id
WHERE f.user_id = ?
ORDER BY b.deadline ASC;
```

### Search open scholarships by level
```sql
SELECT *
FROM beasiswa
WHERE status = 'Buka'
  AND jenjang = ?
  AND deadline > DATE('now')
ORDER BY deadline ASC;
```

### Count stats per user
```sql
SELECT 
    u.username,
    COUNT(DISTINCT f.id) as favorite_count,
    COUNT(DISTINCT l.id) as application_count,
    COUNT(DISTINCT c.id) as note_count
FROM akun u
LEFT JOIN favorit f ON u.id = f.user_id
LEFT JOIN riwayat_lamaran l ON u.id = l.user_id
LEFT JOIN catatan c ON u.id = c.user_id
WHERE u.id = ?
GROUP BY u.id;
```

---

## Maintenance

### Backup
```bash
# Create backup
cp database/beasiswaku.db database/backup/beasiswaku_backup.db

# Restore backup
cp database/backup/beasiswaku_backup.db database/beasiswaku.db
```

### Optimize
```sql
-- Rebuild indexes and optimize storage
VACUUM;
ANALYZE;
```

### Integrity Check
```sql
-- Verify database integrity
PRAGMA integrity_check;
```

---

## Performance Tuning

### Recommended Indexes
```sql
-- For common searches
CREATE INDEX idx_beasiswa_status ON beasiswa(status);
CREATE INDEX idx_beasiswa_deadline ON beasiswa(deadline);
CREATE INDEX idx_beasiswa_jenjang ON beasiswa(jenjang);
CREATE INDEX idx_beasiswa_minimal_ipk ON beasiswa(minimal_ipk);

-- For user queries
CREATE INDEX idx_lamaran_user ON riwayat_lamaran(user_id);
CREATE INDEX idx_favorit_user ON favorit(user_id);
CREATE INDEX idx_catatan_user ON catatan(user_id);
```

### Connection Pooling
Used via `DatabaseManager` singleton - reduces connection overhead.

---

## Backup and Recovery

Regular automated backups via setup script:
```bash
# Backup location
database/backup/beasiswaku_backup.db

# To restore
cp database/backup/beasiswaku_backup.db database/beasiswaku.db
```
