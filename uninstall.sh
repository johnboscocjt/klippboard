#!/bin/bash
# KlippBoard Uninstaller v1.0.0
# Removes the app, launcher, icon and virtual environment.
# Your clipboard history is kept unless you pass --purge.

PURGE=0
if [ "$1" = "--purge" ]; then
    PURGE=1
fi

echo "🗑️  Uninstalling KlippBoard..."
echo ""

# Global command
echo "• Removing global command..."
sudo rm -f /usr/local/bin/klippboard

# Application + runtime icon copy
echo "• Removing application files..."
rm -f ~/clipboard_manager.py
rm -f ~/klippboard.png

# Virtual environment
echo "• Removing virtual environment..."
rm -rf ~/clipboard_env

# Desktop launcher + icon
echo "• Removing launcher and icon..."
rm -f ~/.local/share/applications/klippboard.desktop
rm -f ~/.local/share/icons/klippboard.png
rm -f ~/.config/autostart/klippboard.desktop

# Refresh caches so it disappears from the menu
update-desktop-database ~/.local/share/applications 2>/dev/null || true
gtk-update-icon-cache ~/.local/share/icons 2>/dev/null || true

# Remove bashrc alias
if [ -f ~/.bashrc ]; then
    echo "• Cleaning ~/.bashrc alias..."
    sed -i '/# KlippBoard/d' ~/.bashrc
    sed -i "/alias klippboard=/d" ~/.bashrc
fi

if [ "$PURGE" -eq 1 ]; then
    echo "• Purging saved data (history + env files)..."
    rm -f ~/.clipboard_history.json
    rm -f ~/.klippboard_config.json
    rm -f ~/.klippboard_env_config.json
    rm -rf ~/.klippboard_env
else
    echo ""
    echo "ℹ️  Your data was kept:"
    echo "     ~/.clipboard_history.json"
    echo "     ~/.klippboard_config.json"
    echo "     ~/.klippboard_env/ (env files)"
    echo "   Re-run with:  bash uninstall.sh --purge   to delete it too."
fi

echo ""
echo "✅ KlippBoard has been uninstalled."
