# 7. Data Models & Schema

This section details the database schema managed by Prisma, defined in `prisma/schema.prisma`. The database provider is PostgreSQL.

## Models

### `User`

Represents an application user.

*   `id` (String, CUID): Primary key.
*   `name` (String, Optional): User's display name.
*   `email` (String, Optional, Unique): User's email address.
*   `emailVerified` (DateTime, Optional): Timestamp when the email was verified (used by NextAuth).
*   `image` (String, Optional): URL to the user's profile picture.
*   `password_hash` (String, Optional): Hashed password (if using custom credentials). *Note: This field seems missing in the provided schema but is implied by `lib/auth` usage.*
*   **Relations:**
    *   `accounts` (Account[]): Linked OAuth accounts.
    *   `sessions` (Session[]): Active user sessions.
    *   `conversations` (Conversation[]): User's chat conversations.
    *   `settings` (UserSettings, Optional): User-specific settings (one-to-one).

### `Account`

Stores information for OAuth providers linked to a user (part of NextAuth standard schema).

*   `id` (String, CUID): Primary key.
*   `userId` (String): Foreign key linking to `User`.
*   `type` (String): Account type (e.g., "oauth", "email").
*   `provider` (String): OAuth provider name (e.g., "github", "google").
*   `providerAccountId` (String): User's ID on the provider's system.
*   `refresh_token`, `access_token`, `expires_at`, `token_type`, `scope`, `id_token`, `session_state`: OAuth-specific fields.
*   **Relations:**
    *   `user` (User): The user this account belongs to.
*   **Index:** `@@unique([provider, providerAccountId])`

### `Session`

Stores user session information (part of NextAuth standard schema).

*   `id` (String, CUID): Primary key.
*   `sessionToken` (String, Unique): The unique token identifying the session.
*   `userId` (String): Foreign key linking to `User`.
*   `expires` (DateTime): When the session expires.
*   **Relations:**
    *   `user` (User): The user this session belongs to.

### `VerificationToken`

Used for email verification links (part of NextAuth standard schema).

*   `identifier` (String): Typically the email address.
*   `token` (String, Unique): The verification token.
*   `expires` (DateTime): When the token expires.
*   **Index:** `@@unique([identifier, token])`

### `Conversation`

Represents a single chat conversation.

*   `id` (String, CUID): Primary key.
*   `title` (String): The title of the conversation (e.g., user-defined or generated).
*   `createdAt` (DateTime): Timestamp of creation.
*   `updatedAt` (DateTime): Timestamp of the last update.
*   `isPinned` (Boolean, Default: `false`): Whether the conversation is pinned by the user.
*   `lastMessageAt` (DateTime, Default: `now()`): Timestamp of the last message added (used for sorting).
*   `userId` (String): Foreign key linking to the `User` who owns the conversation.
*   **Relations:**
    *   `user` (User): The owner of the conversation.
    *   `messages` (Message[]): Messages within this conversation.
*   **Index:** `@@index([userId])`

### `Message`

Represents a single message within a conversation.

*   `id` (String, CUID): Primary key.
*   `role` (String): The role of the message sender (e.g., "user", "assistant").
*   `content` (String, Text): The actual text content of the message.
*   `tokensUsed` (Int, Default: 0): Number of tokens used by the AI model for this message (if applicable).
*   `createdAt` (DateTime): Timestamp of creation.
*   `conversationId` (String): Foreign key linking to the `Conversation`.
*   **Relations:**
    *   `conversation` (Conversation): The conversation this message belongs to.
*   **Index:** `@@index([conversationId])`

### `UserSettings`

Stores user-specific preferences and settings.

*   `id` (String, CUID): Primary key.
*   `modelName` (String, Default: "gpt-4o"): Preferred AI model.
*   `temperature` (Float, Default: 0.7): AI model temperature setting.
*   `maxTokens` (Int, Default: 1000): AI model maximum token limit.
*   `theme` (String, Default: "dark"): UI theme preference (e.g., "light", "dark").
*   `fontSize` (String, Default: "medium"): UI font size preference.
*   `createdAt` (DateTime): Timestamp of creation.
*   `updatedAt` (DateTime): Timestamp of the last update.
*   `userId` (String, Unique): Foreign key linking to the `User`.
*   **Relations:**
    *   `user` (User): The user these settings belong to.

## Relationships Summary

*   **User <-> Account:** One-to-Many (A user can have multiple linked OAuth accounts).
*   **User <-> Session:** One-to-Many (A user can have multiple active sessions).
*   **User <-> Conversation:** One-to-Many (A user owns multiple conversations).
*   **User <-> UserSettings:** One-to-One (A user has one set of settings).
*   **Conversation <-> Message:** One-to-Many (A conversation contains multiple messages).

## Notes

*   `onDelete: Cascade` is used extensively, meaning deleting a related record (like a `User`) will automatically delete dependent records (like their `Account`, `Session`, `Conversation`, `Message`, `UserSettings`).
*   `@map` attributes are used to define the underlying database column names (e.g., `createdAt` maps to `created_at`).
*   Default values are set for several fields (e.g., `Conversation.isPinned`, `Message.tokensUsed`, `UserSettings` defaults).