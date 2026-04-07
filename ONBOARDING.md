# 🎓 BeasiswaKu Team Onboarding Guide

Selamat datang di tim BeasiswaKu! 👋

Panduan ini akan memandu Anda setup development environment dan siapkan Copilot untuk role Anda.

**Estimasi waktu:** 15-20 menit

---

## Step 1: Clone Repository & Setup Environment

### 1a. Clone Repository
```bash
git clone https://github.com/[your-repo]/beasiswaku.git
cd beasiswaku
```

### 1b. Create Python Virtual Environment
```bash
# Linux / macOS
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 1c. Install Dependencies
```bash
pip install -r requirements.txt
```

### 1d. Initialize Database
```bash
python -c "from crud import init_db; init_db(); print('✅ Database initialized')"
```

---

## Step 2: Verify Installation

Pastikan semua berhasil:

```bash
# Check Python version (should be 3.8+)
python --version

# Check installed packages
pip list | grep -E "tkinter|bcrypt|requests|beautifulsoup"

# Verify database
ls database/beasiswaku.db && echo "✅ Database exists" || echo "❌ Database not found"

# Test import
python -c "import tkinter, bcrypt, requests; print('✅ All imports OK')"
```

---

## Step 3: Identify Your Role & Setup Copilot

**Pilih peran Anda:**

### Option A: Saya adalah **DARVA** (Database & Authentication)
```bash
# 1. Copy prompt template ke Copilot prompts folder
cp .github/prompts/darva.prompt.md ~/.config/Code/User/prompts/

# 2. Copy personal instructions (optional)
cp .github/instructions/darva.instructions.md ~/.config/Code/User/

# 3. Verify setup
echo "✅ Darva setup complete! Open VS Code dan coba:"
echo "   Prompt: 'Darva: Buatkan CRUD function untuk tambah beasiswa...'"
```

### Option B: Saya adalah **KYLA** (UI/UX - Beasiswa Tab)
```bash
cp .github/prompts/kyla.prompt.md ~/.config/Code/User/prompts/
cp .github/instructions/kyla.instructions.md ~/.config/Code/User/
```

### Option C: Saya adalah **AULIA** (Analytics & Visualization)
```bash
cp .github/prompts/aulia.prompt.md ~/.config/Code/User/prompts/
cp .github/instructions/aulia.instructions.md ~/.config/Code/User/
```

### Option D: Saya adalah **KEMAL** (Scraping & Search)
```bash
cp .github/prompts/kemal.prompt.md ~/.config/Code/User/prompts/
cp .github/instructions/kemal.instructions.md ~/.config/Code/User/
```

### Option E: Saya adalah **RICHARD** (Advanced Analytics)
```bash
cp .github/prompts/richard.prompt.md ~/.config/Code/User/prompts/
cp .github/instructions/richard.instructions.md ~/.config/Code/User/
```

---

## Step 4: Open Project in VS Code

```bash
# Open VS Code di project folder
code .
```

VS Code akan otomatis load:
- ✅ `copilot-instructions.md` (workspace-level, untuk semua orang)
- ✅ Personal prompts dari `~/.config/Code/User/prompts/` (untuk Anda)
- ✅ Personal instructions dari `~/.config/Code/User/` (optional)

---

## Step 5: Verify Copilot Setup

### Test 1: Ask Copilot Team Info
```
"Cek copilot-instructions.md Section 0 — siapa PIC untuk CRUD/database?"
```

**Expected Response:** Copilot akan refer ke Section 0 dan jawab "Darva"

### Test 2: Ask Your First Task
**Contoh untuk Darva:**
```
"Darva: Buatkan init_db() function untuk initialize database schema 
sesuai blueprint Section 6.2"
```

**Expected:** Copilot akan recognize Anda sebagai Darva dan:
- ✅ Refer ke blueprint Section 6.2
- ✅ Suggest database schema
- ✅ Follow code style dari copilot-instructions.md
- ✅ Propose FASE 1 prerequisite tasks

---

## Step 6: First Meaningful Commit

Setelah setup lengkap:

```bash
# Create a personal branch
git checkout -b feature/[task-name]-[yourname]

# Contoh:
git checkout -b feature/init-db-darva

# Make your first task
# ... implement feature ...

# Commit dengan proper format
git add .
git commit -m "[DRV] feat: initialize database schema with init_db() function"

# Push ke branch (jangan push langsung ke main!)
git push origin feature/init-db-darva
```

---

## Step 7: Join Team Communication

### Daily Standup
- **Time:** 9:00 AM setiap weekday
- **Duration:** 15 minutes
- **Format:** Lihat `copilot-instructions.md` Section 15

### PR Review
- Before merging ke `develop`, buat Pull Request
- Request review dari PIC module terkait (lihat Section 0)
- Template sudah ada, ikuti checklist

### Blockers & Issues
- If stuck > 1 hour → Escalate ke group chat
- Format: lihat `copilot-instructions.md` Section 5

---

## Troubleshooting

### Issue: "Python not found"
```bash
# Linux/macOS
which python3
alias python=python3

# Windows: Make sure Python is in PATH
python --version
```

### Issue: "Module not found"
```bash
# Ensure venv is activated
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Reinstall packages
pip install -r requirements.txt
```

### Issue: "Database file not found"
```bash
# Re-initialize
python -c "from crud import init_db; init_db(); print('✅ Done')"
```

### Issue: "Copilot tidak recognize role"
```bash
# 1. Verify workspace-level instructions exist
ls copilot-instructions.md

# 2. Verify personal prompts copied
ls ~/.config/Code/User/prompts/[yourname].prompt.md

# 3. Restart VS Code (Ctrl+Shift+P → Developer: Reload Window)

# 4. Check Copilot Chat sidebar → see if instructions loaded
```

### Issue: "Git branch conflict"
```bash
# Sync dengan latest main
git fetch origin
git rebase origin/main

# Atau set upstream
git branch --set-upstream-to=origin/develop feature/[yourname]-[task]
```

---

## What's Next?

1. ✅ Environment setup complete
2. ✅ Database initialized
3. ✅ Copilot personalized
4. **Next:** Check FASE 1 prerequisites sesuai `copilot-instructions.md` Section 0
   - Lihat "Checklist Prerequisite Sebelum Implement Fitur"
   - Identify task mana yang bisa Anda mulai
   - Ask Copilot: "Saya ([Name]) mau mulai FASE X. Cek prerequisite..."

---

## Quick Reference

| File | Purpose | Location |
|------|---------|----------|
| `copilot-instructions.md` | Team guidelines (untuk semua) | Root |
| `blueprint_beasiswaku.md` | Feature specifications | Root |
| `DEVELOPMENT.md` | Dev environment tips | Root |
| `TESTING.md` | Testing checklist | Root |
| `.github/prompts/[name].prompt.md` | Your personal Copilot prompts | Project folder |
| `requirements.txt` | Python dependencies | Root |
| `database/beasiswaku.db` | SQLite database (auto-created) | project/database/ |
| `venv/` | Python virtual environment | project/venv/ |

---

## Need Help?

1. **Setup issue?** → Check Troubleshooting section above
2. **Don't understand task?** → Ask Copilot: "Explain [task] in Indonesian"
3. **Stuck on code?** → Ask Copilot with your role prefix
4. **Blocked by other task?** → Escalate via group chat or Copilot

---

## Done! ✅

Sekarang Anda ready untuk mulai berkontribusi. Good luck! 🚀

**Next step:** Tanya Copilot tentang FASE 1 prerequisite tasks:
```
"Saya ([Name]) sudah setup environment. 
Apa prerequisites untuk FASE 1? Apa yang harus saya kerjakan duluan?"
```
