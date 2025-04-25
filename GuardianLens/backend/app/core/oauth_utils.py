from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone, timedelta

from app import crud, schemas, models
from app.config import settings

async def refresh_google_token(
    db: AsyncSession, *, linked_account: models.LinkedAccount
) -> models.LinkedAccount | None:
    """
    Refreshes the Google OAuth token if expired or close to expiry.
    Updates the linked account in the database. Returns the updated account or None if refresh fails.
    """
    if not linked_account.refresh_token:
        # Cannot refresh without a refresh token
        # Consider logging this situation
        return linked_account  # Return unchanged account

    # Check if token is expired or needs refresh (e.g., within 5 minutes of expiry)
    needs_refresh = False
    if not linked_account.expires_at:
        needs_refresh = True  # Assume refresh needed if no expiry stored
    else:
        # Make expiry timezone-aware if it's naive
        expiry = linked_account.expires_at
        if expiry.tzinfo is None:
            expiry = expiry.replace(tzinfo=timezone.utc)

        # Refresh if expired or within a buffer (e.g., 5 minutes)
        if expiry < (datetime.now(timezone.utc) + timedelta(minutes=5)):
            needs_refresh = True

    if not needs_refresh:
        return linked_account  # Token is still valid

    # Create credentials object from stored tokens
    try:
        credentials = Credentials(
            token=linked_account.access_token,
            refresh_token=linked_account.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",  # Standard Google token URI
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            scopes=linked_account.scopes.split(" ") if linked_account.scopes else None,
            expiry=linked_account.expires_at  # Pass expiry to credentials object
        )

        # Attempt to refresh the token
        credentials.refresh(Request())  # Uses google.auth.transport.requests

        # Update the linked account with new token info
        update_data = schemas.LinkedAccountUpdate(
            access_token=credentials.token,
            expires_at=credentials.expiry,
            scopes=" ".join(credentials.scopes) if credentials.scopes else None
            # Note: Refresh token usually remains the same, but check Google docs if needed
        )
        updated_account = await crud.crud_linked_account.update_linked_account_tokens(
            db=db, db_obj=linked_account, obj_in=update_data
        )
        return updated_account

    except RefreshError as e:
        # Handle refresh error (e.g., token revoked, invalid grant)
        # Log the error, potentially mark the account as needing re-authentication
        print(f"Failed to refresh token for profile {linked_account.profile_id}: {e}")  # Replace with proper logging
        # Optionally remove the invalid linked account or mark it inactive
        # await crud.crud_linked_account.remove_linked_account(db, linked_account_id=linked_account.id)
        return None  # Indicate refresh failure
    except Exception as e:
        # Handle other potential errors during refresh
        print(f"Unexpected error refreshing token for profile {linked_account.profile_id}: {e}")  # Replace with proper logging
        return None  # Indicate refresh failure