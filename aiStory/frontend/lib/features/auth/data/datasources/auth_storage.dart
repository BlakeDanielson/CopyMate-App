import 'dart:convert';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:ai_story/core/utils/logger.dart';
import 'package:ai_story/features/auth/data/dtos/auth_response.dart';
import 'package:ai_story/features/auth/domain/models/user.dart';

/// Storage keys for authentication data
class AuthStorageKeys {
  /// Access token key
  static const accessToken = 'access_token';
  
  /// Refresh token key
  static const refreshToken = 'refresh_token';
  
  /// User data key
  static const userData = 'user_data';
  
  /// Token expiry date key
  static const tokenExpiry = 'token_expiry';

  /// Private constructor to prevent instantiation
  const AuthStorageKeys._();
}

/// Service to handle secure storage of authentication data
class AuthStorage {
  /// Secure storage instance
  final FlutterSecureStorage _secureStorage;

  /// Creates a new [AuthStorage] instance
  AuthStorage({FlutterSecureStorage? secureStorage})
      : _secureStorage = secureStorage ?? const FlutterSecureStorage();

  /// Save authentication data to secure storage
  Future<void> saveAuthData(AuthResponse response) async {
    try {
      // Save tokens
      await _secureStorage.write(
          key: AuthStorageKeys.accessToken, value: response.accessToken);

      await _secureStorage.write(
          key: AuthStorageKeys.refreshToken, value: response.refreshToken);

      await _secureStorage.write(
          key: AuthStorageKeys.userData, value: jsonEncode(response.user.toJson()));

      // Calculate and save token expiry time if available
      if (response.expiresIn != null) {
        final expiryDate = DateTime.now()
            .add(Duration(seconds: response.expiresIn!))
            .toIso8601String();
        await _secureStorage.write(
            key: AuthStorageKeys.tokenExpiry, value: expiryDate);
      }
    } catch (e) {
      logger.e('Error saving auth data', e);
      rethrow;
    }
  }

  /// Save token data from token response
  Future<void> saveTokenData(TokenResponse response) async {
    try {
      // Save tokens
      await _secureStorage.write(
          key: AuthStorageKeys.accessToken, value: response.accessToken);

      await _secureStorage.write(
          key: AuthStorageKeys.refreshToken, value: response.refreshToken);

      // Calculate and save token expiry time if available
      if (response.expiresIn != null) {
        final expiryDate = DateTime.now()
            .add(Duration(seconds: response.expiresIn!))
            .toIso8601String();
        await _secureStorage.write(
            key: AuthStorageKeys.tokenExpiry, value: expiryDate);
      }
    } catch (e) {
      logger.e('Error saving token data', e);
      rethrow;
    }
  }

  /// Clear all authentication data from storage
  Future<void> clearAuthData() async {
    try {
      await _secureStorage.delete(key: AuthStorageKeys.accessToken);
      await _secureStorage.delete(key: AuthStorageKeys.refreshToken);
      await _secureStorage.delete(key: AuthStorageKeys.userData);
      await _secureStorage.delete(key: AuthStorageKeys.tokenExpiry);
    } catch (e) {
      logger.e('Error clearing auth data', e);
      rethrow;
    }
  }

  /// Get access token from storage
  Future<String?> getAccessToken() async {
    try {
      return await _secureStorage.read(key: AuthStorageKeys.accessToken);
    } catch (e) {
      logger.e('Error getting access token', e);
      return null;
    }
  }

  /// Get refresh token from storage
  Future<String?> getRefreshToken() async {
    try {
      return await _secureStorage.read(key: AuthStorageKeys.refreshToken);
    } catch (e) {
      logger.e('Error getting refresh token', e);
      return null;
    }
  }

  /// Get token expiry date from storage
  Future<DateTime?> getTokenExpiry() async {
    try {
      final expiryString = await _secureStorage.read(key: AuthStorageKeys.tokenExpiry);
      if (expiryString == null) {
        return null;
      }
      return DateTime.parse(expiryString);
    } catch (e) {
      logger.e('Error getting token expiry', e);
      return null;
    }
  }

  /// Get stored user from storage
  Future<User?> getUser() async {
    try {
      final userJson = await _secureStorage.read(key: AuthStorageKeys.userData);
      if (userJson == null) {
        return null;
      }
      
      // Convert JSON string to Map and then create a User object
      final Map<String, dynamic> userMap = jsonDecode(userJson) as Map<String, dynamic>;
      return User.fromJson(userMap);
    } catch (e) {
      logger.e('Error getting user data', e);
      return null;
    }
  }
}