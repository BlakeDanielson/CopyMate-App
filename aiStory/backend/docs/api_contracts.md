# API Contract Definitions

This document defines the exact request and response structures for the AI Story Creator backend API (v1).

## Standard Error Response

All API errors will return a JSON object with the following structure:

```json
{
  "detail": "A human-readable description of the error.",
  "code": "A unique error code string."
}
```

**Common Error Codes:**

*   `UNAUTHENTICATED`: Missing or invalid authentication token.
*   `PERMISSION_DENIED`: Authenticated user lacks permission for the action.
*   `NOT_FOUND`: The requested resource does not exist.
*   `VALIDATION_ERROR`: Input data failed validation checks (often includes more specific details).
*   `INVALID_CREDENTIALS`: Incorrect username or password during login.
*   `USER_ALREADY_EXISTS`: Attempt to sign up with an existing email.
*   `UPLOAD_FAILED`: Photo upload process failed.
*   `STORY_GENERATION_FAILED`: AI story creation process failed.
*   `PAYMENT_FAILED`: Payment processing failed.
*   `WEBHOOK_ERROR`: Error processing an incoming webhook.
*   `INTERNAL_SERVER_ERROR`: An unexpected server-side error occurred.

---

## 1. Authentication

### `POST /v1/auth/register`

Registers a new user account.

**Request Body:**

```json
{
  "email": "newuser@example.com",
  "password": "newsecurepassword456"
}
```

**Success Response (201 Created):**

```json
{
  "id": "a1b2c3d4-e5f6-7890-1234-567890abcdef", // UUID of the newly created user
  "email": "newuser@example.com",
  "created_at": "2025-04-22T17:30:00Z"
}
```

**Error Responses:**

*   `400 Bad Request` (`VALIDATION_ERROR`) - e.g., invalid email format, weak password.
*   `409 Conflict` (`USER_ALREADY_EXISTS`)

### `POST /v1/auth/token`

Exchanges user credentials (email/password) for access and refresh tokens.

**Request Body:**

```json
{
  "username": "user@example.com", // Using email as username
  "password": "securepassword123"
}
```

**Success Response (200 OK):**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...", // Short-lived JWT (15 minutes)
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...", // Longer-lived JWT (7 days)
  "token_type": "bearer",
  "expires_in": 900 // Seconds until access token expires (15 minutes)
}
```

**Error Responses:**

*   `401 Unauthorized` (`INVALID_CREDENTIALS`)

### `POST /v1/auth/refresh`

Uses a refresh token to get a new access token.

**Request Body:**

```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Success Response (200 OK):**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...", // New short-lived JWT
  "token_type": "bearer",
  "expires_in": 900 // Seconds until new access token expires (15 minutes)
}
```

**Error Responses:**

*   `401 Unauthorized` (`UNAUTHENTICATED`) - Invalid, expired, or revoked refresh token

### Token Format and Requirements

The API uses JWT (JSON Web Tokens) for authentication.

*   **Access Token:** A short-lived token used to authenticate API requests.
*   **Refresh Token:** A longer-lived token used to obtain new access tokens.

Tokens are included in the `Authorization` header as a Bearer token:

```
Authorization: Bearer <access_token>
```

---

## 2. User Management

### `POST /v1/users`

Registers a new user account.

**Request Body:**

```json
{
  "email": "newuser@example.com",
  "password": "newsecurepassword456",
  "full_name": "New User Name"
}
```

**Success Response (201 Created):**

```json
{
  "id": "a1b2c3d4-e5f6-7890-1234-567890abcdef", // UUID of the newly created user
  "email": "newuser@example.com",
  "full_name": "New User Name",
  "created_at": "2025-04-22T17:30:00Z",
  "updated_at": "2025-04-22T17:30:00Z"
}
```

**Error Responses:**

*   `400 Bad Request` (`VALIDATION_ERROR`) - e.g., invalid email format, weak password.
*   `409 Conflict` (`USER_ALREADY_EXISTS`)

### `GET /v1/users/me`

Retrieves the authenticated user's profile.

**Request Body:**
None (requires bearer token authentication)

**Success Response (200 OK):**

```json
{
  "id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
  "email": "user@example.com",
  "full_name": "User Name",
  "created_at": "2025-04-20T10:30:00Z",
  "updated_at": "2025-04-21T15:45:00Z"
}
```

**Error Responses:**

*   `401 Unauthorized` (`UNAUTHENTICATED`)

---

## 3. Photo Management

### `POST /v1/photos/upload-url`

Requests a pre-signed URL to allow direct upload of a photo to cloud storage (e.g., S3, GCS).

**Request Body:**

```json
{
  "filename": "profile_pic.jpg",
  "content_type": "image/jpeg" // e.g., image/png, image/jpeg
}
```

**Success Response (200 OK):**

```json
{
  "upload_url": "https://storage.provider.com/bucket-name/unique-object-key?signature=...", // The pre-signed URL for PUT request
  "photo_id": "p1o2t3o4-i5d6-7890-1234-abcdef123456", // UUID assigned to this photo record (initially marked as pending upload)
  "object_key": "unique-object-key", // The key/path within the storage bucket
  "fields": { // Optional: Any additional fields needed for the upload (e.g., for S3 POST policy)
    "Content-Type": "image/jpeg",
    "x-amz-meta-user-id": "a1b2c3d4-e5f6-7890-1234-567890abcdef"
  }
}
```

**Notes:**

*   The client uses the `upload_url` to perform a `PUT` request directly to the storage provider with the image data and the correct `Content-Type` header.
*   After successful upload, the client should call the `/v1/photos/{photo_id}/confirm` endpoint to confirm the upload.

**Error Responses:**

*   `400 Bad Request` (`VALIDATION_ERROR`) - Invalid filename or content type.
*   `401 Unauthorized` (`UNAUTHENTICATED`)
*   `500 Internal Server Error` (`UPLOAD_FAILED`) - If URL generation fails.

### `POST /v1/photos/{photo_id}/confirm`

Confirms that a photo has been uploaded to cloud storage.

**Path Parameters:**

*   `photo_id` (UUID): The ID of the photo to confirm.

**Request Body:**
None

**Success Response (200 OK):**

```json
{
  "id": "p1o2t3o4-i5d6-7890-1234-abcdef123456",
  "user_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
  "object_key": "unique-object-key",
  "status": "uploaded",
  "created_at": "2025-04-22T17:45:00Z",
  "updated_at": "2025-04-22T17:46:00Z"
}
```

**Error Responses:**

*   `401 Unauthorized` (`UNAUTHENTICATED`)
*   `403 Forbidden` (`PERMISSION_DENIED`) - If the photo belongs to another user.
*   `404 Not Found` (`NOT_FOUND`) - If the photo_id doesn't exist.
*   `409 Conflict` - If the photo was not successfully uploaded to storage.

---

## 4. Story Management

### `POST /v1/stories`

Initiates the creation of a new AI-generated story based on user inputs. This is an asynchronous operation.

**Request Body:**

```json
{
  "child_name": "Alex",
  "child_age": 5,
  "story_theme": "space_adventure", // Predefined theme identifier
  "protagonist_photo_id": "p1o2t3o4-i5d6-7890-1234-abcdef123456" // UUID of the uploaded photo to use for personalization
}
```

**Success Response (202 Accepted):**

Indicates the story generation process has started.

```json
{
  "id": "s1t2o3r4-y5i6-7890-1234-abcdef654321", // UUID of the new story record
  "user_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
  "child_name": "Alex",
  "child_age": 5,
  "story_theme": "space_adventure",
  "protagonist_photo_id": "p1o2t3o4-i5d6-7890-1234-abcdef123456",
  "status": "pending", // Initial status
  "created_at": "2025-04-22T18:00:00Z",
  "updated_at": "2025-04-22T18:00:00Z",
  "message": "Story generation initiated. Check status using GET /v1/stories/{id}"
}
```

**Error Responses:**

*   `400 Bad Request` (`VALIDATION_ERROR`) - Invalid inputs (e.g., age out of range, unknown theme, invalid photo_id).
*   `401 Unauthorized` (`UNAUTHENTICATED`)
*   `404 Not Found` (`NOT_FOUND`) - If the provided `protagonist_photo_id` doesn't exist or belong to the user.
*   `500 Internal Server Error` (`STORY_GENERATION_FAILED`) - If the initial request fails unexpectedly.

### `GET /v1/stories/{story_id}`

Retrieves the details and content of a specific story.

**Path Parameters:**

*   `story_id` (UUID): The unique identifier of the story.

**Success Response (200 OK):**

```json
{
  "id": "s1t2o3r4-y5i6-7890-1234-abcdef654321",
  "user_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
  "child_name": "Alex",
  "child_age": 5,
  "story_theme": "space_adventure",
  "protagonist_photo_id": "p1o2t3o4-i5d6-7890-1234-abcdef123456",
  "status": "completed", // e.g., pending, processing, completed, failed
  "error_message": null, // Populated if status is 'failed'
  "created_at": "2025-04-22T18:00:00Z",
  "updated_at": "2025-04-22T18:05:00Z",
  "pages": [
    {
      "page_number": 1,
      "text": "Once upon a time, in a galaxy far, far away, lived a brave explorer named Alex...",
      "base_image_key": "story/s1t2o3r4.../page1_base.jpg", // Key in cloud storage
      "personalized_image_key": "story/s1t2o3r4.../page1_personalized.jpg", // Key in cloud storage (null if personalization failed)
      "personalization_status": "completed" // e.g., pending, processing, completed, failed
    },
    {
      "page_number": 2,
      "text": "Alex zoomed past sparkling nebulae in their trusty spaceship.",
      "base_image_key": "story/s1t2o3r4.../page2_base.jpg",
      "personalized_image_key": "story/s1t2o3r4.../page2_personalized.jpg",
      "personalization_status": "completed"
    }
    // ... more pages
  ]
}
```

**Error Responses:**

*   `401 Unauthorized` (`UNAUTHENTICATED`)
*   `403 Forbidden` (`PERMISSION_DENIED`) - If the story belongs to another user.
*   `404 Not Found` (`NOT_FOUND`) - If the `story_id` does not exist.

### `GET /v1/stories`

Retrieves a list of all stories created by the authenticated user.

**Query Parameters:**

*   `limit` (integer, optional): Maximum number of stories to return, default 20.
*   `offset` (integer, optional): Number of stories to skip, default 0.
*   `status` (string, optional): Filter by story status (e.g., "pending", "completed", "failed").

**Success Response (200 OK):**

```json
{
  "items": [
    {
      "id": "s1t2o3r4-y5i6-7890-1234-abcdef654321",
      "child_name": "Alex",
      "story_theme": "space_adventure",
      "status": "completed",
      "created_at": "2025-04-22T18:00:00Z",
      "updated_at": "2025-04-22T18:05:00Z"
    },
    {
      "id": "a9b8c7d6-e5f4-3210-9876-fedcba654321",
      "child_name": "Taylor",
      "story_theme": "underwater_adventure",
      "status": "pending",
      "created_at": "2025-04-22T19:00:00Z",
      "updated_at": "2025-04-22T19:00:00Z"
    }
    // ... more stories
  ],
  "total": 10, // Total number of stories (for pagination)
  "limit": 20,
  "offset": 0
}
```

**Error Response:**

*   `401 Unauthorized` (`UNAUTHENTICATED`)

---

## 5. Orders

### `POST /v1/orders`

Creates a payment intent (e.g., via Stripe) for purchasing a physical copy of a generated story.

**Request Body:**

```json
{
  "story_id": "s1t2o3r4-y5i6-7890-1234-abcdef654321", // UUID of the story to order
  "product_type": "hardcover_book", // Identifier for the product being ordered (e.g., 'hardcover_book', 'softcover_book')
  "shipping_address": {
    "recipient_name": "Alex Smith",
    "street_address": "123 Main St",
    "city": "Anytown",
    "state": "CA",
    "postal_code": "12345",
    "country": "US"
  }
}
```

**Success Response (201 Created):**

Returns details needed by the client to complete the payment, such as a Stripe Payment Intent client secret.

```json
{
  "id": "o1r2d3e4-r5i6-7890-1234-fedcba987654", // UUID of the newly created order record
  "user_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
  "story_id": "s1t2o3r4-y5i6-7890-1234-abcdef654321",
  "product_type": "hardcover_book",
  "status": "pending_payment", // Initial status
  "amount": 2999, // Amount in cents (e.g., $29.99)
  "currency": "usd",
  "shipping_address": {
    "recipient_name": "Alex Smith",
    "street_address": "123 Main St",
    "city": "Anytown",
    "state": "CA",
    "postal_code": "12345",
    "country": "US"
  },
  "payment_provider": "stripe",
  "payment_intent_id": "pi_3...", // ID from Stripe
  "client_secret": "pi_3..._secret_...", // Stripe client secret for frontend confirmation
  "created_at": "2025-04-22T19:30:00Z",
  "updated_at": "2025-04-22T19:30:00Z"
}
```

**Error Responses:**

*   `400 Bad Request` (`VALIDATION_ERROR`) - Invalid `story_id` or `product_type`.
*   `401 Unauthorized` (`UNAUTHENTICATED`)
*   `403 Forbidden` (`PERMISSION_DENIED`) - If the story belongs to another user.
*   `404 Not Found` (`NOT_FOUND`) - If the `story_id` does not exist or is not 'completed'.
*   `500 Internal Server Error` (`PAYMENT_FAILED`) - If creating the payment intent fails.

### `GET /v1/orders`

Retrieves a list of all orders placed by the authenticated user.

**Query Parameters:**

*   `limit` (integer, optional): Maximum number of orders to return, default 20.
*   `offset` (integer, optional): Number of orders to skip, default 0.
*   `status` (string, optional): Filter by order status (e.g., "pending_payment", "paid", "fulfilled", "shipped").

**Success Response (200 OK):**

```json
{
  "items": [
    {
      "id": "o1r2d3e4-r5i6-7890-1234-fedcba987654",
      "story_id": "s1t2o3r4-y5i6-7890-1234-abcdef654321",
      "product_type": "hardcover_book",
      "status": "paid",
      "amount": 2999,
      "currency": "usd",
      "created_at": "2025-04-22T19:30:00Z",
      "updated_at": "2025-04-22T19:35:00Z"
    },
    {
      "id": "a9b8c7d6-e5f4-3210-9876-fedcba123456",
      "story_id": "a9b8c7d6-e5f4-3210-9876-fedcba654321",
      "product_type": "softcover_book",
      "status": "pending_payment",
      "amount": 1999,
      "currency": "usd",
      "created_at": "2025-04-22T20:00:00Z",
      "updated_at": "2025-04-22T20:00:00Z"
    }
    // ... more orders
  ],
  "total": 5, // Total number of orders (for pagination)
  "limit": 20,
  "offset": 0
}
```

**Error Response:**

*   `401 Unauthorized` (`UNAUTHENTICATED`)

### `GET /v1/orders/{order_id}`

Retrieves the details of a specific order.

**Path Parameters:**

*   `order_id` (UUID): The unique identifier of the order.

**Success Response (200 OK):**

```json
{
  "id": "o1r2d3e4-r5i6-7890-1234-fedcba987654",
  "user_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
  "story_id": "s1t2o3r4-y5i6-7890-1234-abcdef654321",
  "product_type": "hardcover_book",
  "status": "paid", // e.g., pending_payment, paid, processing, fulfilled, shipped
  "amount": 2999,
  "currency": "usd",
  "shipping_address": {
    "recipient_name": "Alex Smith",
    "street_address": "123 Main St",
    "city": "Anytown",
    "state": "CA",
    "postal_code": "12345",
    "country": "US"
  },
  "tracking_number": null, // Populated when shipping is initiated
  "payment_provider": "stripe",
  "payment_intent_id": "pi_3...",
  "paid_at": "2025-04-22T19:35:00Z", // When payment was confirmed
  "fulfilled_at": null, // When production was completed
  "shipped_at": null, // When order was shipped
  "created_at": "2025-04-22T19:30:00Z",
  "updated_at": "2025-04-22T19:35:00Z"
}
```

**Error Responses:**

*   `401 Unauthorized` (`UNAUTHENTICATED`)
*   `403 Forbidden` (`PERMISSION_DENIED`) - If the order belongs to another user.
*   `404 Not Found` (`NOT_FOUND`) - If the `order_id` does not exist.

---

## 6. Webhooks

### `POST /v1/webhooks/stripe`

Endpoint to receive webhook events from Stripe, specifically for payment confirmation. Requires signature verification.

**Headers:**

```
Stripe-Signature: t=1678886400,v1=abcdef123456...,v0=fedcba654321...
```

**Expected Request Body (Example for `payment_intent.succeeded`):**

```json
{
  "id": "evt_1...",
  "object": "event",
  "api_version": "2022-11-15", // Example API version
  "created": 1678886400,
  "data": {
    "object": {
      "id": "pi_3...", // The PaymentIntent ID
      "object": "payment_intent",
      "amount": 2999,
      "amount_received": 2999,
      "currency": "usd",
      "status": "succeeded",
      "metadata": { // Includes order_id set during creation
        "order_id": "o1r2d3e4-r5i6-7890-1234-fedcba987654"
      }
      // ... other payment intent fields
    }
  },
  "livemode": false,
  "pending_webhooks": 0,
  "request": {
    "id": "req_...",
    "idempotency_key": null
  },
  "type": "payment_intent.succeeded"
}
```

**Success Response (200 OK):**

An empty body or a simple confirmation.

```json
{
  "status": "received"
}
```

**Error Responses:**

*   `400 Bad Request` (`WEBHOOK_ERROR`) - Invalid payload, missing signature, or signature verification failed.
*   `404 Not Found` (`NOT_FOUND`) - If the `order_id` from metadata doesn't match an existing order.
*   `500 Internal Server Error` (`WEBHOOK_ERROR`) - If processing the event fails internally.

### `POST /v1/webhooks/pod-provider`

Endpoint to receive webhook events from the Print-on-Demand provider about order status updates.

**Headers:**

```
X-Pod-Signature: abcdef123456... // Provider-specific signature for verification
```

**Expected Request Body (Example):**

```json
{
  "event_type": "order_shipped",
  "order_reference": "o1r2d3e4-r5i6-7890-1234-fedcba987654", // Our order ID stored as reference
  "provider_order_id": "POD12345", // Provider's internal order ID
  "timestamp": "2025-04-25T14:30:00Z",
  "data": {
    "tracking_number": "USPS1234567890",
    "carrier": "USPS",
    "estimated_delivery": "2025-04-30T00:00:00Z"
  }
}
```

**Success Response (200 OK):**

```json
{
  "status": "received"
}
```

**Error Responses:**

*   `400 Bad Request` (`WEBHOOK_ERROR`) - Invalid payload, missing signature, or signature verification failed.
*   `404 Not Found` (`NOT_FOUND`) - If the `order_reference` doesn't match an existing order.
*   `500 Internal Server Error` (`WEBHOOK_ERROR`) - If processing the event fails internally.