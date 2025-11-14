"""
AES-256-GCM Encryption Module
Secure encryption/decryption using PBKDF2 and AES-GCM.
"""

import os
import struct
from typing import Tuple
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag


class DecryptionError(Exception):
    """Custom exception for decryption failures."""
    pass


class AESGCMEncryptor:
    """
    AES-256-GCM encryptor using PBKDF2 for key derivation.
    """
    
    # Constants
    SALT_SIZE = 16
    NONCE_SIZE = 12
    AUTH_TAG_SIZE = 16
    PBKDF2_ITERATIONS = 100000
    
    def _generate_salt(self) -> bytes:
        """Generate cryptographically secure random salt."""
        return os.urandom(self.SALT_SIZE)
    
    def _generate_nonce(self) -> bytes:
        """Generate cryptographically secure random nonce."""
        return os.urandom(self.NONCE_SIZE)
    
    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """Derive AES-256 key from password using PBKDF2-HMAC-SHA256."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=self.PBKDF2_ITERATIONS,
        )
        return kdf.derive(password.encode('utf-8'))
    
    def aes_encrypt(self, plaintext: bytes, password: str) -> bytes:
        """
        Encrypt plaintext using AES-256-GCM.
        
        Args:
            plaintext: Data to encrypt
            password: Password for key derivation
            
        Returns:
            bytes: Combined data [salt(16)][nonce(12)][ciphertext][auth_tag(16)]
        """
        if not password:
            raise ValueError("Password cannot be empty")
        
        salt = self._generate_salt()
        nonce = self._generate_nonce()
        
        key = self._derive_key(password, salt)
        
        aesgcm = AESGCM(key)
        ciphertext_with_tag = aesgcm.encrypt(nonce, plaintext, None)
        
        ciphertext = ciphertext_with_tag[:-self.AUTH_TAG_SIZE]
        auth_tag = ciphertext_with_tag[-self.AUTH_TAG_SIZE:]
        
        encrypted_data = salt + nonce + ciphertext + auth_tag
        
        self._secure_wipe(key)
        
        return encrypted_data
    
    def aes_decrypt(self, encrypted_data: bytes, password: str) -> bytes:
        """
        Decrypt encrypted data using AES-256-GCM.
        
        Args:
            encrypted_data: Combined data [salt(16)][nonce(12)][ciphertext][auth_tag(16)]
            password: Password for key derivation
            
        Returns:
            bytes: Decrypted plaintext
            
        Raises:
            DecryptionError: If decryption fails
        """
        if not password:
            raise ValueError("Password cannot be empty")
        
        if len(encrypted_data) < 44:  # salt(16) + nonce(12) + auth_tag(16)
            raise DecryptionError("Encrypted data is too short")
        
        try:
            salt = encrypted_data[:self.SALT_SIZE]
            nonce = encrypted_data[self.SALT_SIZE:self.SALT_SIZE + self.NONCE_SIZE]
            ciphertext_with_tag = encrypted_data[self.SALT_SIZE + self.NONCE_SIZE:]
            
            key = self._derive_key(password, salt)
            aesgcm = AESGCM(key)
            plaintext = aesgcm.decrypt(nonce, ciphertext_with_tag, None)
            
            self._secure_wipe(key)
            return plaintext
            
        except InvalidTag as e:
            self._secure_wipe(key)
            raise DecryptionError("Decryption failed - wrong password or corrupted data") from e
        except Exception as e:
            self._secure_wipe(key)
            raise DecryptionError(f"Decryption failed: {str(e)}") from e
    
    def _secure_wipe(self, data: bytes) -> None:
        """Attempt to securely wipe sensitive data from memory."""
        if isinstance(data, bytearray):
            for i in range(len(data)):
                data[i] = 0


# Convenience functions
def aes_encrypt(plaintext: bytes, password: str) -> bytes:
    """Encrypt plaintext using AES-256-GCM."""
    encryptor = AESGCMEncryptor()
    return encryptor.aes_encrypt(plaintext, password)


def aes_decrypt(encrypted_data: bytes, password: str) -> bytes:
    """Decrypt encrypted data using AES-256-GCM."""
    encryptor = AESGCMEncryptor()
    return encryptor.aes_decrypt(encrypted_data, password)