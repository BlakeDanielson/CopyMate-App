import 'package:dio/dio.dart';
import 'package:ai_story/core/utils/logger.dart';
import 'package:ai_story/features/auth/data/datasources/auth_storage.dart';
import 'package:ai_story/features/auth/data/dtos/auth_request.dart';
import 'package:ai_story/features/auth/data/dtos/auth_response.dart';
import 'package:ai_story/features/auth/domain/exceptions/auth_exception.dart';

/// API client for authentication requests
class AuthApiClient {
  /// Dio HTTP client
  final Dio _dio;
  
  /// Auth storage for token management
  final AuthStorage _authStorage;
  
  /// Base URL for API requests
  final String _baseUrl;

  /// Creates a new [AuthApiClient] instance
  AuthApiClient({
    required String baseUrl,
    required AuthStorage authStorage,
    Dio? dio,
  })  : _baseUrl = baseUrl,
        _authStorage = authStorage,
        _dio = dio ?? Dio() {
    _setupInterceptors();
  }

  /// Set up request and response interceptors
  void _setupInterceptors() {
    // Add authorization header to requests
    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) async {
          // Skip adding auth token for auth endpoints
          if (_isAuthEndpoint(options.path)) {
            return handler.next(options);
          }

          // Add auth token to other endpoints
          final token = await _authStorage.getAccessToken();
          if (token != null) {
            options.headers['Authorization'] = 'Bearer $token';
          }
          return handler.next(options);
        },
        onError: (error, handler) async {
          if (error.response?.statusCode == 401) {
            // Token has expired, try to refresh
            try {
              final refreshToken = await _authStorage.getRefreshToken();
              if (refreshToken != null) {
                final tokenResponse = await refreshTokenInternal(refreshToken);
                await _authStorage.saveTokenData(tokenResponse);
                
                // Retry the original request with new token
                final RequestOptions requestOptions = error.requestOptions;
                final options = Options(
                  method: requestOptions.method,
                  headers: {
                    ...requestOptions.headers,
                    'Authorization': 'Bearer ${tokenResponse.accessToken}'
                  },
                );
                
                final response = await _dio.request<dynamic>(
                  requestOptions.path,
                  options: options,
                  data: requestOptions.data,
                  queryParameters: requestOptions.queryParameters,
                );
                
                return handler.resolve(response);
              }
            } catch (e) {
              // If refresh fails, logout
              await _authStorage.clearAuthData();
              logger.e('Token refresh error', e);
            }
          }
          
          return handler.next(error);
        },
      ),
    );
  }

  /// Check if the path is an auth endpoint
  bool _isAuthEndpoint(String path) {
    return path.contains('/auth/login') ||
        path.contains('/auth/register') ||
        path.contains('/auth/refresh-token') ||
        path.contains('/auth/password-reset');
  }

  /// Register a new user
  Future<AuthResponse> register(RegisterRequest request) async {
    try {
      final response = await _dio.post(
        '$_baseUrl/auth/register',
        data: request.toJson(),
      );
      
      // Convert response data to auth response
      final responseData = response.data as Map<String, dynamic>;
      return AuthResponse.fromJson(responseData);
    } on DioException catch (e) {
      _handleDioError(e);
      rethrow;
    } catch (e) {
      logger.e('Registration error', e);
      throw AuthException(message: 'Registration failed: ${e.toString()}');
    }
  }

  /// Login with credentials
  Future<AuthResponse> login(LoginRequest request) async {
    try {
      final response = await _dio.post(
        '$_baseUrl/auth/login',
        data: request.toJson(),
      );
      
      // Convert response data to auth response
      final responseData = response.data as Map<String, dynamic>;
      return AuthResponse.fromJson(responseData);
    } on DioException catch (e) {
      _handleDioError(e);
      rethrow;
    } catch (e) {
      logger.e('Login error', e);
      throw AuthException(message: 'Login failed: ${e.toString()}');
    }
  }

  /// Refresh token
  Future<TokenResponse> refreshTokenInternal(String refreshToken) async {
    try {
      final refreshRequest = RefreshTokenRequest(refreshToken: refreshToken);
      final response = await _dio.post(
        '$_baseUrl/auth/refresh-token',
        data: refreshRequest.toJson(),
      );
      
      // Convert response data to token response
      final responseData = response.data as Map<String, dynamic>;
      final tokenResponse = TokenResponse.fromJson(responseData);
      
      return tokenResponse;
    } on DioException catch (e) {
      _handleDioError(e);
      rethrow;
    } catch (e) {
      logger.e('Token refresh error', e);
      throw AuthException(message: 'Token refresh failed: ${e.toString()}');
    }
  }

  /// Request password reset
  Future<void> requestPasswordReset(PasswordResetRequest request) async {
    try {
      await _dio.post(
        '$_baseUrl/auth/password-reset',
        data: request.toJson(),
      );
    } on DioException catch (e) {
      _handleDioError(e);
      rethrow;
    } catch (e) {
      logger.e('Password reset request error', e);
      throw AuthException(message: 'Password reset request failed: ${e.toString()}');
    }
  }

  /// Handle DioException errors
  void _handleDioError(DioException e) {
    logger.e('API error', e);
    
    if (e.type == DioExceptionType.connectionTimeout ||
        e.type == DioExceptionType.sendTimeout ||
        e.type == DioExceptionType.receiveTimeout) {
      throw AuthException(
        message: 'Connection timeout. Please check your network.',
        code: 'timeout',
      );
    }
    
    if (e.type == DioExceptionType.connectionError) {
      throw AuthException(
        message: 'Network error. Please check your connection.',
        code: 'network_error',
      );
    }
    
    if (e.response == null) {
      throw AuthException(
        message: 'An unexpected error occurred. Please try again.',
        code: 'unknown_error',
      );
    }
    
    final statusCode = e.response!.statusCode;
    final responseData = e.response!.data;
    
    if (statusCode == 401) {
      throw AuthException(
        message: 'Invalid credentials or session expired.',
        code: 'unauthorized',
        statusCode: statusCode,
      );
    } else if (statusCode == 409) {
      throw AuthException(
        message: 'User already exists.',
        code: 'conflict',
        statusCode: statusCode,
      );
    } else if (statusCode! >= 500) {
      throw AuthException(
        message: 'Server error. Please try again later.',
        code: 'server_error',
        statusCode: statusCode,
      );
    } else {
      final errorMessage = responseData is Map && responseData['message'] != null
          ? responseData['message']
          : 'An error occurred. Please try again.';
          
      throw AuthException(
        message: errorMessage.toString(),
        code: 'api_error',
        statusCode: statusCode,
      );
    }
  }
}