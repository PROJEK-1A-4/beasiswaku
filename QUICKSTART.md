# 🚀 BeasiswaKu - Quick Start Guide

Selamat datang di **BeasiswaKu** — Personal Scholarship Manager untuk mahasiswa Indonesia!

**Estimasi waktu setup:** 15 menit

---

## 🎯 Quick Start (3 Steps)

### Step 1: Clone & Setup Environment

**Linux / macOS:**
```bash
git clone https://github.com/[your-org]/beasiswaku.git
cd beasiswaku
chmod +x setup.sh
./setup.sh
```

**Windows:**
```bash
git clone https://github.com/[your-org]/beasiswa.git
cd beasiswaku
setup.bat
```

**Manual setup** (if script doesn't work):
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "from crud import init_db; init_db()"

# Verify installation
ls database/beasiswaku.db
```

### Step 2: Open in VS Code

```bash
code .
```

VS Code akan otomatis load `copilot-instructions.md` (workspace guidelines).

### Step 3: Personalize Copilot (Optional but Recommended)

Copy your personal prompt file ke VS Code User Prompts folder:

**Linux/macOS:**
```bash
mkdir -p ~/.config/Code/User/prompts
cp .github/prompts/[yourname].prompt.md ~/.config/Code/User/prompts/
```

**Windows:**
```cmd
copy .github\prompts\[yourname].prompt.md %APPDATA%\Code\User\prompts\
```

**Pilih file sesuai role Anda:**
- **Darva** → `.github/prompts/darva.prompt.md`
- **Kyla** → `.github/prompts/kyla.prompt.md`
- **Aulia** → `.github/prompts/aulia.prompt.md`
- **Kemal** → `.github/prompts/kemal.prompt.md`
- **Richard** → `.github/prompts/richard.prompt.md`

Restart VS Code setelah copy. Copilot akan auto-load file Anda!

---

## 📚 Full Documentation

Setelah setup, baca:

1. **[ONBOARDING.md](ONBOARDING.md)** — Detailed setup & troubleshooting
2. **[copilot-instructions.md](copilot-instructions.md)** — Team guidelines & coding standards (Section 0 = your tasks)
3. **[blueprint_beasiswaku.md](blueprint_beasiswaku.md)** — Project specifications

---

## 🎓 What to Do Next?

### For First-Time Setup:
```
1. Read ONBOARDING.md (15 min)
2. Open VS Code
3. Ask Copilot: "Saya sudah setup. Apa task FASE 1?"
```

### Based on Your Role:

**Darva** (Database):
```
"Darva: Read copilot-instructions.md Section 0. 
Apa task pertama saya? Mulai dari mana?"
```

**Kyla** (UI):
```
"Kyla: Read copilot-instructions.md Section 0.
Saya siap mulai Tab Beasiswa? Apa prerequisitenya?"
```

**Aulia** (Charts):
```
"Aulia: Read copilot-instructions.md Section 0.
Tab Statistik blocked, tapi apa yang bisa saya kerjakan sekarang?"
```

**Kemal** (Scraper):
```
"Kemal: Read copilot-instructions.md Section 0.
Saya mulai scraper sekarang? Apa blockernya?"
```

**Richard** (Advanced):
```
"Richard: Read copilot-instructions.md Section 0.
Saya bisa mulai research trend charts sekarang?"
```

---

## 🔧 Troubleshooting

### Python not found
```bash
# Linux/macOS: Use python3 instead
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt

# Windows: Make sure Python is in PATH
python --version
```

### venv activation fails
**Linux/macOS:**
```bash
source venv/bin/activate
```

**Windows (PowerShell):**
```powershell
venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
venv\Scripts\activate.bat
```

### Database not found
```bash
python -c "from crud import init_db; init_db()"
ls database/beasiswaku.db  # Check if created
```

### Copilot doesn't recognize role
1. Verify `.github/prompts/[yourname].prompt.md` exists
2. Verify copied to `~/.config/Code/User/prompts/[yourname].prompt.md`
3. Restart VS Code (Ctrl+Shift+P → Developer: Reload Window)

---

## 📋 Directory Structure

```
beasiswaku/
├── main.py                           # App entry point
├── crud.py                           # Database CRUD operations
├── gui_beasiswa.py                   # Beasiswa Tab UI
├── scraper.py                        # Web scraping logic
├── visualisasi.py                    # Charts & visualization
│
├── database/
│   └── beasiswaku.db                # SQLite database (auto-created)
├── backup/                           # Backup files
│   ├── beasiswa.json
│   ├── penyelenggara.json
│   └── riwayat_lamaran.json
├── assets/                           # Icons, images
│
├── setup.sh / setup.bat              # Automated setup script
├── ONBOARDING.md                     # Detailed onboarding guide
├── copilot-instructions.md           # Team guidelines (READ THIS!)
├── blueprint_beasiswaku.md           # Project specifications
├── requirements.txt                  # Python dependencies
│
└── .github/
    ├── prompts/
    │   ├── darva.prompt.md
    │   ├── kyla.prompt.md
    │   ├── aulia.prompt.md
    │   ├── kemal.prompt.md
    │   └── richard.prompt.md
    └── instructions/                 # (Optional personalized instructions)
```

---

## ⚡ Common Commands

```bash
# Activate virtual environment
source venv/bin/activate             # Linux/macOS
venv\Scripts\activate                # Windows

# Run application
python main.py

# Run tests (if available)
python -m pytest                     # (After setup)

# Reset database
rm database/beasiswaku.db
python -c "from crud import init_db; init_db()"

# Git workflow
git checkout -b feature/[task-name]-[yourname]
git add .
git commit -m "[INITIALS] type: description"
git push origin feature/[task-name]-[yourname]

# Review copilot instructions
cat copilot-instructions.md | grep "Section 0"   # See team assignments
```

---

## 🎯 First Meaningful Task

After setup:

1. **Open VS Code**
   ```bash
   code .
   ```

2. **Open Copilot Chat** (Ctrl+Shift+I)

3. **Ask based on your role:**

   **Darva:**
   ```
   "Darva: Buatkan init_db() function untuk initialize database beasiswa.
   Gunakan blueprint Section 6.2"
   ```

   **Kyla:**
   ```
   "Kyla: Cek FASE 2 prerequisite. Saya ready mulai Tab Beasiswa?"
   ```

   **Aulia:**
   ```
   "Aulia: Saya bisa mulai prep visualization.py sekarang?"
   ```

   **Kemal:**
   ```
   "Kemal: Buatkan scraper untuk website beasiswa"
   ```

   **Richard:**
   ```
   "Richard: Research trend charts untuk lamaran. Design mockup?"
   ```

---

## 📞 Need Help?

- 📖 **Documentation:** See ONBOARDING.md and copilot-instructions.md
- 💬 **Ask Copilot:** Copilot has team guidelines built-in
- 👥 **Team Chat:** Escalate blockers to group chat
- 🐛 **Bug/Issue:** Create GitHub issue with clear description

---

## ✅ Setup Verified Checklist

- [ ] Python 3.8+ installed
- [ ] Virtual environment created & activated
- [ ] Dependencies installed (`pip list` shows tkinter, bcrypt, requests, etc)
- [ ] Database created (`database/beasiswaku.db` exists)
- [ ] VS Code opened with project folder
- [ ] Copilot prompt copied (optional but recommended)
- [ ] Read ONBOARDING.md
- [ ] Read copilot-instructions.md Section 0 (team assignments)

---

## 🚀 Ready to Start?

Ask Copilot your first task! It's ready to help. 💪

Good luck with the project! 🎓
