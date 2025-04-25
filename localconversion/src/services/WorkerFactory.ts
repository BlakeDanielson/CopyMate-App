/**
 * Worker Factory
 * 
 * This service handles the creation and management of workers for file conversion.
 * It provides a unified interface for the app to interact with workers.
 */

// @ts-ignore - These imports are handled by Webpack worker-loader
import ImageConversionWorker from '../workers/image-conversion.worker.js';
// @ts-ignore
import DocumentConversionWorker from '../workers/document-conversion.worker.js';

export type WorkerType = 'image' | 'document' | 'audio-video' | 'heic';

// Worker configuration with supported conversions
interface WorkerConfig {
  workerConstructor: new () => Worker;
  supportedFormats: {
    [sourceFormat: string]: string[];
  };
}

// Registry of worker types and their configurations
const WORKER_REGISTRY: Record<WorkerType, WorkerConfig> = {
  'image': {
    workerConstructor: ImageConversionWorker,
    supportedFormats: {
      'jpg': ['png'],
      'jpeg': ['png'],
      'png': ['jpg', 'jpeg']
    }
  },
  'document': {
    workerConstructor: DocumentConversionWorker,
    supportedFormats: {
      'pdf': ['docx'],
      'docx': ['pdf']
    }
  },
  // Add other worker types as they are implemented
  'audio-video': {
    workerConstructor: ImageConversionWorker, // Placeholder - will be replaced later
    supportedFormats: {
      'mp4': ['mp3', 'gif'],
      'mov': ['mp4']
    }
  },
  'heic': {
    workerConstructor: ImageConversionWorker, // Placeholder - will be replaced later
    supportedFormats: {
      'heic': ['jpg']
    }
  }
};

export class WorkerFactory {
  private workers: Map<WorkerType, Worker> = new Map();

  /**
   * Get the appropriate worker for the given file conversion
   */
  getWorkerForConversion(sourceFormat: string, targetFormat: string): Worker | null {
    // Find the worker type that supports this conversion
    const workerType = this.findWorkerTypeForConversion(sourceFormat, targetFormat);
    
    if (!workerType) {
      return null;
    }
    
    // Check if the worker already exists
    if (this.workers.has(workerType)) {
      return this.workers.get(workerType) || null;
    }
    
    // Create a new worker
    const workerConfig = WORKER_REGISTRY[workerType];
    const worker = new workerConfig.workerConstructor();
    
    // Store the worker for reuse
    this.workers.set(workerType, worker);
    
    return worker;
  }
  
  /**
   * Find the worker type that supports the given conversion
   */
  private findWorkerTypeForConversion(sourceFormat: string, targetFormat: string): WorkerType | null {
    for (const [workerType, config] of Object.entries(WORKER_REGISTRY)) {
      const supported = config.supportedFormats[sourceFormat]?.includes(targetFormat);
      if (supported) {
        return workerType as WorkerType;
      }
    }
    
    return null;
  }
  
  /**
   * Get all supported conversions from all workers
   */
  getAllSupportedConversions(): Record<string, string[]> {
    const allConversions: Record<string, string[]> = {};
    
    for (const config of Object.values(WORKER_REGISTRY)) {
      for (const [sourceFormat, targetFormats] of Object.entries(config.supportedFormats)) {
        if (!allConversions[sourceFormat]) {
          allConversions[sourceFormat] = [];
        }
        
        allConversions[sourceFormat] = [
          ...allConversions[sourceFormat],
          ...targetFormats.filter(format => !allConversions[sourceFormat].includes(format))
        ];
      }
    }
    
    return allConversions;
  }
  
  /**
   * Terminate all workers
   */
  terminateAll(): void {
    // Convert Map values to array before iterating
    Array.from(this.workers.values()).forEach(worker => {
      worker.terminate();
    });
    
    this.workers.clear();
  }
} 