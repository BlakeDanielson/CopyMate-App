import 'package:flutter/foundation.dart';

/// Login request DTO
@immutable
class LoginRequest {
  /// Username or email
  final String username;
  
  /// Password
  final String password;

  /// Creates a new [LoginRequest] instance
  const LoginRequest({
    required this.username,
    required this.password,
  });

  /// Convert to JSON
  Map<String, dynamic> toJson() {
    return {
      'username': username,
      'password': password,
    };
  }
}

/// Register request DTO
@immutable
class RegisterRequest {
  /// Username
  final String username;
  
  /// Email
  final String email;
  
  /// Password
  final String password;
  
  /// First name (optional)
  final String? firstName;
  
  /// Last name (optional)
  final String? lastName;

  /// Creates a new [RegisterRequest] instance
  const RegisterRequest({
    required this.username,
    required this.email,
    required this.password,
    this.firstName,
    this.lastName,
  });

  /// Convert to JSON
  Map<String, dynamic> toJson() {
    return {
      'username': username,
      'email': email,
      'password': password,
      if (firstName != null) 'firstName': firstName,
      if (lastName != null) 'lastName': lastName,
    };
  }
}

/// Refresh token request DTO
@immutable
class RefreshTokenRequest {
  /// Refresh token
  final String refreshToken;

  /// Creates a new [RefreshTokenRequest] instance
  const RefreshTokenRequest({
    required this.refreshToken,
  });

  /// Convert to JSON
  Map<String, dynamic> toJson() {
    return {
      'refreshToken': refreshToken,
    };
  }
}

/// Password reset request DTO
@immutable
class PasswordResetRequest {
  /// Email
  final String email;

  /// Creates a new [PasswordResetRequest] instance
  const PasswordResetRequest({
    required this.email,
  });

  /// Convert to JSON
  Map<String, dynamic> toJson() {
    return {
      'email': email,
    };
  }
}