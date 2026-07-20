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

# Install icon so the launcher and window can use it
ICON_DEST="$HOME/.local/share/icons/klippboard.png"
if [ -n "$ICON_SRC" ]; then
    echo "🎨 Installing app icon..."
    mkdir -p "$HOME/.local/share/icons"
    cp "$ICON_SRC" "$ICON_DEST"
    # Also drop a copy next to the app so it is always found at runtime
    cp "$ICON_SRC" ~/klippboard.png
else
    echo "⚠️  Icon file not found; using a fallback icon."
    ICON_DEST="klippboard"
fi

# Create global command wrapper
echo "🌐 Setting up global command..."
sudo tee /usr/local/bin/klippboard > /dev/null << 'EOF'
#!/bin/bash
source ~/clipboard_env/bin/activate
python3 ~/clipboard_manager.py
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

# Create desktop shortcut with the app icon
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
Icon=$ICON_DEST
Terminal=false
Categories=Utility;Accessories;
Keywords=clipboard;manager;history;copy;paste;
StartupNotify=true
StartupWMClass=KlippBoard
DESKTOP
chmod +x ~/.local/share/applications/klippboard.desktop

# Refresh desktop + icon caches so it appears immediately
update-desktop-database ~/.local/share/applications 2>/dev/null || true
gtk-update-icon-cache ~/.local/share/icons 2>/dev/null || true

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
