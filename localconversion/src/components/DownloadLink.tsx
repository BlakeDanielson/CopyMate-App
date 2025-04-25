import React from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from './ui/alert-dialog';
import { FileData } from '../types/index';

interface DownloadLinkProps {
  url: string | null;
  fileName: string;
  targetFormat: string;
  onClose: () => void;
  isDialogOpen: boolean;
}

const DownloadLink: React.FC<DownloadLinkProps> = ({
  url,
  fileName,
  targetFormat,
  onClose,
  isDialogOpen
}) => {
  if (!url) {
    return null;
  }

  // Create name for the converted file
  const originalNameWithoutExt = fileName.substring(0, fileName.lastIndexOf('.'));
  const newFileName = `${originalNameWithoutExt}.${targetFormat}`;

  return (
    <>
      <Card className="mt-4">
        <CardHeader>
          <CardTitle className="text-lg">Download Converted File</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm text-muted-foreground">
            Your file has been converted to {targetFormat.toUpperCase()} format.
          </p>
          <div className="flex justify-between items-center">
            <span className="text-sm font-medium">{newFileName}</span>
            <Button asChild>
              <a href={url} download={newFileName}>
                Download
              </a>
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Alert Dialog for Download Notification */}
      <AlertDialog open={isDialogOpen} onOpenChange={onClose}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Conversion Complete!</AlertDialogTitle>
            <AlertDialogDescription>
              Your file has been successfully converted to {targetFormat.toUpperCase()} format.
              Click the button below to download your converted file.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogAction asChild>
              <a href={url} download={newFileName} onClick={onClose}>
                Download File
              </a>
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
};

export default DownloadLink; 