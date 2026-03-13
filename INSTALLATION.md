# 📦 Installation Guide (2026)

## ⚡ Quick Install (Recommended)

```bash
git clone https://github.com/johnboscocjt/klippboard.git
cd klippboard
bash install.sh
klippboard
```

The installer will:
- ✅ Create Python virtual environment
- ✅ Install dependencies (PyQt5, keyboard)
- ✅ Add global command `/usr/local/bin/klippboard`
- ✅ Create desktop shortcut
- ✅ Setup keyboard shortcut (Ctrl+Alt+V)

## 🌐 Global Command Detection

After installation, KlippBoard is available globally:

```bash
# From anywhere, launch with:
klippboard

# Or use Applications menu: KlippBoard
```

The installer creates a global wrapper script at `/usr/local/bin/klippboard` that is accessible from any terminal.

## ⌨️ Keyboard Shortcut Setup

### Default Hotkey: Ctrl+Alt+V

Launch KlippBoard with the global hotkey (Ctrl+Alt+V)

### Change Hotkey

1. Launch KlippBoard: `klippboard`
2. Click ⚙ button in header
3. Enter new hotkey (examples: `super+v`, `ctrl+alt+c`, `shift+alt+v`)
4. Click OK - saved automatically
5. May need `sudo` for system-level access

## Manual Installation

### 1. Install Python 3.7+

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

**Fedora/RHEL:**
```bash
sudo dnf install python3 python3-pip
```

**Arch:**
```bash
sudo pacman -S python
```

### 2. Create Virtual Environment

```bash
python3 -m venv ~/clipboard_env
source ~/clipboard_env/bin/activate
```

### 3. Install Dependencies

```bash
pip install PyQt5 keyboard
```

### 4. Copy Application

```bash
git clone https://github.com/johnboscocjt/klippboard.git
cp klippboard/src/clipboard_manager.py ~/clipboard_manager.py
chmod +x ~/clipboard_manager.py
```

### 5. Create Global Command (Optional)

```bash
sudo tee /usr/local/bin/klippboard > /dev/null << 'EOF'
#!/bin/bash
source ~/clipboard_env/bin/activate
python3 ~/clipboard_manager.py
EOF
sudo chmod +x /usr/local/bin/klippboard
```

Now you can launch from anywhere:
```bash
klippboard
```

### 6. Setup Keyboard Shortcut (Optional)

Add to `~/.bashrc` or use the ⚙ button in the app.

## 🐛 Troubleshooting

### "command not found: klippboard"
```bash
source ~/.bashrc
# Or check if global command exists:
which klippboard
```

### Global hotkey not working
```bash
# Try running with sudo:
sudo klippboard
```

### "ModuleNotFoundError: No module named 'PyQt5'"
```bash
source ~/clipboard_env/bin/activate
pip install PyQt5
```

## ✅ Verify Installation

Check that global command is available:
```bash
which klippboard
# Should show: /usr/local/bin/klippboard

# Test launching:
klippboard
```

## 🗑️ Uninstall

See [UNINSTALL.md](../docs/UNINSTALL.md) for complete removal instructions.

---

For more help, see README.md and PRIVACY.md

Copyright © 2026
