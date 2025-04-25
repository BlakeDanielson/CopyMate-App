import 'package:flutter/foundation.dart';
import 'package:ai_story/features/auth/domain/models/user.dart';

/// Authentication status
enum AuthStatus {
  /// User is authenticated
  authenticated,
  
  /// User is not authenticated
  unauthenticated,
  
  /// Authentication is in progress
  loading,
  
  /// Authentication error occurred
  error,
  
  /// Test mode is active (no real authentication)
  testMode
}

/// Authentication state
@immutable
abstract class AuthState {
  /// Creates a new [AuthState] instance
  const AuthState();

  /// Factory for authenticated state
  const factory AuthState.authenticated({
    required User user,
    required String accessToken,
    required String refreshToken,
  }) = AuthenticatedState;

  /// Factory for unauthenticated state
  const factory AuthState.unauthenticated() = UnauthenticatedState;

  /// Factory for loading state
  const factory AuthState.loading() = LoadingAuthState;

  /// Factory for error state
  const factory AuthState.error({
    required String message,
  }) = ErrorAuthState;
  
  /// Factory for test mode state
  const factory AuthState.testMode({
    required User user,
  }) = TestModeActiveState;

  /// Map the state to a value based on its type
  T map<T>({
    required T Function(AuthenticatedState) authenticated,
    required T Function(UnauthenticatedState) unauthenticated,
    required T Function(LoadingAuthState) loading,
    required T Function(ErrorAuthState) error,
    required T Function(TestModeActiveState) testMode,
  });

  /// Map the state to a value based on its type, with a default value
  T maybeMap<T>({
    T Function(AuthenticatedState)? authenticated,
    T Function(UnauthenticatedState)? unauthenticated,
    T Function(LoadingAuthState)? loading,
    T Function(ErrorAuthState)? error,
    T Function(TestModeActiveState)? testMode,
    required T Function() orElse,
  });
  
  /// Check if the state is test mode
  bool get isTestMode => this is TestModeActiveState;
}

/// Authenticated state
class AuthenticatedState extends AuthState {
  /// Authenticated user
  final User user;
  
  /// Access token
  final String accessToken;
  
  /// Refresh token
  final String refreshToken;

  /// Creates a new [AuthenticatedState] instance
  const AuthenticatedState({
    required this.user,
    required this.accessToken,
    required this.refreshToken,
  });

  @override
  T map<T>({
    required T Function(AuthenticatedState) authenticated,
    required T Function(UnauthenticatedState) unauthenticated,
    required T Function(LoadingAuthState) loading,
    required T Function(ErrorAuthState) error,
    required T Function(TestModeActiveState) testMode,
  }) {
    return authenticated(this);
  }

  @override
  T maybeMap<T>({
    T Function(AuthenticatedState)? authenticated,
    T Function(UnauthenticatedState)? unauthenticated,
    T Function(LoadingAuthState)? loading,
    T Function(ErrorAuthState)? error,
    T Function(TestModeActiveState)? testMode,
    required T Function() orElse,
  }) {
    return authenticated != null ? authenticated(this) : orElse();
  }
}

/// Unauthenticated state
class UnauthenticatedState extends AuthState {
  /// Creates a new [UnauthenticatedState] instance
  const UnauthenticatedState();

  @override
  T map<T>({
    required T Function(AuthenticatedState) authenticated,
    required T Function(UnauthenticatedState) unauthenticated,
    required T Function(LoadingAuthState) loading,
    required T Function(ErrorAuthState) error,
    required T Function(TestModeActiveState) testMode,
  }) {
    return unauthenticated(this);
  }

  @override
  T maybeMap<T>({
    T Function(AuthenticatedState)? authenticated,
    T Function(UnauthenticatedState)? unauthenticated,
    T Function(LoadingAuthState)? loading,
    T Function(ErrorAuthState)? error,
    T Function(TestModeActiveState)? testMode,
    required T Function() orElse,
  }) {
    return unauthenticated != null ? unauthenticated(this) : orElse();
  }
}

/// Loading authentication state
class LoadingAuthState extends AuthState {
  /// Creates a new [LoadingAuthState] instance
  const LoadingAuthState();

  @override
  T map<T>({
    required T Function(AuthenticatedState) authenticated,
    required T Function(UnauthenticatedState) unauthenticated,
    required T Function(LoadingAuthState) loading,
    required T Function(ErrorAuthState) error,
    required T Function(TestModeActiveState) testMode,
  }) {
    return loading(this);
  }

  @override
  T maybeMap<T>({
    T Function(AuthenticatedState)? authenticated,
    T Function(UnauthenticatedState)? unauthenticated,
    T Function(LoadingAuthState)? loading,
    T Function(ErrorAuthState)? error,
    T Function(TestModeActiveState)? testMode,
    required T Function() orElse,
  }) {
    return loading != null ? loading(this) : orElse();
  }
}

/// Error authentication state
class ErrorAuthState extends AuthState {
  /// Error message
  final String message;

  /// Creates a new [ErrorAuthState] instance
  const ErrorAuthState({
    required this.message,
  });

  @override
  T map<T>({
    required T Function(AuthenticatedState) authenticated,
    required T Function(UnauthenticatedState) unauthenticated,
    required T Function(LoadingAuthState) loading,
    required T Function(ErrorAuthState) error,
    required T Function(TestModeActiveState) testMode,
  }) {
    return error(this);
  }

  @override
  T maybeMap<T>({
    T Function(AuthenticatedState)? authenticated,
    T Function(UnauthenticatedState)? unauthenticated,
    T Function(LoadingAuthState)? loading,
    T Function(ErrorAuthState)? error,
    T Function(TestModeActiveState)? testMode,
    required T Function() orElse,
  }) {
    return error != null ? error(this) : orElse();
  }
}

/// Test mode active state
class TestModeActiveState extends AuthState {
  /// Mock user for test mode
  final User user;

  /// Creates a new [TestModeActiveState] instance
  const TestModeActiveState({
    required this.user,
  });

  @override
  T map<T>({
    required T Function(AuthenticatedState) authenticated,
    required T Function(UnauthenticatedState) unauthenticated,
    required T Function(LoadingAuthState) loading,
    required T Function(ErrorAuthState) error,
    required T Function(TestModeActiveState) testMode,
  }) {
    return testMode(this);
  }

  @override
  T maybeMap<T>({
    T Function(AuthenticatedState)? authenticated,
    T Function(UnauthenticatedState)? unauthenticated,
    T Function(LoadingAuthState)? loading,
    T Function(ErrorAuthState)? error,
    T Function(TestModeActiveState)? testMode,
    required T Function() orElse,
  }) {
    return testMode != null ? testMode(this) : orElse();
  }
}

/// Mock user data for test mode
class MockUserData {
  /// Get a mock user for test mode
  static User getMockUser() {
    return User(
      id: 'mock-user-id',
      username: 'test_user',
      email: 'test@example.com',
      firstName: 'Test',
      lastName: 'User',
      role: 'user',
      createdAt: DateTime.now(),
      updatedAt: DateTime.now(),
    );
  }
}