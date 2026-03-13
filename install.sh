#!/bin/bash
# KlippBoard Auto-Installer v1.0.0

echo "📋 Installing KlippBoard v1.0.0..."
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv ~/clipboard_env
source ~/clipboard_env/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --quiet PyQt5 keyboard 2>/dev/null || pip install PyQt5 keyboard

# Copy app
echo "📄 Copying application..."
cp src/clipboard_manager.py ~/clipboard_manager.py
chmod +x ~/clipboard_manager.py

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

# Create desktop shortcut
echo "🎯 Creating desktop shortcut..."
mkdir -p ~/.local/share/applications
cat > ~/.local/share/applications/klippboard.desktop << 'DESKTOP'
[Desktop Entry]
Type=Application
Name=KlippBoard
Comment=Modern clipboard manager for Linux
Exec=/usr/local/bin/klippboard
Icon=document-properties
Terminal=false
Categories=Utility;Accessories;
Keywords=clipboard;manager;history;
StartupNotify=true
DESKTOP

# Create keyboard shortcut setup (optional)
echo ""
echo "⌨️  Keyboard Shortcut Setup (Optional)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "KlippBoard is set to launch with Ctrl+Alt+V (configurable in app)"
echo ""
echo "To configure hotkey:"
echo "  1. Launch: klippboard"
echo "  2. Click ⚙ button"
echo "  3. Enter hotkey (e.g., super+v)"
echo "  4. Click OK"
echo ""

# Source bashrc
source ~/.bashrc

echo "✅ Installation Complete!"
echo ""
echo "🚀 Launch KlippBoard with:"
echo "   klippboard"
echo ""
echo "Or from Applications menu: KlippBoard"
echo ""
echo "Documentation:"
echo "  📖 Help tab in app (❓ button)"
echo "  📄 docs/INSTALLATION.md"
echo "  🔐 docs/PRIVACY.md"
echo ""
echo "Happy copying! 📋✨"
