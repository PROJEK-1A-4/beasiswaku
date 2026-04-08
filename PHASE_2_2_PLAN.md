# 📋 PHASE 2.2: CRUD Beasiswa Implementation Plan

## 🎯 Overview
Implement 4 CRUD functions untuk manage beasiswa data di table `beasiswa`

**Status:** 🔴 NOT STARTED  
**Estimated Time:** 30-45 menit (total 4 functions)  
**Workflow:** 1 function per commit (sesuai request user)

---

## 📝 Functions to Implement (Urutan)

### 1️⃣ **add_beasiswa()** ← START HERE
**Input:**
```python
add_beasiswa(
    judul: str,
    jenjang: str,
    deadline: str,
    penyelenggara_id: int = None,
    deskripsi: str = None,
    benefit: str = None,
    persyaratan: str = None,
    minimal_ipk: float = None,
    coverage: str = None,
    status: str = 'Buka',
    link_aplikasi: str = None
)
```

**Output:**
```python
(success: bool, message: str, beasiswa_id: int or None)
```

**Validations:**
- ✓ judul tidak boleh kosong
- ✓ jenjang harus D3/D4/S1/S2
- ✓ deadline format YYYY-MM-DD
- ✓ minimal_ipk antara 0.0 - 4.0 jika ada
- ✓ coverage harus valid value
- ✓ penyelenggara_id harus ada (FK check)

**Error Handling:**
- ✓ Try-catch IntegrityError
- ✓ Logging untuk info & error

---

### 2️⃣ **get_beasiswa_list()**
**Input:**
```python
get_beasiswa_list(
    filter_jenjang: str = None,
    filter_status: str = None,
    search_judul: str = None,
    sort_by: str = 'deadline',
    sort_order: str = 'ASC'
)
```

**Output:**
```python
(beasiswa_list: List[Dict], total_count: int)
```

**Features:**
- ✓ Optional filter by jenjang (D3, D4, S1, S2)
- ✓ Optional filter by status (Buka, Segera Tutup, Tutup)
- ✓ Optional search by judul (LIKE %search%)
- ✓ Optional sort by column (deadline, created_at, dll)
- ✓ Return total count untuk pagination

---

### 3️⃣ **edit_beasiswa()**
**Input:**
```python
edit_beasiswa(
    beasiswa_id: int,
    **kwargs  # judul, jenjang, deadline, benefit, dll
)
```

**Output:**
```python
(success: bool, message: str)
```

**Features:**
- ✓ Update selected fields only (partial update)
- ✓ Validate input sesuai type
- ✓ Update `updated_at` timestamp
- ✓ Check beasiswa exists sebelum update

---

### 4️⃣ **delete_beasiswa()**
**Input:**
```python
delete_beasiswa(beasiswa_id: int)
```

**Output:**
```python
(success: bool, message: str)
```

**Features:**
- ✓ Delete beasiswa by ID
- ✓ Cascade: Delete related records in riwayat_lamaran & favorit
- ✓ Check beasiswa exists sebelum delete
- ✓ Logging untuk audit trail

---

## 🧪 Testing Strategy

### For each function, create minimal test:
```python
# test_phase_2_2.py akan dibuat dengan:
├─ Test add_beasiswa() with valid & invalid data
├─ Test get_beasiswa_list() with filters
├─ Test edit_beasiswa() with various updates
└─ Test delete_beasiswa() with cascade
```

### Test cases per function:
- ✓ Valid input → Success
- ✓ Invalid input → Rejection
- ✓ Edge cases → Proper error handling
- ✓ Data persistence → Verify in DB

---

## 📊 Workflow (Per Function)

```
For each function (add_beasiswa, get_beasiswa_list, edit, delete):

1. CODE
   └─ Add function to crud.py
   └─ Include docstrings
   └─ Include error handling
   └─ Include logging

2. TEST (isolated)
   └─ Create test in test_phase_2_2.py
   └─ Test valid + invalid cases
   └─ Verify data in database
   └─ Run & ensure all pass

3. COMMIT
   └─ git add -A
   └─ git commit -m "feat: implement add_beasiswa() with validation"
   └─ git push

4. UPDATE TODO
   └─ Mark task as completed
   └─ Move to next function
```

---

## 📌 Key Design Decisions

### Error Handling Pattern
```python
try:
    conn = get_connection()
    cursor = conn.cursor()
    # ... business logic ...
    conn.commit()
    return True, "Success message", result
except sqlite3.IntegrityError as e:
    conn.rollback()
    return False, f"Data error: {str(e)}", None
except sqlite3.Error as e:
    conn.rollback()
    return False, f"Database error: {str(e)}", None
finally:
    cursor.close()
    conn.close()
```

### Logging Pattern
```python
logger.info(f"✅ Beasiswa '{judul}' added successfully (ID: {id})")
logger.warning(f"⚠️ Beasiswa '{judul}' add failed: {error}")
```

### Return Pattern
- All functions return `(success: bool, message: str, [optional_data])`
- Consistent error messages
- Data untuk debugging jika perlu

---

## ✅ Checklist Before Starting

- [x] Database schema verified ✅
- [x] Authentication working ✅
- [x] Connection function tested ✅
- [x] Understanding of table structure ✅
- [ ] Ready to code add_beasiswa() 👈 START HERE

---

## 🚀 Next: Start with add_beasiswa()

Mari kita mulai dengan function pertama!

**Durasi:** ~10 menit untuk code + test  
**Output:** crud.py dengan add_beasiswa() function + test yang pass

Lanjut?
