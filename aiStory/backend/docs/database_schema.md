# Database Schema Definitions

This document outlines the detailed database schemas for the AI Story Creator backend, focusing on tables relevant to Sprint 2 and beyond.

**General Conventions:**

*   **Primary Keys:** All tables use a UUID (`id`) as the primary key unless otherwise noted.
*   **Foreign Keys:** Foreign keys link related tables (e.g., `user_id` links to the `users` table).
*   **Timestamps:** `created_at` and `updated_at` columns use `TIMESTAMP WITH TIME ZONE` and default to `NOW()`. `updated_at` should be automatically updated on row modification (e.g., using a trigger or ORM feature).
*   **Indexes:** Key columns used for filtering or joining (especially foreign keys and status fields) should be indexed for performance.
*   **Nullability:** Columns are `NOT NULL` unless specified as `Nullable`.
*   **Data Types:** PostgreSQL data types are used as a reference.

---

## `photos` Table

Stores information about user-uploaded photos, primarily used as protagonists in stories.

| Column Name              | Type                     | Constraints & Defaults                                  | Description                                                                 | Indexes        |
| :----------------------- | :----------------------- | :------------------------------------------------------ | :-------------------------------------------------------------------------- | :------------- |
| `id`                     | UUID                     | Primary Key, Default: `gen_random_uuid()`               | Unique identifier for the photo record.                                     | PK             |
| `user_id`                | UUID                     | Foreign Key (`users.id`), Not Null                      | The user who uploaded the photo.                                            | FK, Indexed    |
| `storage_provider`       | VARCHAR                  | Not Null                                                | Identifier for the storage service (e.g., 's3', 'gcs', 'local').            |                |
| `bucket`                 | VARCHAR                  | Nullable                                                | The storage bucket name (if applicable).                                    |                |
| `object_key`             | VARCHAR                  | Not Null, Unique                                        | The unique path/key of the photo within the storage provider/bucket.        | Unique Index   |
| `filename`               | VARCHAR                  | Not Null                                                | The original filename provided by the user during upload request.           |                |
| `content_type`           | VARCHAR                  | Not Null                                                | The MIME type of the photo (e.g., 'image/jpeg', 'image/png').               |                |
| `status`                 | VARCHAR                  | Not Null, Default: `'pending_upload'`                   | Tracks the photo's state (e.g., 'pending_upload', 'uploaded', 'failed').    | Indexed        |
| `ai_processing_status`   | VARCHAR                  | Nullable, Default: `'pending'`                          | Tracks the AI analysis state (e.g., 'pending', 'processing', 'completed', 'failed'). | Indexed        |
| `ai_error_message`       | TEXT                     | Nullable                                                | Stores error details if AI processing fails.                                |                |
| `detected_objects`       | JSONB                    | Nullable                                                | Structured data about objects detected in the photo by AI.                  | GIN Index?     |
| `detected_labels`        | JSONB                    | Nullable                                                | Structured data about labels/tags detected in the photo by AI.              | GIN Index?     |
| `face_details`           | JSONB                    | Nullable                                                | Structured data about faces detected (bounding boxes, landmarks, etc.).     | GIN Index?     |
| `created_at`             | TIMESTAMP WITH TIME ZONE | Not Null, Default: `NOW()`                              | Timestamp when the photo record was created.                                |                |
| `updated_at`             | TIMESTAMP WITH TIME ZONE | Not Null, Default: `NOW()`                              | Timestamp when the photo record was last updated.                           |                |

---

## `stories` Table

Stores information about each AI-generated story created by a user.

| Column Name             | Type                     | Constraints & Defaults                               | Description                                                                    | Indexes        |
| :---------------------- | :----------------------- | :--------------------------------------------------- | :----------------------------------------------------------------------------- | :------------- |
| `id`                      | UUID                     | Primary Key, Default: `gen_random_uuid()`            | Unique identifier for the story.                                               | PK             |
| `user_id`                 | UUID                     | Foreign Key (`users.id`), Not Null                   | The user who initiated the story creation.                                     | FK, Indexed    |
| `child_name`              | VARCHAR                  | Not Null                                             | The name of the child protagonist provided by the user.                        |                |
| `child_age`               | INTEGER                  | Not Null                                             | The age of the child protagonist provided by the user.                         |                |
| `story_theme`             | VARCHAR                  | Not Null                                             | Identifier for the selected story theme (e.g., 'space_adventure').             | Indexed        |
| `protagonist_photo_id`  | UUID                     | Foreign Key (`photos.id`), Not Null                  | Reference to the uploaded photo used for personalization.                      | FK, Indexed    |
| `title`                   | VARCHAR                  | Nullable                                             | The title of the story (can be generated or set later).                        |                |
| `status`                  | VARCHAR                  | Not Null, Default: `'pending'`                       | Tracks the overall story generation status (e.g., 'pending', 'processing', 'completed', 'failed'). | Indexed        |
| `error_message`           | TEXT                     | Nullable                                             | Stores error details if story generation fails.                                |                |
| `created_at`              | TIMESTAMP WITH TIME ZONE | Not Null, Default: `NOW()`                           | Timestamp when the story creation was initiated.                               |                |
| `updated_at`              | TIMESTAMP WITH TIME ZONE | Not Null, Default: `NOW()`                           | Timestamp when the story record was last updated.                              |                |

---

## `story_pages` Table

Stores the content (text and image references) for each page within a story.

| Column Name                 | Type                     | Constraints & Defaults                               | Description                                                                    | Indexes              |
| :-------------------------- | :----------------------- | :--------------------------------------------------- | :----------------------------------------------------------------------------- | :------------------- |
| `id`                        | UUID                     | Primary Key, Default: `gen_random_uuid()`            | Unique identifier for the story page.                                          | PK                   |
| `story_id`                  | UUID                     | Foreign Key (`stories.id`), Not Null                 | The story this page belongs to.                                                | FK, Indexed          |
| `page_number`               | INTEGER                  | Not Null                                             | The sequential number of the page within the story (starting from 1).          | Indexed              |
| `text`                      | TEXT                     | Nullable                                             | The generated text content for this page.                                      |                      |
| `base_image_key`          | VARCHAR                  | Nullable                                             | The storage key for the base (non-personalized) generated image for this page. |                      |
| `personalized_image_key`    | VARCHAR                  | Nullable                                             | The storage key for the personalized image for this page.                      |                      |
| `text_generation_status`    | VARCHAR                  | Nullable, Default: `'pending'`                       | Status of text generation for this page.                                       | Indexed              |
| `image_generation_status`   | VARCHAR                  | Nullable, Default: `'pending'`                       | Status of base image generation for this page.                                 | Indexed              |
| `personalization_status`    | VARCHAR                  | Nullable, Default: `'pending'`                       | Status of image personalization for this page.                                 | Indexed              |
| `created_at`                | TIMESTAMP WITH TIME ZONE | Not Null, Default: `NOW()`                           | Timestamp when the page record was created.                                    |                      |
| `updated_at`                | TIMESTAMP WITH TIME ZONE | Not Null, Default: `NOW()`                           | Timestamp when the page record was last updated.                               |                      |
|                             |                          | Unique (`story_id`, `page_number`)                   | Ensures page numbers are unique within a story.                                | Unique Constraint    |

---

## `orders` Table

Stores information about user orders for physical copies of stories.

| Column Name           | Type                     | Constraints & Defaults                               | Description                                                                    | Indexes        |
| :-------------------- | :----------------------- | :--------------------------------------------------- | :----------------------------------------------------------------------------- | :------------- |
| `id`                  | UUID                     | Primary Key, Default: `gen_random_uuid()`            | Unique identifier for the order.                                               | PK             |
| `user_id`             | UUID                     | Foreign Key (`users.id`), Not Null                   | The user who placed the order.                                                 | FK, Indexed    |
| `story_id`            | UUID                     | Foreign Key (`stories.id`), Not Null                 | The story being ordered.                                                       | FK, Indexed    |
| `product_type`        | VARCHAR                  | Not Null                                             | Identifier for the physical product (e.g., 'hardcover_book').                  | Indexed        |
| `status`              | VARCHAR                  | Not Null, Default: `'pending_payment'`               | Tracks the order lifecycle (e.g., 'pending_payment', 'paid', 'fulfilled', 'shipped', 'failed'). | Indexed        |
| `amount`              | INTEGER                  | Not Null                                             | Total price of the order in the smallest currency unit (e.g., cents).          |                |
| `currency`            | VARCHAR(3)               | Not Null                                             | ISO currency code (e.g., 'usd').                                               |                |
| `shipping_address`    | JSONB                    | Nullable                                             | Structured shipping address details provided by the user.                      | GIN Index?     |
| `payment_provider`    | VARCHAR                  | Nullable                                             | Identifier for the payment gateway used (e.g., 'stripe').                      |                |
| `payment_intent_id`   | VARCHAR                  | Nullable, Unique                                     | The unique transaction ID from the payment provider.                           | Unique Index   |
| `pod_provider`        | VARCHAR                  | Nullable                                             | Identifier for the Print-on-Demand provider used (e.g., 'lulu').               |                |
| `pod_order_id`        | VARCHAR                  | Nullable                                             | The order ID assigned by the POD provider.                                     | Indexed        |
| `tracking_number`     | VARCHAR                  | Nullable                                             | Shipping tracking number, provided by POD provider.                            |                |
| `paid_at`             | TIMESTAMP WITH TIME ZONE | Nullable                                             | Timestamp when the payment was successfully confirmed.                         |                |
| `fulfilled_at`        | TIMESTAMP WITH TIME ZONE | Nullable                                             | Timestamp when the POD provider confirmed fulfillment/production.              |                |
| `shipped_at`          | TIMESTAMP WITH TIME ZONE | Nullable                                             | Timestamp when the order was shipped by the POD provider.                      |                |
| `created_at`          | TIMESTAMP WITH TIME ZONE | Not Null, Default: `NOW()`                           | Timestamp when the order record was created (payment intent initiated).        |                |
| `updated_at`          | TIMESTAMP WITH TIME ZONE | Not Null, Default: `NOW()`                           | Timestamp when the order record was last updated.                              |                |