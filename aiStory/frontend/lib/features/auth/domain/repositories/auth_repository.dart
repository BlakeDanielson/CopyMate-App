import 'package:ai_story/features/auth/data/dtos/auth_request.dart';
import 'package:ai_story/features/auth/data/dtos/auth_response.dart';
import 'package:ai_story/features/auth/domain/models/user.dart';

/// Repository for handling authentication operations
abstract class AuthRepository {
  /// Check if user is authenticated
  Future<bool> isAuthenticated();

  /// Get current authenticated user
  Future<User?> getCurrentUser();

  /// Register a new user
  Future<AuthResponse> register(RegisterRequest request);

  /// Login with credentials
  Future<AuthResponse> login(LoginRequest request);

  /// Refresh authentication token
  Future<TokenResponse> refreshToken(RefreshTokenRequest request);

  /// Request password reset
  Future<void> requestPasswordReset(String email);

  /// Logout current user
  Future<void> logout();

  /// Get access token from storage
  Future<String?> getAccessToken();

  /// Get refresh token from storage
  Future<String?> getRefreshToken();
}