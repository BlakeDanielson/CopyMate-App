import { contextBridge, ipcRenderer } from 'electron';

console.log('Preload script running');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('api', {
  // App info
  getAppInfo: () => ipcRenderer.invoke('app-info'),
  
  // Add additional API methods here
  // Example:
  // startVideoCapture: () => ipcRenderer.invoke('start-video-capture'),
  // stopVideoCapture: () => ipcRenderer.invoke('stop-video-capture'),
});

console.log('API exposed to renderer'); 