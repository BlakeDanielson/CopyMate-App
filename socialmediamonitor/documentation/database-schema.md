# Database Schema Documentation

This document provides a detailed overview of the GuardianLens PostgreSQL database schema MVP.

## Key Entities

The primary entities in the database schema are (Section 8, `Tech_Spec.md`):

*   **ParentUser:** Stores information about parent accounts (authentication credentials, settings).
*   **ChildProfile:** Represents a child profile created by a parent (internal identifier/name, age).
*   **LinkedAccount:** Links a ChildProfile to a specific social media account (Platform=YouTube, stores OAuth tokens).
*   **SubscribedChannel:** Stores metadata for a YouTube channel the child is subscribed to (Title, Description, Thumbnail URL, Subscriber Count, Video Count, Topic Details).
*   **AnalyzedVideo:** Stores metadata for recent videos from subscribed channels (Video Title, Description).
*   **AnalysisResult:** Stores the results of the analysis engine for a specific channel/video (flags, risk categories, potentially triggering snippets).
*   **Alert:** Represents a notification summary (e.g., daily scan complete, new flags found).
*   **AuditLog:** Records significant system events, including user actions and data access.
*   **CoppaVerification:** Stores verification records for children under 13 years old to comply with COPPA regulations.

## Table Details

### `parent_users`

| Field          | Data Type | Constraints                  | Description                                   |
|----------------|-----------|------------------------------|-----------------------------------------------|
| `id`           | Integer   | PRIMARY KEY, INDEX           | Unique identifier for the parent user         |
| `email`        | String    | UNIQUE, NOT NULL, INDEX      | Parent's email address                        |
| `hashed_password`| String    | NOT NULL                     | Hashed password for authentication            |
| `first_name`   | String    | NULLABLE                     | Parent's first name                           |
| `last_name`    | String    | NULLABLE                     | Parent's last name                            |
| `is_active`    | Boolean   | DEFAULT TRUE                 | Indicates if the account is active            |
| `last_login`   | Timestamp | NULLABLE                     | Timestamp of last login                       |
| `created_at`   | Timestamp | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Timestamp of user creation                  |
| `updated_at`   | Timestamp | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Timestamp of last update                    |

### `child_profiles`

| Field          | Data Type | Constraints                  | Description                                   |
|----------------|-----------|------------------------------|-----------------------------------------------|
| `id`           | Integer   | PRIMARY KEY, INDEX           | Unique identifier for the child profile       |
| `parent_id`    | Integer   | NOT NULL, FOREIGN KEY (`parent_users.id`) | ID of the parent user who owns this profile |
| `display_name` | String    | NOT NULL                     | Internal name for the child profile           |
| `age`          | Integer   | NULLABLE                     | Age of the child (for COPPA)                  |
| `notes`        | Text      | NULLABLE                     | Additional notes about the child profile      |
| `is_active`    | Boolean   | DEFAULT TRUE                 | Indicates if the profile is active            |
| `created_at`   | Timestamp | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Timestamp of profile creation               |
| `updated_at`   | Timestamp | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Timestamp of last update                    |

### `linked_accounts`

| Field              | Data Type | Constraints                  | Description                                   |
|--------------------|-----------|------------------------------|-----------------------------------------------|
| `id`               | Integer   | PRIMARY KEY, INDEX           | Unique identifier for the linked account      |
| `child_profile_id` | Integer   | NOT NULL, FOREIGN KEY (`child_profiles.id`) | ID of the child profile this account is linked to |
| `platform`         | String    | NOT NULL                     | Social media platform (e.g., 'youtube')       |
| `platform_account_id`| String  | NOT NULL                     | Unique identifier for the user on the platform |
| `platform_username`| String    | NULLABLE                     | Username on the platform                      |
| `access_token`     | String    | NOT NULL                     | Encrypted access token for the platform API   |
| `refresh_token`    | String    | NULLABLE                     | Encrypted refresh token for the platform API  |
| `token_expiry`     | Timestamp | NULLABLE                     | Timestamp when the access token expires       |
| `platform_metadata`| JSON      | NULLABLE                     | Additional platform-specific information      |
| `is_active`        | Boolean   | DEFAULT TRUE                 | Indicates if the account is actively monitored |
| `last_scan_at`     | Timestamp | NULLABLE                     | Timestamp of the last content scan            |
| `created_at`       | Timestamp | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Timestamp of account linking                |
| `updated_at`       | Timestamp | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Timestamp of last update                    |

### `subscribed_channels`

| Field              | Data Type | Constraints                  | Description                                   |
|--------------------|-----------|------------------------------|-----------------------------------------------|
| `id`               | Integer   | PRIMARY KEY, INDEX           | Unique identifier for the subscribed channel  |
| `linked_account_id`| Integer   | NOT NULL, FOREIGN KEY (`linked_accounts.id`) | ID of the linked account this channel belongs to |
| `channel_id`       | String    | NOT NULL, INDEX              | Unique identifier for the channel on YouTube  |
| `title`            | String    | NOT NULL                     | Channel title                                 |
| `description`      | Text      | NULLABLE                     | Channel description                           |
| `thumbnail_url`    | String    | NULLABLE                     | URL of the channel thumbnail                  |
| `subscriber_count` | Integer   | NULLABLE                     | Number of subscribers                         |
| `video_count`      | Integer   | NULLABLE                     | Number of videos on the channel               |
| `topic_details`    | JSON      | NULLABLE                     | YouTube topic details for the channel         |
| `last_fetched_at`  | Timestamp | NULLABLE                     | Timestamp of last metadata fetch              |
| `created_at`       | Timestamp | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Timestamp of channel subscription discovery |
| `updated_at`       | Timestamp | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Timestamp of last update                    |

### `analyzed_videos`

| Field                | Data Type | Constraints                  | Description                                   |
|----------------------|-----------|------------------------------|-----------------------------------------------|
| `id`                 | Integer   | PRIMARY KEY, INDEX           | Unique identifier for the analyzed video      |
| `channel_id`         | Integer   | NOT NULL, FOREIGN KEY (`subscribed_channels.id`) | ID of the subscribed channel this video belongs to |
| `video_platform_id`  | String    | NOT NULL, INDEX              | Unique identifier for the video on YouTube    |
| `title`              | String    | NOT NULL                     | Video title                                   |
| `description`        | Text      | NULLABLE                     | Video description                             |
| `thumbnail_url`      | String    | NULLABLE                     | URL of the video thumbnail                    |
| `published_at`       | Timestamp | NULLABLE                     | Timestamp when the video was published        |
| `duration`           | String    | NULLABLE                     | Duration of the video in ISO 8601 format      |
| `view_count`         | Integer   | NULLABLE                     | Number of views                               |
| `like_count`         | Integer   | NULLABLE                     | Number of likes                               |
| `fetched_at`         | Timestamp | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Timestamp of video metadata fetching        |
| `updated_at`         | Timestamp | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Timestamp of last update                    |

### `analysis_results`

| Field                | Data Type | Constraints                  | Description                                   |
|----------------------|-----------|------------------------------|-----------------------------------------------|
| `id`                 | Integer   | PRIMARY KEY, INDEX           | Unique identifier for the analysis result     |
| `channel_id`         | Integer   | NULLABLE, FOREIGN KEY (`subscribed_channels.id`) | ID of the subscribed channel analyzed       |
| `video_id`           | Integer   | NULLABLE, FOREIGN KEY (`analyzed_videos.id`) | ID of the analyzed video (if analysis is video-specific) |
| `risk_category`      | Enum      | NOT NULL                     | Category of risk identified (e.g., HATE_SPEECH, SELF_HARM) |
| `severity`           | String    | NULLABLE                     | Severity of the risk (e.g., 'high', 'medium', 'low') |
| `flagged_text`       | Text      | NULLABLE                     | Text snippet that triggered the flag          |
| `keywords_matched`   | JSON      | NULLABLE                     | Array of matched keywords                     |
| `confidence_score`   | Float     | NULLABLE                     | Confidence score for the analysis result      |
| `marked_not_harmful` | Boolean   | DEFAULT FALSE                | Indicates if the parent has marked as "Not Harmful" |
| `marked_not_harmful_at` | Timestamp | NULLABLE                  | Timestamp when marked as not harmful          |
| `marked_not_harmful_by` | Integer | NULLABLE, FOREIGN KEY (`parent_users.id`) | ID of the parent who marked as not harmful |
| `created_at`         | Timestamp | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Timestamp of the analysis                   |
| `updated_at`         | Timestamp | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Timestamp of last update                    |

### `alerts`

| Field              | Data Type | Constraints                  | Description                                   |
|--------------------|-----------|------------------------------|-----------------------------------------------|
| `id`               | Integer   | PRIMARY KEY, INDEX           | Unique identifier for the alert               |
| `child_profile_id` | Integer   | NOT NULL, FOREIGN KEY (`child_profiles.id`) | ID of the child profile the alert is for    |
| `alert_type`       | Enum      | NOT NULL                     | Type of alert (e.g., SCAN_COMPLETE, NEW_FLAGS) |
| `title`            | String    | NOT NULL                     | Alert title                                   |
| `message`          | Text      | NOT NULL                     | Alert message content                         |
| `summary_data`     | JSON      | NULLABLE                     | Summary information like number of flags      |
| `is_read`          | Boolean   | DEFAULT FALSE                | Indicates if the alert has been read          |
| `read_at`          | Timestamp | NULLABLE                     | Timestamp when the alert was read             |
| `created_at`       | Timestamp | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Timestamp of alert creation                 |

### `audit_logs`

| Field          | Data Type | Constraints                  | Description                                   |
|----------------|-----------|------------------------------|-----------------------------------------------|
| `id`           | Integer   | PRIMARY KEY, INDEX           | Unique identifier for the audit log entry     |
| `parent_id`    | Integer   | NULLABLE, FOREIGN KEY (`parent_users.id`) | ID of the parent user performing the action  |
| `action`       | Enum      | NOT NULL                     | Type of action performed (e.g., USER_LOGIN, ACCOUNT_LINK) |
| `resource_type`| String    | NULLABLE                     | Type of resource affected (e.g., 'child_profile') |
| `resource_id`  | Integer   | NULLABLE                     | ID of the resource affected                   |
| `details`      | JSON      | NULLABLE                     | Additional details about the action           |
| `ip_address`   | String    | NULLABLE                     | IP address of the user                        |
| `user_agent`   | String    | NULLABLE                     | Browser/client information                    |
| `created_at`   | Timestamp | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Timestamp of the action                     |

### `coppa_verifications`

| Field                | Data Type | Constraints                  | Description                                   |
|----------------------|-----------|------------------------------|-----------------------------------------------|
| `id`                 | Integer   | PRIMARY KEY, INDEX           | Unique identifier for the verification        |
| `child_profile_id`   | Integer   | NOT NULL, FOREIGN KEY (`child_profiles.id`) | ID of the child profile being verified     |
| `verification_method`| Enum      | NOT NULL                     | Method used for verification                  |
| `verification_status`| Enum      | NOT NULL, DEFAULT 'PENDING'  | Status of verification (PENDING, VERIFIED, REJECTED) |
| `verification_notes` | Text      | NULLABLE                     | Notes about the verification process          |
| `parent_email`       | String    | NOT NULL                     | Email of the parent providing verification    |
| `parent_full_name`   | String    | NOT NULL                     | Full name of the parent                       |
| `parent_statement`   | Boolean   | NOT NULL, DEFAULT FALSE      | Parent's consent statement                    |
| `platform`           | String    | NOT NULL                     | Platform being verified for                   |
| `verification_data`  | JSON      | NULLABLE                     | Encrypted or hashed sensitive data            |
| `created_at`         | Timestamp | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Timestamp of verification creation           |
| `verified_at`        | Timestamp | NULLABLE                     | Timestamp when verification was completed     |
| `expires_at`         | Timestamp | NULLABLE                     | Timestamp when verification expires           |

## Indexing Strategies

The database uses several indexing strategies to optimize query performance:

1. **Primary Key Indexes**: All tables have an auto-incrementing integer primary key with an index.

2. **Foreign Key Indexes**: All foreign key columns are indexed to improve join performance:
   - `child_profiles.parent_id`
   - `linked_accounts.child_profile_id`
   - `subscribed_channels.linked_account_id`
   - `analyzed_videos.channel_id`
   - `analysis_results.channel_id` and `analysis_results.video_id`
   - `alerts.child_profile_id`
   - `audit_logs.parent_id`
   - `coppa_verifications.child_profile_id`

3. **Lookup Indexes**: Columns frequently used in WHERE clauses are indexed:
   - `parent_users.email` (for authentication)
   - `subscribed_channels.channel_id` (for YouTube API lookups)
   - `analyzed_videos.video_platform_id` (for YouTube API lookups)

4. **Composite Indexes**: Some tables use composite indexes for common query patterns:
   - `linked_accounts`: Composite index on (child_profile_id, platform) for efficient account lookup
   - `analysis_results`: Composite index on (channel_id, risk_category) for filtering results by risk type
   - `alerts`: Composite index on (child_profile_id, created_at) for chronological alert listing

5. **Timestamp Indexes**: Columns used for time-based filtering have indexes:
   - `analysis_results.created_at` (for filtering recent analysis results)
   - `alerts.created_at` (for filtering recent alerts)
   - `audit_logs.created_at` (for audit trail queries)

These indexing strategies are implemented directly in the SQLAlchemy model definitions using the `index=True` parameter and through the `__table_args__` attribute for composite indexes.