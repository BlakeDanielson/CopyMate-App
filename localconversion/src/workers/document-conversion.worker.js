/**
 * Document Conversion Worker
 * This worker file is loaded into a web worker context and handles document conversions.
 */

import { DocumentConversionWorker } from './DocumentConversionWorker';

// Import PDF.js in a way compatible with both ESM and CJS
const pdfjsLib = require('pdfjs-dist/legacy/build/pdf.js');

// Set the worker source to the copied worker file in the dist directory
pdfjsLib.GlobalWorkerOptions.workerSrc = 'pdf.worker.js';

// Initialize the worker
// `self` refers to the worker scope
const workerInstance = new DocumentConversionWorker(self);

// Listen for any unhandled errors in the worker
self.addEventListener('error', (event) => {
  self.postMessage({
    type: 'WORKER_ERROR',
    payload: {
      message: event.message,
      filename: event.filename,
      lineno: event.lineno,
      colno: event.colno,
      error: event.error ? event.error.toString() : 'Unknown error'
    }
  });
});

// Notify the main thread that the worker is initialized
self.postMessage({
  type: 'INIT',
  payload: { 
    workerType: 'document-converter',
    supportedConversions: {
      'pdf': ['docx', 'jpg', 'jpeg'],
      'docx': ['pdf'],
      'jpg': ['pdf'],
      'jpeg': ['pdf'],
      'png': ['pdf']
    },
    capabilities: {
      wasm: true,
      pdfToDocx: true,
      docxToPdf: true,
      imageToPdf: true,
      pdfToImage: true
    }
  }
}); 