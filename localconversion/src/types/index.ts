export interface FileInputProps {
  onFileSelect: (file: File) => void;
  acceptedFileTypes?: string;
  maxFileSizeMB?: number; // Default will be 100MB as per requirements
}

export interface FileData {
  file: File;
  name: string;
  size: number;
  type: string;
  extension: string;
}

export interface ConversionOption {
  from: string;
  to: string;
  label: string;
  disabled?: boolean;
} 