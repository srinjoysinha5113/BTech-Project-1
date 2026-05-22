from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional, Dict

from app.services.aes_service import AESService

router = APIRouter()


# Pydantic models for request/response
class KeyGenerateRequest(BaseModel):
    """Request model for AES key generation."""
    key_size: Optional[int] = 32


class KeyResponse(BaseModel):
    """Response model for AES key generation."""
    key: str
    key_info: Dict


class EncryptRequest(BaseModel):
    """Request model for AES encryption."""
    plaintext: str
    key: str
    nonce: Optional[str] = None


class EncryptResponse(BaseModel):
    """Response model for AES encryption."""
    ciphertext: str
    nonce: str
    auth_tag: str
    encryption_method: str


class DecryptRequest(BaseModel):
    """Request model for AES decryption."""
    ciphertext: str
    key: str
    nonce: str
    auth_tag: str


class DecryptResponse(BaseModel):
    """Response model for AES decryption."""
    plaintext: str
    decryption_method: str


class EncryptWithAADRequest(BaseModel):
    """Request model for AES encryption with associated data."""
    plaintext: str
    key: str
    associated_data: Optional[str] = None
    nonce: Optional[str] = None


class DecryptWithAADRequest(BaseModel):
    """Request model for AES decryption with associated data."""
    ciphertext: str
    key: str
    nonce: str
    auth_tag: str
    associated_data: Optional[str] = None


class KeyInfoRequest(BaseModel):
    """Request model for AES key information."""
    key: str


class QuantumResistanceInfo(BaseModel):
    """Response model for quantum resistance explanation."""
    algorithm: str
    security_basis: str
    classical_security: str
    quantum_threat: str
    grover_algorithm_complexity: str
    classical_algorithm_complexity: str
    impact: str
    mitigation: str
    current_status: str
    recommendation: str


@router.post("/generate-key", response_model=KeyResponse)
async def generate_key(request: KeyGenerateRequest):
    """
    Generate AES key.
    
    Generates a random AES key for symmetric encryption.
    Default is 32 bytes (AES-256) for maximum security.
    
    Args:
        request: Key generation request with optional key size
        
    Returns:
        Generated key with key information
    """
    try:
        key = AESService.generate_key(key_size=request.key_size)
        key_info = AESService.get_key_info(key)
        
        return KeyResponse(
            key=base64_encode(key),
            key_info=key_info
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/encrypt", response_model=EncryptResponse)
async def encrypt(request: EncryptRequest):
    """
    Encrypt plaintext using AES-256-GCM.
    
    Encrypts a message using AES-256-GCM with the provided key.
    Generates a random nonce if not provided.
    
    Args:
        request: Encryption request with plaintext and key
        
    Returns:
        Encrypted data with nonce and authentication tag
    """
    try:
        key = base64_decode(request.key)
        nonce = base64_decode(request.nonce) if request.nonce else None
        
        result = AESService.encrypt(
            plaintext=request.plaintext,
            key=key,
            nonce=nonce
        )
        
        return EncryptResponse(
            ciphertext=result["ciphertext"],
            nonce=result["nonce"],
            auth_tag=result["auth_tag"],
            encryption_method="AES-256-GCM"
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
async def decrypt(request: DecryptRequest):
    """
    Decrypt ciphertext using AES-256-GCM.
    
    Decrypts a message that was encrypted with AES-256-GCM.
    Verifies the authentication tag to ensure integrity.
    
    Args:
        request: Decryption request with ciphertext, key, nonce, and auth tag
        
    Returns:
        Decrypted plain text message
    """
    try:
        key = base64_decode(request.key)
        
        plaintext = AESService.decrypt(
            ciphertext_b64=request.ciphertext,
            key=key,
            nonce_b64=request.nonce,
            auth_tag_b64=request.auth_tag
        )
        
        return DecryptResponse(
            plaintext=plaintext,
            decryption_method="AES-256-GCM"
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


@router.post("/encrypt-with-aad", response_model=EncryptResponse)
async def encrypt_with_aad(request: EncryptWithAADRequest):
    """
    Encrypt plaintext with additional authenticated data (AAD).
    
    Encrypts a message with optional associated data that is authenticated
    but not encrypted. Useful for metadata like message IDs.
    
    Args:
        request: Encryption request with plaintext, key, and optional AAD
        
    Returns:
        Encrypted data with nonce and authentication tag
    """
    try:
        key = base64_decode(request.key)
        nonce = base64_decode(request.nonce) if request.nonce else None
        
        result = AESService.encrypt_with_associated_data(
            plaintext=request.plaintext,
            key=key,
            associated_data=request.associated_data,
            nonce=nonce
        )
        
        return EncryptResponse(
            ciphertext=result["ciphertext"],
            nonce=result["nonce"],
            auth_tag=result["auth_tag"],
            encryption_method="AES-256-GCM with AAD"
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


@router.post("/decrypt-with-aad", response_model=DecryptResponse)
async def decrypt_with_aad(request: DecryptWithAADRequest):
    """
    Decrypt ciphertext with additional authenticated data (AAD).
    
    Decrypts a message that was encrypted with AAD.
    The AAD must match what was used during encryption.
    
    Args:
        request: Decryption request with ciphertext, key, nonce, auth tag, and AAD
        
    Returns:
        Decrypted plain text message
    """
    try:
        key = base64_decode(request.key)
        
        plaintext = AESService.decrypt_with_associated_data(
            ciphertext_b64=request.ciphertext,
            key=key,
            nonce_b64=request.nonce,
            auth_tag_b64=request.auth_tag,
            associated_data=request.associated_data
        )
        
        return DecryptResponse(
            plaintext=plaintext,
            decryption_method="AES-256-GCM with AAD"
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
    Get information about an AES key.
    
    Returns metadata about the AES key including size, variant, and security level.
    
    Args:
        request: Request with AES key
        
    Returns:
        Key information dictionary
    """
    try:
        key = base64_decode(request.key)
        key_info = AESService.get_key_info(key)
        return key_info
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get key info: {str(e)}"
        )


@router.get("/quantum-resistance", response_model=QuantumResistanceInfo)
async def get_quantum_resistance_info():
    """
    Get information about AES's resistance to quantum computing.
    
    Explains why AES is considered quantum-resistant for symmetric encryption.
    
    Returns:
        Detailed explanation of quantum resistance
    """
    resistance_info = AESService.explain_quantum_resistance()
    return QuantumResistanceInfo(**resistance_info)


# Helper functions
def base64_encode(data: bytes) -> str:
    """Encode bytes to base64 string."""
    import base64
    return base64.b64encode(data).decode('utf-8')


def base64_decode(data: str) -> bytes:
    """Decode base64 string to bytes."""
    import base64
    return base64.b64decode(data)
