import 'dart:io';

import '../models/photo.dart';
import '../models/photo_status.dart';

/// Repository interface for photo operations
abstract class PhotoRepository {
  /// Upload a photo
  Future<String> uploadPhoto({
    required File photoFile,
    String? description,
    List<String>? tags,
  });

  /// Get a photo by ID
  Future<Photo> getPhoto(String photoId);

  /// Get photos with optional filters
  Future<List<Photo>> getPhotos({
    PhotoStatus? status,
    String? fromDate,
    String? toDate,
    List<String>? tags,
    int page = 1,
    int pageSize = 20,
  });

  /// Delete a photo
  Future<void> deletePhoto(String photoId);

  /// Process a photo
  Future<Photo> processPhoto(String photoId);

  /// Get a URL for accessing a photo
  Future<String> getPhotoUrl(String photoId, {int? expiresIn});
}