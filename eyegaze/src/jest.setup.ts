import '@testing-library/jest-dom';

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Mock ImageData class if it doesn't exist in the test environment
if (typeof ImageData === 'undefined') {
  global.ImageData = class ImageData {
    data: Uint8ClampedArray;
    width: number;
    height: number;
    colorSpace: PredefinedColorSpace;

    constructor(width: number, height: number) {
      this.width = width;
      this.height = height;
      this.data = new Uint8ClampedArray(width * height * 4);
      this.colorSpace = 'srgb';
    }
  } as unknown as typeof ImageData;
}

// Mock MediaDevices API
if (!window.MediaDevices) {
  Object.defineProperty(window, 'MediaDevices', {
    writable: true,
    value: jest.fn(),
  });
}

// Mock navigator.mediaDevices
Object.defineProperty(global.navigator, 'mediaDevices', {
  writable: true,
  value: {
    getUserMedia: jest.fn(),
    enumerateDevices: jest.fn().mockResolvedValue([
      { 
        deviceId: 'mock-device-id-1', 
        kind: 'videoinput', 
        label: 'Mock Webcam 1',
        groupId: 'mock-group-1' 
      },
      { 
        deviceId: 'mock-device-id-2', 
        kind: 'videoinput', 
        label: 'Mock Webcam 2',
        groupId: 'mock-group-2' 
      }
    ]),
  },
});

// Mock requestAnimationFrame
global.requestAnimationFrame = (callback: FrameRequestCallback): number => {
  return setTimeout(() => callback(Date.now()), 0) as unknown as number;
};

global.cancelAnimationFrame = (id: number): void => {
  clearTimeout(id);
};

// Mock window.api for Electron
if (!window.api) {
  Object.defineProperty(window, 'api', {
    writable: true,
    value: {
      getAppInfo: jest.fn().mockResolvedValue({
        appName: 'GazeShift',
        appVersion: '0.1.0',
        platform: 'darwin',
      }),
    },
  });
}

// Suppress console errors during tests
global.console.error = jest.fn();
global.console.warn = jest.fn(); 