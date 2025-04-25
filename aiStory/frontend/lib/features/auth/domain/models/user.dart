import 'package:flutter/foundation.dart';

/// User model
@immutable
class User {
  /// User ID
  final String id;
  
  /// Username
  final String username;
  
  /// Email
  final String email;
  
  /// First name
  final String? firstName;
  
  /// Last name
  final String? lastName;
  
  /// User role
  final String role;
  
  /// Created at timestamp
  final DateTime? createdAt;
  
  /// Updated at timestamp
  final DateTime? updatedAt;

  /// Creates a new [User] instance
  const User({
    required this.id,
    required this.username,
    required this.email,
    this.firstName,
    this.lastName,
    required this.role,
    this.createdAt,
    this.updatedAt,
  });

  /// Creates a copy of this User with the given fields replaced with new values
  User copyWith({
    String? id,
    String? username,
    String? email,
    String? firstName,
    String? lastName,
    String? role,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return User(
      id: id ?? this.id,
      username: username ?? this.username,
      email: email ?? this.email,
      firstName: firstName ?? this.firstName,
      lastName: lastName ?? this.lastName,
      role: role ?? this.role,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }

  /// Convert User object to JSON map
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'username': username,
      'email': email,
      'firstName': firstName,
      'lastName': lastName,
      'role': role,
      'createdAt': createdAt?.toIso8601String(),
      'updatedAt': updatedAt?.toIso8601String(),
    };
  }

  /// Create a User object from JSON map
  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'] as String,
      username: json['username'] as String,
      email: json['email'] as String,
      firstName: json['firstName'] as String?,
      lastName: json['lastName'] as String?,
      role: json['role'] as String,
      createdAt: json['createdAt'] != null
          ? DateTime.parse(json['createdAt'] as String)
          : null,
      updatedAt: json['updatedAt'] != null
          ? DateTime.parse(json['updatedAt'] as String)
          : null,
    );
  }
}