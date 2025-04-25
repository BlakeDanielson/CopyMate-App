/**
 * Image Conversion Worker
 * 
 * This worker handles image format conversions using Canvas API:
 * - JPG → PNG
 * - PNG → JPG
 */

import { BaseConversionWorker } from './BaseConversionWorker';

// Supported conversions
const SUPPORTED_CONVERSIONS = {
  'jpg': ['png'],
  'jpeg': ['png'],
  'png': ['jpg', 'jpeg'],
};

// Mime types mapping
const MIME_TYPES = {
  'jpg': 'image/jpeg',
  'jpeg': 'image/jpeg',
  'png': 'image/png',
};

export class ImageConversionWorker extends BaseConversionWorker {
  getWorkerType(): string {
    return 'image-converter';
  }

  async performConversion(file: File, targetFormat: string): Promise<Blob> {
    // Get file extension from name
    const sourceFormat = file.name.split('.').pop()?.toLowerCase() || '';
    
    // Validate conversion is supported
    if (!this.isConversionSupported(sourceFormat, targetFormat)) {
      throw new Error(`Conversion from ${sourceFormat} to ${targetFormat} is not supported`);
    }

    try {
      // Create a Blob URL for the input file
      const imageUrl = URL.createObjectURL(file);
      
      // Load the image
      const image = await this.loadImage(imageUrl);
      
      // Update progress - 50% after loading image
      this.updateProgress(50);
      
      // Convert the image
      const convertedBlob = await this.convertImage(image, targetFormat);
      
      // Cleanup
      URL.revokeObjectURL(imageUrl);
      
      // Update progress - 100% after conversion
      this.updateProgress(100);
      
      return convertedBlob;
    } catch (error) {
      throw new Error(`Image conversion failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  private isConversionSupported(sourceFormat: string, targetFormat: string): boolean {
    return Boolean(
      SUPPORTED_CONVERSIONS[sourceFormat as keyof typeof SUPPORTED_CONVERSIONS]?.includes(targetFormat)
    );
  }

  private loadImage(url: string): Promise<HTMLImageElement> {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => resolve(img);
      img.onerror = () => reject(new Error('Failed to load image'));
      img.src = url;
    });
  }

  private convertImage(image: HTMLImageElement, targetFormat: string): Promise<Blob> {
    return new Promise((resolve, reject) => {
      try {
        // Create canvas with image dimensions
        const canvas = new OffscreenCanvas(image.width, image.height);
        const ctx = canvas.getContext('2d');
        
        if (!ctx) {
          throw new Error('Could not get canvas context');
        }
        
        // Draw the image on the canvas
        ctx.drawImage(image, 0, 0);
        
        // Convert to desired format
        const mimeType = MIME_TYPES[targetFormat as keyof typeof MIME_TYPES];
        
        // For JPG conversion, use quality of 0.9
        const quality = targetFormat === 'jpg' || targetFormat === 'jpeg' ? 0.9 : undefined;
        
        // Convert canvas to blob
        canvas.convertToBlob({
          type: mimeType,
          quality
        }).then(blob => {
          resolve(blob);
        }).catch(error => {
          reject(error);
        });
      } catch (error) {
        reject(error);
      }
    });
  }
} 