import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import App from '../../renderer/App';

// Mock the WebcamPage component
jest.mock('../../renderer/pages/WebcamPage', () => {
  return {
    __esModule: true,
    default: () => <div data-testid="mock-webcam-page">WebcamPage Mock</div>
  };
});

describe('App', () => {
  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();
    
    // Mock window.api.getAppInfo to resolve with test data
    // Already set up in jest.setup.ts
  });

  it('renders the app with title and header', async () => {
    render(<App />);
    
    // App title should be present
    expect(screen.getByText('GazeShift')).toBeInTheDocument();
    
    // Wait for app info to load
    await waitFor(() => {
      expect(screen.getByText(/version/i)).toBeInTheDocument();
    });
    
    // App version and platform should be displayed
    expect(screen.getByText('Version: 0.1.0')).toBeInTheDocument();
    expect(screen.getByText('Platform: darwin')).toBeInTheDocument();
  });

  it('displays welcome section on home page', () => {
    render(<App />);
    
    expect(screen.getByText('Welcome to GazeShift')).toBeInTheDocument();
    expect(screen.getByText('AI-powered eye gaze correction for video calls')).toBeInTheDocument();
  });

  it('displays features section on home page', () => {
    render(<App />);
    
    expect(screen.getByText('Key Features:')).toBeInTheDocument();
    
    // Check individual features
    const features = [
      'Real-time gaze correction',
      'Note-taking overlay',
      'Teleprompter functionality',
      'Completely local processing'
    ];
    
    features.forEach(feature => {
      expect(screen.getByText(feature)).toBeInTheDocument();
    });
  });

  it('displays demo section on home page', () => {
    render(<App />);
    
    expect(screen.getByText('Proof of Concept Demos:')).toBeInTheDocument();
    expect(screen.getByText('Webcam Capture Demo')).toBeInTheDocument();
  });

  it('navigates to Webcam page when button is clicked', async () => {
    render(<App />);
    
    // Find and click the WebcamCapture demo button
    const webcamButton = screen.getByRole('button', { name: /webcam capture demo/i });
    fireEvent.click(webcamButton);
    
    // Should now show the WebcamPage component
    await waitFor(() => {
      expect(screen.getByTestId('mock-webcam-page')).toBeInTheDocument();
    });
    
    // Home page content should not be visible
    expect(screen.queryByText('Welcome to GazeShift')).not.toBeInTheDocument();
  });

  it('navigates back to home page when app title is clicked', async () => {
    render(<App />);
    
    // First navigate to webcam page
    const webcamButton = screen.getByRole('button', { name: /webcam capture demo/i });
    fireEvent.click(webcamButton);
    
    // Confirm we're on webcam page
    await waitFor(() => {
      expect(screen.getByTestId('mock-webcam-page')).toBeInTheDocument();
    });
    
    // Click the app title to go back to home
    const appTitle = screen.getByText('GazeShift');
    fireEvent.click(appTitle);
    
    // Should now show the home page content again
    await waitFor(() => {
      expect(screen.getByText('Welcome to GazeShift')).toBeInTheDocument();
    });
    
    // Webcam page should not be visible
    expect(screen.queryByTestId('mock-webcam-page')).not.toBeInTheDocument();
  });

  it('displays footer with copyright info', () => {
    render(<App />);
    
    const currentYear = new Date().getFullYear();
    expect(screen.getByText(`GazeShift © ${currentYear}`)).toBeInTheDocument();
  });
}); 