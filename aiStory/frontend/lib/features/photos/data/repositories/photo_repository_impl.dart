import 'dart:io';

import '../../../../core/network/api_exception.dart';
import '../../domain/models/photo.dart';
import '../../domain/models/photo_status.dart';
import '../../domain/repositories/photo_repository.dart';
import '../datasources/photo_api_client.dart';
import '../dtos/photo_processing_result.dart';

/// Implementation of PhotoRepository using the API client
class PhotoRepositoryImpl implements PhotoRepository {
  /// API client for photo operations
  final PhotoApiClient _apiClient;

  /// Creates a new PhotoRepositoryImpl
  PhotoRepositoryImpl(this._apiClient);

  @override
  Future<String> uploadPhoto({
    required File photoFile,
    String? description,
    List<String>? tags,
  }) async {
    try {
      final response = await _apiClient.uploadPhoto(
        photoFile: photoFile,
        description: description,
        tags: tags,
      );
      return response.photoId;
    } on ApiException catch (e) {
      throw _handleApiException(e, 'Failed to upload photo');
    } catch (e) {
      throw Exception('Failed to upload photo: ${e.toString()}');
    }
  }

  @override
  Future<Photo> getPhoto(String photoId) async {
    try {
      return await _apiClient.getPhoto(photoId);
    } on ApiException catch (e) {
      throw _handleApiException(e, 'Failed to get photo');
    } catch (e) {
      throw Exception('Failed to get photo: ${e.toString()}');
    }
  }

  @override
  Future<List<Photo>> getPhotos({
    PhotoStatus? status,
    String? fromDate,
    String? toDate,
    List<String>? tags,
    int page = 1,
    int pageSize = 20,
  }) async {
    try {
      return await _apiClient.getPhotos(
        status: status,
        fromDate: fromDate,
        toDate: toDate,
        tags: tags,
        page: page,
        pageSize: pageSize,
      );
    } on ApiException catch (e) {
      throw _handleApiException(e, 'Failed to get photos');
    } catch (e) {
      throw Exception('Failed to get photos: ${e.toString()}');
    }
  }

  @override
  Future<void> deletePhoto(String photoId) async {
    try {
      await _apiClient.deletePhoto(photoId);
    } on ApiException catch (e) {
      throw _handleApiException(e, 'Failed to delete photo');
    } catch (e) {
      throw Exception('Failed to delete photo: ${e.toString()}');
    }
  }

  @override
  Future<Photo> processPhoto(String photoId) async {
    try {
      final PhotoProcessingResult result = await _apiClient.processPhoto(photoId);
      
      // Get the updated photo after processing
      return await _apiClient.getPhoto(photoId);
    } on ApiException catch (e) {
      throw _handleApiException(e, 'Failed to process photo');
    } catch (e) {
      throw Exception('Failed to process photo: ${e.toString()}');
    }
  }

  @override
  Future<String> getPhotoUrl(String photoId, {int? expiresIn}) async {
    try {
      return await _apiClient.getPhotoUrl(photoId, expiresIn: expiresIn);
    } on ApiException catch (e) {
      throw _handleApiException(e, 'Failed to get photo URL');
    } catch (e) {
      throw Exception('Failed to get photo URL: ${e.toString()}');
    }
  }

  /// Translates API exceptions to domain exceptions
  Exception _handleApiException(ApiException e, String message) {
    // Convert API-specific errors to more generic domain errors
    if (e.statusCode == 404) {
      return Exception('Photo not found');
    } else if (e.statusCode == 403) {
      return Exception('You do not have permission to access this photo');
    } else if (e.statusCode == 401) {
      return Exception('Authentication required');
    } else {
      return Exception('$message: ${e.message}');
    }
  }
}