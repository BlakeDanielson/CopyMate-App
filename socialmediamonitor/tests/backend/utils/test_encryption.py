import unittest
from unittest.mock import patch, MagicMock
import os
import sys
from typing import Optional

# Add missing Optional import to fixed in the module later
from cryptography.fernet import Fernet, InvalidToken

# We need to patch the environment settings before importing the module
# to prevent validation errors when EncryptionSettings is instantiated
os.environ['ENCRYPTION_KEY'] = Fernet.generate_key().decode()

# Import the module to test
from backend.utils.encryption import encrypt_token, decrypt_token, EncryptionSettings, fernet

class TestEncryption(unittest.TestCase):
    
    def test_encryption_settings_loads_key(self):
        """Test that EncryptionSettings loads the encryption key from environment"""
        # Arrange & Act - already done during import
        settings = EncryptionSettings()
        
        # Assert
        self.assertEqual(settings.encryption_key, os.environ['ENCRYPTION_KEY'])
        self.assertIsNotNone(settings.encryption_key)
    
    def test_encrypt_token_success(self):
        """Test successful token encryption"""
        # Arrange
        test_token = "test_oauth_token"
        
        # Act
        result = encrypt_token(test_token)
        
        # Assert
        self.assertIsNotNone(result)
        self.assertIsInstance(result, bytes)
        
        # Verify we can decrypt it
        decrypted = Fernet(os.environ['ENCRYPTION_KEY'].encode()).decrypt(result).decode()
        self.assertEqual(decrypted, test_token)
    
    @patch('backend.utils.encryption.fernet', None)
    def test_encrypt_token_none_fernet(self):
        """Test encryption when fernet is None"""
        # Act
        result = encrypt_token("test_token")
        
        # Assert
        self.assertIsNone(result)
    
    @patch('backend.utils.encryption.fernet')
    def test_encrypt_token_exception(self, mock_fernet):
        """Test encryption with exception"""
        # Arrange
        mock_fernet.encrypt.side_effect = Exception("Test exception")
        
        # Act
        result = encrypt_token("test_token")
        
        # Assert
        self.assertIsNone(result)
    
    def test_decrypt_token_success(self):
        """Test successful token decryption"""
        # Arrange
        test_token = "test_oauth_token"
        encrypted_token = Fernet(os.environ['ENCRYPTION_KEY'].encode()).encrypt(test_token.encode())
        
        # Act
        result = decrypt_token(encrypted_token)
        
        # Assert
        self.assertEqual(result, test_token)
    
    @patch('backend.utils.encryption.fernet', None)
    def test_decrypt_token_none_fernet(self):
        """Test decryption when fernet is None"""
        # Act
        result = decrypt_token(b"encrypted_data")
        
        # Assert
        self.assertIsNone(result)
    
    @patch('backend.utils.encryption.fernet')
    def test_decrypt_token_exception(self, mock_fernet):
        """Test decryption with exception"""
        # Arrange
        mock_fernet.decrypt.side_effect = InvalidToken("Invalid token")
        
        # Act
        result = decrypt_token(b"invalid_encrypted_data")
        
        # Assert
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()