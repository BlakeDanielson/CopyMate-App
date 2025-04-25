/**
 * Base Conversion Worker
 * 
 * This is the foundation for all conversion workers. It provides:
 * - Standard message protocol
 * - Progress reporting
 * - Error handling
 */

export interface ConversionWorkerMessage {
  type: 'START_CONVERSION' | 'PROGRESS_UPDATE' | 'CONVERSION_COMPLETE' | 'CONVERSION_ERROR';
  payload?: any;
  progress?: number;
  result?: Blob;
  error?: Error;
}

// NOTE: This will be used in actual worker files
export abstract class BaseConversionWorker {
  protected ctx: Worker;

  constructor(workerContext: Worker) {
    this.ctx = workerContext;

    // Listen for messages from the main thread
    this.ctx.addEventListener('message', this.handleMessage.bind(this));
    
    // Notify that the worker is ready
    this.sendMessage({
      type: 'READY',
      payload: {
        workerType: this.getWorkerType()
      }
    });
  }

  // To be implemented by each specific conversion worker
  abstract getWorkerType(): string;
  abstract performConversion(file: File, targetFormat: string): Promise<Blob>;

  protected sendMessage(message: any): void {
    this.ctx.postMessage(message);
  }

  protected updateProgress(progress: number): void {
    this.sendMessage({
      type: 'PROGRESS_UPDATE',
      progress
    });
  }

  private async handleMessage(event: MessageEvent): Promise<void> {
    const { type, payload } = event.data;

    if (type === 'START_CONVERSION') {
      try {
        const { file, targetFormat } = payload;
        
        // Start conversion process
        this.sendMessage({
          type: 'CONVERSION_STARTED',
          payload: {
            fileName: file.name,
            sourceFormat: file.name.split('.').pop(),
            targetFormat
          }
        });

        // Perform the actual conversion (implemented by subclasses)
        const result = await this.performConversion(file, targetFormat);
        
        // Send back the result
        this.sendMessage({
          type: 'CONVERSION_COMPLETE',
          result,
          payload: {
            fileName: file.name,
            targetFormat
          }
        });
      } catch (error) {
        this.sendMessage({
          type: 'CONVERSION_ERROR',
          error: {
            message: error instanceof Error ? error.message : 'Unknown error occurred',
            name: error instanceof Error ? error.name : 'ConversionError'
          }
        });
      }
    }
  }
} 