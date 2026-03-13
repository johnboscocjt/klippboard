# 📋 KlippBoard v1.0.0

**A modern, ultra-fast clipboard manager for Linux with global hotkeys, line numbers, date filtering, and a beautiful dark theme.**

> Made with ❤️ by [johnboscocjt](https://github.com/johnboscocjt/)

[![Python 3.7+](https://img.shields.io/badge/Python-3.7%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Key Features

### 📋 Complete Clipboard Management
- Real-time clipboard monitoring
- 100-item history (configurable)
- Persistent JSON storage
- Fast search and filtering
- 5-tab interface for organization

### ⚡ Quick Actions
- **📋 Copy** - One-click copy to clipboard
- **👁️ View** - Open in editor with line numbers
- **🗑️ Delete** - Remove items
- **⭐ Star** - Toggle favorites (★ filled / ☆ empty)

### 📑 Organized Tabs
- **📋 All Items** - Complete history with search
- **⭐ Favorites** - Protected starred items
- **📍 Today** - Today's items only
- **🗓 Calendar** - Pick any date with collapsible calendar
- **❓ Help** - Built-in documentation

### 🎨 Modern Interface
- Dark theme (easy on eyes)
- Glass morphism design
- Smooth animations
- Line numbers in editor
- Character & line count display

### ⌨️ Global Hotkey
- Default: `Ctrl+Alt+V`
- Fully configurable
- Launch from anywhere

### 🔐 Privacy First
- 100% local (no cloud)
- No tracking/telemetry
- Open source (MIT License)
- Your data, your control

## 🚀 Quick Start

### Installation

```bash
git clone https://github.com/johnboscocjt/klippboard.git
cd klippboard
bash install.sh
klippboard
```

### Manual Run

```bash
python3 src/clipboard_manager.py
```

## 📋 How to Use

### Select & Manage Items
- Click checkbox to select items
- **☑ Select All** - Select everything
- **📋 Copy** - Copy selected items
- **⭐ Star** - Star selected items
- **🗑️ Delete** - Delete selected items
- **⚠️ Clear All** - Delete all (double confirmation)

### View & Edit
- Click **👁️** to open editor
- View line numbers on left
- See character & line count
- Fullscreen toggle available
- Save changes back to history

### Search & Filter
- Search in All Items tab
- Search in selected date
- Live filtering
- Case-insensitive

### Calendar Features
- Collapsible calendar on left
- Click dates to view items
- Search within selected date
- Large viewing area

## ⚙️ Configuration

### Set Global Hotkey
1. Click ⚙ button
2. Enter your hotkey (e.g., `super+v`)
3. Click OK - saved automatically

### Common Examples
- `ctrl+alt+v` - Default
- `super+v` - Windows/Super key
- `shift+alt+v` - Shift+Alt combo

## 🛠️ Technical Specs

- **Language**: Python 3.7+
- **Framework**: PyQt5
- **Dependencies**: PyQt5, keyboard (optional)
- **Memory**: ~50-70MB
- **Startup**: <2 seconds
- **License**: MIT

## 📦 Files

- `src/clipboard_manager.py` - Main application
- `install.sh` - Automatic installer
- `docs/INSTALLATION.md` - Setup guide
- `docs/PRIVACY.md` - Privacy policy
- `README.md` - This file
- `LICENSE` - MIT License

## 🔐 Privacy

✅ **100% Local** - All data stored locally in `~/.clipboard_history.json`
✅ **No Cloud** - Never connects to internet
✅ **No Tracking** - Zero telemetry
✅ **Open Source** - Full source code available
✅ **MIT License** - Free to use and modify

See [PRIVACY.md](docs/PRIVACY.md) for details.

## 🐛 Troubleshooting

### Global hotkey not working
```bash
sudo python3 src/clipboard_manager.py
```

### ModuleNotFoundError: No module named 'PyQt5'
```bash
pip install PyQt5 keyboard
```

### More help
- Check [INSTALLATION.md](docs/INSTALLATION.md)
- Read [PRIVACY.md](docs/PRIVACY.md)
- See ❓ Help tab in app

## 📄 License

MIT License - See [LICENSE](LICENSE)

## 👤 Author

**johnboscocjt** - [GitHub](https://github.com/johnboscocjt/)

---

**Enjoy managing your clipboard with style!** 🚀
