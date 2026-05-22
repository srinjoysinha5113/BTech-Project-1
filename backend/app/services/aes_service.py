from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from typing import Tuple, Dict
import base64
import json


class AESService:
    """
    AES-256-GCM encryption service for symmetric encryption.
    
    AES (Advanced Encryption Standard) is a symmetric encryption algorithm
    that uses the same key for encryption and decryption. GCM (Galois/Counter Mode)
    provides both confidentiality and integrity through authentication.
    
    Security Features:
    - 256-bit key size (AES-256) for maximum security
    - GCM mode provides authenticated encryption
    - Unique nonce for each encryption operation
    - Authentication tag to verify data integrity
    
    AES is quantum-resistant for symmetric encryption because Grover's algorithm
    only provides a quadratic speedup, effectively halving the key strength.
    AES-256 would still provide 128-bit security against quantum attacks.
    """
    
    @staticmethod
    def generate_nonce() -> bytes:
        """
        Generate a random nonce (number used once).
        
        In GCM mode, the nonce must be unique for each encryption operation
        with the same key. Reusing a nonce with the same key compromises security.
        
        GCM recommends a 12-byte (96-bit) nonce for optimal performance.
        
        Returns:
            Random 12-byte nonce
        """
        return get_random_bytes(12)
    
    @staticmethod
    def generate_key(key_size: int = 32) -> bytes:
        """
        Generate a random AES key.
        
        Args:
            key_size: Key size in bytes (default: 32 for AES-256)
                      16 bytes = AES-128, 24 bytes = AES-192, 32 bytes = AES-256
        
        Returns:
            Random AES key
        """
        return get_random_bytes(key_size)
    
    @staticmethod
    def encrypt(plaintext: str, key: bytes, nonce: bytes = None) -> Dict[str, str]:
        """
        Encrypt plaintext using AES-256-GCM.
        
        AES-GCM Encryption Workflow:
        1. Generate or use provided nonce (must be unique per encryption)
        2. Initialize AES cipher in GCM mode with key and nonce
        3. Encrypt the plaintext
        4. Generate authentication tag (MAC) for integrity verification
        5. Return ciphertext, nonce, and authentication tag
        
        The authentication tag ensures that any modification of the
        ciphertext will be detected during decryption.
        
        Args:
            plaintext: Plain text message to encrypt
            key: AES key (16, 24, or 32 bytes)
            nonce: Optional nonce (12 bytes). If not provided, a random one is generated.
        
        Returns:
            Dictionary containing:
            - ciphertext: Base64-encoded encrypted data
            - nonce: Base64-encoded nonce
            - auth_tag: Base64-encoded authentication tag
        
        Raises:
            ValueError: If key size is invalid or nonce is invalid
        """
        # Validate key size
        if len(key) not in [16, 24, 32]:
            raise ValueError(
                f"Invalid key size: {len(key)} bytes. "
                "Key must be 16, 24, or 32 bytes for AES-128, AES-192, or AES-256."
            )
        
        # Generate nonce if not provided
        if nonce is None:
            nonce = AESService.generate_nonce()
        
        # Validate nonce size
        if len(nonce) != 12:
            raise ValueError(
                f"Invalid nonce size: {len(nonce)} bytes. "
                "Nonce must be 12 bytes for GCM mode."
            )
        
        # Convert plaintext to bytes
        plaintext_bytes = plaintext.encode('utf-8')
        
        # Initialize cipher in GCM mode
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        
        # Encrypt and get authentication tag
        ciphertext, auth_tag = cipher.encrypt_and_digest(plaintext_bytes)
        
        # Return base64-encoded values
        return {
            "ciphertext": base64.b64encode(ciphertext).decode('utf-8'),
            "nonce": base64.b64encode(nonce).decode('utf-8'),
            "auth_tag": base64.b64encode(auth_tag).decode('utf-8')
        }
    
    @staticmethod
    def decrypt(ciphertext_b64: str, key: bytes, nonce_b64: str, auth_tag_b64: str) -> str:
        """
        Decrypt ciphertext using AES-256-GCM.
        
        AES-GCM Decryption Workflow:
        1. Decode base64-encoded ciphertext, nonce, and auth tag
        2. Initialize AES cipher in GCM mode with key and nonce
        3. Decrypt the ciphertext
        4. Verify authentication tag (integrity check)
        5. Return plaintext if verification succeeds
        
        The authentication tag verification ensures that:
        - The ciphertext has not been tampered with
        - The correct key was used for decryption
        - The nonce matches what was used for encryption
        
        Args:
            ciphertext_b64: Base64-encoded encrypted data
            key: AES key (must match the key used for encryption)
            nonce_b64: Base64-encoded nonce (must match the nonce used for encryption)
            auth_tag_b64: Base64-encoded authentication tag
        
        Returns:
            Decrypted plain text message
        
        Raises:
            ValueError: If key size is invalid, nonce is invalid, or authentication fails
        """
        # Validate key size
        if len(key) not in [16, 24, 32]:
            raise ValueError(
                f"Invalid key size: {len(key)} bytes. "
                "Key must be 16, 24, or 32 bytes for AES-128, AES-192, or AES-256."
            )
        
        # Decode base64 values
        ciphertext = base64.b64decode(ciphertext_b64)
        nonce = base64.b64decode(nonce_b64)
        auth_tag = base64.b64decode(auth_tag_b64)
        
        # Validate nonce size
        if len(nonce) != 12:
            raise ValueError(
                f"Invalid nonce size: {len(nonce)} bytes. "
                "Nonce must be 12 bytes for GCM mode."
            )
        
        # Initialize cipher in GCM mode
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        
        try:
            # Decrypt and verify authentication tag
            plaintext_bytes = cipher.decrypt_and_verify(ciphertext, auth_tag)
            
            # Convert bytes to string
            return plaintext_bytes.decode('utf-8')
        
        except ValueError as e:
            raise ValueError(
                f"Authentication failed: {str(e)}. "
                "This could indicate tampering, wrong key, or wrong nonce."
            )
    
    @staticmethod
    def encrypt_with_associated_data(
        plaintext: str,
        key: bytes,
        associated_data: str = None,
        nonce: bytes = None
    ) -> Dict[str, str]:
        """
        Encrypt plaintext with additional authenticated data (AAD).
        
        AAD is data that is authenticated but not encrypted.
        It's useful for metadata like message IDs, timestamps, etc.
        The authentication tag covers both the ciphertext and AAD.
        
        Args:
            plaintext: Plain text message to encrypt
            key: AES key
            associated_data: Optional additional data to authenticate
            nonce: Optional nonce
        
        Returns:
            Dictionary with ciphertext, nonce, and auth_tag
        """
        # Validate key size
        if len(key) not in [16, 24, 32]:
            raise ValueError(
                f"Invalid key size: {len(key)} bytes. "
                "Key must be 16, 24, or 32 bytes for AES-128, AES-192, or AES-256."
            )
        
        # Generate nonce if not provided
        if nonce is None:
            nonce = AESService.generate_nonce()
        
        # Convert plaintext to bytes
        plaintext_bytes = plaintext.encode('utf-8')
        
        # Initialize cipher in GCM mode
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        
        # Add associated data if provided
        if associated_data:
            cipher.update(associated_data.encode('utf-8'))
        
        # Encrypt and get authentication tag
        ciphertext, auth_tag = cipher.encrypt_and_digest(plaintext_bytes)
        
        # Return base64-encoded values
        return {
            "ciphertext": base64.b64encode(ciphertext).decode('utf-8'),
            "nonce": base64.b64encode(nonce).decode('utf-8'),
            "auth_tag": base64.b64encode(auth_tag).decode('utf-8')
        }
    
    @staticmethod
    def decrypt_with_associated_data(
        ciphertext_b64: str,
        key: bytes,
        nonce_b64: str,
        auth_tag_b64: str,
        associated_data: str = None
    ) -> str:
        """
        Decrypt ciphertext with additional authenticated data (AAD).
        
        Args:
            ciphertext_b64: Base64-encoded encrypted data
            key: AES key
            nonce_b64: Base64-encoded nonce
            auth_tag_b64: Base64-encoded authentication tag
            associated_data: Optional additional data that was authenticated
        
        Returns:
            Decrypted plain text message
        """
        # Validate key size
        if len(key) not in [16, 24, 32]:
            raise ValueError(
                f"Invalid key size: {len(key)} bytes. "
                "Key must be 16, 24, or 32 bytes for AES-128, AES-192, or AES-256."
            )
        
        # Decode base64 values
        ciphertext = base64.b64decode(ciphertext_b64)
        nonce = base64.b64decode(nonce_b64)
        auth_tag = base64.b64decode(auth_tag_b64)
        
        # Initialize cipher in GCM mode
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        
        # Add associated data if provided
        if associated_data:
            cipher.update(associated_data.encode('utf-8'))
        
        try:
            # Decrypt and verify authentication tag
            plaintext_bytes = cipher.decrypt_and_verify(ciphertext, auth_tag)
            
            # Convert bytes to string
            return plaintext_bytes.decode('utf-8')
        
        except ValueError as e:
            raise ValueError(
                f"Authentication failed: {str(e)}. "
                "This could indicate tampering, wrong key, wrong nonce, or wrong AAD."
            )
    
    @staticmethod
    def get_key_info(key: bytes) -> Dict:
        """
        Get information about an AES key.
        
        Args:
            key: AES key
        
        Returns:
            Dictionary with key information
        """
        key_size = len(key)
        
        if key_size == 16:
            variant = "AES-128"
            security_bits = 128
        elif key_size == 24:
            variant = "AES-192"
            security_bits = 192
        elif key_size == 32:
            variant = "AES-256"
            security_bits = 256
        else:
            variant = "Invalid"
            security_bits = 0
        
        return {
            "key_size_bytes": key_size,
            "variant": variant,
            "security_bits": security_bits,
            "quantum_resistant": True,
            "quantum_security_bits": security_bits // 2,  # Grover's algorithm halves security
            "mode": "GCM (Galois/Counter Mode)",
            "provides_authentication": True
        }
    
    @staticmethod
    def explain_quantum_resistance() -> Dict:
        """
        Explain why AES is quantum-resistant.
        
        Returns:
            Dictionary explaining AES quantum resistance
        """
        return {
            "algorithm": "AES (Advanced Encryption Standard)",
            "security_basis": "Substitution-permutation network",
            "classical_security": "Brute-force attack requires 2^n operations",
            "quantum_threat": "Grover's algorithm provides quadratic speedup",
            "grover_algorithm_complexity": "O(2^(n/2)) quantum operations",
            "classical_algorithm_complexity": "O(2^n) operations",
            "impact": "AES-256 provides 128-bit security against quantum attacks",
            "mitigation": "Use AES-256 for long-term quantum resistance",
            "current_status": "AES is considered quantum-resistant for symmetric encryption",
            "recommendation": "AES-256 is recommended for post-quantum security"
        }
