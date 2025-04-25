import 'dart:io';

import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';

import '../../../../core/network/api_exception.dart';
import '../../domain/models/photo.dart';
import '../../domain/models/photo_status.dart';
import '../dtos/photo_list_filters.dart';
import '../dtos/photo_processing_result.dart';
import '../dtos/photo_upload_response.dart';

/// API client for photo operations
class PhotoApiClient {
  final Dio _dio;
  static const String _baseEndpoint = '/photos';

  /// Creates a new PhotoApiClient
  PhotoApiClient(this._dio);

  /// Upload a photo to the server
  Future<PhotoUploadResponse> uploadPhoto({
    required File photoFile,
    String? description,
    List<String>? tags,
  }) async {
    try {
      // Create form data
      final formData = FormData.fromMap({
        'file': await MultipartFile.fromFile(
          photoFile.path,
          filename: photoFile.path.split('/').last,
        ),
        if (description != null) 'description': description,
        if (tags != null && tags.isNotEmpty) 'tags': tags.join(','),
      });

      // Send request
      final response = await _dio.post(
        '$_baseEndpoint/upload',
        data: formData,
        options: Options(
          headers: {'Content-Type': 'multipart/form-data'},
        ),
      );

      return PhotoUploadResponse.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw ApiException.fromDioError(e);
    } catch (e) {
      throw ApiException(
        message: 'Failed to upload photo: ${e.toString()}',
        statusCode: 500,
      );
    }
  }

  /// Get a photo by ID
  Future<Photo> getPhoto(String photoId) async {
    try {
      final response = await _dio.get('$_baseEndpoint/$photoId');
      return Photo.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw ApiException.fromDioError(e);
    } catch (e) {
      throw ApiException(
        message: 'Failed to get photo: ${e.toString()}',
        statusCode: 500,
      );
    }
  }

  /// Get photos with optional filters
  Future<List<Photo>> getPhotos({
    PhotoStatus? status,
    String? fromDate,
    String? toDate,
    List<String>? tags,
    int page = 1,
    int pageSize = 20,
  }) async {
    try {
      final filters = PhotoListFilters(
        status: status,
        fromDate: fromDate,
        toDate: toDate,
        tags: tags,
        page: page,
        pageSize: pageSize,
      );

      final response = await _dio.get(
        _baseEndpoint,
        queryParameters: filters.toQueryParameters(),
      );

      return (response.data as List)
          .map((item) => Photo.fromJson(item as Map<String, dynamic>))
          .toList();
    } on DioException catch (e) {
      throw ApiException.fromDioError(e);
    } catch (e) {
      throw ApiException(
        message: 'Failed to get photos: ${e.toString()}',
        statusCode: 500,
      );
    }
  }

  /// Delete a photo
  Future<void> deletePhoto(String photoId) async {
    try {
      await _dio.delete('$_baseEndpoint/$photoId');
    } on DioException catch (e) {
      throw ApiException.fromDioError(e);
    } catch (e) {
      throw ApiException(
        message: 'Failed to delete photo: ${e.toString()}',
        statusCode: 500,
      );
    }
  }

  /// Process a photo (generate thumbnails, apply AI enhancements)
  Future<PhotoProcessingResult> processPhoto(String photoId) async {
    try {
      final response = await _dio.patch('$_baseEndpoint/$photoId/process');
      return PhotoProcessingResult.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw ApiException.fromDioError(e);
    } catch (e) {
      throw ApiException(
        message: 'Failed to process photo: ${e.toString()}',
        statusCode: 500,
      );
    }
  }

  /// Get a URL for a photo (possibly with expiration)
  Future<String> getPhotoUrl(String photoId, {int? expiresIn}) async {
    try {
      final queryParams = expiresIn != null ? {'expires_in': expiresIn.toString()} : null;
      
      final response = await _dio.get(
        '$_baseEndpoint/$photoId/url',
        queryParameters: queryParams,
      );

      // The response is directly the URL string
      return response.data as String;
    } on DioException catch (e) {
      throw ApiException.fromDioError(e);
    } catch (e) {
      throw ApiException(
        message: 'Failed to get photo URL: ${e.toString()}',
        statusCode: 500,
      );
    }
  }
}