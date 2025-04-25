import React, { useEffect, useState } from 'react';
import { 
  Select, 
  SelectContent, 
  SelectGroup, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from './ui/select';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { FileData } from '../types/index';
import { ConversionService } from '../services/ConversionService';

interface FormatSelectorProps {
  fileData: FileData | null;
  onFormatSelect: (format: string) => void;
}

const FormatSelector: React.FC<FormatSelectorProps> = ({ fileData, onFormatSelect }) => {
  const [supportedConversions, setSupportedConversions] = useState<Record<string, string[]>>({});
  
  // Initialize conversion service and get supported conversions
  useEffect(() => {
    const conversionService = new ConversionService();
    setSupportedConversions(conversionService.getSupportedConversions());
    
    // Clean up
    return () => {
      conversionService.dispose();
    };
  }, []);
  
  // If no file selected, don't render anything
  if (!fileData) {
    return null;
  }

  const fileExtension = fileData.extension.toLowerCase();
  const availableFormats = supportedConversions[fileExtension] || [];

  // If no conversion options available for this file type
  if (availableFormats.length === 0) {
    return (
      <Card className="mt-4">
        <CardHeader>
          <CardTitle className="text-lg">Convert To</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-destructive">
            Sorry, conversions for .{fileExtension} files are not supported yet.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="mt-4">
      <CardHeader>
        <CardTitle className="text-lg">Convert To</CardTitle>
      </CardHeader>
      <CardContent>
        <Select onValueChange={onFormatSelect}>
          <SelectTrigger className="w-full">
            <SelectValue placeholder="Select a format" />
          </SelectTrigger>
          <SelectContent>
            <SelectGroup>
              {availableFormats.map((format) => (
                <SelectItem key={format} value={format}>
                  .{format.toUpperCase()}
                </SelectItem>
              ))}
            </SelectGroup>
          </SelectContent>
        </Select>
      </CardContent>
    </Card>
  );
};

export default FormatSelector; 