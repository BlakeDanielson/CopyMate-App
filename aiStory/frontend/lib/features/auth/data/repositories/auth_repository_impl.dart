import 'package:ai_story/core/utils/logger.dart';
import 'package:ai_story/features/auth/data/datasources/auth_api_client.dart';
import 'package:ai_story/features/auth/data/datasources/auth_storage.dart';
import 'package:ai_story/features/auth/data/dtos/auth_request.dart';
import 'package:ai_story/features/auth/data/dtos/auth_response.dart';
import 'package:ai_story/features/auth/domain/exceptions/auth_exception.dart';
import 'package:ai_story/features/auth/domain/models/user.dart';
import 'package:ai_story/features/auth/domain/repositories/auth_repository.dart';

/// Implementation of the [AuthRepository] interface
class AuthRepositoryImpl implements AuthRepository {
  /// API client for auth requests
  final AuthApiClient _apiClient;
  
  /// Storage service for auth data
  final AuthStorage _authStorage;

  /// Creates a new [AuthRepositoryImpl] instance
  AuthRepositoryImpl({
    required AuthApiClient apiClient,
    required AuthStorage authStorage,
  })  : _apiClient = apiClient,
        _authStorage = authStorage;

  @override
  Future<bool> isAuthenticated() async {
    try {
      final accessToken = await _authStorage.getAccessToken();
      final tokenExpiry = await _authStorage.getTokenExpiry();
      
      if (accessToken == null) {
        return false;
      }
      
      // If token has expiry and it has expired, try to refresh
      if (tokenExpiry != null && DateTime.now().isAfter(tokenExpiry)) {
        // Try to refresh token
        final refreshToken = await _authStorage.getRefreshToken();
        
        if (refreshToken == null) {
          return false;
        }
        
        try {
          final request = RefreshTokenRequest(refreshToken: refreshToken);
          await this.refreshToken(request);
          return true;
        } catch (e) {
          // If refresh token failed, user is not authenticated
          await _authStorage.clearAuthData();
          return false;
        }
      }
      
      return true;
    } catch (e) {
      logger.e('Error checking authentication status', e);
      return false;
    }
  }

  @override
  Future<User?> getCurrentUser() async {
    try {
      return await _authStorage.getUser();
    } catch (e) {
      logger.e('Error getting current user', e);
      return null;
    }
  }

  @override
  Future<AuthResponse> register(RegisterRequest request) async {
    try {
      final response = await _apiClient.register(request);
      
      // Store auth data
      await _authStorage.saveAuthData(response);
      
      return response;
    } catch (e) {
      logger.e('Registration error', e);
      throw AuthException(
        message: 'Registration failed. Please try again.',
      );
    }
  }

  @override
  Future<AuthResponse> login(LoginRequest request) async {
    try {
      final response = await _apiClient.login(request);
      
      // Store auth data
      await _authStorage.saveAuthData(response);
      
      return response;
    } catch (e) {
      logger.e('Login error', e);
      throw AuthException(
        message: 'Login failed. Please check your credentials.',
      );
    }
  }

  @override
  Future<TokenResponse> refreshToken(RefreshTokenRequest request) async {
    try {
      final response = await _apiClient.refreshTokenInternal(request.refreshToken);
      
      // Store the new tokens
      await _authStorage.saveTokenData(response);
      
      return response;
    } catch (e) {
      logger.e('Token refresh error', e);
      throw AuthException(
        message: 'Failed to refresh authentication. Please login again.',
      );
    }
  }

  @override
  Future<void> requestPasswordReset(String email) async {
    try {
      final request = PasswordResetRequest(email: email);
      await _apiClient.requestPasswordReset(request);
    } catch (e) {
      logger.e('Password reset request error', e);
      throw AuthException(
        message: 'Password reset request failed. Please try again.',
      );
    }
  }

  @override
  Future<void> logout() async {
    try {
      await _authStorage.clearAuthData();
    } catch (e) {
      logger.e('Logout error', e);
      throw AuthException(
        message: 'Logout failed. Please try again.',
      );
    }
  }

  @override
  Future<String?> getAccessToken() async {
    try {
      return await _authStorage.getAccessToken();
    } catch (e) {
      logger.e('Error getting access token', e);
      return null;
    }
  }

  @override
  Future<String?> getRefreshToken() async {
    try {
      return await _authStorage.getRefreshToken();
    } catch (e) {
      logger.e('Error getting refresh token', e);
      return null;
    }
  }
}