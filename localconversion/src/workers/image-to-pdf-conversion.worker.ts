/**
 * Image to PDF Conversion Worker
 * This worker file is loaded into a web worker context and handles image to PDF conversions.
 */

import { ImageToPdfConversionWorker } from './ImageToPdfConversionWorker';

// Initialize the worker
// `self` refers to the worker scope
const worker = self as unknown as Worker;
new ImageToPdfConversionWorker(worker);

// Notify the main thread that the worker is initialized
self.postMessage({
  type: 'INIT',
  payload: { 
    workerType: 'image-to-pdf-converter',
    supportedConversions: {
      'jpg': ['pdf'],
      'jpeg': ['pdf'],
      'png': ['pdf']
    }
  }
}); 