import React from 'react';
import { render, screen } from '@testing-library/react';
import WebcamPage from '../../../renderer/pages/WebcamPage';

// Mock the WebcamCapture component that WebcamPage depends on
jest.mock('../../../renderer/components/WebcamCapture', () => {
  return {
    __esModule: true,
    default: ({ onFrame }: { onFrame?: (imageData: ImageData) => void }) => {
      // Call the onFrame callback with a mock ImageData if provided
      if (onFrame) {
        const mockImageData = new ImageData(640, 480);
        setTimeout(() => onFrame(mockImageData), 0);
      }
      
      return (
        <div data-testid="mock-webcam-capture">
          <p>Mock WebcamCapture Component</p>
        </div>
      );
    }
  };
});

describe('WebcamPage', () => {
  it('renders the component with title and description', () => {
    render(<WebcamPage />);
    
    expect(screen.getByText('Webcam Capture Demo')).toBeInTheDocument();
    expect(screen.getByText(/proof-of-concept/i)).toBeInTheDocument();
  });
  
  it('renders the WebcamCapture component', () => {
    render(<WebcamPage />);
    
    expect(screen.getByTestId('mock-webcam-capture')).toBeInTheDocument();
  });
  
  it('displays implementation notes', () => {
    render(<WebcamPage />);
    
    expect(screen.getByText('Implementation Notes')).toBeInTheDocument();
    expect(screen.getByText(/uses the browser's mediadevices api/i)).toBeInTheDocument();
    expect(screen.getByText(/canvas is used/i)).toBeInTheDocument();
    expect(screen.getByText(/frame data is available/i)).toBeInTheDocument();
  });
  
  it('updates webcam statistics when frames are processed', async () => {
    render(<WebcamPage />);
    
    // Wait for the stats to update after the mocked onFrame callback is called
    await screen.findByText('1', { exact: false }); // Wait for frame count to become at least 1
    
    // Check that stats are displayed
    expect(screen.getByText(/frames processed/i)).toBeInTheDocument();
    expect(screen.getByText(/frame rate/i)).toBeInTheDocument();
    expect(screen.getByText(/resolution/i)).toBeInTheDocument();
    
    // Verify resolution display
    expect(screen.getByText('640 × 480')).toBeInTheDocument();
  });
}); 