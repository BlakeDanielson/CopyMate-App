import 'package:json_annotation/json_annotation.dart';

import '../../domain/models/photo_status.dart';

part 'photo_upload_response.g.dart';

/// Response from the API when uploading a photo
@JsonSerializable()
class PhotoUploadResponse {
  /// ID of the uploaded photo
  @JsonKey(name: 'photo_id')
  final String photoId;
  
  /// Status of the uploaded photo
  final PhotoStatus status;
  
  /// Message from the server
  final String message;

  /// Creates a new PhotoUploadResponse
  const PhotoUploadResponse({
    required this.photoId,
    required this.status,
    required this.message,
  });

  /// Creates a PhotoUploadResponse from JSON
  factory PhotoUploadResponse.fromJson(Map<String, dynamic> json) => 
      _$PhotoUploadResponseFromJson(json);

  /// Converts this PhotoUploadResponse to JSON
  Map<String, dynamic> toJson() => _$PhotoUploadResponseToJson(this);
}