// Common utilities and shared code

/**
 * Logger utility for consistent logging across the application
 */
export class Logger {
  constructor(private context: string) {}

  info(message: string, ...args: any[]): void {
    console.log(`[${this.context}] INFO: ${message}`, ...args);
  }

  warn(message: string, ...args: any[]): void {
    console.warn(`[${this.context}] WARN: ${message}`, ...args);
  }

  error(message: string, error?: Error, ...args: any[]): void {
    console.error(`[${this.context}] ERROR: ${message}`, error, ...args);
  }

  debug(message: string, ...args: any[]): void {
    if (process.env.NODE_ENV === 'development') {
      console.debug(`[${this.context}] DEBUG: ${message}`, ...args);
    }
  }
}

/**
 * Create a throttled function that only invokes func at most once per threshold
 */
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  threshold: number
): (...args: Parameters<T>) => void {
  let lastCall = 0;
  return (...args: Parameters<T>) => {
    const now = Date.now();
    if (now - lastCall >= threshold) {
      lastCall = now;
      func(...args);
    }
  };
}

/**
 * Create a debounced function that delays invoking func until after wait milliseconds
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: ReturnType<typeof setTimeout> | null = null;
  return (...args: Parameters<T>) => {
    if (timeout) {
      clearTimeout(timeout);
    }
    timeout = setTimeout(() => {
      func(...args);
    }, wait);
  };
} 