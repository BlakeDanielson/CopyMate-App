# API Documentation

## Photo Upload Endpoints

### `POST /photos`

Uploads a new photo.

*   **Request Body:** `multipart/form-data` with the photo file.
*   **Responses:**
    *   `201 Created`: Photo uploaded successfully. Returns the photo ID.
        ```json
        {
            "photo_id": "123"
        }
        ```
    *   `400 Bad Request`: Invalid file format or size.
        ```json
        {
            "error": "Invalid file format or size"
        }
        ```
    *   `500 Internal Server Error`: Server error.
        ```json
        {
            "error": "Internal server error"
        }
        ```

## AI Processing Endpoints

### `GET /photos/{photo_id}/results`

Retrieves the AI processing results for a specific photo.

*   **Responses:**
    *   `200 OK`: Returns the AI processing results.
        ```json
        {
            "results": {
                "label": "cat",
                "confidence": 0.95
            }
        }
        ```
    *   `404 Not Found`: Photo not found.
        ```json
        {
            "error": "Photo not found"
        }
        ```
    *   `500 Internal Server Error`: Server error.
        ```json
        {
            "error": "Internal server error"
        }
        ```

## Response Formats and Status Codes

The API uses JSON for all responses. Standard HTTP status codes are used to indicate the success or failure of a request.