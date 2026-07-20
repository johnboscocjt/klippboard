#!/bin/bash
# KlippBoard Auto-Installer v1.0.0
set -e

echo "📋 Installing KlippBoard v1.0.0..."
echo ""

# Resolve the directory this script lives in (so it works from anywhere)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Locate the application source (supports repo root or src/ layout)
if [ -f "$SCRIPT_DIR/clipboard_manager.py" ]; then
    APP_SRC="$SCRIPT_DIR/clipboard_manager.py"
elif [ -f "$SCRIPT_DIR/src/clipboard_manager.py" ]; then
    APP_SRC="$SCRIPT_DIR/src/clipboard_manager.py"
else
    echo "❌ Could not find clipboard_manager.py next to install.sh"
    exit 1
fi

# Locate the icon
if [ -f "$SCRIPT_DIR/klippboard.png" ]; then
    ICON_SRC="$SCRIPT_DIR/klippboard.png"
elif [ -f "$SCRIPT_DIR/src/klippboard.png" ]; then
    ICON_SRC="$SCRIPT_DIR/src/klippboard.png"
else
    ICON_SRC=""
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv ~/clipboard_env
source ~/clipboard_env/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --quiet PyQt5 2>/dev/null || pip install PyQt5

# Copy app
echo "📄 Copying application..."
cp "$APP_SRC" ~/clipboard_manager.py
chmod +x ~/clipboard_manager.py

# Install icon so the launcher, window, and taskbar can use it
if [ -n "$ICON_SRC" ]; then
    echo "🎨 Installing app icon..."
    mkdir -p "$HOME/.local/share/icons"
    cp "$ICON_SRC" "$HOME/.local/share/icons/klippboard.png"
    # Next to the installed app (runtime lookup)
    cp "$ICON_SRC" ~/klippboard.png

    # Freedesktop hicolor theme — required for reliable taskbar / dock icons
    python3 - "$ICON_SRC" <<'PY'
import os, sys
from PyQt5.QtGui import QImage
from PyQt5.QtCore import Qt

src = sys.argv[1]
img = QImage(src)
home = os.path.expanduser("~")
for size in (16, 24, 32, 48, 64, 128, 256, 512):
    folder = os.path.join(home, ".local/share/icons/hicolor", f"{size}x{size}", "apps")
    os.makedirs(folder, exist_ok=True)
    scaled = img.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    scaled.save(os.path.join(folder, "klippboard.png"), "PNG")
print("hicolor icons installed")
PY
    ICON_NAME="klippboard"
else
    echo "⚠️  Icon file not found; using a fallback icon."
    ICON_NAME="utilities-terminal"
fi

# Create global command wrapper
echo "🌐 Setting up global command..."
sudo tee /usr/local/bin/klippboard > /dev/null << 'EOF'
#!/bin/bash
source ~/clipboard_env/bin/activate
# Ensure Qt can resolve the desktop file / icon association
export XDG_CURRENT_DESKTOP="${XDG_CURRENT_DESKTOP:-}"
exec python3 ~/clipboard_manager.py
EOF
sudo chmod +x /usr/local/bin/klippboard

# Add to bashrc (alias as backup)
if [ -f ~/.bashrc ]; then
    if ! grep -q "alias klippboard" ~/.bashrc; then
        echo "" >> ~/.bashrc
        echo "# KlippBoard" >> ~/.bashrc
        echo "alias klippboard='/usr/local/bin/klippboard'" >> ~/.bashrc
    fi
fi

# Create desktop shortcut with the theme icon name (matches WM class)
echo "🎯 Creating desktop shortcut..."
mkdir -p ~/.local/share/applications
cat > ~/.local/share/applications/klippboard.desktop << DESKTOP
[Desktop Entry]
Type=Application
Version=1.0.0
Name=KlippBoard
GenericName=Clipboard Manager
Comment=Modern, local clipboard manager for Linux
Exec=/usr/local/bin/klippboard
Icon=$ICON_NAME
Terminal=false
Categories=Utility;Accessories;
Keywords=clipboard;manager;history;copy;paste;
StartupNotify=true
StartupWMClass=KlippBoard
DESKTOP
chmod +x ~/.local/share/applications/klippboard.desktop

# Refresh desktop + icon caches so the taskbar picks up the icon
update-desktop-database ~/.local/share/applications 2>/dev/null || true
gtk-update-icon-cache -f -t ~/.local/share/icons/hicolor 2>/dev/null || true
gtk-update-icon-cache -f -t ~/.local/share/icons 2>/dev/null || true
xdg-desktop-menu forceupdate 2>/dev/null || true

echo ""
echo "✅ Installation Complete!"
echo ""
echo "🚀 Launch KlippBoard with:"
echo "   klippboard"
echo ""
echo "Or find 'KlippBoard' in your Applications menu."
echo ""
echo "⌨️  Optional: add a keyboard shortcut"
echo "   Settings → Keyboard → Custom Shortcuts"
echo "   Name: KlippBoard   Command: klippboard"
echo "   See INSTALLATION.md for GNOME / KDE / XFCE steps."
echo ""
echo "Documentation:"
echo "  Help tab inside the app"
echo "  INSTALLATION.md"
echo "  PRIVACY.md"
echo ""
echo "Happy copying!"
