import 'package:flutter/foundation.dart';
import 'package:ai_story/features/auth/domain/models/user.dart';

/// Authentication response DTO
@immutable
class AuthResponse {
  /// Authenticated user
  final User user;
  
  /// Access token
  final String accessToken;
  
  /// Refresh token
  final String refreshToken;
  
  /// Token type (e.g. 'Bearer')
  final String tokenType;
  
  /// Time until the token expires (in seconds)
  final int? expiresIn;

  /// Creates a new [AuthResponse] instance
  const AuthResponse({
    required this.user,
    required this.accessToken,
    required this.refreshToken,
    this.tokenType = 'Bearer',
    this.expiresIn,
  });

  /// Create from JSON
  factory AuthResponse.fromJson(Map<String, dynamic> json) {
    return AuthResponse(
      user: User.fromJson(json['user'] as Map<String, dynamic>),
      accessToken: json['accessToken'] as String,
      refreshToken: json['refreshToken'] as String,
      tokenType: json['tokenType'] as String? ?? 'Bearer',
      expiresIn: json['expiresIn'] as int?,
    );
  }

  /// Convert to JSON
  Map<String, dynamic> toJson() {
    return {
      'user': user.toJson(),
      'accessToken': accessToken,
      'refreshToken': refreshToken,
      'tokenType': tokenType,
      if (expiresIn != null) 'expiresIn': expiresIn,
    };
  }
}

/// Token refresh response DTO
@immutable
class TokenResponse {
  /// Access token
  final String accessToken;
  
  /// Refresh token
  final String refreshToken;
  
  /// Token type (e.g. 'Bearer')
  final String tokenType;
  
  /// Time until the token expires (in seconds)
  final int? expiresIn;

  /// Creates a new [TokenResponse] instance
  const TokenResponse({
    required this.accessToken,
    required this.refreshToken,
    this.tokenType = 'Bearer',
    this.expiresIn,
  });

  /// Create from JSON
  factory TokenResponse.fromJson(Map<String, dynamic> json) {
    return TokenResponse(
      accessToken: json['accessToken'] as String,
      refreshToken: json['refreshToken'] as String,
      tokenType: json['tokenType'] as String? ?? 'Bearer',
      expiresIn: json['expiresIn'] as int?,
    );
  }

  /// Convert to JSON
  Map<String, dynamic> toJson() {
    return {
      'accessToken': accessToken,
      'refreshToken': refreshToken,
      'tokenType': tokenType,
      if (expiresIn != null) 'expiresIn': expiresIn,
    };
  }
}