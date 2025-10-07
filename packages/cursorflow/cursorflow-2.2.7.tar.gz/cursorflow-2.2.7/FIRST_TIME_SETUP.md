# CursorFlow First-Time Setup

## 🎯 The Two-Step Installation Process

CursorFlow requires **two separate installations**:

### 1️⃣ Package Installation (Global)
This installs the CursorFlow Python package and CLI tool into your Python environment:

```bash
pip install cursorflow
playwright install chromium
```

**What this gives you:**
- `cursorflow` command-line tool
- Python API for programmatic usage
- Core testing engine

### 2️⃣ Project Initialization (Per-Project)
This sets up CursorFlow in your specific project:

```bash
cd /path/to/your/project
cursorflow install-rules

# Or for automation/CI (skip prompts)
cursorflow install-rules --yes
```

**What this creates:**
- `.cursor/rules/` - Cursor AI integration rules (tells Cursor how to use CursorFlow)
- `.cursorflow/config.json` - Project-specific settings (base URL, log paths, etc.)
- `.cursorflow/` - Artifacts directory (screenshots, sessions, test results)
- `.gitignore` entries - Excludes entire `.cursorflow/` directory from version control

## 🤔 Why Two Steps?

**Think of it like Git:**
- `pip install cursorflow` = Installing the git CLI globally
- `cursorflow install-rules` = Running `git init` in each project

Each project needs its own CursorFlow configuration because:
- Different base URLs (localhost:3000 vs localhost:8000)
- Different log paths (Django logs vs React logs)
- Different authentication setups
- Different Cursor AI rules location per project

## 🚀 Auto-Initialization

If you forget step 2, CursorFlow will detect it and offer to initialize automatically:

```bash
$ cursorflow test --base-url http://localhost:3000

⚠️  CursorFlow not initialized in this project
This is a one-time setup that creates:
  • .cursor/rules/ (Cursor AI integration)
  • cursorflow-config.json (project configuration)
  • .cursorflow/ (artifacts directory)

🚀 Initialize CursorFlow now? [Y/n]: y

✅ CursorFlow is ready to use!
```

## 📋 What Happens During Project Initialization?

### 1. Cursor AI Integration (`.cursor/rules/`)
Copies usage rules that teach Cursor AI how to use CursorFlow:
- `cursorflow-usage.mdc` - How to run tests and analyze results
- `cursorflow-installation.mdc` - Installation and setup guidance

### 2. Configuration File (`.cursorflow/config.json`)
Auto-detects your project type and creates smart defaults:

```json
{
  "base_url": "http://localhost:3000",
  "logs": {
    "source": "local",
    "paths": ["logs/app.log"]
  },
  "auth": {
    "method": "form",
    "username_selector": "#username",
    "password_selector": "#password",
    "submit_selector": "#login-button",
    "session_storage": ".cursorflow/sessions/"
  },
  "browser": {
    "headless": true,
    "debug_mode": false
  },
  "_project_type": "react",
  "_cursorflow_version": "2.1.5"
}
```

### 3. Project Structure
```
your-project/
├── .cursor/
│   └── rules/
│       ├── cursorflow-usage.mdc
│       └── cursorflow-installation.mdc
├── .cursorflow/
│   ├── config.json
│   ├── artifacts/
│   ├── sessions/
│   └── version_info.json
└── .gitignore (updated with CursorFlow entries)
```

## 🎪 Common Scenarios

### New Team Member Setup
```bash
# They need both steps:
pip install cursorflow
playwright install chromium
cd /path/to/existing/project
# No need to run install-rules - config already exists!
```

### New Project
```bash
# Full setup:
pip install cursorflow
playwright install chromium
cd /path/to/new/project
cursorflow install-rules
```

### Multiple Projects
```bash
# Install once globally:
pip install cursorflow
playwright install chromium

# Initialize each project:
cd ~/projects/project-a && cursorflow install-rules
cd ~/projects/project-b && cursorflow install-rules
cd ~/projects/project-c && cursorflow install-rules
```

## 🔍 Verifying Setup

### Check Package Installation
```bash
cursorflow --version
# Should output: cursorflow, version 2.1.5
```

### Check Project Initialization
```bash
# From project directory:
ls -la .cursor/rules/
# Should show: cursorflow-usage.mdc, cursorflow-installation.mdc

ls -la .cursorflow/config.json
# Should exist

ls -la .cursorflow/
# Should exist
```

## 🚨 Troubleshooting

### "Command not found: cursorflow"
**Problem:** Package not installed  
**Solution:** `pip install cursorflow`

### "CursorFlow not initialized in this project"
**Problem:** Project not initialized  
**Solution:** `cursorflow install-rules`

### "Cursor doesn't know about CursorFlow"
**Problem:** Rules not installed in project  
**Solution:** `cursorflow install-rules` (creates `.cursor/rules/`)

### "pip install worked but CursorFlow doesn't work"
**Problem:** Missing step 2  
**Solution:** Run `cursorflow install-rules` in your project

## 💡 Pro Tips

1. **Add to your project README:**
   ```markdown
   ## Development Setup
   ```bash
   pip install -r requirements.txt
   cursorflow install-rules  # One-time CursorFlow setup
   npm install
   ```
   ```

2. **Add to onboarding checklist:**
   - [ ] Clone repository
   - [ ] Install dependencies
   - [ ] **Run `cursorflow install-rules`** ← Don't forget!
   - [ ] Run tests

3. **Version control:**
   - ❌ Don't commit `.cursorflow/` (config, artifacts, all per-developer)
   - ✅ Commit `.cursor/rules/` (Cursor AI integration)
   - 💡 Each dev runs `cursorflow install-rules` to create their own config

## 🎯 Remember

**Package Installation = Global tool**  
**Project Initialization = Per-project setup**

Just like `npm install -g typescript` vs `tsc --init`! 🚀

