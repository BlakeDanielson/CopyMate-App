# OAuth Requirements Implementation

This document outlines the implementation of the OAuth requirements for the GuardianLens application, focusing on the YouTube account linking functionality.

## Implemented Requirements

### REQ-L01: Initiate linking flow for a specific child profile and YouTube
- Implemented in `backend/routers/linked_account.py` via the `initiate_account_linking` endpoint
- Uses Google OAuth 2.0 flow with the `youtube.readonly` scope
- Generates a secure state token to prevent CSRF attacks

### REQ-L02: Provide clear explanations about the process and data accessed
- Implemented in `backend/routers/oauth_explanation.py` via the `get_oauth_explanation` endpoint
- Provides detailed, age-appropriate explanations about:
  - What data will be accessed (subscriptions, public channel metadata, recent video metadata)
  - How the data will be used
  - Privacy considerations
  - The OAuth flow process
- Explanations are tailored based on the child's age

### REQ-L03: Use Google OAuth 2.0 flow requesting only the youtube.readonly scope
- Implemented in `backend/utils/oauth.py` via the `create_youtube_oauth_flow` function
- Requests only the minimal required scope: `https://www.googleapis.com/auth/youtube.readonly`

### REQ-L04: Securely handle and store OAuth tokens upon successful authorization
- Implemented in `backend/routers/oauth.py` via the `oauth_callback` endpoint
- Tokens are encrypted before storage using the `LinkedAccountRepository`
- Refresh tokens are used to maintain access without requiring re-authorization

### REQ-L05: Display confirmation of successful linking on the dashboard
- Implemented in `backend/routers/oauth.py` via the enhanced `oauth_callback` response
- Returns detailed information about the linked account:
  - Account ID
  - Platform username
  - Whether it's a new or updated account
  - Timestamp of linking
  - Redirect URL to the dashboard

### REQ-L06: Implement robust handling for OAuth errors or consent denial
- Implemented in `backend/routers/oauth.py` via error handling in the `oauth_callback` endpoint
- Handles various error scenarios:
  - User denial of consent
  - Invalid state tokens
  - Token exchange failures
  - API errors
- Logs errors for troubleshooting

### REQ-L07: Implement Verifiable Parental Consent mechanism for children under 13 (COPPA)
- Implemented in `backend/routers/coppa_verification.py`
- Provides multiple verification methods:
  - Credit card verification
  - Government ID verification
  - Digital signature
  - Phone verification
  - Email verification
- Verifications have an expiry date (1 year by default)
- Blocks account linking for children under 13 without valid verification

### REQ-L08: Ensure child consent/login is part of the flow for users 13+
- Implemented in `backend/routers/linked_account.py` and `backend/routers/coppa_verification.py`
- Different flows based on child's age:
  - Under 13: Requires verifiable parental consent before OAuth flow
  - 13+: Proceeds directly to Google OAuth flow where child must log in and consent
- Age-specific messaging and guidance

### REQ-L09: Implement account unlinking functionality
- Implemented in `backend/routers/linked_account.py` via the `unlink_account` endpoint
- Revokes OAuth tokens with the platform provider
- Deactivates the account in the database (soft delete)
- Logs the unlinking action for audit purposes

## Testing

Each requirement has corresponding test files:
- `tests/backend/utils/test_oauth.py`
- `tests/backend/utils/test_oauth_explanation.py`
- `tests/backend/utils/test_oauth_revocation.py`
- `tests/backend/routers/test_oauth.py`
- `tests/backend/routers/test_linked_account_initiate.py`
- `tests/backend/routers/test_linked_account_unlink.py`

## Security Considerations

- All OAuth tokens are encrypted before storage
- State tokens are used to prevent CSRF attacks
- Minimal scopes are requested
- Tokens can be revoked at any time
- Comprehensive audit logging
- Age-appropriate consent flows
- COPPA compliance for children under 13