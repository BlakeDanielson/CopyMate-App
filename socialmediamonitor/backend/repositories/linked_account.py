from typing import Optional, List, Dict, Any, Union
from sqlalchemy.orm import Session
from datetime import datetime
from pydantic import BaseModel

from backend.repositories.base import BaseRepository
from backend.models.user import LinkedAccount
from backend.models.base import PlatformType
from backend.utils.encryption import encrypt_token, decrypt_token


class LinkedAccountRepository(BaseRepository[LinkedAccount, dict, dict]):
    """
    Repository for LinkedAccount operations.
    Handles encryption/decryption of sensitive token data.
    """
    def __init__(self):
        super().__init__(LinkedAccount)

    def _decrypt_account_tokens(self, account: Optional[LinkedAccount]) -> Optional[LinkedAccount]:
        """Decrypts access and refresh tokens for a LinkedAccount object."""
        if account:
            if account.access_token:
                # Ensure access_token is bytes before decrypting
                if isinstance(account.access_token, str):
                     account.access_token = account.access_token.encode('utf-8')
                account.access_token = decrypt_token(account.access_token)
            if account.refresh_token:
                 # Ensure refresh_token is bytes before decrypting
                if isinstance(account.refresh_token, str):
                     account.refresh_token = account.refresh_token.encode('utf-8')
                account.refresh_token = decrypt_token(account.refresh_token)
        return account

    def get(self, db: Session, id: Any) -> Optional[LinkedAccount]:
        """
        Get a single record by ID and decrypt tokens.

        Args:
            db: Database session
            id: ID of the record to get

        Returns:
            The found record with decrypted tokens or None
        """
        account = super().get(db, id)
        return self._decrypt_account_tokens(account)

    def get_by_platform_id(
        self, db: Session, platform: str, platform_account_id: str
    ) -> Optional[LinkedAccount]:
        """
        Get a linked account by platform and platform-specific account ID and decrypt tokens.

        Args:
            db: Database session
            platform: Platform type (e.g., "youtube")
            platform_account_id: Platform-specific account ID

        Returns:
            The found linked account with decrypted tokens or None
        """
        account = db.query(LinkedAccount).filter(
            LinkedAccount.platform == platform,
            LinkedAccount.platform_account_id == platform_account_id
        ).first()
        return self._decrypt_account_tokens(account)

    def get_linked_accounts_for_child(
        self, db: Session, child_profile_id: int, platform: Optional[str] = None, active_only: bool = True
    ) -> List[LinkedAccount]:
        """
        Get linked accounts for a specific child profile, optionally filtered by platform.
        Tokens in the returned objects will be decrypted.

        Args:
            db: Database session
            child_profile_id: ID of the child profile
            platform: Optional platform type to filter by
            active_only: If True, return only active accounts

        Returns:
            List of linked accounts for the child profile with decrypted tokens
        """
        query = db.query(LinkedAccount).filter(LinkedAccount.child_profile_id == child_profile_id)

        if platform:
            query = query.filter(LinkedAccount.platform == platform)

        if active_only:
            query = query.filter(LinkedAccount.is_active == True)

        accounts = query.all()
        return [self._decrypt_account_tokens(acc) for acc in accounts]

    def create(self, db: Session, *, obj_in: Union[dict, BaseModel]) -> LinkedAccount:
        """
        Create a new linked account, encrypting tokens before saving.

        Args:
            db: Database session
            obj_in: Data to create the record with (dict or Pydantic model)

        Returns:
            The created linked account with decrypted tokens
        """
        if isinstance(obj_in, BaseModel):
            obj_data = obj_in.model_dump(exclude_unset=True)
        else:
            obj_data = obj_in

        # Encrypt tokens before creating the object
        if "access_token" in obj_data and obj_data["access_token"] is not None:
            encrypted_access_token = encrypt_token(obj_data["access_token"])
            if encrypted_access_token is not None:
                obj_data["access_token"] = encrypted_access_token
            else:
                # Handle encryption failure - maybe raise an error or log
                print("Warning: Failed to encrypt access token.")
                # Depending on requirements, you might want to raise an exception here
                # raise EncryptionError("Failed to encrypt access token")
                pass # Or proceed with unencrypted token if acceptable (less secure)

        if "refresh_token" in obj_data and obj_data["refresh_token"] is not None:
            encrypted_refresh_token = encrypt_token(obj_data["refresh_token"])
            if encrypted_refresh_token is not None:
                obj_data["refresh_token"] = encrypted_refresh_token
            else:
                 # Handle encryption failure
                print("Warning: Failed to encrypt refresh token.")
                pass # Or proceed with unencrypted token if acceptable (less secure)


        db_obj = super().create(db, obj_in=obj_data)
        return self._decrypt_account_tokens(db_obj)


    def update_tokens(
        self,
        db: Session,
        account_id: int,
        access_token: str,
        refresh_token: Optional[str] = None,
        token_expiry: Optional[datetime] = None
    ) -> Optional[LinkedAccount]:
        """
        Update OAuth tokens for a linked account, encrypting tokens before saving.

        Args:
            db: Database session
            account_id: ID of the linked account
            access_token: New access token
            refresh_token: New refresh token (optional)
            token_expiry: Token expiry timestamp (optional)

        Returns:
            The updated linked account with decrypted tokens or None if not found
        """
        account = self.get(db, account_id) # get() already decrypts
        if not account:
            return None

        update_data = {}

        # Encrypt tokens before updating
        if access_token is not None:
            encrypted_access_token = encrypt_token(access_token)
            if encrypted_access_token is not None:
                 update_data["access_token"] = encrypted_access_token
            else:
                print("Warning: Failed to encrypt access token during update.")
                pass # Handle encryption failure

        if refresh_token is not None:
            encrypted_refresh_token = encrypt_token(refresh_token)
            if encrypted_refresh_token is not None:
                update_data["refresh_token"] = encrypted_refresh_token
            else:
                print("Warning: Failed to encrypt refresh token during update.")
                pass # Handle encryption failure

        if token_expiry is not None:
            update_data["token_expiry"] = token_expiry

        if not update_data: # No valid data to update
             return account # Return the original decrypted account

        updated_account = super().update(db, db_obj=account, obj_in=update_data)
        return self._decrypt_account_tokens(updated_account) # Decrypt before returning


    def deactivate_account(self, db: Session, account_id: int) -> Optional[LinkedAccount]:
        """
        Deactivate a linked account (soft delete).

        Args:
            db: Database session
            account_id: ID of the linked account
            
        Returns:
            The updated linked account with decrypted tokens or None if not found
        """
        account = super().deactivate_account(db, account_id)
        return self._decrypt_account_tokens(account)


    def update_last_scan(self, db: Session, account_id: int) -> Optional[LinkedAccount]:
        """
        Update the last_scan_at timestamp of a linked account.

        Args:
            db: Database session
            account_id: ID of the linked account

        Returns:
            The updated linked account with decrypted tokens or None if not found
        """
        account = super().update_last_scan(db, account_id)
        return self._decrypt_account_tokens(account)