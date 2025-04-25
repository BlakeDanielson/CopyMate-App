import React, { useEffect, useState, useRef } from 'react';
// @ts-ignore
import ExampleWorker from './example.worker.js';
import { getWasmStatus } from './wasmUtils';
import FileInput from './components/FileInput';
import FormatSelector from './components/FormatSelector';
import ProgressIndicator from './components/ProgressIndicator';
import DownloadLink from './components/DownloadLink';
import ErrorMessage from './components/ErrorMessage';
import ConversionDashboard from './components/ConversionDashboard';
import { FileData } from './types/index';
import { ConversionService, ConversionProgress } from './services/ConversionService';

const App: React.FC = () => {
  const [workerMessage, setWorkerMessage] = useState<string | null>(null);
  const [wasmStatus, setWasmStatus] = useState<string>('');
  const [selectedFile, setSelectedFile] = useState<FileData | null>(null);
  const [targetFormat, setTargetFormat] = useState<string | null>(null);
  const [conversionStatus, setConversionStatus] = useState<'idle' | 'converting' | 'completed' | 'error' | 'initializing'>('idle');
  const [progress, setProgress] = useState<number | null>(0);
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null);
  const [isDialogOpen, setIsDialogOpen] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  
  // Create a ref for the conversion service so it persists between renders
  const conversionServiceRef = useRef<ConversionService | null>(null);
  
  // Initialize the conversion service when the component mounts
  useEffect(() => {
    conversionServiceRef.current = new ConversionService();
    
    // Clean up when the component unmounts
    return () => {
      if (conversionServiceRef.current) {
        conversionServiceRef.current.dispose();
      }
    };
  }, []);
  
  // Setup Web Worker and WASM detection
  useEffect(() => {
    // Check WASM support
    setWasmStatus(getWasmStatus());
    
    // Test worker initialization
    const worker = new ExampleWorker();
    
    worker.onmessage = (event: MessageEvent) => {
      console.log('Message from worker:', event.data);
      if (event.data.type === 'READY') {
        setWorkerMessage(event.data.message);
        
        // Test sending a message to the worker
        worker.postMessage({ test: 'Hello from main thread' });
      } else if (event.data.type === 'ECHO') {
        setWorkerMessage(`Worker connection confirmed: ${event.data.message}`);
      }
    };
    
    // Clean up worker when component unmounts
    return () => {
      worker.terminate();
    };
  }, []);

  // Handle file selection
  const handleFileSelect = (file: File) => {
    // Extract file extension from name
    const nameParts = file.name.split('.');
    const extension = nameParts.length > 1 ? nameParts[nameParts.length - 1].toLowerCase() : '';
    
    setSelectedFile({
      file,
      name: file.name,
      size: file.size,
      type: file.type,
      extension
    });
    
    // Reset state when a new file is selected
    setTargetFormat(null);
    setConversionStatus('idle');
    setProgress(0);
    setDownloadUrl(null);
    setErrorMessage(null);
    
    console.log('File selected:', file.name, file.size, file.type, extension);
  };

  // Handle format selection
  const handleFormatSelect = (format: string) => {
    setTargetFormat(format);
    setErrorMessage(null);
  };

  // Handle conversion start
  const handleStartConversion = async () => {
    if (!selectedFile || !targetFormat || !conversionServiceRef.current) return;
    
    setConversionStatus('converting');
    setProgress(0);
    setErrorMessage(null);
    
    // Get file extension
    const sourceFormat = selectedFile.extension;
    
    try {
      // Handle progress updates
      const handleProgress = (progress: ConversionProgress) => {
        setConversionStatus(progress.status);
        setProgress(progress.progress);
        
        if (progress.status === 'error' && progress.error) {
          setErrorMessage(progress.error);
        }
        
        if (progress.status === 'completed' && progress.result) {
          // Create a URL for the result blob
          const url = URL.createObjectURL(progress.result);
          setDownloadUrl(url);
          setIsDialogOpen(true);
        }
      };
      
      // Start conversion
      await conversionServiceRef.current.convertFile(
        selectedFile.file,
        {
          sourceFormat,
          targetFormat,
          onProgress: handleProgress
        }
      );
    } catch (error) {
      console.error('Conversion error:', error);
      setConversionStatus('error');
      setErrorMessage(error instanceof Error ? error.message : 'An unknown error occurred');
    }
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-3xl">
      <header className="text-center mb-8">
        <h1 className="text-3xl font-bold text-primary mb-2">Local File Converter</h1>
        <p className="text-lg text-muted-foreground">
          Privacy-focused file conversion that happens entirely in your browser
        </p>
      </header>
      
      {/* Conversion Dashboard - visual overview of supported conversions */}
      <ConversionDashboard />
      
      <main className="mt-8">
        {/* Technology Status Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
          <div className="bg-secondary/30 rounded-lg p-4">
            <h3 className="font-semibold mb-1">Web Worker Status</h3>
            <p className="text-sm">{workerMessage || 'Initializing...'}</p>
          </div>
          <div className="bg-secondary/30 rounded-lg p-4">
            <h3 className="font-semibold mb-1">WebAssembly Status</h3>
            <p className="text-sm">{wasmStatus}</p>
          </div>
        </div>
        
        {/* File Input Component */}
        <FileInput 
          onFileSelect={handleFileSelect}
        />
        
        {/* Display selected file information */}
        {selectedFile && (
          <div className="bg-secondary/20 rounded-lg p-4 mt-4">
            <h3 className="font-semibold mb-2">Selected File</h3>
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div><span className="font-medium">Name:</span> {selectedFile.name}</div>
              <div><span className="font-medium">Size:</span> {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB</div>
              <div><span className="font-medium">Type:</span> {selectedFile.type || 'Unknown'}</div>
              <div><span className="font-medium">Extension:</span> {selectedFile.extension}</div>
            </div>
          </div>
        )}
        
        {/* Format Selector Component (UI-3) */}
        {selectedFile && (
          <FormatSelector 
            fileData={selectedFile} 
            onFormatSelect={handleFormatSelect} 
          />
        )}
        
        {/* Start Conversion Button */}
        {selectedFile && targetFormat && conversionStatus === 'idle' && (
          <div className="mt-4 flex justify-center">
            <button
              className="bg-primary text-primary-foreground hover:bg-primary/90 px-4 py-2 rounded-md"
              onClick={handleStartConversion}
            >
              Convert to {targetFormat.toUpperCase()}
            </button>
          </div>
        )}
        
        {/* Progress Indicator Component (UI-4) */}
        <ProgressIndicator 
          progress={progress} 
          status={conversionStatus}
          fileName={selectedFile?.name}
        />
        
        {/* Download Link Component (UI-5) */}
        {downloadUrl && selectedFile && targetFormat && (
          <DownloadLink 
            url={downloadUrl} 
            fileName={selectedFile.name}
            targetFormat={targetFormat}
            onClose={() => setIsDialogOpen(false)}
            isDialogOpen={isDialogOpen}
          />
        )}
        
        {/* Error Message Component (UI-6) */}
        <ErrorMessage 
          message={errorMessage} 
          details="Please try again or select a different file/format."
        />
      </main>
    </div>
  );
};

export default App; 