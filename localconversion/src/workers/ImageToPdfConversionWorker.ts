/**
 * Image to PDF Conversion Worker
 * 
 * This worker handles converting images to PDF:
 * - JPG → PDF
 * - PNG → PDF
 */

import { BaseConversionWorker } from './BaseConversionWorker';
import { PDFDocument } from 'pdf-lib';

// Supported conversions
const SUPPORTED_CONVERSIONS = {
  'jpg': ['pdf'],
  'jpeg': ['pdf'],
  'png': ['pdf'],
};

// MIME types mapping
const MIME_TYPES = {
  'pdf': 'application/pdf',
  'jpg': 'image/jpeg',
  'jpeg': 'image/jpeg',
  'png': 'image/png',
};

export class ImageToPdfConversionWorker extends BaseConversionWorker {
  getWorkerType(): string {
    return 'image-to-pdf-converter';
  }

  async performConversion(file: File, targetFormat: string): Promise<Blob> {
    // Get file extension from name
    const sourceFormat = file.name.split('.').pop()?.toLowerCase() || '';
    
    // Validate conversion is supported
    if (!this.isConversionSupported(sourceFormat, targetFormat)) {
      throw new Error(`Conversion from ${sourceFormat} to ${targetFormat} is not supported`);
    }

    // Make sure the target is PDF
    if (targetFormat !== 'pdf') {
      throw new Error(`This worker only supports converting to PDF format`);
    }

    try {
      // Create a new PDF document
      const pdfDoc = await PDFDocument.create();
      this.updateProgress(20);
      
      // Read the image file
      const imageBytes = new Uint8Array(await file.arrayBuffer());
      this.updateProgress(40);
      
      // Embed the image in the PDF
      let embeddedImage;
      if (sourceFormat === 'png') {
        embeddedImage = await pdfDoc.embedPng(imageBytes);
      } else { // jpg/jpeg
        embeddedImage = await pdfDoc.embedJpg(imageBytes);
      }
      this.updateProgress(60);
      
      // Get dimensions of the image
      const { width, height } = embeddedImage;
      
      // Add a page with the same dimensions as the image
      const page = pdfDoc.addPage([width, height]);
      
      // Draw the image on the page (full page)
      page.drawImage(embeddedImage, {
        x: 0,
        y: 0,
        width: width,
        height: height,
      });
      
      this.updateProgress(80);
      
      // Save the PDF
      const pdfBytes = await pdfDoc.save();
      
      // Convert to Blob
      const pdfBlob = new Blob([pdfBytes], { type: MIME_TYPES.pdf });
      
      this.updateProgress(100);
      
      return pdfBlob;
    } catch (error) {
      throw new Error(`Image to PDF conversion failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }
  
  private isConversionSupported(sourceFormat: string, targetFormat: string): boolean {
    return Boolean(
      SUPPORTED_CONVERSIONS[sourceFormat as keyof typeof SUPPORTED_CONVERSIONS]?.includes(targetFormat)
    );
  }
} 