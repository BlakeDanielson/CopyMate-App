import React, { useState, useEffect } from 'react';
import './styles/App.css';
import WebcamPage from './pages/WebcamPage';

interface AppInfo {
  appName: string;
  appVersion: string;
  platform: string;
}

// This ensures that TypeScript recognizes the window.api property
declare global {
  interface Window {
    api: {
      getAppInfo: () => Promise<AppInfo>;
      // Add other API methods as they're implemented
    };
  }
}

const App: React.FC = () => {
  const [appInfo, setAppInfo] = useState<AppInfo | null>(null);
  const [currentPage, setCurrentPage] = useState<string>('home');

  useEffect(() => {
    console.log('App component mounted');
    
    const getAppInfo = async () => {
      try {
        console.log('Fetching app info...');
        const info = await window.api.getAppInfo();
        console.log('App info received:', info);
        setAppInfo(info);
      } catch (error) {
        console.error('Failed to get app info:', error);
      }
    };

    getAppInfo();
  }, []);

  const renderPage = () => {
    switch (currentPage) {
      case 'webcam':
        return <WebcamPage />;
      case 'home':
      default:
        return (
          <>
            <section className="welcome-section">
              <h2>Welcome to GazeShift</h2>
              <p>AI-powered eye gaze correction for video calls</p>
            </section>
            
            <section className="features-section">
              <h3>Key Features:</h3>
              <ul>
                <li>Real-time gaze correction</li>
                <li>Note-taking overlay</li>
                <li>Teleprompter functionality</li>
                <li>Completely local processing</li>
              </ul>
            </section>

            <section className="demo-section">
              <h3>Proof of Concept Demos:</h3>
              <div className="demo-buttons">
                <button onClick={() => setCurrentPage('webcam')}>
                  Webcam Capture Demo
                </button>
              </div>
            </section>
          </>
        );
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1 onClick={() => setCurrentPage('home')} style={{ cursor: 'pointer' }}>GazeShift</h1>
        {appInfo && (
          <div className="app-info">
            <p>Version: {appInfo.appVersion}</p>
            <p>Platform: {appInfo.platform}</p>
          </div>
        )}
      </header>
      <main className="app-main">
        {renderPage()}
      </main>
      <footer className="app-footer">
        <p>GazeShift © {new Date().getFullYear()}</p>
      </footer>
    </div>
  );
};

export default App; 