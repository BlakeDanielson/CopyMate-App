import 'package:dio/dio.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

import '../../../../core/network/api_client.dart';
import '../../data/datasources/photo_api_client.dart';
import '../../data/repositories/photo_repository_impl.dart';
import '../../domain/repositories/photo_repository.dart';
import 'photo_notifier.dart';

part 'photo_providers.g.dart';

/// Provider for the API client
@riverpod
ApiClient apiClient(ApiClientRef ref) {
  return ApiClient.create();
}

/// Provider for the Dio HTTP client
@riverpod
Dio dioClient(DioClientRef ref) {
  return ref.watch(apiClientProvider).dio;
}

/// Provider for the photo API client
@riverpod
PhotoApiClient photoApiClient(PhotoApiClientRef ref) {
  final dio = ref.watch(dioClientProvider);
  return PhotoApiClient(dio);
}

/// Provider for the photo repository
@riverpod
PhotoRepository photoRepository(PhotoRepositoryRef ref) {
  final apiClient = ref.watch(photoApiClientProvider);
  return PhotoRepositoryImpl(apiClient);
}