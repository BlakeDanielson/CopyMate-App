import 'package:json_annotation/json_annotation.dart';

import 'photo_status.dart';

part 'photo.g.dart';

/// Photo model for storing user-uploaded images
@JsonSerializable()
class Photo {
  /// Database ID
  final String id;
  
  /// User ID that owns this photo
  @JsonKey(name: 'user_id')
  final int userId;
  
  /// Cloud storage provider (e.g., aws_s3, google_cloud)
  @JsonKey(name: 'storage_provider')
  final String storageProvider;
  
  /// Storage bucket name
  @JsonKey(name: 'bucket_name')
  final String bucketName;
  
  /// Storage key (path within bucket)
  @JsonKey(name: 'storage_key')
  final String storageKey;
  
  /// Original filename from user's device
  @JsonKey(name: 'original_filename')
  final String originalFilename;
  
  /// MIME type of the photo
  @JsonKey(name: 'content_type')
  final String contentType;
  
  /// Current status of the photo
  final PhotoStatus status;
  
  /// When the photo was created
  @JsonKey(name: 'created_at')
  final DateTime createdAt;
  
  /// When the photo was last updated
  @JsonKey(name: 'updated_at')
  final DateTime updatedAt;
  
  /// URL to access the photo (may be temporary)
  final String? url;
  
  /// List of thumbnail URLs if available
  final List<String>? thumbnails;
  
  /// Optional additional metadata
  final Map<String, dynamic>? metadata;

  /// Creates a new Photo instance
  const Photo({
    required this.id,
    required this.userId,
    required this.storageProvider,
    required this.bucketName,
    required this.storageKey,
    required this.originalFilename,
    required this.contentType,
    required this.status,
    required this.createdAt,
    required this.updatedAt,
    this.url,
    this.thumbnails,
    this.metadata,
  });

  /// Creates a Photo from JSON
  factory Photo.fromJson(Map<String, dynamic> json) => _$PhotoFromJson(json);

  /// Converts this Photo to JSON
  Map<String, dynamic> toJson() => _$PhotoToJson(this);
}