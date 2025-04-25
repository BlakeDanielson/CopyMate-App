import React from 'react';
import { Badge } from './ui/badge';
import { 
  FileText, 
  FileImage, 
  File,
  FileAudio, 
  FileVideo
} from 'lucide-react';

interface FileTypeIconProps {
  fileType: string;
  size?: 'default' | 'sm' | 'lg';
  showText?: boolean;
  className?: string;
}

// Get appropriate file extension without dots
const normalizeExtension = (extension: string): string => {
  return extension.toLowerCase().replace(/^\./, '');
};

// Map file extensions to icon components
const getIconForExtension = (extension: string) => {
  const ext = normalizeExtension(extension);
  
  switch (ext) {
    case 'pdf':
      return <FileText className="w-5 h-5 mr-1.5 text-red-500" />;
    case 'docx':
    case 'doc':
      return <FileText className="w-5 h-5 mr-1.5 text-blue-500" />;
    case 'jpg':
    case 'jpeg':
      return <FileImage className="w-5 h-5 mr-1.5 text-purple-500" />;
    case 'png':
      return <FileImage className="w-5 h-5 mr-1.5 text-green-500" />;
    case 'gif':
      return <FileImage className="w-5 h-5 mr-1.5 text-indigo-500" />;
    case 'heic':
      return <FileImage className="w-5 h-5 mr-1.5 text-teal-500" />;
    case 'mp3':
    case 'wav':
      return <FileAudio className="w-5 h-5 mr-1.5" />;
    case 'mp4':
    case 'mov':
      return <FileVideo className="w-5 h-5 mr-1.5" />;
    default:
      return <File className="w-5 h-5 mr-1.5" />;
  }
};

// Get badge size classes
const getBadgeSizeClasses = (size: 'default' | 'sm' | 'lg') => {
  switch (size) {
    case 'sm':
      return 'text-xs py-0.5 px-2';
    case 'lg':
      return 'text-sm py-1 px-3';
    default:
      return 'text-xs py-1 px-2.5';
  }
};

// Get colors for specific file types
const getFileTypeColors = (extension: string) => {
  const ext = normalizeExtension(extension);
  
  switch (ext) {
    case 'pdf':
      return 'bg-red-100 text-red-700 border-red-200';
    case 'docx':
    case 'doc':
      return 'bg-blue-100 text-blue-700 border-blue-200';
    case 'jpg':
    case 'jpeg':
      return 'bg-purple-100 text-purple-700 border-purple-200';
    case 'png':
      return 'bg-green-100 text-green-700 border-green-200';
    case 'mp4':
      return 'bg-amber-100 text-amber-700 border-amber-200';
    case 'mp3':
      return 'bg-pink-100 text-pink-700 border-pink-200';
    case 'gif':
      return 'bg-indigo-100 text-indigo-700 border-indigo-200';
    case 'heic':
      return 'bg-teal-100 text-teal-700 border-teal-200';
    case 'mov':
      return 'bg-orange-100 text-orange-700 border-orange-200';
    default:
      return 'bg-gray-100 text-gray-700 border-gray-200';
  }
};

const FileTypeIcon: React.FC<FileTypeIconProps> = ({
  fileType,
  size = 'default',
  showText = true,
  className = ''
}) => {
  const extension = normalizeExtension(fileType);
  const icon = getIconForExtension(extension);
  const sizeClasses = getBadgeSizeClasses(size);
  const colorClasses = getFileTypeColors(extension);
  
  return (
    <span 
      className={`inline-flex items-center rounded-full border ${sizeClasses} ${colorClasses} font-medium ${className}`}
    >
      {icon}
      {showText && extension.toUpperCase()}
    </span>
  );
};

export default FileTypeIcon; 