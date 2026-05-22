from typing import Tuple, Dict
import base64
import hashlib
import os

try:
    from oqs import KeyEncapsulation
    OQS_AVAILABLE = True
except ImportError:
    OQS_AVAILABLE = False


class KyberService:
    """
    Kyber post-quantum key encapsulation mechanism (KEM) service.
    
    Kyber is a lattice-based post-quantum KEM selected by NIST in 2022
    as the standard for post-quantum key exchange. It's based on the
    Learning With Errors (LWE) problem over module lattices.
    
    Security Basis:
    - Based on the hardness of the Module-LWE problem
    - LWE is believed to be quantum-resistant (no known quantum algorithm solves it efficiently)
    - Security reduces to worst-case lattice problems
    
    Why Kyber is Quantum-Resistant:
    - Shor's algorithm doesn't apply to lattice-based problems
    - Best known quantum attacks only provide polynomial speedup
    - Grover's algorithm doesn't help with lattice problems
    - Security estimates account for quantum attacks
    
    Architecture:
    Kyber is a Key Encapsulation Mechanism (KEM):
    1. Key Generation: Generate public/private key pair
    2. Encapsulation: Client generates shared secret and ciphertext from public key
    3. Decapsulation: Server recovers shared secret from ciphertext using private key
    
    Hybrid Encryption Workflow:
    1. Server generates Kyber keypair
    2. Server publishes Kyber public key
    3. Client fetches Kyber public key
    4. Client encapsulates shared secret using Kyber
    5. Client encrypts message with AES using the shared secret
    6. Server decapsulates shared secret using Kyber
    7. Server decrypts message with AES using the shared secret
    
    Installation:
    To use actual post-quantum cryptography, install liboqs and oqs-python:
    1. Install dependencies: cmake, ninja, python3-dev
    2. Clone liboqs: git clone https://github.com/open-quantum-safe/liboqs.git
    3. Build liboqs: cd liboqs && mkdir build && cd build && cmake .. && make
    4. Install liboqs: sudo make install
    5. Install Python bindings: pip install oqs-python
    """
    
    @staticmethod
    def _check_oqs_available():
        """Check if oqs-python is available and raise error if not."""
        if not OQS_AVAILABLE:
            raise RuntimeError(
                "oqs-python is not installed. For actual post-quantum security, "
                "install liboqs and oqs-python from https://github.com/open-quantum-safe/liboqs"
            )
    
    @staticmethod
    def generate_keypair(variant: str = "Kyber512") -> Tuple[str, str]:
        """
        Generate Kyber keypair using actual oqs-python.
        
        Kyber Key Generation Workflow:
        1. Generate random matrix A from uniform distribution
        2. Generate random secret vectors s and e
        3. Compute public key: (pk = A*s + e, t)
        4. Private key: (sk = s)
        
        The security relies on the difficulty of recovering s from (A, pk).
        
        Args:
            variant: Kyber variant (Kyber512, Kyber768, Kyber1024)
                      Kyber512: ~128-bit quantum security
                      Kyber768: ~192-bit quantum security
                      Kyber1024: ~256-bit quantum security
        
        Returns:
            Tuple of (public_key_b64, secret_key_b64) in base64 format
        
        Raises:
            RuntimeError: If oqs-python is not installed
        """
        KyberService._check_oqs_available()
        
        kem = KeyEncapsulation(variant)
        public_key, secret_key = kem.generate_keypair()
        
        return (
            base64.b64encode(public_key).decode('utf-8'),
            base64.b64encode(secret_key).decode('utf-8')
        )
    
    @staticmethod
    def encapsulate(public_key_b64: str, variant: str = "Kyber512") -> Tuple[str, str]:
        """
        Encapsulate shared secret using Kyber public key with actual oqs-python.
        
        Kyber Encapsulation Workflow:
        1. Generate random message vector m
        2. Generate random error vectors e1, e2
        3. Compute ciphertext: (u = A^T*m + e1, v = t^T*m + e2 + encode(m))
        4. Derive shared secret from ciphertext and message
        
        The client generates the shared secret and ciphertext, which
        can only be decapsulated by the holder of the private key.
        
        Args:
            public_key_b64: Base64-encoded Kyber public key
            variant: Kyber variant
        
        Returns:
            Tuple of (ciphertext_b64, shared_secret_b64) in base64 format
        
        Raises:
            RuntimeError: If oqs-python is not installed
        """
        KyberService._check_oqs_available()
        
        kem = KeyEncapsulation(variant)
        public_key = base64.b64decode(public_key_b64)
        kem.import_public_key(public_key)
        ciphertext, shared_secret = kem.encap_secret()
        
        return (
            base64.b64encode(ciphertext).decode('utf-8'),
            base64.b64encode(shared_secret).decode('utf-8')
        )
    
    @staticmethod
    def decapsulate(ciphertext_b64: str, secret_key_b64: str, variant: str = "Kyber512") -> str:
        """
        Decapsulate shared secret using Kyber private key with actual oqs-python.
        
        Kyber Decapsulation Workflow:
        1. Parse ciphertext into (u, v)
        2. Recover message: m' = B*u (where B is derived from secret key)
        3. Verify consistency of ciphertext
        4. Derive shared secret from recovered message
        
        The server recovers the same shared secret that the client generated.
        
        Args:
            ciphertext_b64: Base64-encoded Kyber ciphertext
            secret_key_b64: Base64-encoded Kyber secret key
            variant: Kyber variant
        
        Returns:
            Base64-encoded shared secret
        
        Raises:
            RuntimeError: If oqs-python is not installed
        """
        KyberService._check_oqs_available()
        
        kem = KeyEncapsulation(variant)
        secret_key = base64.b64decode(secret_key_b64)
        kem.import_secret_key(secret_key)
        ciphertext = base64.b64decode(ciphertext_b64)
        shared_secret = kem.decap_secret(ciphertext)
        
        return base64.b64encode(shared_secret).decode('utf-8')
    
    @staticmethod
    def get_variant_info(variant: str) -> Dict:
        """
        Get information about a Kyber variant.
        
        Args:
            variant: Kyber variant name
        
        Returns:
            Dictionary with variant information
        """
        variant_info = {
            "Kyber512": {
                "public_key_size": 800,
                "secret_key_size": 1632,
                "ciphertext_size": 768,
                "shared_secret_size": 32,
                "quantum_security_bits": 128,
                "nist_security_level": 1,
                "recommended_for": "Most applications requiring post-quantum security"
            },
            "Kyber768": {
                "public_key_size": 1184,
                "secret_key_size": 2400,
                "ciphertext_size": 1088,
                "shared_secret_size": 32,
                "quantum_security_bits": 192,
                "nist_security_level": 3,
                "recommended_for": "High-security applications"
            },
            "Kyber1024": {
                "public_key_size": 1568,
                "secret_key_size": 3168,
                "ciphertext_size": 1568,
                "shared_secret_size": 32,
                "quantum_security_bits": 256,
                "nist_security_level": 5,
                "recommended_for": "Maximum security requirements"
            }
        }
        
        return variant_info.get(variant, {"error": "Unknown variant"})
    
    @staticmethod
    def explain_lwe_basis() -> Dict:
        """
        Explain the Learning With Errors (LWE) problem that Kyber is based on.
        
        Returns:
            Dictionary explaining LWE and why it's quantum-resistant
        """
        return {
            "problem": "Learning With Errors (LWE)",
            "description": "Given random matrix A and vector b = A*s + e (mod q), find s",
            "components": {
                "A": "Random matrix (public)",
                "s": "Secret vector (private)",
                "e": "Small error vector (noise)",
                "b": "Result vector (public)",
                "q": "Modulus (large prime)"
            },
            "hardness": "Finding s without e is easy, but with e it's computationally hard",
            "quantum_resistance": {
                "shor_algorithm": "Does not apply - LWE is not based on integer factorization",
                "best_quantum_attack": "Only provides polynomial speedup",
                "security_reduction": "Reduces to worst-case lattice problems",
                "lattice_problems": "Shortest Vector Problem (SVP), Closest Vector Problem (CVP)"
            },
            "module_lwe": "Kyber uses Module-LWE for efficiency while maintaining security",
            "nist_selection": "Selected as primary KEM in NIST PQC Standardization (2022)",
            "advantages_over_rsa": [
                "Quantum-resistant",
                "Smaller ciphertext sizes",
                "Faster operations",
                "Based on well-studied mathematical problems"
            ]
        }
    
    @staticmethod
    def explain_kem_architecture() -> Dict:
        """
        Explain the Key Encapsulation Mechanism (KEM) architecture.
        
        Returns:
            Dictionary explaining KEM architecture
        """
        return {
            "architecture": "Key Encapsulation Mechanism (KEM)",
            "purpose": "Securely establish a shared secret over an insecure channel",
            "components": {
                "key_generation": "Generate (pk, sk) key pair",
                "encapsulation": "Generate (ct, ss) from pk",
                "decapsulation": "Recover ss from (ct, sk)"
            },
            "comparison_with_key_exchange": {
                "kem": "One-way communication, simpler API",
                "key_exchange": "Two-way communication, more complex",
                "advantage": "KEM is easier to implement and analyze"
            },
            "hybrid_encryption": {
                "step1": "Use Kyber KEM to establish shared secret",
                "step2": "Use shared secret as AES key",
                "step3": "Encrypt actual data with AES",
                "benefit": "Combines post-quantum key exchange with efficient symmetric encryption"
            },
            "security_properties": [
                "Indistinguishability under chosen ciphertext attacks (IND-CCA2)",
                "Forward secrecy (with proper key management)",
                "Resistance to quantum attacks"
            ]
        }
    
    @staticmethod
    def get_installation_instructions() -> Dict:
        """
        Get instructions for installing actual oqs-python for production use.
        
        Returns:
            Dictionary with installation instructions
        """
        return {
            "note": "This implementation requires oqs-python for actual post-quantum security",
            "production_requirement": "Install liboqs and Python bindings",
            "installation_steps": [
                "1. Install dependencies: cmake, ninja, python3-dev",
                "2. Clone liboqs: git clone https://github.com/open-quantum-safe/liboqs.git",
                "3. Build liboqs: cd liboqs && mkdir build && cd build && cmake .. && make",
                "4. Install liboqs: sudo make install",
                "5. Install Python bindings: pip install oqs-python",
                "6. Or install from source: cd liboqs/python && pip install ."
            ],
            "alternative": "Use pre-built binaries from Open Quantum Safe releases",
            "documentation": "https://github.com/open-quantum-safe/liboqs",
            "variants_available": ["Kyber512", "Kyber768", "Kyber1024"]
        }
