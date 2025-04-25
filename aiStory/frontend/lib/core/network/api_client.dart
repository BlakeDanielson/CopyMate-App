import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

import '../../config/env_config.dart';
import '../utils/logger.dart';

/// Base API client for network requests
class ApiClient {
  /// Dio HTTP client instance
  final Dio dio;
  
  /// Secure storage for tokens
  final FlutterSecureStorage _secureStorage;
  
  /// Auth token key in secure storage
  static const String _authTokenKey = 'auth_token';
  
  /// Refresh token key in secure storage
  static const String _refreshTokenKey = 'refresh_token';

  /// Creates a new API client
  ApiClient({
    required this.dio,
    FlutterSecureStorage? secureStorage,
  }) : _secureStorage = secureStorage ?? const FlutterSecureStorage() {
    _setupInterceptors();
  }

  /// Create a properly configured ApiClient
  factory ApiClient.create() {
    final dio = Dio(
      BaseOptions(
        baseUrl: EnvConfig.apiBaseUrl,
        connectTimeout: const Duration(seconds: 10),
        receiveTimeout: const Duration(seconds: 10),
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      ),
    );

    return ApiClient(dio: dio);
  }

  /// Setup interceptors for logging and authentication
  void _setupInterceptors() {
    // Log requests in debug mode
    if (kDebugMode) {
      dio.interceptors.add(
        InterceptorsWrapper(
          onRequest: (options, handler) {
            logger.d('REQUEST[${options.method}] => PATH: ${options.path}');
            return handler.next(options);
          },
          onResponse: (response, handler) {
            logger.d(
              'RESPONSE[${response.statusCode}] => PATH: ${response.requestOptions.path}',
            );
            return handler.next(response);
          },
          onError: (DioException e, handler) {
            logger.e(
              'ERROR[${e.response?.statusCode}] => PATH: ${e.requestOptions.path}',
              e,
            );
            return handler.next(e);
          },
        ),
      );
    }

    // Authentication interceptor
    dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) async {
          final token = await getAuthToken();
          if (token != null) {
            options.headers['Authorization'] = 'Bearer $token';
          }
          return handler.next(options);
        },
        onError: (DioException e, handler) async {
          // Handle 401 errors (unauthorized)
          if (e.response?.statusCode == 401) {
            // Try to refresh the token
            if (await refreshAuthToken()) {
              // Retry the request with the new token
              final token = await getAuthToken();
              e.requestOptions.headers['Authorization'] = 'Bearer $token';
              
              // Create a new request with the updated token
              final opts = Options(
                method: e.requestOptions.method,
                headers: e.requestOptions.headers,
              );
              
              final response = await dio.request<dynamic>(
                e.requestOptions.path,
                options: opts,
                cancelToken: e.requestOptions.cancelToken,
                onReceiveProgress: e.requestOptions.onReceiveProgress,
                data: e.requestOptions.data,
                queryParameters: e.requestOptions.queryParameters,
              );
              
              return handler.resolve(response);
            }
          }
          return handler.next(e);
        },
      ),
    );
  }

  /// Get the current auth token
  Future<String?> getAuthToken() async {
    return await _secureStorage.read(key: _authTokenKey);
  }

  /// Set the auth token
  Future<void> setAuthToken(String token) async {
    await _secureStorage.write(key: _authTokenKey, value: token);
  }

  /// Get the refresh token
  Future<String?> getRefreshToken() async {
    return await _secureStorage.read(key: _refreshTokenKey);
  }

  /// Set the refresh token
  Future<void> setRefreshToken(String token) async {
    await _secureStorage.write(key: _refreshTokenKey, value: token);
  }

  /// Attempt to refresh the auth token
  Future<bool> refreshAuthToken() async {
    try {
      final refreshToken = await getRefreshToken();
      if (refreshToken == null) {
        return false;
      }

      final response = await dio.post(
        '/auth/refresh',
        data: {'refresh_token': refreshToken},
        options: Options(headers: {'Authorization': null}),
      );

      if (response.statusCode == 200 && response.data != null) {
        final Map<String, dynamic> data = response.data as Map<String, dynamic>;
        final String newToken = data['access_token'] as String;
        final String newRefreshToken = data['refresh_token'] as String;
        
        await setAuthToken(newToken);
        await setRefreshToken(newRefreshToken);
        
        return true;
      }
      
      return false;
    } catch (e) {
      logger.e('Failed to refresh token', e);
      return false;
    }
  }

  /// Clear all auth tokens (logout)
  Future<void> clearTokens() async {
    await _secureStorage.delete(key: _authTokenKey);
    await _secureStorage.delete(key: _refreshTokenKey);
  }
}