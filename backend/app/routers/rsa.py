from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional, Dict

from app.services.rsa_service import RSAService

router = APIRouter()


# Pydantic models for request/response
class KeypairGenerateRequest(BaseModel):
    """Request model for RSA keypair generation."""
    key_size: Optional[int] = 2048


class KeypairResponse(BaseModel):
    """Response model for RSA keypair generation."""
    private_key: str
    public_key: str
    key_info: Dict


class EncryptRequest(BaseModel):
    """Request model for RSA encryption."""
    message: str
    public_key: str


class EncryptResponse(BaseModel):
    """Response model for RSA encryption."""
    ciphertext: str
    encryption_method: str


class DecryptRequest(BaseModel):
    """Request model for RSA decryption."""
    ciphertext: str
    private_key: str


class DecryptResponse(BaseModel):
    """Response model for RSA decryption."""
    message: str
    decryption_method: str


class KeyInfoRequest(BaseModel):
    """Request model for RSA key information."""
    public_key: str


class QuantumVulnerabilityInfo(BaseModel):
    """Response model for quantum vulnerability explanation."""
    algorithm: str
    security_basis: str
    classical_security: str
    quantum_threat: str
    shor_algorithm_complexity: str
    classical_algorithm_complexity: str
    impact: str
    mitigation: str
    harvest_now_decrypt_later: str


@router.post("/generate-keypair", response_model=KeypairResponse)
async def generate_keypair(request: KeypairGenerateRequest):
    """
    Generate RSA keypair.
    
    Generates a new RSA public/private key pair for encryption/decryption.
    The default key size is 2048 bits, which is the current standard.
    
    Args:
        request: Keypair generation request with optional key size
        
    Returns:
        Generated keypair with key information
    """
    try:
        private_key, public_key = RSAService.generate_keypair(
            key_size=request.key_size
        )
        
        key_info = RSAService.get_key_info(public_key)
        
        return KeypairResponse(
            private_key=private_key,
            public_key=public_key,
            key_info=key_info
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/encrypt", response_model=EncryptResponse)
async def encrypt_message(request: EncryptRequest):
    """
    Encrypt a message using RSA public key.
    
    Encrypts a message using the provided RSA public key.
    Note: RSA can only encrypt messages smaller than the key size.
    For larger messages, use hybrid encryption (encrypt AES key with RSA).
    
    Args:
        request: Encryption request with message and public key
        
    Returns:
        Encrypted message (base64-encoded)
    """
    try:
        ciphertext = RSAService.encrypt_message(
            message=request.message,
            public_key_pem=request.public_key
        )
        
        return EncryptResponse(
            ciphertext=ciphertext,
            encryption_method="RSA-PKCS1-OAEP"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Encryption failed: {str(e)}"
        )


@router.post("/decrypt", response_model=DecryptResponse)
async def decrypt_message(request: DecryptRequest):
    """
    Decrypt a message using RSA private key.
    
    Decrypts a message that was encrypted with the corresponding RSA public key.
    
    Args:
        request: Decryption request with ciphertext and private key
        
    Returns:
        Decrypted plain text message
    """
    try:
        message = RSAService.decrypt_message(
            ciphertext_b64=request.ciphertext,
            private_key_pem=request.private_key
        )
        
        return DecryptResponse(
            message=message,
            decryption_method="RSA-PKCS1-OAEP"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Decryption failed: {str(e)}"
        )


@router.post("/key-info", response_model=Dict)
async def get_key_info(request: KeyInfoRequest):
    """
    Get information about an RSA public key.
    
    Returns metadata about the RSA key including size, exponent, etc.
    
    Args:
        request: Request with public key
        
    Returns:
        Key information dictionary
    """
    try:
        key_info = RSAService.get_key_info(request.public_key)
        return key_info
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get key info: {str(e)}"
        )


@router.get("/quantum-vulnerability", response_model=QuantumVulnerabilityInfo)
async def get_quantum_vulnerability_info():
    """
    Get information about RSA's vulnerability to quantum computing.
    
    Explains why RSA is vulnerable to Shor's algorithm on quantum computers
    and the implications for current security systems.
    
    Returns:
        Detailed explanation of quantum vulnerability
    """
    vulnerability_info = RSAService.explain_quantum_vulnerability()
    return QuantumVulnerabilityInfo(**vulnerability_info)
