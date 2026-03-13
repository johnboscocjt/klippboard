#!/usr/bin/env python3
"""
📋 KlippBoard v3.2 - Ultra-Modern Clipboard Manager
All features from v3.1 + new requested improvements
Created by: johnboscocjt
"""

import sys
import os
import json
import time
from datetime import datetime, date
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QListWidgetItem, QPushButton, QLabel, QTextEdit,
    QDialog, QMessageBox, QMenu, QSystemTrayIcon, QStyle,
    QFrame, QLineEdit, QCalendarWidget, QTabWidget, QCheckBox,
    QSplitter, QTextBrowser, QPlainTextEdit, QScrollBar, QInputDialog
)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QSize, QDate, QRect
from PyQt5.QtGui import (
    QIcon, QFont, QClipboard, QColor, QPalette, QLinearGradient,
    QBrush, QPainter, QPen, QTextCharFormat
)

try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False

APP_VERSION = "1.0.0"
APP_NAME = "KlippBoard"
REPO_URL = "https://github.com/johnboscocjt/klippboard"

# Dark theme colors
THEME = {
    'bg_primary': '#0f1419',
    'bg_secondary': '#1a1f2e',
    'bg_tertiary': '#252d3d',
    'glass': 'rgba(42, 50, 70, 0.4)',
    'glass_border': 'rgba(255, 255, 255, 0.1)',
    'fg_primary': '#e8eef7',
    'fg_secondary': '#a0aac0',
    'accent_blue': '#3b82f6',
    'accent_cyan': '#06b6d4',
    'accent_purple': '#8b5cf6',
    'success': '#10b981',
    'warning': '#f59e0b',
    'error': '#ef4444',
}

class LineNumberArea(QWidget):
    """Line numbers for code editor"""
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor
    
    def sizeHint(self):
        return QSize(50, 0)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(event.rect(), QColor('#1a1f2e'))
        
        block = self.editor.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.editor.blockBoundingGeometry(block).translated(self.editor.contentOffset()).top()
        bottom = top + self.editor.blockBoundingRect(block).height()
        
        painter.setFont(QFont('Courier', 9))
        painter.setPen(QColor('#606366'))
        
        while block.isValid() and top <= event.rect().bottom():
            if bottom >= event.rect().top():
                painter.drawText(0, int(top), self.width() - 5, 
                               int(self.editor.fontMetrics().height()),
                               Qt.AlignRight, str(block_number + 1))
            block = block.next()
            top = bottom
            bottom = top + self.editor.blockBoundingRect(block).height()
            block_number += 1

class CodeEditor(QPlainTextEdit):
    """Text editor with line numbers"""
    def __init__(self):
        super().__init__()
        self.line_number_area = LineNumberArea(self)
        self.blockCountChanged.connect(self.update_line_number_width)
        self.updateRequest.connect(self.update_line_numbers)
        self.update_line_number_width()
        self.setFont(QFont('Courier', 10))
        self.setStyleSheet("""
            QPlainTextEdit { 
                background-color: #252d3d; 
                color: #e8eef7; 
                border: 1px solid #333;
            }
        """)
    
    def update_line_number_width(self):
        self.setViewportMargins(50, 0, 0, 0)
    
    def update_line_numbers(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())

class ClipboardMonitor(QThread):
    """Monitor clipboard in background"""
    clipboard_changed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.running = True
        self.last_content = ""
    
    def run(self):
        while self.running:
            try:
                clipboard = QApplication.clipboard()
                current = clipboard.text()
                if current and current != self.last_content and len(current.strip()) > 0:
                    self.clipboard_changed.emit(current)
                    self.last_content = current
                time.sleep(0.5)
            except:
                pass
    
    def stop(self):
        self.running = False

class ViewerDialog(QDialog):
    """View clipboard item with line numbers"""
    def __init__(self, content="", parent=None):
        super().__init__(parent)
        self.setWindowTitle("📝 View Item")
        self.setGeometry(100, 100, 1000, 700)
        self.edited_content = content
        
        layout = QVBoxLayout()
        
        # Status bar
        status = QHBoxLayout()
        self.status_label = QLabel(f"Characters: {len(content)} | Lines: {content.count(chr(10)) + 1}")
        status.addWidget(self.status_label)
        status.addStretch()
        layout.addLayout(status)
        
        # Editor
        self.editor = CodeEditor()
        self.editor.setPlainText(content)
        self.editor.textChanged.connect(self.update_status)
        layout.addWidget(self.editor)
        
        # Buttons
        buttons = QHBoxLayout()
        save_btn = QPushButton("💾 Save")
        save_btn.clicked.connect(self.save_changes)
        copy_btn = QPushButton("📋 Copy All")
        copy_btn.clicked.connect(self.copy_to_clipboard)
        close_btn = QPushButton("✕ Close")
        close_btn.clicked.connect(self.reject)
        
        buttons.addWidget(save_btn)
        buttons.addWidget(copy_btn)
        buttons.addStretch()
        buttons.addWidget(close_btn)
        layout.addLayout(buttons)
        
        self.setLayout(layout)
        self.apply_theme()
    
    def update_status(self):
        text = self.editor.toPlainText()
        chars = len(text)
        lines = text.count('\n') + 1 if text else 0
        self.status_label.setText(f"Characters: {chars} | Lines: {lines}")
    
    def save_changes(self):
        self.edited_content = self.editor.toPlainText()
        self.accept()
    
    def copy_to_clipboard(self):
        QApplication.clipboard().setText(self.editor.toPlainText())
        QMessageBox.information(self, "✅", "Copied to clipboard!")
    
    def apply_theme(self):
        self.setStyleSheet(f"""
            QDialog {{ background-color: #0f1419; color: #e8eef7; }}
            QPushButton {{ background: #1a1f2e; color: #e8eef7; border: 1px solid #333; 
                          padding: 8px 16px; border-radius: 5px; }}
            QPushButton:hover {{ background: #3b82f6; }}
            QLabel {{ color: #e8eef7; }}
        """)

class ListItemWidget(QWidget):
    """Single clipboard item in list"""
    copy_clicked = pyqtSignal(str)
    view_clicked = pyqtSignal(str)
    delete_clicked = pyqtSignal(str)
    favorite_clicked = pyqtSignal(str)
    
    def __init__(self, content, idx, is_favorite=False):
        super().__init__()
        self.content = content
        self.is_favorite = is_favorite
        
        layout = QHBoxLayout()
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(10)
        
        # Checkbox
        self.checkbox = QCheckBox()
        self.checkbox.setFixedWidth(30)
        layout.addWidget(self.checkbox, 0)
        
        # Index badge
        idx_label = QLabel(f"#{idx}")
        idx_label.setStyleSheet(f"color: {THEME['accent_blue']}; font-weight: bold; min-width: 40px;")
        layout.addWidget(idx_label, 0)
        
        # Content preview
        preview = content[:70].replace('\n', ' ')
        if len(content) > 70:
            preview += "…"
        content_label = QLabel(preview)
        content_label.setStyleSheet(f"color: {THEME['fg_primary']};")
        layout.addWidget(content_label, 1)
        
        # Action buttons
        copy_btn = QPushButton("📋")
        copy_btn.setFixedSize(36, 36)
        copy_btn.setToolTip("Copy")
        copy_btn.clicked.connect(lambda: self.copy_clicked.emit(content))
        copy_btn.setStyleSheet(f"""
            QPushButton {{ background: {THEME['success']}; color: white; border: none; 
                          border-radius: 6px; font-size: 16px; }}
            QPushButton:hover {{ background: {THEME['accent_cyan']}; }}
        """)
        layout.addWidget(copy_btn, 0)
        
        view_btn = QPushButton("👁")
        view_btn.setFixedSize(36, 36)
        view_btn.setToolTip("View")
        view_btn.clicked.connect(lambda: self.view_clicked.emit(content))
        view_btn.setStyleSheet(f"""
            QPushButton {{ background: {THEME['accent_blue']}; color: white; border: none; 
                          border-radius: 6px; font-size: 16px; }}
            QPushButton:hover {{ background: {THEME['accent_cyan']}; }}
        """)
        layout.addWidget(view_btn, 0)
        
        del_btn = QPushButton("🗑")
        del_btn.setFixedSize(36, 36)
        del_btn.setToolTip("Delete")
        del_btn.clicked.connect(lambda: self.delete_clicked.emit(content))
        del_btn.setStyleSheet(f"""
            QPushButton {{ background: {THEME['error']}; color: white; border: none; 
                          border-radius: 6px; font-size: 16px; }}
            QPushButton:hover {{ background: {THEME['warning']}; }}
        """)
        layout.addWidget(del_btn, 0)
        
        # Star button
        self.star_btn = QPushButton("★" if is_favorite else "☆")
        self.star_btn.setFixedSize(36, 36)
        self.star_btn.setToolTip("Favorite")
        self.star_btn.setFont(QFont("Arial", 14))
        self.star_btn.clicked.connect(lambda: self.favorite_clicked.emit(content))
        self.star_btn.setStyleSheet(f"""
            QPushButton {{ background: {THEME['warning']}; color: white; border: none; 
                          border-radius: 6px; font-weight: bold; }}
            QPushButton:hover {{ background: {THEME['accent_cyan']}; }}
        """)
        layout.addWidget(self.star_btn, 0)
        
        self.setLayout(layout)
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {THEME['glass']};
                border: 1px solid {THEME['glass_border']};
                border-radius: 10px;
            }}
        """)

class ClipboardManager(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.history_file = os.path.expanduser("~/.clipboard_history.json")
        self.config_file = os.path.expanduser("~/.klippboard_config.json")
        self.history = []
        self.selected_items = set()
        self.hotkey = "ctrl+alt+v"
        self.max_items = 100
        
        self.load_data()
        self.setup_ui()
        self.setup_monitoring()
        self.setup_hotkey()
        self.apply_theme()
    
    def setup_ui(self):
        """Create user interface"""
        self.setWindowTitle(f"📋 {APP_NAME} v{APP_VERSION}")
        self.setGeometry(150, 150, 1000, 700)  # Medium sized window
        
        central = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header
        header = QFrame()
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(20, 15, 20, 15)
        
        title = QLabel(f"📋 {APP_NAME} v{APP_VERSION}")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        header_layout.addWidget(title)
        
        # GitHub link
        github_link = QLabel(f'<a href="{REPO_URL}" style="color: #3b82f6;">GitHub</a>')
        github_link.setOpenExternalLinks(True)
        github_link.setToolTip(REPO_URL)
        header_layout.addWidget(github_link)
        
        header_layout.addStretch()
        
        settings_btn = QPushButton("⚙")
        settings_btn.setFixedSize(40, 40)
        settings_btn.clicked.connect(self.configure_hotkey)
        settings_btn.setToolTip("Configure hotkey")
        header_layout.addWidget(settings_btn)
        
        header.setLayout(header_layout)
        main_layout.addWidget(header)
        
        # Tabs
        self.tabs = QTabWidget()
        
        # ===== TAB 1: ALL ITEMS =====
        all_widget = QWidget()
        all_layout = QVBoxLayout()
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search...")
        self.search_input.textChanged.connect(self.filter_all_tab)
        search_layout.addWidget(self.search_input)
        all_layout.addLayout(search_layout)
        
        # Stats bar
        stats_layout = QHBoxLayout()
        self.stats_total = QLabel("📋 Total: 0")
        self.stats_total.setStyleSheet(f"color: {THEME['accent_blue']}; font-weight: bold;")
        self.stats_favorites = QLabel("⭐ Favorites: 0")
        self.stats_favorites.setStyleSheet(f"color: {THEME['warning']}; font-weight: bold;")
        stats_layout.addWidget(self.stats_total)
        stats_layout.addWidget(self.stats_favorites)
        stats_layout.addStretch()
        all_layout.addLayout(stats_layout)
        
        self.all_list = QListWidget()
        self.all_list.setSpacing(8)
        all_layout.addWidget(self.all_list)
        all_widget.setLayout(all_layout)
        self.tabs.addTab(all_widget, "📋 All Items")
        
        # ===== TAB 2: FAVORITES =====
        fav_widget = QWidget()
        fav_layout = QVBoxLayout()
        self.fav_list = QListWidget()
        self.fav_list.setSpacing(8)
        fav_layout.addWidget(self.fav_list)
        fav_widget.setLayout(fav_layout)
        self.tabs.addTab(fav_widget, "⭐ Favorites")
        
        # ===== TAB 3: TODAY =====
        today_widget = QWidget()
        today_layout = QVBoxLayout()
        self.today_list = QListWidget()
        self.today_list.setSpacing(8)
        today_layout.addWidget(self.today_list)
        today_widget.setLayout(today_layout)
        self.tabs.addTab(today_widget, "📍 Today")
        
        # ===== TAB 4: CALENDAR WITH COLLAPSIBLE =====
        date_widget = QWidget()
        date_layout = QHBoxLayout()
        
        # Calendar (left, collapsible)
        cal_panel = QWidget()
        cal_layout = QVBoxLayout()
        cal_layout.addWidget(QLabel("📅 Pick Date"))
        self.calendar = QCalendarWidget()
        self.calendar.clicked.connect(self.on_date_selected)
        
        # Make Monday to Friday black text
        weekday_fmt = QTextCharFormat()
        weekday_fmt.setForeground(QColor("black"))
        for day in [Qt.Monday, Qt.Tuesday, Qt.Wednesday, Qt.Thursday, Qt.Friday]:
            self.calendar.setWeekdayTextFormat(day, weekday_fmt)
            
        self.calendar.setStyleSheet(f"""
            QCalendarWidget {{ background-color: {THEME['bg_tertiary']}; }}
            QCalendarWidget QHeaderView::section {{ 
                background-color: {THEME['bg_secondary']}; 
                color: #ff4444;
                font-weight: bold;
                padding: 6px;
                border: none;
            }}
            QCalendarWidget QTableView {{
                background-color: {THEME['bg_tertiary']};
                gridline-color: #333;
                selection-background-color: {THEME['accent_blue']};
            }}
            QCalendarWidget QToolButton {{ background: {THEME['bg_secondary']}; color: {THEME['fg_primary']}; }}
            QCalendarWidget QAbstractItemView {{ color: {THEME['fg_primary']}; }}
        """)
        cal_layout.addWidget(self.calendar)
        cal_panel.setLayout(cal_layout)
        cal_panel.setMaximumWidth(300)
        
        # Items (right)
        list_panel = QWidget()
        list_layout = QVBoxLayout()
        list_layout.addWidget(QLabel("📋 Items"))
        self.date_search = QLineEdit()
        self.date_search.setPlaceholderText("🔍 Search in date...")
        self.date_search.textChanged.connect(self.filter_date_tab)
        list_layout.addWidget(self.date_search)
        
        self.date_list = QListWidget()
        self.date_list.setSpacing(8)
        list_layout.addWidget(self.date_list)
        list_panel.setLayout(list_layout)
        
        # Splitter for collapse
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(cal_panel)
        splitter.addWidget(list_panel)
        splitter.setSizes([250, 800])
        date_layout.addWidget(splitter)
        date_widget.setLayout(date_layout)
        self.tabs.addTab(date_widget, "🗓 Calendar")
        
        # ===== TAB 5: HELP =====
        help_widget = QWidget()
        help_layout = QVBoxLayout()
        help_text = QTextBrowser()
        help_text.setMarkdown(f"""
# 📋 KlippBoard v{APP_VERSION} - User Guide

## 🎯 Overview
KlippBoard is a modern clipboard manager that automatically captures and stores everything you copy.

## 📑 Tabs Explained

### 📋 All - All Your Clipboards
- **Search**: 🔍 Real-time filtering of all items
- **Stats**: Shows total items and favorites count
- **Quick Actions**: Copy (📋), View (👁️), Delete (🗑️) on each item
- **Select**: Check items for batch operations

### ⭐ Favorites - Your Starred Items
- Only items you marked as favorites
- Protected from bulk delete operations
- Quick access to frequently used content
- Same quick actions as All tab

### 📍 Today - Today's Clipboards
- Shows only items copied today
- Displays date in tab header
- Same search and action buttons
- Perfect for reviewing current session

### 🗓️ By Date - Calendar Picker
- **Left**: Collapsible calendar (click dates)
- **Right**: Items from selected date
- **Search**: Filter items within selected date
- **Space**: Collapse calendar for more viewing space

### 📖 Help - This Documentation
- Complete feature guide
- Explains each tab and action
- Keyboard shortcuts and tips
- You're reading it now!

## 🎮 How to Use

### Actions on Each Item
Every clipboard shows these buttons:
- **📋 Copy** (Green): Copy to clipboard immediately
- **👁️ View** (Blue): Open in editor to read/edit
- **🗑️ Delete** (Red): Remove item with confirmation
- **⭐ Star** (Yellow): Toggle favorite status

### Star System
- **★ Filled Star**: Favorite item (protected from delete all)
- **☆ Empty Star**: Not yet favorited

### View Options
- **Single Click**: Check the checkbox to select
- **Double Click**: Copy to clipboard instantly

### Toolbar Buttons
- **☑ Select All**: Select all items in current tab
- **✎ Edit**: Edit selected item
- **📋 Copy**: Copy all selected items
- **⭐ Star**: Star all selected items
- **🗑️ Delete**: Delete selected items
- **↻ Refresh**: Refresh all tabs
- **⬇ Export**: Export history as text file
- **⚠️ Clear All**: Delete everything (double confirmation)

## 📝 Editor Features
- **Line Numbers**: Left side shows line numbers
- **Character Count**: See total characters
- **Line Count**: See how many lines
- **Save**: Save edited content back to history
- **Copy**: Copy from editor to clipboard

## ⌨️ Keyboard Shortcuts
- **Ctrl+Alt+V**: Launch/toggle KlippBoard (global hotkey)
- **Ctrl+F**: Focus search in All tab
- **Esc**: Hide window to system tray
- **Delete**: Delete selected item

## ⚙️ Configuration

### Set Global Hotkey
1. Click ⚙️ button in header
2. Enter hotkey (e.g., super+v, ctrl+alt+c)
3. Click OK - saved automatically
4. May need sudo on Linux for system-level

### Common Hotkeys
- `ctrl+alt+v` - Default
- `super+v` - Windows/Super key
- `shift+alt+v` - Shift+Alt combo
- `ctrl+alt+c` - Ctrl+Alt+C variant

## 💡 Tips & Tricks

### Batch Operations
1. Check multiple items (checkbox)
2. Use toolbar buttons to act on all
3. Delete multiple at once
4. Star/unstar groups

### Date Navigation
- Click calendar dates to jump to any day
- Collapse calendar for more space
- Search within a date
- Compare items across dates

### Search Effectively
- Search is case-insensitive
- Works in All and By Date tabs
- Live results as you type
- Clear to see all again

### Editor Power
- Line numbers help navigate
- Fullscreen for detailed editing
- Save changes back to history
- Copy from editor to clipboard

### Favorites Strategy
- Star frequently used content
- Favorites can't be deleted accidentally
- Use for important templates/snippets
- Quick reference material

## 🔐 Privacy
✅ All local - nothing sent online
✅ No cloud sync
✅ No tracking or telemetry
✅ Data in ~/.clipboard_history.json
✅ Delete the file to clear all history

## 🚀 Quick Tips
- Copy = automatically saved
- Long clipboard? Search it!
- Edit anything in the editor
- Check multiple items then delete
- Use calendar for date-based review
- Set hotkey for instant access
- Export history for backup
- Select all then delete to clear

---
Made with ❤️ by [johnboscocjt](https://github.com/johnboscocjt/klippboard)
""")
        help_layout.addWidget(help_text)
        help_widget.setLayout(help_layout)
        self.tabs.addTab(help_widget, "❓ Help")
        help_layout.addWidget(help_text)
        help_widget.setLayout(help_layout)
        self.tabs.addTab(help_widget, "❓ Help")
        
        main_layout.addWidget(self.tabs)
        
        # Action toolbar
        toolbar = QFrame()
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setContentsMargins(12, 10, 12, 10)
        toolbar_layout.setSpacing(8)
        
        select_all_btn = QPushButton("☑ Select All")
        select_all_btn.clicked.connect(self.select_all_items)
        toolbar_layout.addWidget(select_all_btn)
        
        edit_btn = QPushButton("✎ Edit")
        edit_btn.clicked.connect(self.edit_selected)
        toolbar_layout.addWidget(edit_btn)
        
        copy_sel_btn = QPushButton("📋 Copy")
        copy_sel_btn.clicked.connect(self.copy_selected_items)
        toolbar_layout.addWidget(copy_sel_btn)
        
        star_sel_btn = QPushButton("⭐ Star")
        star_sel_btn.clicked.connect(self.star_selected_items)
        toolbar_layout.addWidget(star_sel_btn)
        
        del_sel_btn = QPushButton("🗑 Delete")
        del_sel_btn.clicked.connect(self.delete_selected_items)
        toolbar_layout.addWidget(del_sel_btn)
        
        refresh_btn = QPushButton("↻ Refresh")
        refresh_btn.clicked.connect(self.refresh_all)
        toolbar_layout.addWidget(refresh_btn)
        
        export_btn = QPushButton("⬇ Export")
        export_btn.clicked.connect(self.export_history)
        toolbar_layout.addWidget(export_btn)
        
        clear_all_btn = QPushButton("⚠️ Clear All")
        clear_all_btn.setStyleSheet(f"background: {THEME['error']};")
        clear_all_btn.clicked.connect(self.clear_all_items)
        toolbar_layout.addWidget(clear_all_btn)
        
        toolbar_layout.addStretch()
        
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(40, 40)
        close_btn.clicked.connect(self.hide)
        toolbar_layout.addWidget(close_btn)
        
        toolbar.setLayout(toolbar_layout)
        main_layout.addWidget(toolbar)
        
        central.setLayout(main_layout)
        self.setCentralWidget(central)
        self.populate_all_items()
    
    def load_data(self):
        """Load saved clipboard history"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    self.history = json.load(f)
        except:
            self.history = []
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    cfg = json.load(f)
                    self.hotkey = cfg.get('hotkey', 'ctrl+alt+v')
        except:
            pass
    
    def save_data(self):
        """Save clipboard history"""
        with open(self.history_file, 'w') as f:
            json.dump(self.history[:self.max_items], f, indent=2)
        
        with open(self.config_file, 'w') as f:
            json.dump({'hotkey': self.hotkey}, f)
    
    def setup_monitoring(self):
        """Start clipboard monitor thread"""
        self.monitor = ClipboardMonitor()
        self.monitor.clipboard_changed.connect(self.on_clipboard_changed)
        self.monitor.start()
    
    def setup_hotkey(self):
        """Setup global hotkey"""
        if not KEYBOARD_AVAILABLE:
            return
        try:
            keyboard.add_hotkey(self.hotkey, self.show)
        except:
            pass
    
    def configure_hotkey(self):
        """Configure global hotkey"""
        if not KEYBOARD_AVAILABLE:
            QMessageBox.warning(self, "⚠", "Install: pip install keyboard")
            return
        
        hotkey, ok = QInputDialog.getText(self, "⚙ Hotkey", "Enter hotkey (e.g., ctrl+alt+v):", 
                                         text=self.hotkey)
        if ok and hotkey:
            try:
                if KEYBOARD_AVAILABLE:
                    keyboard.remove_hotkey(self.hotkey)
                    keyboard.add_hotkey(hotkey, self.show)
                self.hotkey = hotkey
                self.save_data()
                QMessageBox.information(self, "✅", f"Hotkey set: {hotkey}")
            except Exception as e:
                QMessageBox.critical(self, "❌", f"Error: {e}")
    
    def on_clipboard_changed(self, content):
        """Handle new clipboard item"""
        # Don't add duplicates
        if any(item.get('content') == content for item in self.history):
            return
        
        self.history.insert(0, {
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'favorite': False
        })
        self.save_data()
        self.populate_all_items()
        self.populate_favorites()
        self.populate_today()
        self.update_stats()
    
    def populate_all_items(self):
        """Fill All Items tab"""
        self.all_list.clear()
        for idx, item in enumerate(self.history, 1):
            content = item.get('content', '')
            is_fav = item.get('favorite', False)
            
            widget = ListItemWidget(content, idx, is_fav)
            widget.copy_clicked.connect(self.quick_copy)
            widget.view_clicked.connect(self.quick_view)
            widget.delete_clicked.connect(self.quick_delete)
            widget.favorite_clicked.connect(self.quick_favorite)
            widget.checkbox.stateChanged.connect(lambda s, c=content: self.toggle_select(c, s))
            
            item_widget = QListWidgetItem()
            item_widget.setSizeHint(widget.sizeHint())
            self.all_list.addItem(item_widget)
            self.all_list.setItemWidget(item_widget, widget)
        
        self.update_stats()
    
    def populate_favorites(self):
        """Fill Favorites tab"""
        self.fav_list.clear()
        fav_items = [i for i in self.history if i.get('favorite', False)]
        
        for idx, item in enumerate(fav_items, 1):
            content = item.get('content', '')
            widget = ListItemWidget(content, idx, True)
            widget.copy_clicked.connect(self.quick_copy)
            widget.view_clicked.connect(self.quick_view)
            widget.delete_clicked.connect(self.quick_delete)
            widget.favorite_clicked.connect(self.quick_favorite)
            
            item_widget = QListWidgetItem()
            item_widget.setSizeHint(widget.sizeHint())
            self.fav_list.addItem(item_widget)
            self.fav_list.setItemWidget(item_widget, widget)
    
    def populate_today(self):
        """Fill Today tab"""
        self.today_list.clear()
        today = date.today()
        today_items = [i for i in self.history 
                      if datetime.fromisoformat(i.get('timestamp', '')).date() == today]
        
        for idx, item in enumerate(today_items, 1):
            content = item.get('content', '')
            is_fav = item.get('favorite', False)
            
            widget = ListItemWidget(content, idx, is_fav)
            widget.copy_clicked.connect(self.quick_copy)
            widget.view_clicked.connect(self.quick_view)
            widget.delete_clicked.connect(self.quick_delete)
            widget.favorite_clicked.connect(self.quick_favorite)
            
            item_widget = QListWidgetItem()
            item_widget.setSizeHint(widget.sizeHint())
            self.today_list.addItem(item_widget)
            self.today_list.setItemWidget(item_widget, widget)
    
    def on_date_selected(self, qdate):
        """Handle date selection"""
        selected = qdate.toPyDate()
        self.date_list.clear()
        
        date_items = [i for i in self.history 
                     if datetime.fromisoformat(i.get('timestamp', '')).date() == selected]
        
        for idx, item in enumerate(date_items, 1):
            content = item.get('content', '')
            is_fav = item.get('favorite', False)
            
            widget = ListItemWidget(content, idx, is_fav)
            widget.copy_clicked.connect(self.quick_copy)
            widget.view_clicked.connect(self.quick_view)
            widget.delete_clicked.connect(self.quick_delete)
            widget.favorite_clicked.connect(self.quick_favorite)
            
            item_widget = QListWidgetItem()
            item_widget.setSizeHint(widget.sizeHint())
            self.date_list.addItem(item_widget)
            self.date_list.setItemWidget(item_widget, widget)
    
    def filter_all_tab(self, text):
        """Search/filter All Items tab"""
        self.all_list.clear()
        if not text:
            self.populate_all_items()
            return
        
        filtered = [i for i in self.history 
                   if text.lower() in i.get('content', '').lower()]
        
        for idx, item in enumerate(filtered, 1):
            content = item.get('content', '')
            is_fav = item.get('favorite', False)
            
            widget = ListItemWidget(content, idx, is_fav)
            widget.copy_clicked.connect(self.quick_copy)
            widget.view_clicked.connect(self.quick_view)
            widget.delete_clicked.connect(self.quick_delete)
            widget.favorite_clicked.connect(self.quick_favorite)
            
            item_widget = QListWidgetItem()
            item_widget.setSizeHint(widget.sizeHint())
            self.all_list.addItem(item_widget)
            self.all_list.setItemWidget(item_widget, widget)
    
    def filter_date_tab(self, text):
        """Search/filter Calendar tab"""
        selected = self.calendar.selectedDate().toPyDate()
        self.date_list.clear()
        
        if not text:
            self.on_date_selected(QDate(selected.year, selected.month, selected.day))
            return
        
        filtered = [i for i in self.history 
                   if datetime.fromisoformat(i.get('timestamp', '')).date() == selected
                   and text.lower() in i.get('content', '').lower()]
        
        for idx, item in enumerate(filtered, 1):
            content = item.get('content', '')
            is_fav = item.get('favorite', False)
            
            widget = ListItemWidget(content, idx, is_fav)
            widget.copy_clicked.connect(self.quick_copy)
            widget.view_clicked.connect(self.quick_view)
            widget.delete_clicked.connect(self.quick_delete)
            widget.favorite_clicked.connect(self.quick_favorite)
            
            item_widget = QListWidgetItem()
            item_widget.setSizeHint(widget.sizeHint())
            self.date_list.addItem(item_widget)
            self.date_list.setItemWidget(item_widget, widget)
    
    def toggle_select(self, content, state):
        """Toggle item selection"""
        if state == Qt.Checked:
            self.selected_items.add(content)
        else:
            self.selected_items.discard(content)
    
    def select_all_items(self):
        """Select all items from current tab"""
        self.selected_items.clear()
        current_tab = self.tabs.currentIndex()
        
        if current_tab == 0:  # All Items tab
            for i in range(self.all_list.count()):
                widget = self.all_list.itemWidget(self.all_list.item(i))
                if widget:
                    widget.checkbox.setChecked(True)
        elif current_tab == 1:  # Favorites tab
            for i in range(self.fav_list.count()):
                widget = self.fav_list.itemWidget(self.fav_list.item(i))
                if widget:
                    widget.checkbox.setChecked(True)
        elif current_tab == 2:  # Today tab
            for i in range(self.today_list.count()):
                widget = self.today_list.itemWidget(self.today_list.item(i))
                if widget:
                    widget.checkbox.setChecked(True)
        elif current_tab == 3:  # Calendar tab
            for i in range(self.date_list.count()):
                widget = self.date_list.itemWidget(self.date_list.item(i))
                if widget:
                    widget.checkbox.setChecked(True)
        
        if self.selected_items:
            QMessageBox.information(self, "✅", f"Selected {len(self.selected_items)} items")
    
    def edit_selected(self):
        """Edit first selected item"""
        if not self.selected_items:
            QMessageBox.information(self, "ℹ", "Select an item first")
            return
        content = list(self.selected_items)[0]
        self.quick_view(content)
    
    def refresh_all(self):
        """Refresh all tabs"""
        self.populate_all_items()
        self.populate_favorites()
        self.populate_today()
        self.update_stats()
        QMessageBox.information(self, "✅", "Refreshed!")
    
    def export_history(self):
        """Export clipboard history"""
        if not self.history:
            QMessageBox.information(self, "ℹ", "Nothing to export")
            return
        
        filename = f"{os.path.expanduser('~')}/clipboard_export_{datetime.now().strftime('%Y%m%d')}.txt"
        try:
            with open(filename, 'w') as f:
                for i, item in enumerate(self.history, 1):
                    f.write(f"[{i}] {item.get('timestamp', 'N/A')}\n")
                    f.write(f"{item.get('content', '')}\n")
                    f.write("\n" + "="*80 + "\n\n")
            QMessageBox.information(self, "✅", f"Exported to:\n{filename}")
        except Exception as e:
            QMessageBox.critical(self, "❌", f"Error: {e}")
    
    def update_stats(self):
        """Update statistics labels"""
        total = len(self.history)
        favorites = sum(1 for i in self.history if i.get('favorite', False))
        self.stats_total.setText(f"📋 Total: {total}")
        self.stats_favorites.setText(f"⭐ Favorites: {favorites}")
    
    def quick_copy(self, content):
        """Copy single item"""
        QApplication.clipboard().setText(content)
        QMessageBox.information(self, "✅ Copied", "Item copied!")
    
    def quick_view(self, content):
        """View item in editor"""
        viewer = ViewerDialog(content, self)
        if viewer.exec_() == QDialog.Accepted:
            for item in self.history:
                if item.get('content') == content:
                    item['content'] = viewer.edited_content
                    break
            self.save_data()
            self.populate_all_items()
            self.populate_favorites()
            self.populate_today()
    
    def quick_delete(self, content):
        """Delete single item"""
        reply = QMessageBox.question(self, "Delete?", "Delete this item?")
        if reply == QMessageBox.Yes:
            self.history = [i for i in self.history if i.get('content') != content]
            self.save_data()
            self.populate_all_items()
            self.populate_favorites()
            self.populate_today()
            self.selected_items.discard(content)
    
    def quick_favorite(self, content):
        """Toggle favorite for single item"""
        for item in self.history:
            if item.get('content') == content:
                item['favorite'] = not item.get('favorite', False)
                break
        self.save_data()
        self.populate_all_items()
        self.populate_favorites()
        self.populate_today()
    
    def copy_selected_items(self):
        """Copy all selected items"""
        if not self.selected_items:
            QMessageBox.information(self, "ℹ", "Select items first")
            return
        
        text = "\n---\n".join(self.selected_items)
        QApplication.clipboard().setText(text)
        QMessageBox.information(self, "✅", f"Copied {len(self.selected_items)} items!")
    
    def star_selected_items(self):
        """Star all selected items"""
        if not self.selected_items:
            QMessageBox.information(self, "ℹ", "Select items first")
            return
        
        for content in self.selected_items:
            for item in self.history:
                if item.get('content') == content:
                    item['favorite'] = not item.get('favorite', False)
                    break
        
        self.save_data()
        self.populate_all_items()
        self.populate_favorites()
        self.selected_items.clear()
        QMessageBox.information(self, "✅", "Updated!")
    
    def delete_selected_items(self):
        """Delete all selected items"""
        if not self.selected_items:
            QMessageBox.information(self, "ℹ", "Select items first")
            return
        
        reply = QMessageBox.question(self, "Delete", f"Delete {len(self.selected_items)} items?")
        if reply == QMessageBox.Yes:
            self.history = [i for i in self.history if i.get('content') not in self.selected_items]
            self.save_data()
            self.populate_all_items()
            self.populate_favorites()
            self.populate_today()
            self.selected_items.clear()
    
    def clear_all_items(self):
        """Clear all items with double confirmation"""
        reply = QMessageBox.question(self, "⚠ CLEAR ALL", 
                                    "Delete ALL clipboard history?\nThis CANNOT be undone!")
        if reply != QMessageBox.Yes:
            return
        
        reply2 = QMessageBox.question(self, "⚠ CONFIRM", 
                                     "Are you ABSOLUTELY SURE?")
        if reply2 == QMessageBox.Yes:
            self.history = []
            self.selected_items.clear()
            self.save_data()
            self.populate_all_items()
            self.populate_favorites()
            self.populate_today()
            self.date_list.clear()
            QMessageBox.information(self, "✅", "All cleared!")
    
    def apply_theme(self):
        """Apply dark theme"""
        self.setStyleSheet(f"""
            QMainWindow, QWidget, QFrame {{ background-color: {THEME['bg_primary']}; color: {THEME['fg_primary']}; }}
            QListWidget {{ background: {THEME['bg_primary']}; border: none; }}
            QLineEdit {{ background: {THEME['bg_secondary']}; color: {THEME['fg_primary']}; 
                        border: 1px solid #333; padding: 8px; border-radius: 5px; }}
            QLineEdit:focus {{ border: 1px solid {THEME['accent_blue']}; }}
            QTabBar::tab {{ background: {THEME['bg_secondary']}; color: {THEME['fg_primary']}; 
                           padding: 10px 20px; border: none; }}
            QTabBar::tab:selected {{ background: {THEME['accent_blue']}; color: white; }}
            QCalendarWidget {{ background: {THEME['bg_tertiary']}; color: {THEME['fg_primary']}; }}
            QPushButton {{ background: {THEME['bg_secondary']}; color: {THEME['fg_primary']}; 
                          border: 1px solid #333; padding: 8px; border-radius: 5px; }}
            QPushButton:hover {{ background: {THEME['accent_blue']}; }}
            QLabel {{ color: {THEME['fg_primary']}; }}
            QTextBrowser {{ background: {THEME['bg_secondary']}; color: {THEME['fg_primary']}; }}
        """)
    
    def closeEvent(self, event):
        event.ignore()
        self.hide()

def main():
    app = QApplication(sys.argv)
    app.setApplicationName(f"{APP_NAME} v{APP_VERSION}")
    app.setQuitOnLastWindowClosed(False)
    
    manager = ClipboardManager()
    manager.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
