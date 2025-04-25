import { app, BrowserWindow, ipcMain } from 'electron';
import * as path from 'path';

// Handle creating/removing shortcuts on Windows when installing/uninstalling
if (require('electron-squirrel-startup')) {
  app.quit();
}

let mainWindow: BrowserWindow | null = null;

const createWindow = (): void => {
  // Create the browser window
  mainWindow = new BrowserWindow({
    width: 1024,
    height: 768,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js'),
    },
  });

  // Load the index.html
  if (process.env.NODE_ENV === 'development') {
    // Load from webpack dev server in development
    mainWindow.loadFile(path.join(__dirname, '../index.html'));
    // Open DevTools in development mode
    mainWindow.webContents.openDevTools();
  } else {
    // Load the local file in production
    mainWindow.loadFile(path.join(__dirname, '../index.html'));
    // Temporarily open DevTools in production mode for debugging
    mainWindow.webContents.openDevTools();
  }

  // Event handlers
  mainWindow.on('closed', () => {
    mainWindow = null;
  });
};

// Create window when Electron is ready
app.on('ready', createWindow);

// Quit when all windows are closed, except on macOS
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// Re-create window on macOS when dock icon is clicked
app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

// IPC handlers for communication with renderer process
ipcMain.handle('app-info', () => {
  return {
    appName: app.getName(),
    appVersion: app.getVersion(),
    platform: process.platform,
    // Additional app info can be added here
  };
});

// Handle any other IPC messages here 