import React, { useState } from 'react';
import WebcamCapture from '../components/WebcamCapture';
import '../styles/WebcamPage.css';

const WebcamPage: React.FC = () => {
  const [frameCount, setFrameCount] = useState(0);
  const [frameSize, setFrameSize] = useState({ width: 0, height: 0 });
  const [frameRate, setFrameRate] = useState(0);
  const [lastFrameTime, setLastFrameTime] = useState(Date.now());
  const [frameRates, setFrameRates] = useState<number[]>([]);

  // Handle incoming frames from the webcam
  const handleFrame = (imageData: ImageData) => {
    // Update frame count
    setFrameCount(prev => prev + 1);
    
    // Update frame size
    setFrameSize({
      width: imageData.width,
      height: imageData.height
    });
    
    // Calculate and update frame rate
    const now = Date.now();
    const elapsed = now - lastFrameTime;
    setLastFrameTime(now);
    
    if (elapsed > 0) {
      const fps = 1000 / elapsed;
      setFrameRates(prev => {
        const newRates = [...prev, fps].slice(-30); // Keep last 30 samples
        const averageFps = newRates.reduce((sum, rate) => sum + rate, 0) / newRates.length;
        setFrameRate(Math.round(averageFps * 10) / 10); // Round to 1 decimal place
        return newRates;
      });
    }
  };

  return (
    <div className="webcam-page">
      <h1>Webcam Capture Demo</h1>
      <p>This is a proof-of-concept for capturing and displaying webcam video.</p>
      
      <WebcamCapture 
        onFrame={handleFrame}
        width={640}
        height={480}
      />
      
      <div className="webcam-stats">
        <h2>Webcam Statistics</h2>
        <div className="stats-grid">
          <div className="stat-item">
            <span className="stat-label">Frames Processed:</span>
            <span className="stat-value">{frameCount}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Frame Rate:</span>
            <span className="stat-value">{frameRate} FPS</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Resolution:</span>
            <span className="stat-value">{frameSize.width} × {frameSize.height}</span>
          </div>
        </div>
      </div>
      
      <div className="webcam-info">
        <h3>Implementation Notes</h3>
        <ul>
          <li>Uses the browser's MediaDevices API for webcam access</li>
          <li>Canvas is used to process video frames</li>
          <li>The component provides device selection and control</li>
          <li>Frame data is available for AI processing</li>
        </ul>
      </div>
    </div>
  );
};

export default WebcamPage; 