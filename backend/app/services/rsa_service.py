from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import scrypt
from typing import Tuple, Dict
import base64
import json


class RSAService:
    """
    RSA cryptographic service for classical encryption demonstration.
    
    IMPORTANT SECURITY NOTE:
    RSA is vulnerable to Shor's algorithm on quantum computers.
    Shor's algorithm can factor large integers exponentially faster
    than classical algorithms, breaking RSA's security foundation.
    
    This module is provided for educational comparison with post-quantum
    cryptography (Kyber) to demonstrate the quantum threat to classical
    public-key cryptography.
    """
    
    @staticmethod
    def generate_keypair(key_size: int = 2048) -> Tuple[str, str]:
        """
        Generate RSA keypair.
        
        RSA Workflow:
        1. Generate two large prime numbers p and q
        2. Compute n = p * q (modulus)
        3. Compute φ(n) = (p-1) * (q-1) (Euler's totient)
        4. Choose public exponent e (typically 65537)
        5. Compute private exponent d = e^(-1) mod φ(n)
        6. Public key: (e, n), Private key: (d, n)
        
        Args:
            key_size: Key size in bits (default: 2048)
                      Common sizes: 1024 (insecure), 2048 (current standard),
                      4096 (future-proof but slow)
        
        Returns:
            Tuple of (private_key_pem, public_key_pem) in PEM format
        
        Raises:
            ValueError: If key_size is invalid
        """
        if key_size < 1024:
            raise ValueError("Key size must be at least 1024 bits")
        
        # Generate RSA key pair
        key = RSA.generate(key_size)
        
        # Export keys in PEM format
        private_key = key.export_key()
        public_key = key.publickey().export_key()
        
        return private_key.decode('utf-8'), public_key.decode('utf-8')
    
    @staticmethod
    def encrypt_message(message: str, public_key_pem: str) -> str:
        """
        Encrypt a message using RSA public key.
        
        RSA Encryption Workflow:
        1. Convert message to bytes
        2. Use PKCS#1 OAEP padding scheme for security
        3. Encrypt with public key: c = m^e mod n
        4. Return base64-encoded ciphertext
        
        Note: RSA can only encrypt data smaller than the key size.
        For larger messages, hybrid encryption is used (encrypt AES key with RSA).
        
        Args:
            message: Plain text message to encrypt
            public_key_pem: Public key in PEM format
        
        Returns:
            Base64-encoded encrypted message
        
        Raises:
            ValueError: If message is too long for RSA encryption
        """
        # Load public key
        public_key = RSA.import_key(public_key_pem)
        
        # Create cipher with OAEP padding
        cipher = PKCS1_OAEP.new(public_key)
        
        # Convert message to bytes
        message_bytes = message.encode('utf-8')
        
        # Check message size
        max_message_size = (public_key.size_in_bytes() - 42)  # OAEP overhead
        if len(message_bytes) > max_message_size:
            raise ValueError(
                f"Message too long for RSA encryption. "
                f"Maximum size: {max_message_size} bytes, "
                f"Provided: {len(message_bytes)} bytes"
            )
        
        # Encrypt message
        ciphertext = cipher.encrypt(message_bytes)
        
        # Return base64-encoded ciphertext
        return base64.b64encode(ciphertext).decode('utf-8')
    
    @staticmethod
    def decrypt_message(ciphertext_b64: str, private_key_pem: str) -> str:
        """
        Decrypt a message using RSA private key.
        
        RSA Decryption Workflow:
        1. Decode base64 ciphertext
        2. Load private key
        3. Use PKCS#1 OAEP padding scheme
        4. Decrypt with private key: m = c^d mod n
        5. Convert bytes back to string
        
        Args:
            ciphertext_b64: Base64-encoded encrypted message
            private_key_pem: Private key in PEM format
        
        Returns:
            Decrypted plain text message
        
        Raises:
            ValueError: If decryption fails
        """
        # Load private key
        private_key = RSA.import_key(private_key_pem)
        
        # Create cipher with OAEP padding
        cipher = PKCS1_OAEP.new(private_key)
        
        # Decode base64 ciphertext
        ciphertext = base64.b64decode(ciphertext_b64)
        
        # Decrypt message
        message_bytes = cipher.decrypt(ciphertext)
        
        # Convert bytes to string
        return message_bytes.decode('utf-8')
    
    @staticmethod
    def generate_aes_key(key_size: int = 32) -> bytes:
        """
        Generate a random AES session key.
        
        AES (Advanced Encryption Standard) is a symmetric encryption algorithm
        used for encrypting the actual message data. RSA is used only to
        securely exchange the AES session key.
        
        Args:
            key_size: Key size in bytes (default: 32 for AES-256)
                      16 bytes = AES-128, 32 bytes = AES-256
        
        Returns:
            Random AES key as bytes
        """
        return get_random_bytes(key_size)
    
    @staticmethod
    def encrypt_aes_key_with_rsa(aes_key: bytes, public_key_pem: str) -> str:
        """
        Encrypt an AES session key using RSA public key.
        
        This is the hybrid encryption approach:
        1. Generate random AES session key
        2. Encrypt the AES key with RSA (public key)
        3. Encrypt the actual message with AES (using the session key)
        4. Send both encrypted AES key and encrypted message
        
        This allows encrypting messages of any size while maintaining
        the security of public-key cryptography.
        
        Args:
            aes_key: AES session key as bytes
            public_key_pem: Public key in PEM format
        
        Returns:
            Base64-encoded encrypted AES key
        """
        # Load public key
        public_key = RSA.import_key(public_key_pem)
        
        # Create cipher with OAEP padding
        cipher = PKCS1_OAEP.new(public_key)
        
        # Encrypt AES key
        encrypted_key = cipher.encrypt(aes_key)
        
        # Return base64-encoded encrypted key
        return base64.b64encode(encrypted_key).decode('utf-8')
    
    @staticmethod
    def decrypt_aes_key_with_rsa(encrypted_key_b64: str, private_key_pem: str) -> bytes:
        """
        Decrypt an AES session key using RSA private key.
        
        Args:
            encrypted_key_b64: Base64-encoded encrypted AES key
            private_key_pem: Private key in PEM format
        
        Returns:
            Decrypted AES session key as bytes
        """
        # Load private key
        private_key = RSA.import_key(private_key_pem)
        
        # Create cipher with OAEP padding
        cipher = PKCS1_OAEP.new(private_key)
        
        # Decode base64 encrypted key
        encrypted_key = base64.b64decode(encrypted_key_b64)
        
        # Decrypt AES key
        aes_key = cipher.decrypt(encrypted_key)
        
        return aes_key
    
    @staticmethod
    def get_key_info(public_key_pem: str) -> Dict:
        """
        Get information about an RSA public key.
        
        Args:
            public_key_pem: Public key in PEM format
        
        Returns:
            Dictionary with key information (size, exponent, etc.)
        """
        public_key = RSA.import_key(public_key_pem)
        
        return {
            "key_size_bits": public_key.size_in_bits(),
            "key_size_bytes": public_key.size_in_bytes(),
            "public_exponent": public_key.e,
            "modulus_size_bits": public_key.n.bit_length()
        }
    
    @staticmethod
    def explain_quantum_vulnerability() -> Dict:
        """
        Explain why RSA is vulnerable to quantum computing.
        
        Returns:
            Dictionary explaining the quantum threat to RSA
        """
        return {
            "algorithm": "RSA",
            "security_basis": "Integer factorization problem",
            "classical_security": "Factoring large integers is computationally infeasible",
            "quantum_threat": "Shor's algorithm can factor integers exponentially faster",
            "shor_algorithm_complexity": "O((log n)^3) quantum operations",
            "classical_algorithm_complexity": "O(exp((64/9)^(1/3) (log n)^(1/3) (log log n)^(2/3)))",
            "impact": "All RSA-encrypted data can be decrypted once quantum computers are available",
            "mitigation": "Use post-quantum cryptography (e.g., Kyber) for key exchange",
            "harvest_now_decrypt_later": "Attackers can store RSA-encrypted data now and decrypt it later when quantum computers become available"
        }
