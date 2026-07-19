# 📦 Installation Guide (2026)

## ⚡ Quick Install (Recommended)

```bash
git clone https://github.com/johnboscocjt/klippboard.git
cd klippboard
bash install.sh
klippboard
```

The installer will:
- ✅ Create a Python virtual environment
- ✅ Install dependencies (PyQt5, keyboard)
- ✅ Add global command `/usr/local/bin/klippboard`
- ✅ Install the app icon to `~/.local/share/icons/klippboard.png`
- ✅ Create an Applications-menu launcher (with icon) so KlippBoard is easy to start
- ✅ Enable the global hotkey (Ctrl+Alt+V)

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

If the hotkey does not respond, run KlippBoard once with elevated
permissions so it can register the shortcut system-wide:

```bash
sudo klippboard
```

The hotkey is stored in `~/.klippboard_config.json`.

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

### 4. Copy Application & Icon

```bash
git clone https://github.com/johnboscocjt/klippboard.git
cp klippboard/clipboard_manager.py ~/clipboard_manager.py
cp klippboard/klippboard.png ~/klippboard.png
mkdir -p ~/.local/share/icons
cp klippboard/klippboard.png ~/.local/share/icons/klippboard.png
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

### 6. Create the Applications Launcher (Optional)

```bash
mkdir -p ~/.local/share/applications
cat > ~/.local/share/applications/klippboard.desktop << 'DESKTOP'
[Desktop Entry]
Type=Application
Version=1.0.0
Name=KlippBoard
Comment=Modern, local clipboard manager for Linux
Exec=/usr/local/bin/klippboard
Icon=/home/$USER/.local/share/icons/klippboard.png
Terminal=false
Categories=Utility;Accessories;
StartupWMClass=KlippBoard
DESKTOP
update-desktop-database ~/.local/share/applications 2>/dev/null || true
```

KlippBoard will now appear in your Applications menu with its icon.

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

One command from the repo folder:

```bash
bash uninstall.sh          # keep your data
bash uninstall.sh --purge  # also delete history + env files
```

See [UNINSTALL.md](UNINSTALL.md) for full manual removal steps.

---

For more help, see README.md and PRIVACY.md

Copyright © 2026
