# 📝 Changelog

## Unreleased

### 😀 Emoji support
- **Emoji now render properly** - copied emoji showed up as empty boxes (tofu)
  because the UI font stack named no emoji family and Qt would not reach for
  the system emoji font by itself. Every font stack now includes the first
  emoji font actually installed (Noto Color Emoji / Apple Color Emoji /
  Segoe UI Emoji / …), detected at runtime.
- **Previews no longer split emoji** - truncating an item at 140 characters
  could cut through a multi-codepoint sequence (family, skin tone, flag,
  accent) and leave a stray box. Previews now cut on sequence boundaries.
- **UTF-8 for all file I/O** - history, env files and `Export History` used the
  locale's default encoding. On a non-UTF-8 locale that makes `Export History`
  fail with `UnicodeEncodeError` as soon as any item contains an emoji, and
  makes env files unreadable. All of them now specify `encoding='utf-8'`.

## v1.0.0 - Release (2026)

### ✨ Full Featured Release
- **Line numbers in editor** - View line numbers on left sidebar  
- **Character & line count** - See total characters and lines
- **Collapsible calendar** - Hide calendar panel for more space
- **Search in date** - Filter items from selected date
- **Improved star icons** - ★ filled / ☆ empty
- **Relevant emoji buttons** - Distinct icons for all actions
- **Complete help page** - Detailed line-by-line documentation
- **Select All per-tab** - Select works for current tab only
- **Clear All button** - Double confirmation prevents accidents
- **Hotkey configuration** - Configurable global hotkey (⚙ button)
- **Fixed calendar text** - Monday-Friday headers now BLACK
- **Edit Selected** - Edit button in toolbar
- **Export History** - Export clipboard as text file
- **Refresh** - Refresh all tabs button
- **Stats Display** - Shows total items and favorites count
- **GitHub Link** - Quick link to GitHub repository
- **Window Size** - Normal window (not fullscreen by default)

### 🎨 UI Improvements
- Dark theme with glass morphism
- Professional color scheme
- Intuitive icon usage
- Responsive design
- Better readability

### 🚀 Performance
- Fast startup (< 2 seconds)
- Optimized memory usage
- No crashes
- Responsive UI

---

Made with ❤️ by [johnboscocjt](https://github.com/johnboscocjt/)
Copyright © 2026
