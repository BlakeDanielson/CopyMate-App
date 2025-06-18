# CopyMate 📋

A simple, lightweight clipboard manager for macOS built with Tauri, React, and TypeScript.

## ✨ Features

- **Automatic Clipboard Monitoring**: Instantly captures any text you copy
- **Clean, Compact UI**: Shows your last 3 clipboard items with scrolling for more
- **Single-Click Copying**: Click any item to instantly copy it back to your clipboard  
- **No Duplicates**: Smart detection prevents duplicate entries
- **Always On Top**: Quick access without switching apps
- **Lightweight**: Built with Tauri for minimal system resources

## 📥 Download & Installation

### For End Users

**[Download CopyMate v0.1.0 DMG](https://github.com/BlakeDanielson/CopyMate/releases/tag/v0.1.0)**

1. Download the DMG file from the release page
2. Open the downloaded DMG file
3. Drag CopyMate to your Applications folder
4. Launch from Applications
   - **First time**: Right-click → "Open" (required for unsigned apps)
   - **Subsequent launches**: Double-click normally

### System Requirements
- macOS (Apple Silicon/Intel)
- No additional dependencies required

## 🛠️ Development

### Prerequisites
- Node.js (18+)
- Rust (latest stable)
- Xcode Command Line Tools

### Setup
```bash
# Clone the repository
git clone https://github.com/BlakeDanielson/CopyMate.git
cd CopyMate

# Install dependencies
npm install

# Run in development mode
npm run tauri dev
```

### Building
```bash
# Build for production
npm run tauri build

# Output locations:
# - App Bundle: src-tauri/target/release/bundle/macos/copy-mate.app
# - DMG Installer: src-tauri/target/release/bundle/macos/*.dmg
```

## 🏗️ Tech Stack

- **Frontend**: React + TypeScript + Vite
- **Backend**: Rust + Tauri
- **Styling**: CSS3 with modern UI patterns
- **Clipboard**: Tauri Clipboard Plugin

## 📝 Usage

1. Launch CopyMate - it runs in the background
2. Copy any text from any application
3. Your clipboard history appears automatically
4. Click any item to copy it back to your clipboard
5. Use the "Clear All" button to reset your history

## 🚀 Roadmap

- [ ] Data persistence across app restarts
- [ ] Search functionality for clipboard history  
- [ ] Keyboard shortcuts for quick access
- [ ] Support for images and rich content
- [ ] Windows and Linux support

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License - see LICENSE file for details

---

**⭐ Star this repo if CopyMate helps you stay organized!**
