import React, { useRef, useState, useCallback } from 'react';
import { FileInputProps } from '../types/index';
import { Card, CardContent } from './ui/card';
import { Button } from './ui/button';
import { UploadCloud, AlertCircle } from 'lucide-react';

const FileInput: React.FC<FileInputProps> = ({
  onFileSelect,
  acceptedFileTypes = '',
  maxFileSizeMB = 100 // 100MB default as per requirements
}) => {
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  // Convert MB to bytes
  const maxFileSizeBytes = maxFileSizeMB * 1024 * 1024;
  
  const handleDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  }, []);
  
  const handleDragLeave = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);
  
  const validateFile = useCallback((file: File): boolean => {
    // Check file size
    if (file.size > maxFileSizeBytes) {
      setError(`File is too large. Maximum size is ${maxFileSizeMB}MB.`);
      return false;
    }
    
    // Check file type if acceptedFileTypes is provided
    if (acceptedFileTypes && !acceptedFileTypes.includes(file.type) && !acceptedFileTypes.includes('*')) {
      setError('File type not supported');
      return false;
    }
    
    setError(null);
    return true;
  }, [acceptedFileTypes, maxFileSizeBytes, maxFileSizeMB]);
  
  const handleDrop = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    
    const { files } = e.dataTransfer;
    
    if (files && files.length) {
      const file = files[0]; // For now, just take the first file
      
      if (validateFile(file)) {
        onFileSelect(file);
      }
    }
  }, [onFileSelect, validateFile]);
  
  const handleFileInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const { files } = e.target;
    
    if (files && files.length) {
      const file = files[0];
      
      if (validateFile(file)) {
        onFileSelect(file);
      }
    }
  }, [onFileSelect, validateFile]);
  
  const handleButtonClick = useCallback(() => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  }, []);
  
  return (
    <Card>
      <CardContent className="pt-6">
        <div
          className={`border-2 ${isDragging ? 'border-primary border-solid' : 'border-dashed border-muted'} 
                    rounded-lg p-8 transition-all flex flex-col items-center justify-center 
                    hover:border-primary hover:bg-secondary/10 cursor-pointer`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={handleButtonClick}
        >
          <UploadCloud className="h-12 w-12 text-muted-foreground mb-4" />
          <p className="text-muted-foreground text-center mb-2">
            Drag & drop files here or click to select
          </p>
          <p className="text-xs text-muted-foreground text-center mb-4">
            Supports PDF, DOCX, JPG, PNG, MP4, and more
          </p>
          <Button variant="outline" className="mt-2">
            Select File
          </Button>
          <input
            ref={fileInputRef}
            type="file"
            className="hidden"
            onChange={handleFileInputChange}
            accept={acceptedFileTypes}
          />
        </div>
        
        {error && (
          <div className="flex items-center mt-3 p-2 bg-destructive/10 text-destructive rounded text-sm">
            <AlertCircle className="w-4 h-4 mr-2" />
            {error}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default FileInput; 