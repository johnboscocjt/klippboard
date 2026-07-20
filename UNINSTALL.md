# 🗑️ Uninstall Guide

## Quick Uninstall (Recommended)

From the cloned repo folder:

```bash
bash uninstall.sh
```

This removes the app, global command, virtual environment, desktop launcher
and icon — but **keeps your clipboard history and env files**.

To also delete all saved data:

```bash
bash uninstall.sh --purge
```

---

## Manual Removal

### Step 1: Remove Global Command

```bash
sudo rm -f /usr/local/bin/klippboard
```

### Step 2: Remove Alias (if added)

Remove the KlippBoard lines from `~/.bashrc`:

```bash
sed -i '/# KlippBoard/d;/alias klippboard=/d' ~/.bashrc
source ~/.bashrc
```

### Step 3: Remove Virtual Environment

```bash
rm -rf ~/clipboard_env
```

### Step 4: Remove Application

```bash
rm -f ~/clipboard_manager.py
rm -f ~/klippboard.png
```

### Step 5: Remove Desktop Launcher & Icon

```bash
rm -f ~/.local/share/applications/klippboard.desktop
rm -f ~/.local/share/icons/klippboard.png
update-desktop-database ~/.local/share/applications 2>/dev/null || true
gtk-update-icon-cache ~/.local/share/icons 2>/dev/null || true
```

### Step 6: Remove Autostart (if enabled)

```bash
rm -f ~/.config/autostart/klippboard.desktop
```

## Your Data

Clipboard history and env files are stored in:

```
~/.clipboard_history.json        # clipboard history
~/.klippboard_config.json        # app settings
~/.klippboard_env_config.json    # env manager settings
~/.klippboard_env/               # your saved env files
```

### Keep Data for Reinstall
Leave the files above in place — they will be picked up automatically next time.

### Delete All Data
```bash
rm -f ~/.clipboard_history.json ~/.klippboard_config.json ~/.klippboard_env_config.json
rm -rf ~/.klippboard_env
```

## Verify Removal

```bash
which klippboard                 # should print nothing / "not found"
ls ~/clipboard_manager.py        # should show: No such file
ls /usr/local/bin/klippboard     # should show: No such file
```

## Need Help?

- [INSTALLATION.md](INSTALLATION.md) for setup and troubleshooting
- [README.md](README.md) for more info

---

Made with love by [johnboscocjt](https://github.com/johnboscocjt/klippboard)
