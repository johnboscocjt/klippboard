# KlippBoard Features

**Version:** 1.0.0  
**Platform:** Linux · Python 3.7+ · PyQt5

A calm, local clipboard manager with env-file sync. Everything you copy stays on your machine.

---

## Clipboard Management

- **Real-time capture** — every copy is saved automatically and silently
- **100-item history** — newest first; older items roll off automatically
- **Persistent storage** — saved to `~/.clipboard_history.json`
- **Live search** — filter the All tab instantly (case-insensitive)
- **Favorites** — star clips you reuse often; they stay in the Favorites tab
- **Today tab** — see only what you copied today
- **Calendar browse** — pick any date and filter that day's clips
- **Select & bulk copy** — checkbox items, Select All, then Copy Selected
- **Export** — save the full history to a timestamped `.txt` in your home folder
- **Clear All** — wipe history with double confirmation (cannot be undone)

## Per-item Actions

Each clipboard card includes:

| Action | What it does |
|--------|----------------|
| **Copy** | Puts the clip back on the clipboard (quiet toast confirmation) |
| **View** | Opens the full editor with line numbers |
| **☆ / ★** | Toggle favorite |
| **✕** | Delete this item (asks first) |
| **Checkbox** | Select for bulk actions |

## Viewer / Editor

- Line numbers on the left
- Live character and line count
- Save edits back into history
- Copy All without leaving the editor
- Clean dark document surface

## Env Manager

Open with the **Env** button in the header:

- Create, view, edit, copy, and delete `.env` files
- Optional private GitHub sync (Set Repo → Push / Pull)
- Files stored locally in `~/.klippboard_env/`
- Metadata in `~/.klippboard_env_config.json`

## Interface

- Dark-minimal graphite / indigo theme
- Compact clipboard cards with preview + metadata
- Quiet toast feedback for routine actions (no popup spam)
- High-contrast buttons in system dialogs (OK / Cancel readable)
- Empty states for history, favorites, today, date, and search misses
- Pixel scrolling with no unwanted horizontal scrollbars
- Help tab with full in-app documentation

## Tabs

| Tab | Purpose |
|-----|---------|
| **All** | Full history + search |
| **Favorites** | Starred clips only |
| **Today** | Today's items |
| **Calendar** | Browse by date |
| **Help** | Built-in docs |

## Launch & Tray

- Launch from Applications menu or `klippboard` in a terminal
- Set your own keyboard shortcut in desktop Settings (see [INSTALLATION.md](INSTALLATION.md))
- Double-click tray icon — show / hide
- Right-click tray — Show or Quit
- Closing the window minimizes to tray (keeps capturing)
- Quit only from the tray menu

## Privacy

- 100% local — no cloud, no telemetry
- History: `~/.clipboard_history.json`
- Settings: `~/.klippboard_config.json`
- Env files: `~/.klippboard_env/`
- Nothing leaves your machine unless you push env files yourself

## Install & Uninstall

```bash
# Install
git clone https://github.com/johnboscocjt/klippboard.git
cd klippboard
bash install.sh
klippboard
```

The installer sets up:

- Python virtualenv + dependencies
- Global `klippboard` command
- App icon (`klippboard.png`) for window, tray, and Applications menu
- Desktop launcher with the KlippBoard icon

```bash
# Uninstall (keep your data)
bash uninstall.sh

# Uninstall and delete history + env files
bash uninstall.sh --purge
```

See [INSTALLATION.md](INSTALLATION.md) and [UNINSTALL.md](UNINSTALL.md) for details.

## Technical Specs

| | |
|--|--|
| Language | Python 3.7+ |
| Framework | PyQt5 |
| Dependencies | PyQt5 |
| Memory | ~50–70 MB |
| Startup | &lt; 2 seconds |
| License | MIT |

## Project Files

```
klippboard/
├── clipboard_manager.py   # Main application
├── klippboard.png         # App / launcher / tray icon
├── install.sh             # Installer
├── uninstall.sh           # Uninstaller (--purge for data wipe)
├── README.md
├── FEATURES.md            # This file
├── INSTALLATION.md
├── UNINSTALL.md
├── PRIVACY.md
├── CHANGELOG.md
└── LICENSE
```

---

Made by [johnboscocjt](https://github.com/johnboscocjt/klippboard) · MIT License
