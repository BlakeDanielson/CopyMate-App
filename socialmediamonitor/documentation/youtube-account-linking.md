# YouTube Account Linking Guide

This document provides information about the YouTube account linking feature in GuardianLens, including implementation details, usage instructions, and troubleshooting tips.

## Overview

The YouTube account linking feature allows parents to link their child's YouTube account to GuardianLens. This enables the system to analyze the child's subscribed channels for potential risks.

The linking process follows the OAuth 2.0 flow:

1. Parent initiates the linking process for a specific child profile.
2. Based on the child's age, the appropriate consent flow is followed (COPPA for under 13, Google OAuth for 13+).
3. Child (with parent guidance) is redirected to Google's consent screen if applicable.
4. Child authorizes GuardianLens to access their YouTube data (read-only).
5. Google redirects back to GuardianLens with an authorization code.
6. GuardianLens exchanges the code for access and refresh tokens.
7. GuardianLens securely stores the tokens and initiates the monitoring process for the subscribed channels.

## Implementation Details

### Configuration

The following environment variables must be set for YouTube account linking to work:

- `YOUTUBE_CLIENT_ID`: OAuth client ID from Google Developer Console
- `YOUTUBE_CLIENT_SECRET`: OAuth client secret from Google Developer Console
- `YOUTUBE_REDIRECT_URI`: Redirect URI registered in Google Developer Console (default: `http://localhost:8000/api/v1/oauth/callback`)
- `JWT_SECRET_KEY`: Secret key for signing JWT tokens used in the OAuth state parameter.

### API Endpoints

#### Initiate Linking

```
POST /api/v1/linked_accounts/initiate-linking
```

Request body:

```json
{
  "child_profile_id": "uuid-of-child-profile",
  "platform": "youtube"
}
```

Response:

```json
{
  "authorization_url": "https://accounts.google.com/o/oauth2/auth?...",
  "state": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

The frontend should redirect the user to the `authorization_url` to begin the OAuth flow.

#### OAuth Callback

```
GET /api/v1/oauth/callback?code={code}&state={state}
```

This endpoint is called by Google after the user authorizes or denies the application. It should not be called directly by the frontend.

Response (success):

```json
{
  "status": "success",
  "message": "Account successfully linked",
  "linked_account_id": "uuid-of-linked-account",
  "platform_username": "YouTube Username",
  "is_new_account": true,
  "linked_at": "timestamp",
  "redirect_to": "/dashboard/child/uuid-of-child-profile"
}
```

Response (error):

```json
{
  "status": "error",
  "message": "Authorization denied or error occurred: access_denied",
  "redirect_to": "/account-linking-error"
}
```

The frontend should check the `status` field and redirect the user to the URL specified in the `redirect_to` field.

#### Unlink Account

```
DELETE /api/v1/linked_accounts/{linked_account_id}
```

This endpoint allows a parent to unlink a child's YouTube account.

Response (success):

```json
{
  "status": "success",
  "message": "Account successfully unlinked"
}
```

Response (error):

```json
{
  "status": "error",
  "message": "Error unlinking account: Account not found"
}
```

## Scopes and Permissions

GuardianLens requests the following OAuth scopes:

- `https://www.googleapis.com/auth/youtube.readonly`: Allows read-only access to YouTube data, including subscriptions, channel information, and video metadata.

This scope does not allow:
- Viewing private videos
- Accessing watch history
- Posting comments or videos
- Making any changes to the YouTube account

## User Experience Flow

1. Parent navigates to the child's profile in GuardianLens.
2. Parent clicks "Link YouTube Account" button.
3. Based on the child's age, the appropriate consent flow is initiated (COPPA verification for under 13, or direct to Google OAuth for 13+).
4. Parent is shown information about what data will be accessed and how it will be used.
5. Parent clicks "Continue" to initiate the linking process.
6. Child (with parent guidance) logs in to their Google account if not already logged in (for 13+).
7. Child sees the Google consent screen explaining what permissions GuardianLens is requesting.
8. Child clicks "Allow" to grant permission.
9. Child is redirected back to GuardianLens.
10. Parent sees confirmation that the account was successfully linked.
11. Parent can now view the child's subscribed channels and analysis results in the dashboard.

## Troubleshooting

### Common Issues

1. **"Invalid client" error on Google consent screen**
   - Ensure the `YOUTUBE_CLIENT_ID` and `YOUTUBE_CLIENT_SECRET` are correctly set in environment variables.
   - Verify that the application is properly configured in the Google Developer Console.

2. **Redirect URI mismatch error**
   - Ensure the `YOUTUBE_REDIRECT_URI` matches exactly what is registered in the Google Developer Console.
   - Check for any trailing slashes or protocol differences (http vs https).

3. **"Access denied" error after consent screen**
   - The user denied permission on the consent screen.
   - Check if the user is using a Google Workspace account with restrictions.

4. **Token refresh failures**
   - Check if the refresh token is still valid.
   - Verify that the application still has the necessary permissions in Google Developer Console.

### Debugging

The system logs all OAuth-related actions and errors in the audit log. To debug issues:

1. Check the audit log for entries with `resource_type="oauth"`.
2. Look for `SYSTEM_ERROR` entries related to the OAuth flow.
3. Check the `details` field for specific error messages.

## Security Considerations

1. **State Parameter**: The state parameter is used to prevent CSRF attacks. It contains a JWT token with the child profile ID, platform, parent ID, and a timestamp.
2. **Token Storage**: Access and refresh tokens are stored encrypted in the database.
3. **Token Expiry**: Access tokens expire after 1 hour. The system automatically refreshes them using the refresh token.
4. **Minimal Scopes**: Only the minimal required scopes are requested to limit the access to the user's data.
5. **Revocation**: Parents can unlink the YouTube account at any time, which revokes the access and deletes the tokens.
6. **COPPA Compliance**: For children under 13, verifiable parental consent is required before initiating the OAuth flow.