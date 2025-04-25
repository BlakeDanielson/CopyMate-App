import React, { useRef, useEffect, useState } from 'react';
import '../styles/WebcamCapture.css';

interface WebcamCaptureProps {
  onFrame?: (imageData: ImageData) => void;
  width?: number;
  height?: number;
  deviceId?: string;
}

const WebcamCapture: React.FC<WebcamCaptureProps> = ({
  onFrame,
  width = 640,
  height = 480,
  deviceId
}) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [devices, setDevices] = useState<MediaDeviceInfo[]>([]);
  const [selectedDeviceId, setSelectedDeviceId] = useState<string | undefined>(deviceId);
  const [isCapturing, setIsCapturing] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Get available video devices
  useEffect(() => {
    const getVideoDevices = async () => {
      try {
        const devices = await navigator.mediaDevices.enumerateDevices();
        const videoDevices = devices.filter(device => device.kind === 'videoinput');
        setDevices(videoDevices);
        
        // If no device ID is specified and we have devices, use the first one
        if (!selectedDeviceId && videoDevices.length > 0) {
          setSelectedDeviceId(videoDevices[0].deviceId);
        }
      } catch (err) {
        setError('Failed to enumerate video devices');
        console.error('Error getting video devices:', err);
      }
    };

    getVideoDevices();
  }, [selectedDeviceId]);

  // Start/stop webcam capture
  useEffect(() => {
    let stream: MediaStream | null = null;
    let animationFrameId: number | null = null;

    const startCapture = async () => {
      if (!videoRef.current || !canvasRef.current) return;
      
      try {
        // Request video stream with chosen device or default
        const constraints: MediaStreamConstraints = {
          video: selectedDeviceId 
            ? { deviceId: { exact: selectedDeviceId }, width, height }
            : { width, height },
          audio: false,
        };
        
        stream = await navigator.mediaDevices.getUserMedia(constraints);
        
        // Connect stream to video element
        videoRef.current.srcObject = stream;
        
        // Wait for video to load metadata
        await new Promise<void>((resolve) => {
          if (!videoRef.current) return;
          videoRef.current.onloadedmetadata = () => resolve();
        });
        
        // Start video playback
        await videoRef.current.play();
        
        // Set canvas dimensions to match video
        canvasRef.current.width = videoRef.current.videoWidth;
        canvasRef.current.height = videoRef.current.videoHeight;
        
        setIsCapturing(true);
        setError(null);
        
        // Start capture loop if onFrame callback provided
        if (onFrame) {
          const captureFrame = () => {
            if (!videoRef.current || !canvasRef.current) return;
            
            const ctx = canvasRef.current.getContext('2d');
            if (!ctx) return;
            
            // Draw video frame to canvas
            ctx.drawImage(
              videoRef.current,
              0, 0,
              canvasRef.current.width,
              canvasRef.current.height
            );
            
            // Get image data and pass to callback
            const imageData = ctx.getImageData(
              0, 0,
              canvasRef.current.width,
              canvasRef.current.height
            );
            
            onFrame(imageData);
            
            // Schedule next frame
            animationFrameId = requestAnimationFrame(captureFrame);
          };
          
          captureFrame();
        }
      } catch (err) {
        setError('Failed to access webcam');
        setIsCapturing(false);
        console.error('Error starting video capture:', err);
      }
    };

    const stopCapture = () => {
      if (animationFrameId) {
        cancelAnimationFrame(animationFrameId);
        animationFrameId = null;
      }
      
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
        stream = null;
      }
      
      if (videoRef.current) {
        videoRef.current.srcObject = null;
      }
      
      setIsCapturing(false);
    };

    // If we have a device ID, start capturing
    if (selectedDeviceId) {
      startCapture();
    } else {
      stopCapture();
    }

    // Cleanup on unmount
    return () => {
      stopCapture();
    };
  }, [selectedDeviceId, width, height, onFrame]);

  const handleDeviceChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedDeviceId(e.target.value);
  };

  return (
    <div className="webcam-capture">
      <div className="webcam-container">
        <video 
          ref={videoRef}
          className="webcam-video"
          muted
          playsInline
        />
        <canvas 
          ref={canvasRef}
          className="webcam-canvas"
        />
      </div>
      
      {error && (
        <div className="webcam-error">
          {error}
        </div>
      )}
      
      <div className="webcam-controls">
        <select 
          value={selectedDeviceId}
          onChange={handleDeviceChange}
          disabled={isCapturing}
          className="webcam-device-select"
        >
          {devices.map(device => (
            <option key={device.deviceId} value={device.deviceId}>
              {device.label || `Camera ${device.deviceId.substring(0, 5)}...`}
            </option>
          ))}
        </select>
        
        <button
          onClick={() => setSelectedDeviceId(undefined)}
          disabled={!isCapturing}
          className="webcam-stop-button"
        >
          Stop Camera
        </button>
        
        <button
          onClick={() => {
            if (devices.length > 0) {
              setSelectedDeviceId(devices[0].deviceId);
            }
          }}
          disabled={isCapturing || devices.length === 0}
          className="webcam-start-button"
        >
          Start Camera
        </button>
      </div>
    </div>
  );
};

export default WebcamCapture; 