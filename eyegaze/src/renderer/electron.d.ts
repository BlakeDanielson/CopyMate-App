interface AppInfo {
  appName: string;
  appVersion: string;
  platform: string;
}

interface ElectronAPI {
  getAppInfo: () => Promise<AppInfo>;
  // Add additional API methods here as they're implemented
}

declare global {
  interface Window {
    api: ElectronAPI;
  }
} 