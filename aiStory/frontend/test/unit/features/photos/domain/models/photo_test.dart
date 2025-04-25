import 'package:flutter_test/flutter_test.dart';
import 'package:ai_story/features/photos/domain/models/photo.dart';
import 'package:ai_story/features/photos/domain/models/photo_status.dart';

void main() {
  group('Photo model', () {
    final testDateTime = DateTime(2025, 4, 22, 15, 30);
    
    test('should create a Photo instance with required fields', () {
      // Arrange
      final photo = Photo(
        id: '123e4567-e89b-12d3-a456-426614174000',
        userId: 1,
        storageProvider: 'aws_s3',
        bucketName: 'app-photos',
        storageKey: 'user-1/photo-123.jpg',
        originalFilename: 'beach.jpg',
        contentType: 'image/jpeg',
        status: PhotoStatus.uploaded,
        createdAt: testDateTime,
        updatedAt: testDateTime,
      );
      
      // Assert
      expect(photo.id, '123e4567-e89b-12d3-a456-426614174000');
      expect(photo.userId, 1);
      expect(photo.storageProvider, 'aws_s3');
      expect(photo.bucketName, 'app-photos');
      expect(photo.storageKey, 'user-1/photo-123.jpg');
      expect(photo.originalFilename, 'beach.jpg');
      expect(photo.contentType, 'image/jpeg');
      expect(photo.status, PhotoStatus.uploaded);
      expect(photo.createdAt, testDateTime);
      expect(photo.updatedAt, testDateTime);
      expect(photo.url, null);
      expect(photo.thumbnails, null);
      expect(photo.metadata, null);
    });
    
    test('should create a Photo instance with optional fields', () {
      // Arrange
      final photo = Photo(
        id: '123e4567-e89b-12d3-a456-426614174000',
        userId: 1,
        storageProvider: 'aws_s3',
        bucketName: 'app-photos',
        storageKey: 'user-1/photo-123.jpg',
        originalFilename: 'beach.jpg',
        contentType: 'image/jpeg',
        status: PhotoStatus.completed,
        createdAt: testDateTime,
        updatedAt: testDateTime,
        url: 'https://example.com/photos/123.jpg',
        thumbnails: ['https://example.com/thumbnails/123_sm.jpg'],
        metadata: {'width': 1920, 'height': 1080},
      );
      
      // Assert
      expect(photo.url, 'https://example.com/photos/123.jpg');
      expect(photo.thumbnails, ['https://example.com/thumbnails/123_sm.jpg']);
      expect(photo.metadata, {'width': 1920, 'height': 1080});
    });
    
    test('should serialize to JSON correctly', () {
      // Arrange
      final photo = Photo(
        id: '123e4567-e89b-12d3-a456-426614174000',
        userId: 1,
        storageProvider: 'aws_s3',
        bucketName: 'app-photos',
        storageKey: 'user-1/photo-123.jpg',
        originalFilename: 'beach.jpg',
        contentType: 'image/jpeg',
        status: PhotoStatus.uploaded,
        createdAt: testDateTime,
        updatedAt: testDateTime,
        url: 'https://example.com/photos/123.jpg',
      );
      
      // Act
      final json = photo.toJson();
      
      // Assert
      expect(json['id'], '123e4567-e89b-12d3-a456-426614174000');
      expect(json['user_id'], 1);
      expect(json['storage_provider'], 'aws_s3');
      expect(json['bucket_name'], 'app-photos');
      expect(json['storage_key'], 'user-1/photo-123.jpg');
      expect(json['original_filename'], 'beach.jpg');
      expect(json['content_type'], 'image/jpeg');
      expect(json['status'], 'uploaded');
      expect(json['created_at'], testDateTime.toIso8601String());
      expect(json['updated_at'], testDateTime.toIso8601String());
      expect(json['url'], 'https://example.com/photos/123.jpg');
    });
    
    test('should deserialize from JSON correctly', () {
      // Arrange
      final json = {
        'id': '123e4567-e89b-12d3-a456-426614174000',
        'user_id': 1,
        'storage_provider': 'aws_s3',
        'bucket_name': 'app-photos',
        'storage_key': 'user-1/photo-123.jpg',
        'original_filename': 'beach.jpg',
        'content_type': 'image/jpeg',
        'status': 'completed',
        'created_at': testDateTime.toIso8601String(),
        'updated_at': testDateTime.toIso8601String(),
        'url': 'https://example.com/photos/123.jpg',
        'thumbnails': ['https://example.com/thumbnails/123_sm.jpg'],
        'metadata': {'width': 1920, 'height': 1080},
      };
      
      // Act
      final photo = Photo.fromJson(json);
      
      // Assert
      expect(photo.id, '123e4567-e89b-12d3-a456-426614174000');
      expect(photo.userId, 1);
      expect(photo.storageProvider, 'aws_s3');
      expect(photo.bucketName, 'app-photos');
      expect(photo.storageKey, 'user-1/photo-123.jpg');
      expect(photo.originalFilename, 'beach.jpg');
      expect(photo.contentType, 'image/jpeg');
      expect(photo.status, PhotoStatus.completed);
      expect(photo.createdAt, testDateTime);
      expect(photo.updatedAt, testDateTime);
      expect(photo.url, 'https://example.com/photos/123.jpg');
      expect(photo.thumbnails, ['https://example.com/thumbnails/123_sm.jpg']);
      expect(photo.metadata, {'width': 1920, 'height': 1080});
    });
  });
  
  group('PhotoStatus', () {
    test('should convert from string to enum', () {
      expect(PhotoStatus.fromString('pending'), PhotoStatus.pending);
      expect(PhotoStatus.fromString('uploaded'), PhotoStatus.uploaded);
      expect(PhotoStatus.fromString('processing'), PhotoStatus.processing);
      expect(PhotoStatus.fromString('completed'), PhotoStatus.completed);
      expect(PhotoStatus.fromString('failed'), PhotoStatus.failed);
      
      // Should default to pending for unknown status
      expect(PhotoStatus.fromString('unknown'), PhotoStatus.pending);
    });
    
    test('should convert enum to string', () {
      expect(PhotoStatus.pending.toJson(), 'pending');
      expect(PhotoStatus.uploaded.toJson(), 'uploaded');
      expect(PhotoStatus.processing.toJson(), 'processing');
      expect(PhotoStatus.completed.toJson(), 'completed');
      expect(PhotoStatus.failed.toJson(), 'failed');
    });
  });
}