import os
from typing import Optional
from cryptography.fernet import Fernet
from pydantic_settings import BaseSettings

class EncryptionSettings(BaseSettings):
    """Configuration settings for encryption."""
    encryption_key: str = os.getenv("ENCRYPTION_KEY")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Create settings instance
settings = EncryptionSettings()

# Initialize Fernet with the encryption key
# Ensure the key is base64-encoded and 32 bytes long
try:
    fernet = Fernet(settings.encryption_key)
except Exception as e:
    # Handle the case where the encryption key is missing or invalid
    print(f"Error initializing Fernet: {e}")
    # In a production environment, you might want to raise an exception or exit
    fernet = None # Or handle this more robustly

def encrypt_token(token: str) -> Optional[bytes]:
    """
    Encrypts a string token using Fernet.

    Args:
        token: The string token to encrypt.

    Returns:
        The encrypted token as bytes, or None if encryption is not configured.
    """
    if fernet is None:
        print("Encryption key not configured. Cannot encrypt.")
        return None
    try:
        return fernet.encrypt(token.encode())
    except Exception as e:
        print(f"Error encrypting token: {e}")
        return None

def decrypt_token(encrypted_token: bytes) -> Optional[str]:
    """
    Decrypts a Fernet-encrypted token.

    Args:
        encrypted_token: The encrypted token as bytes.

    Returns:
        The decrypted token as a string, or None if decryption fails or is not configured.
    """
    if fernet is None:
        print("Encryption key not configured. Cannot decrypt.")
        return None
    try:
        return fernet.decrypt(encrypted_token).decode()
    except Exception as e:
        print(f"Error decrypting token: {e}")
        return None

# Example usage (for testing purposes, remove in production)
# if __name__ == "__main__":
#     # Generate a key (run this once and set ENCRYPTION_KEY in your .env)
#     # key = Fernet.generate_key()
#     # print(f"Generated Key: {key.decode()}")

#     # Example encryption/decryption
#     # original_token = "your_sensitive_oauth_token_here"
#     # encrypted = encrypt_token(original_token)
#     # print(f"Original: {original_token}")
#     # print(f"Encrypted: {encrypted}")

#     # if encrypted:
#     #     decrypted = decrypt_token(encrypted)
#     #     print(f"Decrypted: {decrypted}")