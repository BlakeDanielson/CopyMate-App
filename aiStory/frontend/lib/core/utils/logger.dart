import 'package:logger/logger.dart';
import 'package:ai_story/config/env_config.dart';

/// Logger utility for the application
class AppLogger {
  static final AppLogger _instance = AppLogger._internal();
  
  /// Singleton instance
  factory AppLogger() => _instance;
  
  /// Logger instance
  late final Logger _logger;
  
  /// Private constructor
  AppLogger._internal() {
    final logLevel = _getLogLevel(EnvConfig.logLevel);
    
    _logger = Logger(
      printer: PrettyPrinter(
        methodCount: 2,
        errorMethodCount: 8,
        lineLength: 120,
        colors: true,
        printEmojis: true,
        printTime: true,
      ),
      level: logLevel,
    );
  }
  
  /// Get the log level from the environment configuration
  Level _getLogLevel(String logLevel) {
    switch (logLevel.toLowerCase()) {
      case 'debug':
        return Level.debug;
      case 'info':
        return Level.info;
      case 'warning':
        return Level.warning;
      case 'error':
        return Level.error;
      default:
        return Level.info;
    }
  }
  
  /// Log a debug message
  void d(String message, [dynamic error, StackTrace? stackTrace]) {
    _logger.d(message, error: error, stackTrace: stackTrace);
  }
  
  /// Log an info message
  void i(String message, [dynamic error, StackTrace? stackTrace]) {
    _logger.i(message, error: error, stackTrace: stackTrace);
  }
  
  /// Log a warning message
  void w(String message, [dynamic error, StackTrace? stackTrace]) {
    _logger.w(message, error: error, stackTrace: stackTrace);
  }
  
  /// Log an error message
  void e(String message, [dynamic error, StackTrace? stackTrace]) {
    _logger.e(message, error: error, stackTrace: stackTrace);
  }
  
  /// Log a fatal error message
  void wtf(String message, [dynamic error, StackTrace? stackTrace]) {
    _logger.f(message, error: error, stackTrace: stackTrace);
  }
}

/// Global logger instance
final logger = AppLogger();