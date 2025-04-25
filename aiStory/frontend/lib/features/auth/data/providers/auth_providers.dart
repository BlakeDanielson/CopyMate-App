import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:ai_story/config/env_config.dart';
import 'package:ai_story/features/auth/data/datasources/auth_api_client.dart';
import 'package:ai_story/features/auth/data/datasources/auth_storage.dart';
import 'package:ai_story/features/auth/data/repositories/auth_repository_impl.dart';
import 'package:ai_story/features/auth/domain/repositories/auth_repository.dart';

/// Provider for the auth storage
final authStorageProvider = Provider<AuthStorage>((ref) {
  return AuthStorage();
});

/// Provider for the auth API client
final authApiClientProvider = Provider<AuthApiClient>((ref) {
  final authStorage = ref.watch(authStorageProvider);
  
  return AuthApiClient(
    baseUrl: EnvConfig.apiBaseUrl,
    authStorage: authStorage,
  );
});

/// Provider for the auth repository
final authRepositoryProvider = Provider<AuthRepository>((ref) {
  final apiClient = ref.watch(authApiClientProvider);
  final authStorage = ref.watch(authStorageProvider);
  
  return AuthRepositoryImpl(
    apiClient: apiClient,
    authStorage: authStorage,
  );
});