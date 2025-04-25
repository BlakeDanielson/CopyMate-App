import 'package:flutter/foundation.dart';

/// Exception thrown when an authentication error occurs
@immutable
class AuthException implements Exception {
  /// Error message
  final String message;
  
  /// Error code
  final String? code;
  
  /// HTTP status code
  final int? statusCode;

  /// Creates a new [AuthException] instance
  const AuthException({
    required this.message,
    this.code,
    this.statusCode,
  });

  @override
  String toString() {
    final codeInfo = code != null ? ' [Code: $code]' : '';
    final statusInfo = statusCode != null ? ' [Status: $statusCode]' : '';
    return 'AuthException: $message$codeInfo$statusInfo';
  }

  /// Factory for a generic authentication error
  factory AuthException.generic() {
    return const AuthException(
      message: 'An authentication error occurred. Please try again later.',
      code: 'auth_error',
    );
  }

  /// Factory for an invalid credentials error
  factory AuthException.invalidCredentials() {
    return const AuthException(
      message: 'Invalid username or password.',
      code: 'invalid_credentials',
      statusCode: 401,
    );
  }

  /// Factory for a user already exists error
  factory AuthException.userAlreadyExists() {
    return const AuthException(
      message: 'User with this username or email already exists.',
      code: 'user_exists',
      statusCode: 409,
    );
  }

  /// Factory for a token expired error
  factory AuthException.tokenExpired() {
    return const AuthException(
      message: 'Your session has expired. Please sign in again.',
      code: 'token_expired',
      statusCode: 401,
    );
  }

  /// Factory for a network error
  factory AuthException.network() {
    return const AuthException(
      message: 'Network error. Please check your connection and try again.',
      code: 'network_error',
    );
  }

  /// Factory for a server error
  factory AuthException.server() {
    return const AuthException(
      message: 'Server error. Please try again later.',
      code: 'server_error',
      statusCode: 500,
    );
  }
}