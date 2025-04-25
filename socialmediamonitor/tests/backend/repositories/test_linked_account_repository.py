import unittest
from unittest.mock import MagicMock, patch, call
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.repositories.linked_account import LinkedAccountRepository
from backend.models.user import LinkedAccount
from backend.models.base import PlatformType
from backend.utils.encryption import encrypt_token, decrypt_token


class TestLinkedAccountRepository(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test"""
        self.db = MagicMock(spec=Session)
        self.repo = LinkedAccountRepository()
        
        # Create mock linked account
        self.mock_account = MagicMock(spec=LinkedAccount)
        self.mock_account.id = 1
        self.mock_account.child_profile_id = 101
        self.mock_account.platform = "youtube"
        self.mock_account.platform_account_id = "account123"
        self.mock_account.account_name = "Test Account"
        self.mock_account.access_token = b"encrypted_access_token"
        self.mock_account.refresh_token = b"encrypted_refresh_token"
        self.mock_account.token_expiry = datetime.now() + timedelta(hours=1)
        self.mock_account.last_scan_at = datetime.now() - timedelta(days=1)
        self.mock_account.is_active = True
        
        # Create a second mock account for the same child
        self.mock_account2 = MagicMock(spec=LinkedAccount)
        self.mock_account2.id = 2
        self.mock_account2.child_profile_id = 101
        self.mock_account2.platform = "youtube"
        self.mock_account2.platform_account_id = "account456"
        self.mock_account2.account_name = "Test Account 2"
        self.mock_account2.access_token = b"encrypted_access_token2"
        self.mock_account2.refresh_token = b"encrypted_refresh_token2"
        self.mock_account2.is_active = True
    
    def test_decrypt_account_tokens(self):
        """Test decryption of account tokens"""
        # Arrange
        account = MagicMock(spec=LinkedAccount)
        account.access_token = b"encrypted_access_token"
        account.refresh_token = b"encrypted_refresh_token"
        
        # Act
        with patch('backend.repositories.linked_account.decrypt_token') as mock_decrypt:
            mock_decrypt.side_effect = ["decrypted_access_token", "decrypted_refresh_token"]
            result = self.repo._decrypt_account_tokens(account)
        
        # Assert
        self.assertEqual(mock_decrypt.call_count, 2)
        self.assertEqual(account.access_token, "decrypted_access_token")
        self.assertEqual(account.refresh_token, "decrypted_refresh_token")
        self.assertEqual(result, account)
    
    def test_decrypt_account_tokens_string_tokens(self):
        """Test decryption when tokens are strings instead of bytes"""
        # Arrange
        account = MagicMock(spec=LinkedAccount)
        account.access_token = "encrypted_access_token_string"
        account.refresh_token = "encrypted_refresh_token_string"
        
        # Act
        with patch('backend.repositories.linked_account.decrypt_token') as mock_decrypt:
            mock_decrypt.side_effect = ["decrypted_access_token", "decrypted_refresh_token"]
            result = self.repo._decrypt_account_tokens(account)
        
        # Assert
        self.assertEqual(mock_decrypt.call_count, 2)
        mock_decrypt.assert_any_call(b"encrypted_access_token_string")
        mock_decrypt.assert_any_call(b"encrypted_refresh_token_string")
        self.assertEqual(account.access_token, "decrypted_access_token")
        self.assertEqual(account.refresh_token, "decrypted_refresh_token")
        self.assertEqual(result, account)
    
    def test_decrypt_account_tokens_none(self):
        """Test that None account returns None"""
        # Act
        result = self.repo._decrypt_account_tokens(None)
        
        # Assert
        self.assertIsNone(result)
    
    def test_decrypt_account_tokens_no_tokens(self):
        """Test decryption when tokens are None"""
        # Arrange
        account = MagicMock(spec=LinkedAccount)
        account.access_token = None
        account.refresh_token = None
        
        # Act
        result = self.repo._decrypt_account_tokens(account)
        
        # Assert
        self.assertEqual(result, account)
    
    @patch.object(LinkedAccountRepository, '_decrypt_account_tokens')
    def test_get(self, mock_decrypt):
        """Test getting a linked account by ID with decryption"""
        # Arrange
        with patch.object(BaseRepository, 'get') as mock_super_get:
            mock_super_get.return_value = self.mock_account
            mock_decrypt.return_value = self.mock_account
            
            # Act
            result = self.repo.get(self.db, 1)
            
            # Assert
            mock_super_get.assert_called_once_with(self.db, 1)
            mock_decrypt.assert_called_once_with(self.mock_account)
            self.assertEqual(result, self.mock_account)
    
    def test_get_by_platform_id(self):
        """Test getting a linked account by platform ID with decryption"""
        # Arrange
        query_mock = self.db.query.return_value
        filter_mock = query_mock.filter.return_value
        filter_mock.first.return_value = self.mock_account
        
        # Act
        with patch.object(LinkedAccountRepository, '_decrypt_account_tokens') as mock_decrypt:
            mock_decrypt.return_value = self.mock_account
            result = self.repo.get_by_platform_id(self.db, "youtube", "account123")
        
        # Assert
        self.db.query.assert_called_once_with(LinkedAccount)
        query_mock.filter.assert_called_once()
        filter_mock.first.assert_called_once()
        mock_decrypt.assert_called_once_with(self.mock_account)
        self.assertEqual(result, self.mock_account)
    
    def test_get_linked_accounts_for_child(self):
        """Test getting linked accounts for a child profile"""
        # Arrange
        query_mock = self.db.query.return_value
        filter_mock = query_mock.filter.return_value
        filter_active_mock = filter_mock.filter.return_value
        filter_active_mock.all.return_value = [self.mock_account, self.mock_account2]
        
        # Act
        with patch.object(LinkedAccountRepository, '_decrypt_account_tokens') as mock_decrypt:
            mock_decrypt.side_effect = lambda x: x  # Return the input unchanged
            result = self.repo.get_linked_accounts_for_child(self.db, 101)
        
        # Assert
        self.db.query.assert_called_once_with(LinkedAccount)
        query_mock.filter.assert_called_once()
        filter_mock.filter.assert_called_once()
        filter_active_mock.all.assert_called_once()
        self.assertEqual(mock_decrypt.call_count, 2)
        self.assertEqual(len(result), 2)
        self.assertIn(self.mock_account, result)
        self.assertIn(self.mock_account2, result)
    
    def test_get_linked_accounts_for_child_with_platform(self):
        """Test getting linked accounts for a child profile with platform filter"""
        # Arrange
        query_mock = self.db.query.return_value
        filter_child_mock = query_mock.filter.return_value
        filter_platform_mock = filter_child_mock.filter.return_value
        filter_active_mock = filter_platform_mock.filter.return_value
        filter_active_mock.all.return_value = [self.mock_account, self.mock_account2]
        
        # Act
        with patch.object(LinkedAccountRepository, '_decrypt_account_tokens') as mock_decrypt:
            mock_decrypt.side_effect = lambda x: x  # Return the input unchanged
            result = self.repo.get_linked_accounts_for_child(self.db, 101, platform="youtube")
        
        # Assert
        self.db.query.assert_called_once_with(LinkedAccount)
        query_mock.filter.assert_called_once()
        filter_child_mock.filter.assert_called_once()
        filter_platform_mock.filter.assert_called_once()
        filter_active_mock.all.assert_called_once()
        self.assertEqual(mock_decrypt.call_count, 2)
        self.assertEqual(len(result), 2)
    
    def test_get_linked_accounts_for_child_include_inactive(self):
        """Test getting linked accounts for a child profile including inactive"""
        # Arrange
        query_mock = self.db.query.return_value
        filter_child_mock = query_mock.filter.return_value
        filter_child_mock.all.return_value = [self.mock_account, self.mock_account2]
        
        # Act
        with patch.object(LinkedAccountRepository, '_decrypt_account_tokens') as mock_decrypt:
            mock_decrypt.side_effect = lambda x: x  # Return the input unchanged
            result = self.repo.get_linked_accounts_for_child(self.db, 101, active_only=False)
        
        # Assert
        self.db.query.assert_called_once_with(LinkedAccount)
        query_mock.filter.assert_called_once()
        filter_child_mock.all.assert_called_once()
        self.assertEqual(mock_decrypt.call_count, 2)
        self.assertEqual(len(result), 2)
    
    @patch('backend.repositories.linked_account.encrypt_token')
    @patch.object(BaseRepository, 'create')
    @patch.object(LinkedAccountRepository, '_decrypt_account_tokens')
    def test_create_dict_input(self, mock_decrypt, mock_super_create, mock_encrypt):
        """Test creating a linked account with dict input"""
        # Arrange
        account_data = {
            "child_profile_id": 101,
            "platform": "youtube",
            "platform_account_id": "account123",
            "account_name": "Test Account",
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token"
        }
        mock_encrypt.side_effect = [b"encrypted_access_token", b"encrypted_refresh_token"]
        mock_super_create.return_value = self.mock_account
        mock_decrypt.return_value = self.mock_account
        
        # Act
        result = self.repo.create(self.db, obj_in=account_data)
        
        # Assert
        self.assertEqual(mock_encrypt.call_count, 2)
        mock_encrypt.assert_any_call("test_access_token")
        mock_encrypt.assert_any_call("test_refresh_token")
        
        expected_data = account_data.copy()
        expected_data["access_token"] = b"encrypted_access_token"
        expected_data["refresh_token"] = b"encrypted_refresh_token"
        
        mock_super_create.assert_called_once_with(self.db, obj_in=expected_data)
        mock_decrypt.assert_called_once_with(self.mock_account)
        self.assertEqual(result, self.mock_account)
    
    @patch('backend.repositories.linked_account.encrypt_token')
    @patch.object(BaseRepository, 'create')
    @patch.object(LinkedAccountRepository, '_decrypt_account_tokens')
    def test_create_pydantic_input(self, mock_decrypt, mock_super_create, mock_encrypt):
        """Test creating a linked account with Pydantic model input"""
        # Arrange
        class AccountCreate(BaseModel):
            child_profile_id: int
            platform: str
            platform_account_id: str
            account_name: str
            access_token: str
            refresh_token: str
        
        account_data = AccountCreate(
            child_profile_id=101,
            platform="youtube",
            platform_account_id="account123",
            account_name="Test Account",
            access_token="test_access_token",
            refresh_token="test_refresh_token"
        )
        
        mock_encrypt.side_effect = [b"encrypted_access_token", b"encrypted_refresh_token"]
        mock_super_create.return_value = self.mock_account
        mock_decrypt.return_value = self.mock_account
        
        # Act
        result = self.repo.create(self.db, obj_in=account_data)
        
        # Assert
        self.assertEqual(mock_encrypt.call_count, 2)
        mock_super_create.assert_called_once()
        mock_decrypt.assert_called_once_with(self.mock_account)
        self.assertEqual(result, self.mock_account)
    
    @patch('backend.repositories.linked_account.encrypt_token')
    @patch.object(LinkedAccountRepository, 'get')
    @patch.object(BaseRepository, 'update')
    def test_update_tokens(self, mock_super_update, mock_get, mock_encrypt):
        """Test updating tokens for a linked account"""
        # Arrange
        mock_get.return_value = self.mock_account
        mock_encrypt.side_effect = [b"new_encrypted_access", b"new_encrypted_refresh"]
        mock_super_update.return_value = self.mock_account
        
        new_expiry = datetime.now() + timedelta(hours=2)
        
        # Act
        with patch.object(LinkedAccountRepository, '_decrypt_account_tokens') as mock_decrypt:
            mock_decrypt.return_value = self.mock_account
            result = self.repo.update_tokens(
                self.db, 1, "new_access_token", "new_refresh_token", new_expiry
            )
        
        # Assert
        mock_get.assert_called_once_with(self.db, 1)
        mock_encrypt.assert_any_call("new_access_token")
        mock_encrypt.assert_any_call("new_refresh_token")
        
        expected_update = {
            "access_token": b"new_encrypted_access",
            "refresh_token": b"new_encrypted_refresh",
            "token_expiry": new_expiry
        }
        
        mock_super_update.assert_called_once_with(self.db, db_obj=self.mock_account, obj_in=expected_update)
        mock_decrypt.assert_called_once_with(self.mock_account)
        self.assertEqual(result, self.mock_account)
    
    @patch('backend.repositories.linked_account.encrypt_token')
    @patch.object(LinkedAccountRepository, 'get')
    @patch.object(BaseRepository, 'update')
    def test_update_tokens_partial(self, mock_super_update, mock_get, mock_encrypt):
        """Test updating only access token"""
        # Arrange
        mock_get.return_value = self.mock_account
        mock_encrypt.return_value = b"new_encrypted_access"
        mock_super_update.return_value = self.mock_account
        
        # Act
        with patch.object(LinkedAccountRepository, '_decrypt_account_tokens') as mock_decrypt:
            mock_decrypt.return_value = self.mock_account
            result = self.repo.update_tokens(
                self.db, 1, "new_access_token"
            )
        
        # Assert
        mock_get.assert_called_once_with(self.db, 1)
        mock_encrypt.assert_called_once_with("new_access_token")
        
        expected_update = {
            "access_token": b"new_encrypted_access"
        }
        
        mock_super_update.assert_called_once_with(self.db, db_obj=self.mock_account, obj_in=expected_update)
        mock_decrypt.assert_called_once_with(self.mock_account)
        self.assertEqual(result, self.mock_account)
    
    @patch.object(LinkedAccountRepository, 'get')
    def test_update_tokens_nonexistent(self, mock_get):
        """Test updating tokens for a nonexistent account"""
        # Arrange
        mock_get.return_value = None
        
        # Act
        result = self.repo.update_tokens(
            self.db, 999, "new_access_token"
        )
        
        # Assert
        mock_get.assert_called_once_with(self.db, 999)
        self.assertIsNone(result)
    
    @patch.object(BaseRepository, 'update')
    @patch.object(LinkedAccountRepository, '_decrypt_account_tokens')
    def test_deactivate_account(self, mock_decrypt, mock_super_deactivate):
        """Test deactivating a linked account"""
        # Arrange
        mock_super_deactivate.return_value = self.mock_account
        mock_decrypt.return_value = self.mock_account
        
        # Act
        result = self.repo.deactivate_account(self.db, 1)
        
        # Assert
        mock_super_deactivate.assert_called_once_with(self.db, 1)
        mock_decrypt.assert_called_once_with(self.mock_account)
        self.assertEqual(result, self.mock_account)
    
    @patch.object(BaseRepository, 'update_last_scan')
    @patch.object(LinkedAccountRepository, '_decrypt_account_tokens')
    def test_update_last_scan(self, mock_decrypt, mock_super_update_scan):
        """Test updating last scan timestamp"""
        # Arrange
        mock_super_update_scan.return_value = self.mock_account
        mock_decrypt.return_value = self.mock_account
        
        # Act
        result = self.repo.update_last_scan(self.db, 1)
        
        # Assert
        mock_super_update_scan.assert_called_once_with(self.db, 1)
        mock_decrypt.assert_called_once_with(self.mock_account)
        self.assertEqual(result, self.mock_account)


if __name__ == '__main__':
    unittest.main()