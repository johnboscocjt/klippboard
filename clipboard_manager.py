#!/usr/bin/env python3
"""
KlippBoard - Modern dark-minimal clipboard manager with Env Sync
Created by: johnboscocjt
"""

import sys
import os
import json
import time
import subprocess
import unicodedata
from datetime import datetime, date
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QListWidgetItem, QPushButton, QLabel, QLineEdit,
    QDialog, QMessageBox, QMenu, QSystemTrayIcon, QStyle,
    QFrame, QCalendarWidget, QCheckBox, QTextBrowser, QStackedWidget,
    QInputDialog, QPlainTextEdit, QSizePolicy, QAbstractItemView, QTextEdit,
    QButtonGroup
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize, QDate, QRect, QTimer
from PyQt5.QtGui import (
    QFont, QColor, QPainter, QTextFormat, QIcon, QPixmap, QFontDatabase
)

APP_VERSION = "1.0.0"
APP_NAME = "KlippBoard"
REPO_URL = "https://github.com/johnboscocjt/klippboard"
DESKTOP_FILE_ID = "klippboard"


def resolve_icon_path():
    """Find the app icon across dev and installed locations."""
    candidates = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "klippboard.png"),
        os.path.expanduser("~/.local/share/icons/hicolor/512x512/apps/klippboard.png"),
        os.path.expanduser("~/.local/share/icons/hicolor/256x256/apps/klippboard.png"),
        os.path.expanduser("~/.local/share/icons/klippboard.png"),
        os.path.expanduser("~/klippboard.png"),
        "/usr/local/share/icons/hicolor/512x512/apps/klippboard.png",
        "/usr/share/icons/hicolor/512x512/apps/klippboard.png",
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return ""


def load_app_icon():
    """Build a multi-size QIcon so the taskbar/dock can pick a sharp glyph."""
    path = resolve_icon_path()
    if not path:
        return QIcon()
    icon = QIcon()
    base = QPixmap(path)
    if base.isNull():
        return QIcon(path)
    for size in (16, 24, 32, 48, 64, 128, 256, 512):
        icon.addPixmap(base.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation))
    return icon


ICON_PATH = resolve_icon_path()
APP_ICON = None  # filled after QApplication exists

# ---------------------------------------------------------------------------
# Dark-minimal design system
# ---------------------------------------------------------------------------
THEME = {
    "bg": "#0c0e14",
    "bg_elevated": "#141824",
    "bg_surface": "#1a1f2e",
    "bg_card": "#161b28",
    "bg_hover": "#1e2436",
    "bg_input": "#12161f",
    "border": "#2a3144",
    "border_subtle": "#1e2433",
    "border_focus": "#4f6ef7",
    "text_primary": "#e8eaef",
    "text_secondary": "#8b93a7",
    "text_muted": "#5c6578",
    "accent": "#4f6ef7",
    "accent_hover": "#6b86ff",
    "accent_soft": "rgba(79, 110, 247, 0.14)",
    "accent_gradient": "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4f6ef7, stop:1 #6366f1)",
    "success": "#34d399",
    "success_soft": "rgba(52, 211, 153, 0.12)",
    "warning": "#fbbf24",
    "warning_soft": "rgba(251, 191, 36, 0.12)",
    "error": "#f87171",
    "error_soft": "rgba(248, 113, 113, 0.12)",
    "radius_sm": "8px",
    "radius_md": "12px",
    "radius_lg": "16px",
}

ENV_DIR = os.path.expanduser("~/.klippboard_env")
ENV_CONFIG = os.path.expanduser("~/.klippboard_env_config.json")

# ---------------------------------------------------------------------------
# Emoji support
#
# The UI fonts below carry no emoji glyphs, and Qt will not reach for the
# system emoji font on its own -- copied emoji land in the history as empty
# tofu boxes. Naming an emoji family explicitly in every font stack fixes it.
# ---------------------------------------------------------------------------
EMOJI_FONT_CANDIDATES = (
    "Noto Color Emoji",       # most Linux distros
    "Apple Color Emoji",      # macOS
    "Segoe UI Emoji",         # Windows
    "Twemoji Mozilla",
    "JoyPixels",
    "EmojiOne Color",
    "Symbola",                # monochrome last resort
)

GENERIC_FONT_FAMILIES = ("sans-serif", "serif", "monospace", "cursive", "fantasy")

_emoji_font = None


def emoji_font_family():
    """First emoji-capable font actually installed, or "" if none is."""
    global _emoji_font
    if _emoji_font is None:
        try:
            installed = set(QFontDatabase().families())
        except Exception:
            installed = set()
        if not installed:
            # No QApplication yet -- don't cache, the font list isn't real.
            return ""
        _emoji_font = next(
            (f for f in EMOJI_FONT_CANDIDATES if f in installed), ""
        )
    return _emoji_font


def font_stack(*families):
    """Build a CSS font-family list with the system emoji font mixed in.

    The emoji family goes just before the generic fallback so real text keeps
    using the UI font and only missing glyphs fall through to emoji.
    """
    stack = list(families)
    emoji = emoji_font_family()
    if emoji and emoji not in stack:
        if stack and stack[-1] in GENERIC_FONT_FAMILIES:
            stack.insert(len(stack) - 1, emoji)
        else:
            stack.append(emoji)
    return ", ".join(
        f if f in GENERIC_FONT_FAMILIES else f"'{f}'" for f in stack
    )


def ui_font_stack():
    return font_stack("Inter", "Segoe UI", "Ubuntu", "sans-serif")


def mono_font_stack():
    return font_stack("JetBrains Mono", "monospace")


def with_emoji_fallback(font):
    """Let a QFont fall back to the emoji font for glyphs it doesn't have."""
    emoji = emoji_font_family()
    if emoji and hasattr(font, "setFamilies"):  # setFamilies() needs Qt 5.13+
        font.setFamilies([font.family(), emoji])
    return font


# Codepoints that bind to the character before them. Cutting a preview
# directly in front of one of these strands it and renders as a stray box.
_ZWJ = "‍"
_KEYCAP = "⃣"


def _joins_previous(ch):
    cp = ord(ch)
    return (
        ch in (_ZWJ, _KEYCAP)
        or 0xFE00 <= cp <= 0xFE0F          # variation selectors
        or 0x1F3FB <= cp <= 0x1F3FF        # skin tone modifiers
        or 0xE0020 <= cp <= 0xE007F        # tag characters (subdivision flags)
        or unicodedata.category(ch) in ("Mn", "Mc", "Me")
    )


def _is_regional_indicator(ch):
    return 0x1F1E6 <= ord(ch) <= 0x1F1FF


def truncate_preview(text, limit):
    """Cut text to ~limit chars without splitting an emoji or accent sequence.

    Returns (shortened_text, was_truncated).
    """
    if len(text) <= limit:
        return text, False

    cut = limit
    # Don't strand a combining mark, skin tone or variation selector.
    while cut > 0 and _joins_previous(text[cut]):
        cut -= 1
    # A ZWJ before the cut means the sequence continues past it -- drop it all.
    while cut > 0 and text[cut - 1] == _ZWJ:
        cut -= 1
        while cut > 0 and _joins_previous(text[cut]):
            cut -= 1
    # Flags are pairs of regional indicators; never keep half of one.
    run = 0
    while run < cut and _is_regional_indicator(text[cut - 1 - run]):
        run += 1
    if run % 2:
        cut -= 1

    return text[:cut], True


def global_stylesheet():
    t = THEME
    return f"""
        QMainWindow, QDialog {{
            background-color: {t['bg']};
            color: {t['text_primary']};
        }}
        QWidget {{
            color: {t['text_primary']};
            font-family: {ui_font_stack()};
            font-size: 13px;
        }}
        QToolTip {{
            background-color: {t['bg_surface']};
            color: {t['text_primary']};
            border: 1px solid {t['border']};
            border-radius: 6px;
            padding: 6px 10px;
        }}
        QMenu {{
            background-color: {t['bg_surface']};
            color: {t['text_primary']};
            border: 1px solid {t['border']};
            border-radius: 10px;
            padding: 6px;
        }}
        QMenu::item {{
            padding: 8px 28px 8px 16px;
            border-radius: 6px;
        }}
        QMenu::item:selected {{
            background: {t['accent_soft']};
            color: {t['accent_hover']};
        }}
        QMenu::separator {{
            height: 1px;
            background: {t['border']};
            margin: 4px 8px;
        }}
        QScrollBar:vertical {{
            background: transparent;
            width: 8px;
            margin: 4px 2px 4px 0;
        }}
        QScrollBar::handle:vertical {{
            background: {t['border']};
            border-radius: 4px;
            min-height: 32px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: {t['text_muted']};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
            height: 0; background: none;
        }}
        QScrollBar:horizontal {{
            height: 0px;
            background: transparent;
        }}
        QLineEdit {{
            background: {t['bg_input']};
            color: {t['text_primary']};
            border: 1px solid {t['border']};
            border-radius: {t['radius_md']};
            padding: 10px 14px;
            selection-background-color: {t['accent']};
        }}
        QLineEdit:focus {{
            border: 1px solid {t['border_focus']};
        }}
        QLineEdit::placeholder {{
            color: {t['text_muted']};
        }}
        QPlainTextEdit {{
            background: {t['bg_input']};
            color: {t['text_primary']};
            border: 1px solid {t['border']};
            border-radius: {t['radius_md']};
            padding: 12px;
            selection-background-color: {t['accent']};
        }}
        QPlainTextEdit:focus {{
            border: 1px solid {t['border_focus']};
        }}
        QListWidget {{
            background: transparent;
            border: none;
            outline: none;
        }}
        QListWidget::item {{
            background: transparent;
            border: none;
            padding: 0;
            margin: 0;
        }}
        QListWidget::item:selected {{
            background: transparent;
        }}
        QMessageBox, QInputDialog {{
            background-color: {t['bg_elevated']};
        }}
        QMessageBox QLabel, QInputDialog QLabel {{
            color: {t['text_primary']};
        }}
        /* High-contrast buttons for native dialogs (QMessageBox / QInputDialog) */
        QMessageBox QPushButton,
        QInputDialog QPushButton,
        QDialogButtonBox QPushButton {{
            background: {t['bg_surface']};
            color: {t['text_primary']};
            border: 1px solid {t['border']};
            border-radius: {t['radius_sm']};
            padding: 8px 20px;
            min-width: 84px;
            font-size: 13px;
            font-weight: 600;
        }}
        QMessageBox QPushButton:hover,
        QInputDialog QPushButton:hover,
        QDialogButtonBox QPushButton:hover {{
            background: {t['bg_hover']};
            border-color: {t['accent']};
            color: {t['accent_hover']};
        }}
        QMessageBox QPushButton:pressed,
        QInputDialog QPushButton:pressed,
        QDialogButtonBox QPushButton:pressed {{
            background: {t['accent']};
            color: white;
            border-color: {t['accent']};
        }}
        /* Default / focused action reads as the primary choice */
        QMessageBox QPushButton:default,
        QInputDialog QPushButton:default,
        QDialogButtonBox QPushButton:default,
        QMessageBox QPushButton:focus,
        QInputDialog QPushButton:focus,
        QDialogButtonBox QPushButton:focus {{
            background: {t['accent']};
            color: white;
            border: 1px solid {t['accent']};
        }}
    """


def btn_primary():
    t = THEME
    return f"""
        QPushButton {{
            background: {t['accent_gradient']};
            color: white;
            border: none;
            border-radius: {t['radius_sm']};
            padding: 9px 18px;
            font-size: 13px;
            font-weight: 600;
        }}
        QPushButton:hover {{
            background: {t['accent_hover']};
        }}
        QPushButton:pressed {{
            background: {t['accent']};
        }}
    """


def btn_secondary():
    t = THEME
    return f"""
        QPushButton {{
            background: {t['bg_surface']};
            color: {t['text_primary']};
            border: 1px solid {t['border']};
            border-radius: {t['radius_sm']};
            padding: 9px 16px;
            font-size: 13px;
            font-weight: 500;
        }}
        QPushButton:hover {{
            background: {t['bg_hover']};
            border-color: {t['accent']};
            color: {t['accent_hover']};
        }}
    """


def btn_ghost():
    t = THEME
    return f"""
        QPushButton {{
            background: transparent;
            color: {t['text_secondary']};
            border: none;
            border-radius: {t['radius_sm']};
            padding: 9px 14px;
            font-size: 13px;
            font-weight: 500;
        }}
        QPushButton:hover {{
            background: {t['bg_hover']};
            color: {t['text_primary']};
        }}
    """


def btn_danger():
    t = THEME
    return f"""
        QPushButton {{
            background: {t['error_soft']};
            color: {t['error']};
            border: 1px solid transparent;
            border-radius: {t['radius_sm']};
            padding: 9px 16px;
            font-size: 13px;
            font-weight: 600;
        }}
        QPushButton:hover {{
            background: {t['error']};
            color: white;
        }}
    """


def btn_icon(active=False, danger=False):
    t = THEME
    if danger:
        return f"""
            QPushButton {{
                background: transparent;
                color: {t['text_muted']};
                border: none;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 12px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background: {t['error_soft']};
                color: {t['error']};
            }}
        """
    if active:
        return f"""
            QPushButton {{
                background: {t['warning_soft']};
                color: {t['warning']};
                border: none;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 12px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background: {t['warning']};
                color: #0c0e14;
            }}
        """
    return f"""
        QPushButton {{
            background: transparent;
            color: {t['text_muted']};
            border: none;
            border-radius: 6px;
            padding: 6px 10px;
            font-size: 12px;
            font-weight: 500;
        }}
        QPushButton:hover {{
            background: {t['accent_soft']};
            color: {t['accent_hover']};
        }}
    """


def panel_style():
    t = THEME
    return f"""
        QFrame#Panel {{
            background: {t['bg_card']};
            border: 1px solid {t['border_subtle']};
            border-radius: {t['radius_lg']};
        }}
    """


# ---------------------------------------------------------------------------
# Editor with line numbers
# ---------------------------------------------------------------------------
class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QSize(self.editor.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        self.editor.lineNumberAreaPaintEvent(event)


class CodeEditor(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.lineNumberArea = LineNumberArea(self)
        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)
        self.updateLineNumberAreaWidth(0)
        self.highlightCurrentLine()

        mono = QFont("JetBrains Mono", 12)
        mono.setStyleHint(QFont.Monospace)
        self.setFont(with_emoji_fallback(mono))
        self.setStyleSheet(f"""
            QPlainTextEdit {{
                background: {THEME['bg_input']};
                color: {THEME['text_primary']};
                border: 1px solid {THEME['border']};
                border-radius: {THEME['radius_md']};
                padding: 8px;
                selection-background-color: {THEME['accent']};
            }}
            QPlainTextEdit:focus {{
                border: 1px solid {THEME['border_focus']};
            }}
        """)

    def lineNumberAreaWidth(self):
        digits = 1
        max_digits = max(1, self.blockCount())
        while max_digits >= 10:
            max_digits //= 10
            digits += 1
        return 12 + self.fontMetrics().horizontalAdvance('9') * digits

    def updateLineNumberAreaWidth(self, _=0):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def updateLineNumberArea(self, rect, dy):
        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()))

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.lineNumberArea)
        painter.fillRect(event.rect(), QColor(18, 22, 31))
        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                painter.setPen(QColor(92, 101, 120))
                painter.setFont(QFont("JetBrains Mono", 10))
                painter.drawText(
                    0, int(top), self.lineNumberArea.width() - 6,
                    self.fontMetrics().height(), Qt.AlignRight, str(blockNumber + 1)
                )
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            blockNumber += 1

    def highlightCurrentLine(self):
        extra = []
        if not self.isReadOnly():
            sel = QTextEdit.ExtraSelection()
            sel.format.setBackground(QColor(30, 36, 54))
            sel.format.setProperty(QTextFormat.FullWidthSelection, True)
            sel.cursor = self.textCursor()
            sel.cursor.clearSelection()
            extra.append(sel)
        self.setExtraSelections(extra)


# ---------------------------------------------------------------------------
# Clipboard monitor
# ---------------------------------------------------------------------------
class ClipboardMonitor(QThread):
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
                time.sleep(0.3)
            except Exception:
                pass

    def stop(self):
        self.running = False


# ---------------------------------------------------------------------------
# Empty state widget
# ---------------------------------------------------------------------------
class EmptyState(QFrame):
    def __init__(self, title, subtitle, parent=None):
        super().__init__(parent)
        self.setObjectName("EmptyState")
        self.setStyleSheet(f"""
            QFrame#EmptyState {{
                background: transparent;
                border: 1px dashed {THEME['border']};
                border-radius: {THEME['radius_lg']};
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(8)
        layout.setContentsMargins(32, 48, 32, 48)

        title_lbl = QLabel(title)
        title_lbl.setAlignment(Qt.AlignCenter)
        title_lbl.setStyleSheet(f"color: {THEME['text_secondary']}; font-size: 15px; font-weight: 600; border: none;")
        layout.addWidget(title_lbl)

        sub_lbl = QLabel(subtitle)
        sub_lbl.setAlignment(Qt.AlignCenter)
        sub_lbl.setWordWrap(True)
        sub_lbl.setStyleSheet(f"color: {THEME['text_muted']}; font-size: 13px; border: none;")
        layout.addWidget(sub_lbl)


# ---------------------------------------------------------------------------
# Status toast (quiet feedback)
# ---------------------------------------------------------------------------
class StatusToast(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setFixedHeight(0)
        self.hide()
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._hide)

    def show_message(self, text, kind="info"):
        colors = {
            "info": (THEME['accent_soft'], THEME['accent_hover']),
            "success": (THEME['success_soft'], THEME['success']),
            "error": (THEME['error_soft'], THEME['error']),
        }
        bg, fg = colors.get(kind, colors["info"])
        self.setText(text)
        self.setStyleSheet(f"""
            QLabel {{
                background: {bg};
                color: {fg};
                border-radius: {THEME['radius_sm']};
                padding: 8px 16px;
                font-size: 12px;
                font-weight: 600;
            }}
        """)
        self.setFixedHeight(36)
        self.show()
        self._timer.start(2200)

    def _hide(self):
        self.setFixedHeight(0)
        self.hide()


# ---------------------------------------------------------------------------
# Viewer / Editor dialog
# ---------------------------------------------------------------------------
class ViewerDialog(QDialog):
    def __init__(self, content="", parent=None, title="Clipboard Item"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(720, 520)
        self.resize(900, 680)
        self.edited_content = content

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(16)

        # Header
        header = QHBoxLayout()
        header.setSpacing(12)
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(f"color: {THEME['text_primary']}; font-size: 18px; font-weight: 700;")
        header.addWidget(title_lbl)
        header.addStretch()

        self.status_label = QLabel()
        self.status_label.setStyleSheet(f"color: {THEME['text_muted']}; font-size: 12px; font-weight: 500;")
        header.addWidget(self.status_label)
        root.addLayout(header)

        # Editor
        self.editor = CodeEditor()
        self.editor.setPlainText(content)
        self.editor.textChanged.connect(self._update_status)
        root.addWidget(self.editor, 1)

        # Footer actions
        footer = QHBoxLayout()
        footer.setSpacing(8)

        save_btn = QPushButton("Save Changes")
        save_btn.setStyleSheet(btn_primary())
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.clicked.connect(self._save)
        footer.addWidget(save_btn)

        copy_btn = QPushButton("Copy All")
        copy_btn.setStyleSheet(btn_secondary())
        copy_btn.setCursor(Qt.PointingHandCursor)
        copy_btn.clicked.connect(self._copy)
        footer.addWidget(copy_btn)

        footer.addStretch()

        close_btn = QPushButton("Close")
        close_btn.setStyleSheet(btn_ghost())
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.reject)
        footer.addWidget(close_btn)

        root.addLayout(footer)
        self._update_status()
        self.setStyleSheet(f"QDialog {{ background: {THEME['bg']}; }}")

    def _update_status(self):
        text = self.editor.toPlainText()
        chars = len(text)
        lines = text.count('\n') + 1 if text else 0
        self.status_label.setText(f"{chars:,} chars  ·  {lines:,} lines")

    def _save(self):
        self.edited_content = self.editor.toPlainText()
        self.accept()

    def _copy(self):
        QApplication.clipboard().setText(self.editor.toPlainText())
        self.status_label.setText("Copied to clipboard")
        self.status_label.setStyleSheet(f"color: {THEME['success']}; font-size: 12px; font-weight: 600;")
        QTimer.singleShot(1600, self._update_status)


# ---------------------------------------------------------------------------
# Env Manager dialog
# ---------------------------------------------------------------------------
class EnvDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Env Manager")
        self.setMinimumSize(700, 500)
        self.resize(920, 640)
        self.config = self._load_config()

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(16)

        # Header
        header = QHBoxLayout()
        title = QLabel("Env Manager")
        title.setStyleSheet(f"color: {THEME['text_primary']}; font-size: 18px; font-weight: 700;")
        header.addWidget(title)
        header.addStretch()

        subtitle = QLabel("Store and sync environment files")
        subtitle.setStyleSheet(f"color: {THEME['text_muted']}; font-size: 12px;")
        header.addWidget(subtitle)
        root.addLayout(header)

        # Command bar
        bar = QHBoxLayout()
        bar.setSpacing(8)

        add_btn = QPushButton("New File")
        add_btn.setStyleSheet(btn_primary())
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.clicked.connect(self.add_env_file)
        bar.addWidget(add_btn)

        pull_btn = QPushButton("Pull")
        pull_btn.setStyleSheet(btn_secondary())
        pull_btn.setCursor(Qt.PointingHandCursor)
        pull_btn.setToolTip("Pull env files from GitHub")
        pull_btn.clicked.connect(self.pull_from_github)
        bar.addWidget(pull_btn)

        push_btn = QPushButton("Push")
        push_btn.setStyleSheet(btn_secondary())
        push_btn.setCursor(Qt.PointingHandCursor)
        push_btn.setToolTip("Push env files to GitHub")
        push_btn.clicked.connect(self.push_to_github)
        bar.addWidget(push_btn)

        repo_btn = QPushButton("Set Repo")
        repo_btn.setStyleSheet(btn_ghost())
        repo_btn.setCursor(Qt.PointingHandCursor)
        repo_btn.clicked.connect(self.set_github_repo)
        bar.addWidget(repo_btn)

        bar.addStretch()
        root.addLayout(bar)

        self.toast = StatusToast()
        root.addWidget(self.toast)

        # File list
        self.env_list = QListWidget()
        self.env_list.setSpacing(8)
        self.env_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.env_list.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        root.addWidget(self.env_list, 1)

        self.empty = EmptyState("No env files yet", "Create a new file or pull from your GitHub repo")
        root.addWidget(self.empty)

        # Footer
        footer = QHBoxLayout()
        footer.addStretch()
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet(btn_ghost())
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.accept)
        footer.addWidget(close_btn)
        root.addLayout(footer)

        self.setStyleSheet(f"QDialog {{ background: {THEME['bg']}; }}")
        self.load_env_files()

    def _load_config(self):
        if os.path.exists(ENV_CONFIG):
            try:
                with open(ENV_CONFIG, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def save_config(self):
        with open(ENV_CONFIG, 'w') as f:
            json.dump(self.config, f, indent=2)

    def set_github_repo(self):
        url, ok = QInputDialog.getText(
            self, "Set Repo URL", "GitHub repo URL for env files:",
            text=self.config.get('repo_url', '')
        )
        if ok and url:
            self.config['repo_url'] = url
            self.save_config()
            self.toast.show_message(f"Repo set", "success")

    def add_env_file(self):
        name, ok1 = QInputDialog.getText(self, "New Env File", "Filename (e.g. myproject.env):")
        if not ok1 or not name:
            return
        desc, ok2 = QInputDialog.getText(self, "Description", "Short description:")
        if not ok2:
            return
        initial_content, ok3 = QInputDialog.getMultiLineText(self, "Initial Content", "Paste env content:")
        if not ok3:
            initial_content = ""

        os.makedirs(ENV_DIR, exist_ok=True)
        file_path = os.path.join(ENV_DIR, name)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(initial_content)

        if 'files' not in self.config:
            self.config['files'] = {}
        self.config['files'][name] = {
            'description': desc,
            'created_at': datetime.now().isoformat()
        }
        self.save_config()
        self.load_env_files()
        self.toast.show_message(f"Created {name}", "success")

    def load_env_files(self):
        self.env_list.clear()
        files = []
        if os.path.exists(ENV_DIR):
            files = [f for f in os.listdir(ENV_DIR) if not f.startswith('.') and os.path.isfile(os.path.join(ENV_DIR, f))]

        has_files = len(files) > 0
        self.env_list.setVisible(has_files)
        self.empty.setVisible(not has_files)

        for filename in sorted(files):
            self._add_env_item(filename)

    def _add_env_item(self, filename):
        widget = self._create_env_card(filename)
        item = QListWidgetItem()
        item.setSizeHint(QSize(0, widget.sizeHint().height()))
        self.env_list.addItem(item)
        self.env_list.setItemWidget(item, widget)

    def _create_env_card(self, filename):
        card = QFrame()
        card.setObjectName("EnvCard")
        card.setStyleSheet(f"""
            QFrame#EnvCard {{
                background: {THEME['bg_card']};
                border: 1px solid {THEME['border_subtle']};
                border-radius: {THEME['radius_md']};
            }}
            QFrame#EnvCard:hover {{
                border-color: {THEME['border']};
                background: {THEME['bg_hover']};
            }}
        """)
        layout = QHBoxLayout(card)
        layout.setContentsMargins(16, 14, 12, 14)
        layout.setSpacing(12)

        info = QVBoxLayout()
        info.setSpacing(3)
        name_lbl = QLabel(filename)
        name_lbl.setStyleSheet(f"color: {THEME['text_primary']}; font-size: 14px; font-weight: 600; border: none; background: transparent;")
        info.addWidget(name_lbl)

        meta = self.config.get('files', {}).get(filename, {})
        desc = meta.get('description', '')
        if desc:
            desc_lbl = QLabel(desc)
            desc_lbl.setStyleSheet(f"color: {THEME['text_muted']}; font-size: 12px; border: none; background: transparent;")
            info.addWidget(desc_lbl)
        layout.addLayout(info, 1)

        for label, handler, style in [
            ("View", lambda: self.view_env_file(filename), btn_icon()),
            ("Edit", lambda: self.edit_env_file(filename), btn_icon()),
            ("Copy", lambda: self.copy_env_file(filename), btn_icon()),
            ("Delete", lambda: self.delete_env_file(filename), btn_icon(danger=True)),
        ]:
            b = QPushButton(label)
            b.setStyleSheet(style)
            b.setCursor(Qt.PointingHandCursor)
            b.clicked.connect(handler)
            layout.addWidget(b)

        card.setMinimumHeight(64)
        return card

    def view_env_file(self, filename):
        path = os.path.join(ENV_DIR, filename)
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        ViewerDialog(content, self, title=filename).exec_()

    def edit_env_file(self, filename):
        path = os.path.join(ENV_DIR, filename)
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        dlg = ViewerDialog(content, self, title=f"Edit · {filename}")
        if dlg.exec_() == QDialog.Accepted:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(dlg.edited_content)
            self.toast.show_message(f"Saved {filename}", "success")

    def copy_env_file(self, filename):
        path = os.path.join(ENV_DIR, filename)
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        QApplication.clipboard().setText(content)
        self.toast.show_message(f"Copied {filename}", "success")

    def delete_env_file(self, filename):
        reply = QMessageBox.question(
            self, "Delete Env File",
            f"Delete {filename}? This cannot be undone.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            os.remove(os.path.join(ENV_DIR, filename))
            if 'files' in self.config and filename in self.config['files']:
                del self.config['files'][filename]
                self.save_config()
            self.load_env_files()
            self.toast.show_message(f"Deleted {filename}", "success")

    def pull_from_github(self):
        if not self.config.get('repo_url'):
            QMessageBox.warning(self, "No Repo", "Set a GitHub repo URL first.")
            return
        try:
            os.makedirs(ENV_DIR, exist_ok=True)
            git_dir = os.path.join(ENV_DIR, ".git")
            if not os.path.exists(git_dir):
                subprocess.check_call(["git", "init"], cwd=ENV_DIR)
                subprocess.check_call(["git", "remote", "add", "origin", self.config['repo_url']], cwd=ENV_DIR)
            subprocess.check_call(["git", "fetch", "origin"], cwd=ENV_DIR)
            try:
                subprocess.check_call(["git", "reset", "--hard", "origin/main"], cwd=ENV_DIR)
            except subprocess.CalledProcessError:
                subprocess.check_call(["git", "reset", "--hard", "origin/master"], cwd=ENV_DIR)
            self.load_env_files()
            self.toast.show_message("Pulled from GitHub", "success")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to pull:\n{e}")

    def push_to_github(self):
        if not self.config.get('repo_url'):
            QMessageBox.warning(self, "No Repo", "Set a GitHub repo URL first.")
            return
        try:
            os.makedirs(ENV_DIR, exist_ok=True)
            git_dir = os.path.join(ENV_DIR, ".git")
            if not os.path.exists(git_dir):
                subprocess.check_call(["git", "init"], cwd=ENV_DIR)
                subprocess.check_call(["git", "remote", "add", "origin", self.config['repo_url']], cwd=ENV_DIR)
            subprocess.check_call(["git", "add", "-A"], cwd=ENV_DIR)
            try:
                subprocess.check_call(["git", "commit", "-m", "Update env files"], cwd=ENV_DIR)
            except subprocess.CalledProcessError:
                pass
            try:
                subprocess.check_call(["git", "push", "-u", "origin", "main"], cwd=ENV_DIR)
            except subprocess.CalledProcessError:
                subprocess.check_call(["git", "push", "-u", "origin", "master"], cwd=ENV_DIR)
            self.toast.show_message("Pushed to GitHub", "success")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to push:\n{e}")


# ---------------------------------------------------------------------------
# Clipboard list item card
# ---------------------------------------------------------------------------
class ListItemWidget(QWidget):
    copy_clicked = pyqtSignal(str)
    view_clicked = pyqtSignal(str)
    delete_clicked = pyqtSignal(str)
    favorite_clicked = pyqtSignal(str)

    def __init__(self, content, idx, is_favorite=False, timestamp=None):
        super().__init__()
        self.content = content
        self.is_favorite = is_favorite
        self.setMinimumHeight(72)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        self.card = QFrame()
        self.card.setObjectName("ClipCard")
        self.card.setStyleSheet(f"""
            QFrame#ClipCard {{
                background: {THEME['bg_card']};
                border: 1px solid {THEME['border_subtle']};
                border-radius: {THEME['radius_md']};
            }}
            QFrame#ClipCard:hover {{
                border-color: {THEME['border']};
                background: {THEME['bg_hover']};
            }}
        """)

        layout = QHBoxLayout(self.card)
        layout.setContentsMargins(14, 12, 10, 12)
        layout.setSpacing(12)

        # Checkbox
        self.checkbox = QCheckBox()
        self.checkbox.setFixedSize(20, 20)
        self.checkbox.setCursor(Qt.PointingHandCursor)
        self.checkbox.setStyleSheet(f"""
            QCheckBox::indicator {{
                width: 18px; height: 18px;
                border-radius: 5px;
                border: 1.5px solid {THEME['border']};
                background: {THEME['bg_input']};
            }}
            QCheckBox::indicator:checked {{
                background: {THEME['accent']};
                border: none;
            }}
            QCheckBox::indicator:hover {{
                border-color: {THEME['accent']};
            }}
        """)
        layout.addWidget(self.checkbox, 0, Qt.AlignTop)

        # Content
        col = QVBoxLayout()
        col.setSpacing(4)
        col.setContentsMargins(0, 0, 0, 0)

        preview, truncated = truncate_preview(content, 140)
        preview = preview.replace('\n', ' ').strip()
        if truncated:
            preview += "…"
        self.content_label = QLabel(preview)
        self.content_label.setWordWrap(True)
        self.content_label.setStyleSheet(
            f"color: {THEME['text_primary']}; font-size: 13px; font-weight: 500; "
            f"border: none; background: transparent;"
        )
        col.addWidget(self.content_label)

        meta_row = QHBoxLayout()
        meta_row.setSpacing(8)
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp)
                time_str = dt.strftime("%H:%M · %b %d")
            except Exception:
                time_str = ""
            if time_str:
                time_lbl = QLabel(time_str)
                time_lbl.setStyleSheet(
                    f"color: {THEME['text_muted']}; font-size: 11px; border: none; background: transparent;"
                )
                meta_row.addWidget(time_lbl)

        chars = len(content)
        size_lbl = QLabel(f"{chars:,} chars")
        size_lbl.setStyleSheet(
            f"color: {THEME['text_muted']}; font-size: 11px; border: none; background: transparent;"
        )
        meta_row.addWidget(size_lbl)

        if is_favorite:
            fav_badge = QLabel("★ Favorited")
            fav_badge.setStyleSheet(
                f"color: {THEME['warning']}; font-size: 11px; font-weight: 600; "
                f"border: none; background: transparent;"
            )
            meta_row.addWidget(fav_badge)

        meta_row.addStretch()
        col.addLayout(meta_row)
        layout.addLayout(col, 1)

        # Actions
        actions = QHBoxLayout()
        actions.setSpacing(2)
        actions.setContentsMargins(0, 0, 0, 0)

        copy_btn = QPushButton("Copy")
        copy_btn.setStyleSheet(btn_icon())
        copy_btn.setCursor(Qt.PointingHandCursor)
        copy_btn.setToolTip("Copy to clipboard")
        copy_btn.clicked.connect(lambda: self.copy_clicked.emit(content))
        actions.addWidget(copy_btn)

        view_btn = QPushButton("View")
        view_btn.setStyleSheet(btn_icon())
        view_btn.setCursor(Qt.PointingHandCursor)
        view_btn.setToolTip("View / edit")
        view_btn.clicked.connect(lambda: self.view_clicked.emit(content))
        actions.addWidget(view_btn)

        self.star_btn = QPushButton("★" if is_favorite else "☆")
        self.star_btn.setStyleSheet(btn_icon(active=is_favorite))
        self.star_btn.setCursor(Qt.PointingHandCursor)
        self.star_btn.setToolTip("Toggle favorite")
        self.star_btn.clicked.connect(lambda: self.favorite_clicked.emit(content))
        actions.addWidget(self.star_btn)

        del_btn = QPushButton("✕")
        del_btn.setStyleSheet(btn_icon(danger=True))
        del_btn.setCursor(Qt.PointingHandCursor)
        del_btn.setToolTip("Delete")
        del_btn.clicked.connect(lambda: self.delete_clicked.emit(content))
        actions.addWidget(del_btn)

        layout.addLayout(actions)
        outer.addWidget(self.card)

    def sizeHint(self):
        return QSize(400, 78)


# ---------------------------------------------------------------------------
# Nav tab button
# ---------------------------------------------------------------------------
class TabButton(QPushButton):
    def __init__(self, text):
        super().__init__(text)
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {THEME['text_muted']};
                border: none;
                border-radius: {THEME['radius_sm']};
                padding: 8px 16px;
                font-size: 13px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                color: {THEME['text_primary']};
                background: {THEME['bg_hover']};
            }}
            QPushButton:checked {{
                background: {THEME['accent_soft']};
                color: {THEME['accent_hover']};
            }}
        """)


# ---------------------------------------------------------------------------
# Main window
# ---------------------------------------------------------------------------
class ClipboardManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.history_file = os.path.expanduser("~/.clipboard_history.json")
        self.config_file = os.path.expanduser("~/.klippboard_config.json")
        self.history = []
        self.selected_items = set()
        self.max_items = 100
        # Rebuild lists only when data changed (keeps tab switches instant)
        self._dirty = {"all": True, "fav": True, "today": True, "date": True}
        self._date_timer = QTimer(self)
        self._date_timer.setSingleShot(True)
        self._date_timer.timeout.connect(self._apply_pending_date)
        self._pending_date = None

        self.load_data()
        self.setup_ui()
        self.setup_tray()
        self.setup_monitoring()
        self.apply_theme()
        # Only build the visible list at startup; others wait until first open
        self.populate_all_items()
        self.update_stats()

    # ---- UI construction ----
    def setup_ui(self):
        self.setWindowTitle(APP_NAME)
        icon = APP_ICON or load_app_icon()
        if not icon.isNull():
            self.setWindowIcon(icon)
        self.setGeometry(120, 100, 1080, 720)
        self.setMinimumSize(780, 520)

        central = QWidget()
        main = QVBoxLayout(central)
        main.setContentsMargins(20, 16, 20, 16)
        main.setSpacing(14)

        # Header
        header = QHBoxLayout()
        header.setSpacing(12)

        brand = QVBoxLayout()
        brand.setSpacing(1)
        title = QLabel(APP_NAME)
        title.setStyleSheet(f"color: {THEME['text_primary']}; font-size: 20px; font-weight: 700;")
        brand.addWidget(title)
        subtitle = QLabel("Clipboard history · local & private")
        subtitle.setStyleSheet(f"color: {THEME['text_muted']}; font-size: 12px;")
        brand.addWidget(subtitle)
        header.addLayout(brand)
        header.addStretch()

        self.stats_chip = QLabel("0 items")
        self.stats_chip.setStyleSheet(f"""
            QLabel {{
                background: {THEME['bg_surface']};
                color: {THEME['text_secondary']};
                border: 1px solid {THEME['border_subtle']};
                border-radius: 20px;
                padding: 6px 14px;
                font-size: 12px;
                font-weight: 600;
            }}
        """)
        header.addWidget(self.stats_chip)

        env_btn = QPushButton("Env")
        env_btn.setFixedHeight(36)
        env_btn.setMinimumWidth(72)
        env_btn.setStyleSheet(btn_primary())
        env_btn.setCursor(Qt.PointingHandCursor)
        env_btn.setToolTip("Open Env Manager")
        env_btn.clicked.connect(self.open_env_manager)
        header.addWidget(env_btn)

        main.addLayout(header)

        # Nav tabs
        self.tab_buttons = []
        self.tab_group = QButtonGroup(self)
        self.tab_group.setExclusive(True)
        nav = QHBoxLayout()
        nav.setSpacing(4)
        tabs = ["All", "Favorites", "Today", "Calendar", "Help"]
        for i, text in enumerate(tabs):
            btn = TabButton(text)
            self.tab_group.addButton(btn, i)
            self.tab_buttons.append(btn)
            nav.addWidget(btn)
        self.tab_group.buttonClicked.connect(self._on_tab_button)
        nav.addStretch()
        main.addLayout(nav)

        # Toast
        self.toast = StatusToast()
        main.addWidget(self.toast)

        # Content stack
        self.content_area = QStackedWidget()
        main.addWidget(self.content_area, 1)

        self.content_area.addWidget(self.create_list_page("all"))
        self.content_area.addWidget(self.create_list_page("fav"))
        self.content_area.addWidget(self.create_list_page("today"))
        self.content_area.addWidget(self.create_calendar_page())
        self.content_area.addWidget(self.create_help_page())
        self.tab_buttons[0].setChecked(True)

        # Bottom toolbar — only bulk actions that matter
        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)

        select_all_btn = QPushButton("Select All")
        select_all_btn.setStyleSheet(btn_secondary())
        select_all_btn.setCursor(Qt.PointingHandCursor)
        select_all_btn.clicked.connect(self.select_all_items)
        toolbar.addWidget(select_all_btn)

        copy_sel_btn = QPushButton("Copy Selected")
        copy_sel_btn.setStyleSheet(btn_secondary())
        copy_sel_btn.setCursor(Qt.PointingHandCursor)
        copy_sel_btn.clicked.connect(self.copy_selected_items)
        toolbar.addWidget(copy_sel_btn)

        toolbar.addStretch()

        export_btn = QPushButton("Export")
        export_btn.setStyleSheet(btn_ghost())
        export_btn.setCursor(Qt.PointingHandCursor)
        export_btn.clicked.connect(self.export_history)
        toolbar.addWidget(export_btn)

        clear_btn = QPushButton("Clear All")
        clear_btn.setStyleSheet(btn_danger())
        clear_btn.setCursor(Qt.PointingHandCursor)
        clear_btn.clicked.connect(self.clear_all_items)
        toolbar.addWidget(clear_btn)

        main.addLayout(toolbar)
        self.setCentralWidget(central)

    def open_env_manager(self):
        EnvDialog(self).exec_()

    def create_list_page(self, kind):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        if kind == "all":
            self.all_search = QLineEdit()
            self.all_search.setPlaceholderText("Search clipboard history…")
            self.all_search.setClearButtonEnabled(True)
            self.all_search.textChanged.connect(self.filter_all_tab)
            layout.addWidget(self.all_search)

            stats = QHBoxLayout()
            self.stats_total = QLabel("0 items")
            self.stats_total.setStyleSheet(f"color: {THEME['text_secondary']}; font-size: 12px; font-weight: 600;")
            self.stats_fav = QLabel("0 favorites")
            self.stats_fav.setStyleSheet(f"color: {THEME['warning']}; font-size: 12px; font-weight: 600;")
            stats.addWidget(self.stats_total)
            stats.addSpacing(16)
            stats.addWidget(self.stats_fav)
            stats.addStretch()
            layout.addLayout(stats)

        list_map = {
            "all": "all_list",
            "fav": "fav_list",
            "today": "today_list",
        }
        empty_map = {
            "all": ("No clipboard history", "Copy something and it will appear here automatically"),
            "fav": ("No favorites yet", "Star an item to keep it within easy reach"),
            "today": ("Nothing today", "Items you copy today will show up here"),
        }

        lw = QListWidget()
        lw.setSpacing(8)
        lw.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        lw.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        lw.setUniformItemSizes(False)
        setattr(self, list_map[kind], lw)
        layout.addWidget(lw, 1)

        empty = EmptyState(*empty_map[kind])
        empty.hide()
        setattr(self, f"{kind}_empty", empty)
        layout.addWidget(empty)

        return page

    def create_calendar_page(self):
        page = QWidget()
        layout = QHBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # Calendar panel
        cal_panel = QFrame()
        cal_panel.setObjectName("Panel")
        cal_panel.setStyleSheet(panel_style())
        cal_panel.setMinimumWidth(280)
        cal_panel.setMaximumWidth(340)
        cal_lay = QVBoxLayout(cal_panel)
        cal_lay.setContentsMargins(16, 16, 16, 16)
        cal_lay.setSpacing(12)

        cal_title = QLabel("Browse by date")
        cal_title.setStyleSheet(f"color: {THEME['text_primary']}; font-size: 14px; font-weight: 700; border: none;")
        cal_lay.addWidget(cal_title)

        self.calendar = QCalendarWidget()
        self.calendar.clicked.connect(self.on_date_selected)
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        self.calendar.setGridVisible(False)
        self.calendar.setNavigationBarVisible(True)
        self.calendar.setStyleSheet(f"""
            QCalendarWidget {{
                background: transparent;
                color: {THEME['text_primary']};
                border: none;
            }}
            QCalendarWidget QWidget {{
                alternate-background-color: {THEME['bg_elevated']};
            }}
            QCalendarWidget QAbstractItemView {{
                background: {THEME['bg_input']};
                selection-background-color: {THEME['accent']};
                selection-color: white;
                color: {THEME['text_primary']};
                outline: none;
                border-radius: 8px;
                font-size: 12px;
            }}
            QCalendarWidget QToolButton {{
                background: {THEME['bg_surface']};
                color: {THEME['text_primary']};
                border: none;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 13px;
                font-weight: 600;
            }}
            QCalendarWidget QToolButton:hover {{
                background: {THEME['accent_soft']};
                color: {THEME['accent_hover']};
            }}
            QCalendarWidget QSpinBox {{
                background: {THEME['bg_input']};
                color: {THEME['text_primary']};
                border: 1px solid {THEME['border']};
                border-radius: 6px;
                padding: 2px 6px;
            }}
            QCalendarWidget QWidget#qt_calendar_navigationbar {{
                background: transparent;
            }}
        """)
        cal_lay.addWidget(self.calendar)
        layout.addWidget(cal_panel)

        # Date list panel
        list_panel = QFrame()
        list_panel.setObjectName("Panel")
        list_panel.setStyleSheet(panel_style())
        list_lay = QVBoxLayout(list_panel)
        list_lay.setContentsMargins(16, 16, 16, 16)
        list_lay.setSpacing(10)

        self.date_title = QLabel("Select a date")
        self.date_title.setStyleSheet(f"color: {THEME['text_primary']}; font-size: 14px; font-weight: 700; border: none;")
        list_lay.addWidget(self.date_title)

        self.date_search = QLineEdit()
        self.date_search.setPlaceholderText("Filter this date…")
        self.date_search.setClearButtonEnabled(True)
        self.date_search.textChanged.connect(self.filter_date_tab)
        list_lay.addWidget(self.date_search)

        self.date_list = QListWidget()
        self.date_list.setSpacing(8)
        self.date_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.date_list.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        list_lay.addWidget(self.date_list, 1)

        self.date_empty = EmptyState("No items for this date", "Pick another day or copy something new")
        self.date_empty.hide()
        list_lay.addWidget(self.date_empty)

        layout.addWidget(list_panel, 1)
        return page

    def create_help_page(self):
        page = QFrame()
        page.setObjectName("Panel")
        page.setStyleSheet(panel_style())
        layout = QVBoxLayout(page)
        layout.setContentsMargins(8, 8, 8, 8)

        help_text = QTextBrowser()
        help_text.setOpenExternalLinks(True)
        help_text.setHtml(f"""
        <style>
            body {{
                color: {THEME['text_primary']};
                font-family: {ui_font_stack()};
                font-size: 14px;
                line-height: 1.6;
                background: transparent;
            }}
            h1 {{
                font-size: 22px;
                font-weight: 700;
                margin: 8px 0 4px 0;
                color: {THEME['text_primary']};
            }}
            h2 {{
                font-size: 15px;
                font-weight: 700;
                margin: 28px 0 10px 0;
                color: {THEME['accent_hover']};
                letter-spacing: 0.02em;
            }}
            p {{ color: {THEME['text_secondary']}; margin: 6px 0; }}
            ul {{ color: {THEME['text_secondary']}; padding-left: 20px; }}
            li {{ margin: 6px 0; }}
            code {{
                background: {THEME['bg_input']};
                color: {THEME['accent_hover']};
                padding: 2px 7px;
                border-radius: 5px;
                font-family: {mono_font_stack()};
                font-size: 12px;
            }}
            a {{ color: {THEME['accent_hover']}; text-decoration: none; }}
            .muted {{ color: {THEME['text_muted']}; font-size: 12px; }}
            .card {{
                background: {THEME['bg_input']};
                border: 1px solid {THEME['border_subtle']};
                border-radius: 10px;
                padding: 14px 16px;
                margin: 10px 0;
            }}
            .kbd {{
                display: inline-block;
                background: {THEME['bg_surface']};
                border: 1px solid {THEME['border']};
                border-radius: 5px;
                padding: 2px 8px;
                font-family: monospace;
                font-size: 12px;
                color: {THEME['text_primary']};
            }}
        </style>

        <h1>KlippBoard <span class="muted">v{APP_VERSION}</span></h1>
        <p>A calm, local clipboard manager. Everything you copy stays on your machine —
        no accounts, no cloud, no tracking.</p>

        <div class="card">
            <b style="color:{THEME['text_primary']}">Quick start</b>
            <p style="margin-top:8px">
            <b>1.</b> Copy anything (<span class="kbd">Ctrl</span> + <span class="kbd">C</span>) — it lands in <b>All</b> automatically<br>
            <b>2.</b> Open KlippBoard from the Applications menu, the tray, or a shortcut you set yourself<br>
            <b>3.</b> Click <b>Copy</b> on any item to paste it back into your work<br>
            <b>4.</b> Star (<b>☆</b>) the clips you reuse, and search to find anything fast</p>
        </div>

        <h2>The tabs</h2>
        <ul>
            <li><b>All</b> — your full history, newest first, with a live search box</li>
            <li><b>Favorites</b> — only the clips you starred, kept safe and handy</li>
            <li><b>Today</b> — everything you copied today</li>
            <li><b>Calendar</b> — pick any date to see what you copied that day</li>
            <li><b>Help</b> — this page</li>
        </ul>

        <h2>Working with a clip</h2>
        <p>Each item is a card. Hover it and use the actions on the right:</p>
        <ul>
            <li><b>Copy</b> — put this clip back on the clipboard, ready to paste</li>
            <li><b>View</b> — open the full text in the editor to read or edit it</li>
            <li><b>☆ / ★</b> — add or remove it from Favorites</li>
            <li><b>✕</b> — delete this single clip (asks first)</li>
            <li><b>Checkbox</b> — select it for a bulk action below</li>
        </ul>

        <h2>Viewing &amp; editing</h2>
        <p>Click <b>View</b> to open a clip in the full editor. It shows line numbers and a
        live character / line count. Make changes and press <b>Save Changes</b> to update the
        stored clip, or <b>Copy All</b> to copy the whole thing.</p>

        <h2>Selecting &amp; bulk actions</h2>
        <p>Tick the checkbox on one or more cards, then use the bar at the bottom:</p>
        <ul>
            <li><b>Select All</b> — check every item in the current tab</li>
            <li><b>Copy Selected</b> — copy all checked clips together (separated by <code>---</code>)</li>
            <li><b>Export</b> — save your whole history to a timestamped <code>.txt</code> file in your home folder</li>
            <li><b>Clear All</b> — wipe the entire history (double confirmation, cannot be undone)</li>
        </ul>

        <h2>Search &amp; browse by date</h2>
        <p>In <b>All</b>, type in the search box to filter instantly (case-insensitive).
        In <b>Calendar</b>, click a day on the left to load that day's clips on the right,
        and use its filter box to narrow further.</p>

        <h2>Env Manager</h2>
        <p>Press the <b>Env</b> button in the top-right to manage project <code>.env</code> files:</p>
        <ul>
            <li><b>New File</b> — create an env file with a name, description and contents</li>
            <li><b>View / Edit / Copy</b> — open, change, or copy a file's contents</li>
            <li><b>Set Repo</b> — point KlippBoard at a private GitHub repo</li>
            <li><b>Push / Pull</b> — sync your env files to and from that repo with <code>git</code></li>
        </ul>
        <p class="muted">Requires <code>git</code> installed and access to the repo you configure.</p>

        <h2>Launch &amp; tray</h2>
        <ul>
            <li>Open from the Applications menu or run <code>klippboard</code> in a terminal</li>
            <li>Add your own keyboard shortcut in desktop Settings (see tip below)</li>
            <li>Double-click the tray icon — show / hide the window</li>
            <li>Right-click the tray icon — Show or Quit</li>
            <li>Closing the window minimizes to the tray (KlippBoard keeps capturing)</li>
            <li>To fully exit, use <b>Quit</b> from the tray menu</li>
        </ul>

        <h2>Tips</h2>
        <ul>
            <li>History keeps your most recent 100 items automatically.</li>
            <li>To open KlippBoard with a key combo: open
                <b>Settings → Keyboard → Custom Shortcuts</b>, add a shortcut named
                KlippBoard with command <code>klippboard</code>, and choose your keys
                (e.g. Ctrl+Alt+V). Full steps are in INSTALLATION.md.</li>
            <li>Star clips you paste often — they stay in <b>Favorites</b> even as history rolls over.</li>
        </ul>

        <h2>Privacy</h2>
        <p>History lives in <code>~/.clipboard_history.json</code>. Env files live in
        <code>~/.klippboard_env/</code>. Nothing ever leaves your computer unless you
        push env files yourself.</p>

        <p class="muted" style="margin-top:32px">Made by
        <a href="{REPO_URL}">johnboscocjt</a> · MIT License · v{APP_VERSION}</p>
        """)
        help_text.setStyleSheet(f"""
            QTextBrowser {{
                background: transparent;
                border: none;
                padding: 12px 16px;
            }}
        """)
        layout.addWidget(help_text)
        return page

    def _on_tab_button(self, button):
        self.switch_tab(self.tab_group.id(button))

    def switch_tab(self, index):
        # Pane first for instant feedback; rebuild only if that list is stale
        if 0 <= index < len(self.tab_buttons):
            self.tab_buttons[index].setChecked(True)
        self.content_area.setCurrentIndex(index)
        if index == 0 and self._dirty.get("all"):
            self.populate_all_items()
        elif index == 1 and self._dirty.get("fav"):
            self.populate_favorites()
        elif index == 2 and self._dirty.get("today"):
            self.populate_today()

    # ---- Tray / theme / data ----
    def setup_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        icon = APP_ICON or load_app_icon()
        if icon.isNull():
            style = self.style()
            icon = style.standardIcon(QStyle.SP_ComputerIcon)
            if icon.isNull():
                icon = style.standardIcon(QStyle.SP_ArrowForward)
        self.tray_icon.setIcon(icon)
        self.tray_icon.setToolTip(f"{APP_NAME} v{APP_VERSION}")

        tray_menu = QMenu(self)
        show_action = tray_menu.addAction("Show KlippBoard")
        show_action.triggered.connect(self.show)
        tray_menu.addSeparator()
        quit_action = tray_menu.addAction("Quit")
        quit_action.triggered.connect(self.quit_app)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_icon_activated)
        self.tray_icon.show()

    def tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            if self.isVisible():
                self.hide()
            else:
                self.show()
                self.raise_()
                self.activateWindow()

    def quit_app(self):
        self.monitor.stop()
        QApplication.instance().quit()

    def apply_theme(self):
        self.setStyleSheet(global_stylesheet())

    def load_data(self):
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
        except Exception:
            self.history = []
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    json.load(f)
        except Exception:
            pass

    def save_data(self):
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.history[:self.max_items], f, indent=2, ensure_ascii=False)
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump({}, f)

    def setup_monitoring(self):
        self.monitor = ClipboardMonitor()
        self.monitor.clipboard_changed.connect(self.on_clipboard_changed)
        self.monitor.start()

    # ---- History management ----
    def on_clipboard_changed(self, content):
        if any(item.get('content') == content for item in self.history):
            return
        self.history.insert(0, {
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'favorite': False
        })
        self.save_data()
        self.mark_lists_dirty()
        self.refresh_visible_list()
        self.update_stats()

    def mark_lists_dirty(self):
        self._dirty = {"all": True, "fav": True, "today": True, "date": True}

    def refresh_visible_list(self):
        idx = self.content_area.currentIndex()
        if idx == 0:
            self.populate_all_items()
        elif idx == 1:
            self.populate_favorites()
        elif idx == 2:
            self.populate_today()
        elif idx == 3 and self._pending_date is not None:
            self._fill_date_list(self._pending_date)

    def add_item_widget(self, list_widget, item, idx):
        content = item.get('content', '')
        is_fav = item.get('favorite', False)
        timestamp = item.get('timestamp', None)

        widget = ListItemWidget(content, idx, is_fav, timestamp)
        widget.copy_clicked.connect(self.quick_copy)
        widget.view_clicked.connect(self.quick_view)
        widget.delete_clicked.connect(self.quick_delete)
        widget.favorite_clicked.connect(self.quick_favorite)
        widget.checkbox.stateChanged.connect(lambda s, c=content: self.toggle_select(c, s))

        list_item = QListWidgetItem()
        list_item.setSizeHint(QSize(400, 78))
        list_widget.addItem(list_item)
        list_widget.setItemWidget(list_item, widget)

    def _set_list_empty(self, list_widget, empty_widget, count):
        list_widget.setVisible(count > 0)
        empty_widget.setVisible(count == 0)

    def _fill_list(self, list_widget, empty_widget, items, dirty_key):
        list_widget.setUpdatesEnabled(False)
        list_widget.blockSignals(True)
        try:
            list_widget.clear()
            for idx, item in enumerate(items, 1):
                self.add_item_widget(list_widget, item, idx)
        finally:
            list_widget.blockSignals(False)
            list_widget.setUpdatesEnabled(True)
        self._set_list_empty(list_widget, empty_widget, len(items))
        self._dirty[dirty_key] = False

    def populate_all_items(self):
        query = ""
        if hasattr(self, "all_search"):
            query = self.all_search.text().strip()
        if query:
            items = [i for i in self.history if query.lower() in i.get('content', '').lower()]
        else:
            items = list(self.history)
        self._fill_list(self.all_list, self.all_empty, items, "all")
        if not items and query:
            labels = self.all_empty.findChildren(QLabel)
            if len(labels) >= 2:
                labels[0].setText("No matches")
                labels[1].setText(f"Nothing found for “{query}”")
        elif not query:
            labels = self.all_empty.findChildren(QLabel)
            if len(labels) >= 2:
                labels[0].setText("No clipboard history")
                labels[1].setText("Copy something and it will appear here automatically")
        self.update_stats()

    def populate_favorites(self):
        fav_items = [i for i in self.history if i.get('favorite', False)]
        self._fill_list(self.fav_list, self.fav_empty, fav_items, "fav")

    def populate_today(self):
        today = date.today()
        today_items = []
        for i in self.history:
            try:
                if datetime.fromisoformat(i.get('timestamp', '')).date() == today:
                    today_items.append(i)
            except Exception:
                pass
        self._fill_list(self.today_list, self.today_empty, today_items, "today")

    def on_date_selected(self, qdate):
        # Debounce rapid calendar clicks so the UI stays responsive
        self._pending_date = qdate.toPyDate()
        self.date_title.setText(self._pending_date.strftime("%A, %b %d %Y"))
        self._date_timer.start(40)

    def _apply_pending_date(self):
        if self._pending_date is None:
            return
        self._fill_date_list(self._pending_date)

    def _fill_date_list(self, selected):
        query = ""
        if hasattr(self, "date_search"):
            query = self.date_search.text().strip().lower()
        date_items = []
        for i in self.history:
            try:
                if datetime.fromisoformat(i.get('timestamp', '')).date() != selected:
                    continue
                content = i.get('content', '')
                if query and query not in content.lower():
                    continue
                date_items.append(i)
            except Exception:
                pass
        self._fill_list(self.date_list, self.date_empty, date_items, "date")

    def filter_all_tab(self, text):
        self._dirty["all"] = True
        self.populate_all_items()

    def filter_date_tab(self, text):
        selected = self.calendar.selectedDate().toPyDate()
        self._pending_date = selected
        self._fill_date_list(selected)

    def toggle_select(self, content, state):
        if state == Qt.Checked:
            self.selected_items.add(content)
        else:
            self.selected_items.discard(content)

    def select_all_items(self):
        self.selected_items.clear()
        current_idx = self.content_area.currentIndex()
        lists = [self.all_list, self.fav_list, self.today_list, self.date_list]
        if current_idx >= len(lists):
            return
        widget = lists[current_idx]
        for i in range(widget.count()):
            item_widget = widget.itemWidget(widget.item(i))
            if item_widget:
                item_widget.checkbox.setChecked(True)
        self.toast.show_message(f"Selected {len(self.selected_items)} items", "info")

    def update_stats(self):
        total = len(self.history)
        favorites = sum(1 for i in self.history if i.get('favorite', False))
        self.stats_total.setText(f"{total} item{'s' if total != 1 else ''}")
        self.stats_fav.setText(f"{favorites} favorite{'s' if favorites != 1 else ''}")
        self.stats_chip.setText(f"{total} items")

    def quick_copy(self, content):
        QApplication.clipboard().setText(content)
        # Avoid re-capturing the same content as a new history entry immediately
        if hasattr(self, 'monitor'):
            self.monitor.last_content = content
        self.toast.show_message("Copied", "success")

    def quick_view(self, content):
        viewer = ViewerDialog(content, self)
        if viewer.exec_() == QDialog.Accepted:
            for item in self.history:
                if item.get('content') == content:
                    item['content'] = viewer.edited_content
                    break
            self.save_data()
            self.mark_lists_dirty()
            self.refresh_visible_list()
            self.update_stats()
            self.toast.show_message("Saved changes", "success")

    def quick_delete(self, content):
        reply = QMessageBox.question(
            self, "Delete Item", "Delete this clipboard item?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.history = [i for i in self.history if i.get('content') != content]
            self.save_data()
            self.selected_items.discard(content)
            self.mark_lists_dirty()
            self.refresh_visible_list()
            self.update_stats()
            self.toast.show_message("Deleted", "success")

    def quick_favorite(self, content):
        for item in self.history:
            if item.get('content') == content:
                item['favorite'] = not item.get('favorite', False)
                starred = item['favorite']
                break
        else:
            return
        self.save_data()
        self.mark_lists_dirty()
        self.refresh_visible_list()
        self.update_stats()
        self.toast.show_message("Favorited" if starred else "Removed from favorites", "success")

    def copy_selected_items(self):
        if not self.selected_items:
            self.toast.show_message("Select items first", "info")
            return
        text = "\n---\n".join(self.selected_items)
        QApplication.clipboard().setText(text)
        if hasattr(self, 'monitor'):
            self.monitor.last_content = text
        self.toast.show_message(f"Copied {len(self.selected_items)} items", "success")

    def export_history(self):
        if not self.history:
            self.toast.show_message("Nothing to export", "info")
            return
        filename = f"{os.path.expanduser('~')}/clipboard_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                for i, item in enumerate(self.history, 1):
                    f.write(f"[{i}] {item.get('timestamp', 'N/A')}\n")
                    f.write(f"{item.get('content', '')}\n")
                    f.write("\n" + "─" * 60 + "\n\n")
            self.toast.show_message("Exported", "success")
            QMessageBox.information(self, "Export Complete", f"Saved to:\n{filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export:\n{e}")

    def clear_all_items(self):
        reply = QMessageBox.question(
            self, "Clear All?",
            "Delete ALL clipboard history?\nThis cannot be undone.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return
        reply2 = QMessageBox.question(
            self, "Confirm Clear",
            "Are you absolutely sure?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply2 == QMessageBox.Yes:
            self.history = []
            self.selected_items.clear()
            self.save_data()
            self.mark_lists_dirty()
            self.refresh_visible_list()
            if hasattr(self, "date_list"):
                self.date_list.clear()
                self._set_list_empty(self.date_list, self.date_empty, 0)
            self.update_stats()
            self.toast.show_message("History cleared", "success")

    def closeEvent(self, event):
        event.ignore()
        self.hide()


def main():
    # Better font rendering on Linux
    os.environ.setdefault("QT_AUTO_SCREEN_SCALE_FACTOR", "1")
    app = QApplication(sys.argv)
    # Application name MUST match StartupWMClass for the taskbar icon
    app.setApplicationName(APP_NAME)
    app.setApplicationDisplayName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    # Lets GNOME/KDE map this window to klippboard.desktop
    if hasattr(app, "setDesktopFileName"):
        app.setDesktopFileName(DESKTOP_FILE_ID)
    app.setQuitOnLastWindowClosed(False)
    app.setStyle("Fusion")

    global APP_ICON
    APP_ICON = load_app_icon()
    if not APP_ICON.isNull():
        app.setWindowIcon(APP_ICON)

    # App-level stylesheet so every dialog (QMessageBox / QInputDialog) is styled
    app.setStyleSheet(global_stylesheet())

    manager = ClipboardManager()
    manager.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
