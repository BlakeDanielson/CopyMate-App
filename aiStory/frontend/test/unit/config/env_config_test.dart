import 'package:flutter_test/flutter_test.dart';
import 'package:ai_story/config/env_config.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'dart:io';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  group('EnvConfig', () {
    setUp(() async {
      // Create a temporary test .env file
      final testEnv = File('test/.env.test');
      await testEnv.writeAsString('''
API_BASE_URL=https://test-api.example.com
ENVIRONMENT=test
LOG_LEVEL=debug
ENABLE_MOCK=true
''');
      
      // Load the test .env file
      await dotenv.load(fileName: 'test/.env.test');
    });

    tearDown(() async {
      // Clean up the temporary file
      final testEnv = File('test/.env.test');
      if (await testEnv.exists()) {
        await testEnv.delete();
      }
    });

    test('should get API base URL from environment', () {
      expect(dotenv.env['API_BASE_URL'], 'https://test-api.example.com');
      expect(EnvConfig.get('API_BASE_URL'), 'https://test-api.example.com');
    });

    test('should get environment from environment variables', () {
      expect(dotenv.env['ENVIRONMENT'], 'test');
      expect(EnvConfig.environment, 'test');
    });

    test('should get log level from environment variables', () {
      expect(dotenv.env['LOG_LEVEL'], 'debug');
      expect(EnvConfig.logLevel, 'debug');
    });

    test('should get enable mock flag from environment variables', () {
      expect(dotenv.env['ENABLE_MOCK'], 'true');
      expect(EnvConfig.enableMock, true);
    });
  });
}