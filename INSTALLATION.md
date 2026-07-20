# Installation Guide

## Quick Install (Recommended)

```bash
git clone https://github.com/johnboscocjt/klippboard.git
cd klippboard
bash install.sh
klippboard
```

The installer will:
- Create a Python virtual environment
- Install dependencies (PyQt5)
- Add the `klippboard` command at `/usr/local/bin/klippboard`
- Install the app icon to `~/.local/share/icons/klippboard.png`
- Create an Applications-menu launcher (with icon)

After install you can launch from:
- Terminal: `klippboard`
- Applications menu: **KlippBoard**

---

## Set a Keyboard Shortcut (Manual)

KlippBoard does **not** install its own system-wide hotkey.  
Add a shortcut yourself in your desktop settings so a key combo launches `klippboard`.

### GNOME (Ubuntu, Fedora Workstation, Pop!_OS, …)

1. Open **Settings → Keyboard → View and Customize Shortcuts**
2. Scroll to **Custom Shortcuts** → click **+**
3. Fill in:
   - **Name:** `KlippBoard`
   - **Command:** `klippboard`
   - **Shortcut:** press your preferred keys (e.g. `Ctrl+Alt+V`)
4. Click **Add**

### KDE Plasma

1. Open **System Settings → Shortcuts → Custom Shortcuts**
2. **Edit → New → Global Shortcut → Command/URL**
3. Name it `KlippBoard`
4. Under **Trigger**, set your key combo
5. Under **Action**, set Command to `klippboard`
6. Apply

### XFCE

1. Open **Settings → Keyboard → Application Shortcuts**
2. Click **Add**
3. Command: `klippboard`
4. Press the keys you want when prompted

### Cinnamon / MATE / Budgie

Use **Keyboard → Shortcuts → Custom** (wording varies slightly) and add a shortcut that runs `klippboard`.

Tip: pick a combo that is not already used by your desktop (e.g. `Ctrl+Alt+V` or `Super+V`).

---

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
pip install PyQt5
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

### 5. Create the `klippboard` Command (Optional)

```bash
sudo tee /usr/local/bin/klippboard > /dev/null << 'EOF'
#!/bin/bash
source ~/clipboard_env/bin/activate
python3 ~/clipboard_manager.py
EOF
sudo chmod +x /usr/local/bin/klippboard
```

Then launch with:
```bash
klippboard
```

### 6. Create the Applications Launcher (Optional)

```bash
mkdir -p ~/.local/share/applications
cat > ~/.local/share/applications/klippboard.desktop << DESKTOP
[Desktop Entry]
Type=Application
Version=1.0.0
Name=KlippBoard
Comment=Modern, local clipboard manager for Linux
Exec=/usr/local/bin/klippboard
Icon=$HOME/.local/share/icons/klippboard.png
Terminal=false
Categories=Utility;Accessories;
StartupWMClass=KlippBoard
DESKTOP
update-desktop-database ~/.local/share/applications 2>/dev/null || true
```

Then set a keyboard shortcut as described above.

---

## Troubleshooting

### `command not found: klippboard`

```bash
source ~/.bashrc
which klippboard
# Should show: /usr/local/bin/klippboard
```

If it is missing, re-run `bash install.sh` from the repo folder.

### Shortcut does nothing

- Confirm `klippboard` works from a terminal first
- Make sure the custom shortcut Command is exactly `klippboard` (or `/usr/local/bin/klippboard`)
- Check that the key combo is not already taken by another app

## Verify Installation

```bash
which klippboard
# /usr/local/bin/klippboard

klippboard
```

## Uninstall

```bash
bash uninstall.sh          # keep your data
bash uninstall.sh --purge  # also delete history + env files
```

See [UNINSTALL.md](UNINSTALL.md) for full manual removal steps.

---

For more help, see [README.md](README.md) and [PRIVACY.md](PRIVACY.md)
