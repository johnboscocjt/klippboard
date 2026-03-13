# 🗑️ Uninstall Guide

## Complete Removal

### Step 1: Remove Global Command

```bash
sudo rm /usr/local/bin/klippboard
```

### Step 2: Remove Alias (if added)

Remove from `~/.bashrc`:
```bash
nano ~/.bashrc
```

Find and delete this line:
```bash
alias klippboard='/usr/local/bin/klippboard'
```

Then reload:
```bash
source ~/.bashrc
```

### Step 3: Remove Virtual Environment

```bash
rm -rf ~/clipboard_env
```

### Step 4: Remove Application

```bash
rm ~/clipboard_manager.py
```

### Step 5: Remove Desktop Shortcut

```bash
rm ~/.local/share/applications/klippboard.desktop
```

### Step 6: Remove Autostart (if enabled)

```bash
rm ~/.config/autostart/klippboard.desktop
```

### Step 7: Remove Systemd Service (if enabled)

```bash
systemctl --user disable klippboard.service
rm ~/.config/systemd/user/klippboard.service
```

## Keep Data (Optional)

Your clipboard history is stored in:
```
~/.clipboard_history.json
~/.klippboard_config.json
```

### Keep Data for Reinstall
If you want to reinstall later and keep your history:
```bash
# Do NOT delete these files
```

### Delete All Data
```bash
rm ~/.clipboard_history.json
rm ~/.klippboard_config.json
```

## Verify Removal

Check that everything is gone:

```bash
which klippboard
# Should show: command not found
```

```bash
ls -la ~/clipboard_manager.py
# Should show: No such file
```

```bash
ls -la /usr/local/bin/klippboard
# Should show: No such file
```

## Need Help?

If you have issues removing KlippBoard, check:
- [INSTALLATION.md](INSTALLATION.md) for troubleshooting
- [README.md](../README.md) for more info

---

Made with ❤️ by [johnboscocjt](https://github.com/johnboscocjt/klippboard)
