import { Logger, throttle, debounce } from '@common/utils';

describe('Logger', () => {
  let originalConsole: Console;
  
  beforeEach(() => {
    // Save original console methods
    originalConsole = { ...console };
    // Mock console methods
    console.log = jest.fn();
    console.warn = jest.fn();
    console.error = jest.fn();
    console.debug = jest.fn();
  });
  
  afterEach(() => {
    // Restore original console methods
    console.log = originalConsole.log;
    console.warn = originalConsole.warn;
    console.error = originalConsole.error;
    console.debug = originalConsole.debug;
  });
  
  test('info method should log with correct format', () => {
    const logger = new Logger('TestContext');
    logger.info('Test message');
    expect(console.log).toHaveBeenCalledWith('[TestContext] INFO: Test message');
  });
  
  test('warn method should warn with correct format', () => {
    const logger = new Logger('TestContext');
    logger.warn('Test warning');
    expect(console.warn).toHaveBeenCalledWith('[TestContext] WARN: Test warning');
  });
  
  test('error method should error with correct format', () => {
    const logger = new Logger('TestContext');
    const testError = new Error('Test error object');
    logger.error('Test error', testError);
    expect(console.error).toHaveBeenCalledWith('[TestContext] ERROR: Test error', testError);
  });
});

describe('Throttle', () => {
  test('throttled function should only execute once within threshold', () => {
    jest.useFakeTimers();
    const mockFn = jest.fn();
    const throttled = throttle(mockFn, 1000);
    
    throttled();
    expect(mockFn).toHaveBeenCalledTimes(1);
    
    // Call multiple times within threshold
    throttled();
    throttled();
    expect(mockFn).toHaveBeenCalledTimes(1);
    
    // Advance time beyond threshold
    jest.advanceTimersByTime(1001);
    
    throttled();
    expect(mockFn).toHaveBeenCalledTimes(2);
    
    jest.useRealTimers();
  });
}); 