# API Reference - BeasiswaKu CRUD Operations

## Import

All CRUD functions are available from `src.database.crud`:

```python
from src.database.crud import (
    # Authentication
    register_user, login_user, hash_password, verify_password,
    
    # Beasiswa CRUD
    create_beasiswa, get_beasiswa, get_all_beasiswa,
    update_beasiswa, delete_beasiswa, search_beasiswa,
    
    # Lamaran CRUD
    add_lamaran, get_lamaran, update_lamaran, delete_lamaran,
    get_lamaran_list, check_user_applied,
    
    # Favorit CRUD
    add_favorit, delete_favorit, get_favorit_list, check_favorit,
    
    # Catatan CRUD
    add_catatan, get_catatan, edit_catatan, delete_catatan,
    get_catatan_list,
    
    # Database Management
    init_db, get_connection
)
```

## Authentication Functions

### register_user
```python
user_id = register_user(username, email, password, nama_lengkap, jenjang)
```
**Parameters:**
- `username` (str): Unique username
- `email` (str): User email address
- `password` (str): Plain text password (auto-hashed with bcrypt)
- `nama_lengkap` (str): Full name
- `jenjang` (str): Education level (S1, S2, S3, etc.)  
**Returns:** `int` - User ID
**Raises:** `sqlite3.IntegrityError` if username/email already exists

### login_user
```python
user_id = login_user(username, password)
```
**Parameters:**
- `username` (str): Username
- `password` (str): Plain text password
**Returns:** `int` - User ID if successful
**Raises:** `ValueError` if username not found or password incorrect

### hash_password
```python
hashed = hash_password(password)
```
**Parameters:**
- `password` (str): Plain text password
**Returns:** `str` - bcrypt hashed password

### verify_password
```python
is_valid = verify_password(password, hashed_password)
```
**Parameters:**
- `password` (str): Plain text password to verify
- `hashed_password` (str): bcrypt hash from database
**Returns:** `bool` - True if password matches

---

## Beasiswa CRUD Functions

### create_beasiswa
```python
beasiswa_id = create_beasiswa(
    judul, penyelenggara_id, jenjang, deadline,
    deskripsi, benefit, persyaratan, minimal_ipk, 
    coverage, status, link_aplikasi
)
```
**Returns:** `int` - Beasiswa ID
**Note:** `scrape_date` is auto-set to current timestamp

### get_beasiswa
```python
beasiswa = get_beasiswa(beasiswa_id)
```
**Returns:** `dict` - Single beasiswa record with all fields
**Returns:** `None` if not found

### get_all_beasiswa
```python
beasiswa_list = get_all_beasiswa(limit=None)
```
**Parameters:**
- `limit` (int): Optional limit on results
**Returns:** `list[dict]` - All beasiswa records

### update_beasiswa
```python
updated = update_beasiswa(beasiswa_id, **updates)
```
**Parameters:**
- `beasiswa_id` (int): ID to update
- `**updates`: Any columns and new values
**Returns:** `bool` - True if successful
**Example:**
```python
update_beasiswa(1, status='Ditutup', deadline='2026-12-31')
```

### delete_beasiswa
```python
deleted = delete_beasiswa(beasiswa_id)
```
**Parameters:**
- `beasiswa_id` (int): ID to delete
**Returns:** `bool` - True if successful

### search_beasiswa
```python
results = search_beasiswa(
    jenjang=None, status=None, keyword=None,
    minimal_ipk=None, penyelenggara_id=None
)
```
**Parameters:**
- `jenjang` (str): Filter by education level
- `status` (str): Filter by status
- `keyword` (str): Search in judul/deskripsi
- `minimal_ipk` (float): Filter by minimum IPK
- `penyelenggara_id` (int): Filter by provider
**Returns:** `list[dict]` - Matching beasiswa records

---

## Lamaran (Applications) CRUD Functions

### add_lamaran
```python
lamaran_id = add_lamaran(user_id, beasiswa_id, status='Pending', tanggal_daftar=None, catatan='')
```
**Parameters:**
- `user_id` (int): User ID
- `beasiswa_id` (int): Beasiswa ID
- `status` (str): Application status (Pending, Submitted, Accepted, Rejected)
- `tanggal_daftar` (date): Application date (auto-current date if None)
- `catatan` (str): Internal notes
**Returns:** `int` - Lamaran ID

### get_lamaran
```python
lamaran = get_lamaran(lamaran_id)
```
**Returns:** `dict` - Single lamaran record

### update_lamaran
```python
updated = update_lamaran(lamaran_id, **updates)
```
**Example:**
```python
update_lamaran(1, status='Submitted', catatan='Updated status')
```

### delete_lamaran
```python
deleted = delete_lamaran(lamaran_id)
```

### get_lamaran_list
```python
lamarans = get_lamaran_list(user_id, status=None)
```
**Parameters:**
- `user_id` (int): Filter by user
- `status` (str): Optional filter by status
**Returns:** `list[dict]` - User's applications

### check_user_applied
```python
has_applied = check_user_applied(user_id, beasiswa_id)
```
**Returns:** `bool` - True if user already applied for this beasiswa

---

## Favorit (Favorites) CRUD Functions

### add_favorit
```python
favorit_id = add_favorit(user_id, beasiswa_id)
```
**Returns:** `int` - Favorit ID
**Raises:** `sqlite3.IntegrityError` if already favorited

### delete_favorit
```python
deleted = delete_favorit(user_id, beasiswa_id)
```
**Returns:** `bool` - True if successful

### get_favorit_list
```python
favorits = get_favorit_list(user_id)
```
**Returns:** `list[dict]` - User's favorite beasiswa (with beasiswa details)

### check_favorit
```python
is_favorited = check_favorit(user_id, beasiswa_id)
```
**Returns:** `bool` - True if beasiswa is in favorites

---

## Catatan (Notes) CRUD Functions

### add_catatan
```python
catatan_id = add_catatan(user_id, beasiswa_id, content)
```
**Parameters:**
- `user_id` (int): User ID
- `beasiswa_id` (int): Beasiswa ID
- `content` (str): Note content
**Returns:** `int` - Catatan ID

### get_catatan
```python
catatan = get_catatan(user_id, beasiswa_id)
```
**Returns:** `dict` - Single note record
**Returns:** `None` if not found

### edit_catatan
```python
updated = edit_catatan(user_id, beasiswa_id, content)
```
**Returns:** `bool` - True if successful

### delete_catatan
```python
deleted = delete_catatan(user_id, beasiswa_id)
```

### get_catatan_list
```python
catatan_list = get_catatan_list(user_id)
```
**Returns:** `list[dict]` - All notes for user

---

## Database Management Functions

### init_db
```python
init_db()
```
**Purpose:** Initialize database schema (6 tables) if not already exists
**Note:** Called automatically on first import via DatabaseManager

### get_connection
```python
conn = get_connection()
```
**Returns:** `sqlite3.Connection` - Database connection via DatabaseManager singleton

---

## Error Handling

```python
from sqlite3 import IntegrityError, Error

try:
    register_user('john', 'john@example.com', 'password123', 'John Doe', 'S1')
except IntegrityError as e:
    print(f"User already exists: {e}")
except Error as e:
    print(f"Database error: {e}")
```

---

## Usage Examples

### Complete User Workflow

```python
from src.database.crud import *

# 1. Register user
user_id = register_user(
    'darva_user',
    'darva@example.com',
    'securepassword',
    'Darva Pratama',
    'S1'
)

# 2. Login user
logged_in_id = login_user('darva_user', 'securepassword')
assert logged_in_id == user_id

# 3. Search beasiswa
scholarships = search_beasiswa(jenjang='S1', status='Buka')

# 4. Add to favorites
for beasiswa in scholarships[:3]:
    add_favorit(user_id, beasiswa['id'])

# 5. Apply to scholarship
lamaran_id = add_lamaran(user_id, scholarships[0]['id'])

# 6. Add notes
add_catatan(
    user_id,
    scholarships[0]['id'],
    'Perlu dokumen SPI dan transkrip nilai'
)

# 7. View favorites with details
my_favorites = get_favorit_list(user_id)
for fav in my_favorites:
    print(f"{fav['judul']} - IPK Min: {fav['minimal_ipk']}")

# 8. Get user's applications
my_applications = get_lamaran_list(user_id)
print(f"Total applications: {len(my_applications)}")

# 9. View notes
notes = get_catatan_list(user_id)
for note in notes:
    print(f"Note on {note['beasiswa_id']}: {note['content']}")
```

---

## Database Transactions

For multi-step operations requiring atomicity:

```python
from src.core.database import DatabaseManager

db = DatabaseManager()
conn = db.get_connection()

try:
    cursor = conn.cursor()
    # Perform multiple operations
    cursor.execute("INSERT INTO favorit ...")
    cursor.execute("UPDATE beasiswa SET ...")
    cursor.execute("INSERT INTO lamaran ...")
    conn.commit()
except Exception as e:
    conn.rollback()
    raise
finally:
    cursor.close()
```

---

## Return Value Formats

### Dict Records
```python
{
    'id': 1,
    'username': 'darva_user',
    'email': 'darva@example.com',
    'nama_lengkap': 'Darva Pratama',
    'jenjang': 'S1',
    'created_at': '2026-04-11 14:15:53',
    'updated_at': '2026-04-11 14:15:53'
}
```

### List Returns
```python
[
    {'id': 1, 'judul': 'Beasiswa A', ...},
    {'id': 2, 'judul': 'Beasiswa B', ...},
    {'id': 3, 'judul': 'Beasiswa C', ...}
]
```

---

## Performance Tips

1. **Use search_beasiswa()** for filtered queries instead of get_all_beasiswa()
2. **Cache frequently accessed data** (Config values, team structure)
3. **Batch operations** when possible (add multiple records)
4. **Use indexes** for frequently searched columns
5. **Connection pooling** via DatabaseManager singleton (prevents recreating connections)
