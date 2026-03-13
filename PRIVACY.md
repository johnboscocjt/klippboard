# 🔐 Privacy & Security (2026)

## Overview

KlippBoard is **100% local and private**. No data ever leaves your computer.

## Data Storage

Your clipboard history is saved in:
```
~/.clipboard_history.json
```

This file contains:
- Clipboard text you copied
- Timestamp of copy
- Favorite flag (true/false)

**Nothing else.** No:
- ❌ User ID or account info
- ❌ IP addresses
- ❌ Browsing history
- ❌ System info
- ❌ Analytics or tracking

## Security

### Local Only
- 100% runs on your computer
- No network connections
- No cloud sync
- No external servers

### File Permissions
Default permissions: `-rw-r--r-- (644)`

Make it private:
```bash
chmod 600 ~/.clipboard_history.json
```

### Delete All Data
```bash
rm ~/.clipboard_history.json
```

App will create new history next run.

## Open Source

- Full source code on GitHub
- MIT License (free to use)
- Anyone can audit the code
- No hidden features

## What's Monitored?

Your clipboard:
- Is monitored locally
- New items added to history
- Duplicates skipped
- Old items removed when limit reached

## Third-Party Libraries

### PyQt5
- GUI framework
- Renders interface locally
- No data collection

### keyboard
- Detects hotkey press
- Runs locally
- No tracking

Both are open source and auditable.

## Best Practices

1. **Keep system updated** - Install security patches
2. **Restrict file permissions** - `chmod 600 ~/.clipboard_history.json`
3. **Don't copy secrets** - Be careful with passwords/tokens
4. **Use strong password** - Protects your account
5. **Lock screen** - When away from computer

## Questions?

- Review source code
- Check GitHub issues
- Read this file thoroughly

**Your privacy is paramount.** ❤️
