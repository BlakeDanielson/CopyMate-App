import 'package:flutter/foundation.dart';

import 'photo.dart';

/// Represents the state of photos for the application
class PhotoState {
  /// List of photos
  final List<Photo> photos;
  
  /// Currently selected photo
  final Photo? selectedPhoto;
  
  /// Whether photos are currently being loaded
  final bool isLoading;
  
  /// Error message if there was an error loading photos
  final String? errorMessage;
  
  /// Whether a photo is currently being uploaded
  final bool isUploading;
  
  /// Upload progress (0.0 to 1.0)
  final double uploadProgress;
  
  /// Whether a photo is currently being processed
  final bool isProcessing;
  
  /// Creates a new PhotoState
  const PhotoState({
    this.photos = const [],
    this.selectedPhoto,
    this.isLoading = false,
    this.errorMessage,
    this.isUploading = false,
    this.uploadProgress = 0.0,
    this.isProcessing = false,
  });

  /// Creates a copy of this PhotoState with the given fields replaced with new values
  PhotoState copyWith({
    List<Photo>? photos,
    ValueGetter<Photo?>? selectedPhoto,
    bool? isLoading,
    ValueGetter<String?>? errorMessage,
    bool? isUploading,
    double? uploadProgress,
    bool? isProcessing,
  }) {
    return PhotoState(
      photos: photos ?? this.photos,
      selectedPhoto: selectedPhoto != null ? selectedPhoto() : this.selectedPhoto,
      isLoading: isLoading ?? this.isLoading,
      errorMessage: errorMessage != null ? errorMessage() : this.errorMessage,
      isUploading: isUploading ?? this.isUploading,
      uploadProgress: uploadProgress ?? this.uploadProgress,
      isProcessing: isProcessing ?? this.isProcessing,
    );
  }

  /// Initial state with no photos
  static PhotoState get initial => const PhotoState();
}