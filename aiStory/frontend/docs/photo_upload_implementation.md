# Photo Upload Implementation

This document outlines the implementation of the photo upload feature in the AI Story Creator app.

## Architecture

The implementation follows clean architecture principles:

- **Domain Layer**: Contains business logic and entities
- **Data Layer**: Handles data fetching and storage
- **Presentation Layer**: Handles UI components and user interaction

## Components

### Models

- `PhotoStatus`: Enum representing the status of a photo (pending, uploaded, processing, completed, failed)
- `Photo`: Model class representing a photo with all properties matching the backend schema
- `PhotoState`: State model for managing photo data in the application

### Data Sources

- `PhotoApiClient`: API client for communicating with the backend with methods for all photo operations:
  - `uploadPhoto`: Upload a new photo
  - `getPhoto`: Get a specific photo by ID
  - `getPhotos`: Get a list of photos with optional filtering
  - `deletePhoto`: Delete a photo
  - `processPhoto`: Process a photo (generate thumbnails, etc.)
  - `getPhotoUrl`: Get a URL for accessing a photo

### Repositories

- `PhotoRepository`: Interface defining photo operations
- `PhotoRepositoryImpl`: Implementation of the repository using the API client

### State Management

- `PhotoNotifier`: Riverpod notifier for managing photo state and operations
- `photoRepositoryProvider`: Provider for the photo repository
- `photoNotifierProvider`: Provider for the photo notifier

### UI Components

- **Screens**:
  - `PhotoUploadScreen`: Screen for uploading photos with form fields
  - `PhotoGalleryScreen`: Grid view of all photos with pagination
  - `PhotoDetailScreen`: Detailed view of a single photo

- **Widgets**:
  - `PhotoGridItem`: Card widget for displaying a photo in the gallery
  - `PhotoUploadForm`: Form for entering photo metadata

## Features

- Photo upload with progress indication
- Gallery view with pagination
- Photo detail view with metadata
- Photo processing
- Photo deletion with confirmation
- Error handling and user feedback
- Responsive design

## Architecture Diagram

[Diagram showing the data flow from the frontend, through the backend services (API, processing queue, storage), to the database and back. Include the main components and their interactions.]

The architecture diagram illustrates the flow of data during the photo upload process. It includes the frontend, backend API, processing queue, storage service (e.g., S3), and the database. The diagram should clearly show how the components interact with each other.


## Data Flow

1. User selects a photo to upload on the PhotoUploadScreen
2. PhotoNotifier calls the repository's uploadPhoto method
3. Repository delegates to the API client
4. API client sends the request to the backend
5. Response is parsed into PhotoUploadResponse
6. PhotoNotifier updates state with the new photo
7. UI reflects the changes

## Error Handling

- API errors are wrapped in ApiException
- Repository translates API exceptions to domain-specific exceptions
- UI displays appropriate error messages to users
- Loading indicators during operations

## Testing

- Unit tests for the Photo model
- Unit tests for the PhotoRepository implementation
- Widget tests for UI components
- Integration tests for the complete flow

## Future Improvements

- Add offline support with local caching
- Implement batch upload functionality
- Add search capabilities to the gallery view
- Support custom filtering options
## API Endpoints

### Upload Photo

- **Endpoint:** `/photos`
- **Method:** `POST`
- **Request Body:**

```json
{
  "file": "<binary data>",
  "metadata": {
    "title": "My Photo",
    "description": "A beautiful photo"
  }
}
```

- **Response Body (Success):**

```json
{
  "id": "123",
  "url": "https://example.com/photos/123.jpg",
  "status": "pending",
  "metadata": {
    "title": "My Photo",
    "description": "A beautiful photo"
  }
}
```

- **Response Body (Error):**

```json
{
  "error": "Upload failed",
  "message": "File too large"
}
```

### Get Photo

- **Endpoint:** `/photos/{id}`
- **Method:** `GET`
- **Response Body (Success):**

```json
{
  "id": "123",
  "url": "https://example.com/photos/123.jpg",
  "status": "completed",
  "metadata": {
    "title": "My Photo",
    "description": "A beautiful photo"
  }
}
```

- **Response Body (Error):**

```json
{
  "error": "Photo not found",
  "message": "Photo with id 123 not found"
}
```

### Get Photos

- **Endpoint:** `/photos`
## Configuration Requirements

The following environment variables need to be configured for the photo upload feature to work:

- `STORAGE_TYPE`: Specifies the storage type (e.g., `local`, `s3`).
- `S3_BUCKET_NAME`: The name of the S3 bucket to store photos (required if `STORAGE_TYPE` is `s3`).
- `S3_REGION`: The AWS region of the S3 bucket (required if `STORAGE_TYPE` is `s3`).
- `S3_ACCESS_KEY_ID`: The AWS access key ID (required if `STORAGE_TYPE` is `s3`).
- `S3_SECRET_ACCESS_KEY`: The AWS secret access key (required if `STORAGE_TYPE` is `s3`).
- `PHOTO_PROCESSING_QUEUE_URL`: The URL of the photo processing queue.

The following permissions are required:

- Backend:
  - Read/Write access to the storage bucket.
  - Read/Write access to the photo processing queue.
  - Database access to the `photos` table.
- Frontend:
  - Network access to the backend API.

## Frontend Usage Examples

### Photo Upload Screen

[Screenshot of the Photo Upload Screen]

```dart
// Example code for uploading a photo
final pickedFile = await ImagePicker().pickImage(source: ImageSource.gallery);
if (pickedFile != null) {
  final bytes = await pickedFile.readAsBytes();
  final photoNotifier = ref.read(photoNotifierProvider.notifier);
  await photoNotifier.uploadPhoto(bytes, {
    'title': 'My Photo',
    'description': 'A beautiful photo'
  });
}
```

### Photo Gallery Screen

[Screenshot of the Photo Gallery Screen]

```dart
// Example code for displaying photos
final photos = ref.watch(photoNotifierProvider);
return GridView.builder(
  itemCount: photos.length,
  gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
## Common Troubleshooting Scenarios

### Upload fails with "File too large" error

- **Possible Cause:** The file size exceeds the maximum allowed limit.
- **Solution:** Check the backend configuration for the maximum allowed file size. Reduce the file size by compressing the image or selecting a smaller image.

### Photo is stuck in "pending" status

- **Possible Cause:** The photo processing queue is not working or the backend service is not processing the photo.
- **Solution:** Check the photo processing queue for errors. Check the backend service logs for any issues. Ensure that the backend service has the necessary permissions to access the storage bucket.

### Photo is not displayed in the gallery

- **Possible Cause:** The photo has not been processed yet or there is an error retrieving the photo from the backend.
- **Solution:** Check the photo status in the database. Check the backend service logs for any errors. Ensure that the frontend is correctly configured to retrieve photos from the backend.

### Image Picker not working on iOS

- **Possible Cause:** Missing permissions in `Info.plist`.
- **Solution:** Add the `NSPhotoLibraryUsageDescription` and `NSCameraUsageDescription` keys to the `ios/Runner/Info.plist` file.

    crossAxisCount: 3,
  ),
  itemBuilder: (context, index) {
    final photo = photos[index];
    return PhotoGridItem(photo: photo);
  },
);
```

- **Method:** `GET`
- **Query Parameters:**
  - `status`: Filter by photo status (optional)
  - `limit`: Limit the number of results (optional)
  - `offset`: Offset for pagination (optional)
- **Response Body (Success):**

```json
[
  {
    "id": "123",
    "url": "https://example.com/photos/123.jpg",
    "status": "completed",
    "metadata": {
      "title": "My Photo",
      "description": "A beautiful photo"
    }
  },
  {
    "id": "456",
    "url": "https://example.com/photos/456.jpg",
    "status": "completed",
    "metadata": {
      "title": "Another Photo",
      "description": "Another beautiful photo"
    }
  }
]
```

- **Response Body (Error):**

```json
{
  "error": "Failed to retrieve photos",
  "message": "Database error"
}
```

- Add photo editing capabilities