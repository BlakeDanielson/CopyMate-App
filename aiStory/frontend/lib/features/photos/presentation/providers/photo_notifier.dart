import 'dart:io';

import 'package:flutter/material.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

import '../../../domain/models/photo.dart';
import '../../../domain/models/photo_state.dart';
import '../../../domain/models/photo_status.dart';
import '../../../domain/repositories/photo_repository.dart';

part 'photo_notifier.g.dart';

/// Notifier for managing photo state and operations
@riverpod
class PhotoNotifier extends _$PhotoNotifier {
  @override
  PhotoState build() {
    return PhotoState.initial;
  }

  /// Get photo repository instance
  PhotoRepository get _repository => ref.read(photoRepositoryProvider);

  /// Load all photos for the current user
  Future<void> loadPhotos({
    PhotoStatus? status,
    String? fromDate,
    String? toDate,
    List<String>? tags,
    int page = 1,
    int pageSize = 20,
    bool refresh = false,
  }) async {
    // Don't show loading indicator if refreshing
    if (!refresh) {
      state = state.copyWith(isLoading: true, errorMessage: (_) => null);
    }

    try {
      final photos = await _repository.getPhotos(
        status: status,
        fromDate: fromDate,
        toDate: toDate,
        tags: tags,
        page: page,
        pageSize: pageSize,
      );

      state = state.copyWith(
        photos: photos,
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: () => e.toString(),
      );
    }
  }

  /// Load a specific photo by ID
  Future<void> loadPhoto(String photoId) async {
    state = state.copyWith(isLoading: true, errorMessage: (_) => null);

    try {
      final photo = await _repository.getPhoto(photoId);
      state = state.copyWith(
        selectedPhoto: () => photo,
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: () => e.toString(),
      );
    }
  }

  /// Upload a new photo
  Future<String?> uploadPhoto({
    required File photoFile,
    String? description,
    List<String>? tags,
  }) async {
    state = state.copyWith(
      isUploading: true,
      uploadProgress: 0.0,
      errorMessage: (_) => null,
    );

    try {
      // For demo purposes, simulate upload progress
      for (var i = 1; i <= 10; i++) {
        await Future.delayed(const Duration(milliseconds: 100));
        state = state.copyWith(uploadProgress: i / 10);
      }

      final photoId = await _repository.uploadPhoto(
        photoFile: photoFile,
        description: description,
        tags: tags,
      );

      // Reset upload state
      state = state.copyWith(
        isUploading: false,
        uploadProgress: 1.0,
      );

      // Refresh photos list
      loadPhotos(refresh: true);

      return photoId;
    } catch (e) {
      state = state.copyWith(
        isUploading: false,
        errorMessage: () => e.toString(),
      );
      return null;
    }
  }

  /// Delete a photo
  Future<bool> deletePhoto(String photoId) async {
    try {
      // Show confirmation dialog through the UI, not handled here
      await _repository.deletePhoto(photoId);

      // Remove the photo from the state
      final updatedPhotos = [...state.photos];
      updatedPhotos.removeWhere((photo) => photo.id == photoId);

      state = state.copyWith(photos: updatedPhotos);
      
      // If the deleted photo was selected, clear selection
      if (state.selectedPhoto?.id == photoId) {
        state = state.copyWith(selectedPhoto: () => null);
      }

      return true;
    } catch (e) {
      state = state.copyWith(errorMessage: () => e.toString());
      return false;
    }
  }

  /// Process a photo (generate thumbnails, apply AI processing)
  Future<bool> processPhoto(String photoId) async {
    if (state.isProcessing) {
      return false; // Already processing
    }

    state = state.copyWith(
      isProcessing: true,
      errorMessage: (_) => null,
    );

    try {
      final updatedPhoto = await _repository.processPhoto(photoId);

      // Update photo in the list
      final updatedPhotos = state.photos.map((photo) {
        if (photo.id == photoId) {
          return updatedPhoto;
        }
        return photo;
      }).toList();

      state = state.copyWith(
        photos: updatedPhotos,
        isProcessing: false,
        // If this is the selected photo, update it
        selectedPhoto: state.selectedPhoto?.id == photoId ? () => updatedPhoto : null,
      );

      return true;
    } catch (e) {
      state = state.copyWith(
        isProcessing: false,
        errorMessage: () => e.toString(),
      );
      return false;
    }
  }

  /// Get a URL for a photo
  Future<String?> getPhotoUrl(String photoId, {int? expiresIn}) async {
    try {
      return await _repository.getPhotoUrl(photoId, expiresIn: expiresIn);
    } catch (e) {
      state = state.copyWith(errorMessage: () => e.toString());
      return null;
    }
  }

  /// Clear any error messages
  void clearError() {
    if (state.errorMessage != null) {
      state = state.copyWith(errorMessage: (_) => null);
    }
  }

  /// Select a photo from the list
  void selectPhoto(String photoId) {
    final photo = state.photos.firstWhere(
      (p) => p.id == photoId,
      orElse: () => throw Exception('Photo not found'),
    );
    
    state = state.copyWith(selectedPhoto: () => photo);
  }

  /// Clear selected photo
  void clearSelectedPhoto() {
    state = state.copyWith(selectedPhoto: (_) => null);
  }
}

/// Provider for the photo repository
@riverpod
PhotoRepository photoRepository(PhotoRepositoryRef ref) {
  throw UnimplementedError('Must be overridden in the provider declaration');
}