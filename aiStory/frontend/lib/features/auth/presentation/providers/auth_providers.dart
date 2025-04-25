import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:ai_story/features/auth/data/providers/auth_providers.dart';
import 'package:ai_story/features/auth/domain/models/auth_state.dart';
import 'package:ai_story/features/auth/presentation/providers/auth_notifier.dart';

/// Provider for the AuthNotifier
final authNotifierProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  final repository = ref.watch(authRepositoryProvider);
  return AuthNotifier(authRepository: repository);
});

/// Provider for the auth state
final authStateProvider = Provider<AuthState>((ref) {
  return ref.watch(authNotifierProvider);
});