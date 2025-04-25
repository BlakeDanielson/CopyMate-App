# GazeShift Developer Setup Guide

This document provides instructions for setting up your development environment to work on the GazeShift project.

## Prerequisites

Before beginning, ensure you have the following installed:

- **Node.js** (v20 LTS or later): [Download from nodejs.org](https://nodejs.org/)
- **Git**: [Download from git-scm.com](https://git-scm.com/downloads)
- **Visual Studio Code** (recommended): [Download from code.visualstudio.com](https://code.visualstudio.com/)
- **Yarn** (optional but recommended): `npm install -g yarn`

### Platform-Specific Requirements

#### macOS
- macOS 12 (Monterey) or newer
- Xcode Command Line Tools: `xcode-select --install`
- [Homebrew](https://brew.sh/) (recommended)

#### Windows
- Windows 10 (64-bit) or Windows 11
- Visual Studio Build Tools with Desktop development with C++ workload
- Windows 10 SDK

## Setting Up the Development Environment

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/gazeshift.git
cd gazeshift
```

### 2. Install Dependencies

Using npm:
```bash
npm install
```

Or using yarn (recommended):
```bash
yarn install
```

### 3. Install Recommended VS Code Extensions

We recommend the following VS Code extensions for development:

- ESLint
- Prettier
- React Developer Tools
- TypeScript and JavaScript Language Features

You can install them from the Extensions view (Ctrl+Shift+X) in VS Code.

### 4. Set Up Platform-Specific Development Tools

#### macOS Virtual Camera Development

1. Install additional dependencies:
```bash
brew install cmake pkg-config
```

2. Set up AVFoundation development permissions:
```bash
# Enable developer mode
sudo DevToolsSecurity -enable
# Add current user to developer group
sudo dscl . -append /Groups/_developer GroupMembership $(whoami)
```

#### Windows Virtual Camera Development

1. Install DirectShow Filter dependencies:
```bash
# Using PowerShell as Administrator
npm run install-directshow-deps
```

2. Register test certificates for development:
```bash
npm run register-dev-certs
```

## Project Structure

```
├── docs/                  # Documentation
├── src/                   # Source code
│   ├── main/              # Electron main process
│   ├── renderer/          # Electron renderer process (React)
│   ├── common/            # Shared code
│   ├── ai/                # AI processing modules
│   ├── virtualcam/        # Virtual camera implementations
│   └── notes/             # Note management system
├── assets/                # Static assets
├── build/                 # Build configuration
├── test/                  # Tests
└── scripts/               # Build and utility scripts
```

## Development Workflow

### Starting the Development Server

```bash
# Start in development mode
npm run dev

# Or with yarn
yarn dev
```

This will start the Electron app with hot-reload enabled.

### Running Tests

```bash
# Run all tests
npm run test

# Run specific test suite
npm run test -- -t "Component Name"

# Run with coverage report
npm run test:coverage
```

### Building for Production

```bash
# Build for current platform
npm run build

# Build for specific platform
npm run build:mac
npm run build:win
```

## Working with the AI Pipeline

The AI pipeline requires additional setup for development:

1. Download the pre-trained models:
```bash
npm run download-models
```

2. Set up TensorFlow/ONNX development environment:
```bash
npm run setup-ai-dev
```

## Virtual Camera Development

### Testing Virtual Camera Output

We provide a helper tool for testing the virtual camera output:

```bash
npm run test:virtualcam
```

This launches a simple test application that shows both the input and output camera feeds.

### macOS-Specific Camera Development

For macOS development, you need to build and install the virtual camera extension:

```bash
npm run build:cam:mac
npm run install:cam:mac
```

### Windows-Specific Camera Development

For Windows development, register the DirectShow filter:

```bash
npm run register:cam:win
```

## Contribution Guidelines

1. Create a feature branch from `develop` branch
2. Make your changes
3. Ensure tests pass
4. Submit a pull request to `develop`

Please refer to CONTRIBUTING.md for detailed contribution guidelines.

## Debugging

### Main Process Debugging

You can debug the main process in VS Code using the "Debug Main Process" launch configuration.

### Renderer Process Debugging

For renderer (UI) debugging, you can use Chrome DevTools by pressing F12 in the running application.

### Enabling Debug Logs

Set the environment variable `DEBUG=gazeshift:*` to enable detailed logging:

```bash
# macOS/Linux
DEBUG=gazeshift:* npm run dev

# Windows (PowerShell)
$env:DEBUG="gazeshift:*"; npm run dev
```

## Common Issues

### Virtual Camera Not Installing

#### macOS
- Ensure you have proper permissions: `sudo chmod -R a+rwx /Library/CoreMediaIO/Plug-Ins/DAL`
- Restart the coreaudiod service: `sudo killall coreaudiod`

#### Windows
- Run as Administrator when registering the DirectShow filter
- Check Windows Security settings if camera access is blocked

### Build Errors

- Clear node_modules and reinstall: `rm -rf node_modules && yarn install`
- Ensure you have the correct Node.js version: `nvm use`
- Check platform-specific dependencies are installed

## Additional Resources

- [Electron Documentation](https://www.electronjs.org/docs)
- [React Documentation](https://reactjs.org/docs)
- [MediaPipe Documentation](https://google.github.io/mediapipe/)
- [TensorFlow Lite Documentation](https://www.tensorflow.org/lite/guide)
- [DirectShow Documentation](https://docs.microsoft.com/en-us/windows/win32/directshow/directshow)
- [AVFoundation Documentation](https://developer.apple.com/av-foundation/) 