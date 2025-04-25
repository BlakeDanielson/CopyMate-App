import 'package:json_annotation/json_annotation.dart';

import '../../domain/models/photo_status.dart';

part 'photo_processing_result.g.dart';

/// Result from processing a photo
@JsonSerializable()
class PhotoProcessingResult {
  /// ID of the processed photo
  @JsonKey(name: 'photo_id')
  final String photoId;
  
  /// Current status of the photo
  final PhotoStatus status;
  
  /// URL to access the processed photo
  @JsonKey(name: 'processed_url')
  final String? processedUrl;
  
  /// List of thumbnail URLs if available
  final List<String>? thumbnails;
  
  /// Additional metadata from processing
  final Map<String, dynamic>? metadata;
  
  /// Error message if processing failed
  @JsonKey(name: 'error_message')
  final String? errorMessage;

  /// Creates a new PhotoProcessingResult
  const PhotoProcessingResult({
    required this.photoId,
    required this.status,
    this.processedUrl,
    this.thumbnails,
    this.metadata,
    this.errorMessage,
  });

  /// Creates a PhotoProcessingResult from JSON
  factory PhotoProcessingResult.fromJson(Map<String, dynamic> json) => 
      _$PhotoProcessingResultFromJson(json);

  /// Converts this PhotoProcessingResult to JSON
  Map<String, dynamic> toJson() => _$PhotoProcessingResultToJson(this);
}