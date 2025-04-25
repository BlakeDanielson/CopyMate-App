import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';

import 'package:ai_story/features/photos/data/datasources/photo_api_client.dart';
import 'package:ai_story/features/photos/data/dtos/photo_processing_result.dart';
import 'package:ai_story/features/photos/data/dtos/photo_upload_response.dart';
import 'package:ai_story/features/photos/data/repositories/photo_repository_impl.dart';
import 'package:ai_story/features/photos/domain/models/photo.dart';
import 'package:ai_story/features/photos/domain/models/photo_status.dart';

class MockPhotoApiClient extends Mock implements PhotoApiClient {}
class MockFile extends Mock implements File {}

void main() {
  late PhotoRepositoryImpl repository;
  late MockPhotoApiClient mockApiClient;
  late MockFile mockFile;

  final testPhoto = Photo(
    id: 'test-123',
    userId: 1,
    storageProvider: 'aws_s3',
    bucketName: 'test-bucket',
    storageKey: 'users/1/photos/test.jpg',
    originalFilename: 'test.jpg',
    contentType: 'image/jpeg',
    status: PhotoStatus.uploaded,
    createdAt: DateTime(2025, 4, 22),
    updatedAt: DateTime(2025, 4, 22),
  );

  final testPhotoUploadResponse = PhotoUploadResponse(
    photoId: 'test-123',
    status: PhotoStatus.pending,
    message: 'Photo uploaded successfully',
  );

  final testPhotoProcessingResult = PhotoProcessingResult(
    photoId: 'test-123',
    status: PhotoStatus.completed,
    processedUrl: 'https://test-bucket.s3.amazonaws.com/users/1/photos/test.jpg',
  );

  setUp(() {
    mockApiClient = MockPhotoApiClient();
    repository = PhotoRepositoryImpl(mockApiClient);
    mockFile = MockFile();
  });

  group('PhotoRepository', () {
    test('uploadPhoto should return photo ID from API response', () async {
      // Arrange
      when(() => mockApiClient.uploadPhoto(
        photoFile: mockFile,
        description: any(named: 'description'),
        tags: any(named: 'tags'),
      )).thenAnswer((_) async => testPhotoUploadResponse);

      // Act
      final result = await repository.uploadPhoto(
        photoFile: mockFile,
        description: 'Test description',
        tags: ['test', 'photo'],
      );

      // Assert
      expect(result, 'test-123');
      verify(() => mockApiClient.uploadPhoto(
        photoFile: mockFile,
        description: 'Test description',
        tags: ['test', 'photo'],
      )).called(1);
    });

    test('getPhoto should return photo from API', () async {
      // Arrange
      when(() => mockApiClient.getPhoto('test-123'))
          .thenAnswer((_) async => testPhoto);

      // Act
      final result = await repository.getPhoto('test-123');

      // Assert
      expect(result, testPhoto);
      verify(() => mockApiClient.getPhoto('test-123')).called(1);
    });

    test('getPhotos should return photos from API', () async {
      // Arrange
      when(() => mockApiClient.getPhotos(
        status: any(named: 'status'),
        fromDate: any(named: 'fromDate'),
        toDate: any(named: 'toDate'),
        tags: any(named: 'tags'),
        page: any(named: 'page'),
        pageSize: any(named: 'pageSize'),
      )).thenAnswer((_) async => [testPhoto]);

      // Act
      final result = await repository.getPhotos(
        status: PhotoStatus.uploaded,
        page: 1,
        pageSize: 10,
      );

      // Assert
      expect(result, [testPhoto]);
      verify(() => mockApiClient.getPhotos(
        status: PhotoStatus.uploaded,
        page: 1,
        pageSize: 10,
      )).called(1);
    });

    test('deletePhoto should delegate to API client', () async {
      // Arrange
      when(() => mockApiClient.deletePhoto('test-123'))
          .thenAnswer((_) async => {});

      // Act
      await repository.deletePhoto('test-123');

      // Assert
      verify(() => mockApiClient.deletePhoto('test-123')).called(1);
    });

    test('processPhoto should return updated photo after processing', () async {
      // Arrange
      when(() => mockApiClient.processPhoto('test-123'))
          .thenAnswer((_) async => testPhotoProcessingResult);
      when(() => mockApiClient.getPhoto('test-123'))
          .thenAnswer((_) async => testPhoto);

      // Act
      final result = await repository.processPhoto('test-123');

      // Assert
      expect(result, testPhoto);
      verify(() => mockApiClient.processPhoto('test-123')).called(1);
      verify(() => mockApiClient.getPhoto('test-123')).called(1);
    });

    test('getPhotoUrl should return URL from API', () async {
      // Arrange
      const testUrl = 'https://test-bucket.s3.amazonaws.com/users/1/photos/test.jpg';
      when(() => mockApiClient.getPhotoUrl('test-123', expiresIn: any(named: 'expiresIn')))
          .thenAnswer((_) async => testUrl);

      // Act
      final result = await repository.getPhotoUrl('test-123', expiresIn: 3600);

      // Assert
      expect(result, testUrl);
      verify(() => mockApiClient.getPhotoUrl('test-123', expiresIn: 3600)).called(1);
    });
  });
}