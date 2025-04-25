import React from 'react';
import { Alert, AlertTitle, AlertDescription } from './ui/alert';
import { XCircle } from 'lucide-react';

interface ErrorMessageProps {
  message: string | null;
  details?: string;
  variant?: 'default' | 'destructive';
}

const ErrorMessage: React.FC<ErrorMessageProps> = ({ 
  message, 
  details,
  variant = 'destructive'
}) => {
  if (!message) {
    return null;
  }

  return (
    <Alert variant={variant} className="mt-4">
      <XCircle className="h-4 w-4" />
      <AlertTitle>{message}</AlertTitle>
      {details && <AlertDescription>{details}</AlertDescription>}
    </Alert>
  );
};

export default ErrorMessage; 