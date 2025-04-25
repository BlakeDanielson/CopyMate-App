import 'package:flutter_dotenv/flutter_dotenv.dart';

/// Environment configuration for the application
/// Provides access to environment variables defined in .env files
class EnvConfig {
  static final EnvConfig _instance = EnvConfig._internal();
  factory EnvConfig() => _instance;
  EnvConfig._internal();

  /// Initialize the environment configuration
  /// Loads the appropriate .env file based on environment
  static Future<void> initialize(String environment) async {
    String envFile;
    
    switch (environment) {
      case 'development':
        envFile = '.env.development';
        break;
      case 'staging':
        envFile = '.env.staging';
        break;
      case 'production':
        envFile = '.env.production';
        break;
      default:
        envFile = '.env.development'; // Default to development
    }
    
    await dotenv.load(fileName: envFile);
  }

  /// Get the value of an environment variable
  static String get(String key) {
    return dotenv.env[key] ?? '';
  }

  /// Get the API base URL
  static String get apiBaseUrl => get('API_BASE_URL');
  
  /// Get the current environment
  static String get environment => get('ENVIRONMENT');
  
  /// Get the log level
  static String get logLevel => get('LOG_LEVEL');
  
  /// Check if mock data should be enabled
  static bool get enableMock => get('ENABLE_MOCK').toLowerCase() == 'true';
}