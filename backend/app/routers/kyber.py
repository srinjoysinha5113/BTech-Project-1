from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional, Dict

from app.services.kyber_service import KyberService
from app.services.aes_service import AESService
import base64

router = APIRouter()


# Pydantic models for request/response
class KeypairGenerateRequest(BaseModel):
    """Request model for Kyber keypair generation."""
    variant: Optional[str] = "Kyber512"


class KeypairResponse(BaseModel):
    """Response model for Kyber keypair generation."""
    public_key: str
    secret_key: str
    variant_info: Dict


class EncapsulateRequest(BaseModel):
    """Request model for Kyber encapsulation."""
    public_key: str
    variant: Optional[str] = "Kyber512"


class EncapsulateResponse(BaseModel):
    """Response model for Kyber encapsulation."""
    ciphertext: str
    shared_secret: str
    variant: str
    kem_method: str


class DecapsulateRequest(BaseModel):
    """Request model for Kyber decapsulation."""
    ciphertext: str
    secret_key: str
    variant: Optional[str] = "Kyber512"


class DecapsulateResponse(BaseModel):
    """Response model for Kyber decapsulation."""
    shared_secret: str
    variant: str
    kem_method: str


class VariantInfoRequest(BaseModel):
    """Request model for Kyber variant information."""
    variant: str


class HybridEncryptRequest(BaseModel):
    """Request model for hybrid encryption (Kyber + AES)."""
    plaintext: str
    public_key: str
    variant: Optional[str] = "Kyber512"


class HybridEncryptResponse(BaseModel):
    """Response model for hybrid encryption."""
    kyber_ciphertext: str
    aes_ciphertext: str
    aes_nonce: str
    aes_auth_tag: str
    encryption_method: str


class HybridDecryptRequest(BaseModel):
    """Request model for hybrid decryption (Kyber + AES)."""
    kyber_ciphertext: str
    aes_ciphertext: str
    aes_nonce: str
    aes_auth_tag: str
    secret_key: str
    variant: Optional[str] = "Kyber512"


class HybridDecryptResponse(BaseModel):
    """Response model for hybrid decryption."""
    plaintext: str
    decryption_method: str


@router.post("/generate-keypair", response_model=KeypairResponse)
async def generate_keypair(request: KeypairGenerateRequest):
    """
    Generate Kyber keypair.
    
    Generates a new Kyber public/private key pair for post-quantum
    key encapsulation. The default variant is Kyber512 which provides
    ~128-bit quantum security.
    
    Args:
        request: Keypair generation request with optional variant
        
    Returns:
        Generated keypair with variant information
    """
    try:
        public_key, secret_key = KyberService.generate_keypair(
            variant=request.variant
        )
        
        variant_info = KyberService.get_variant_info(request.variant)
        
        return KeypairResponse(
            public_key=public_key,
            secret_key=secret_key,
            variant_info=variant_info
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Key generation failed: {str(e)}"
        )


@router.post("/encapsulate", response_model=EncapsulateResponse)
async def encapsulate(request: EncapsulateRequest):
    """
    Encapsulate shared secret using Kyber public key.
    
    The client generates a shared secret and ciphertext from the server's
    public key. Only the server with the private key can decapsulate
    the shared secret.
    
    Args:
        request: Encapsulation request with public key
        
    Returns:
        Ciphertext and shared secret
    """
    try:
        ciphertext, shared_secret = KyberService.encapsulate(
            public_key_b64=request.public_key,
            variant=request.variant
        )
        
        return EncapsulateResponse(
            ciphertext=ciphertext,
            shared_secret=shared_secret,
            variant=request.variant,
            kem_method="Kyber-KEM"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Encapsulation failed: {str(e)}"
        )


@router.post("/decapsulate", response_model=DecapsulateResponse)
async def decapsulate(request: DecapsulateRequest):
    """
    Decapsulate shared secret using Kyber private key.
    
    The server recovers the shared secret from the ciphertext using
    the private key. This shared secret matches what the client generated.
    
    Args:
        request: Decapsulation request with ciphertext and secret key
        
    Returns:
        Shared secret
    """
    try:
        shared_secret = KyberService.decapsulate(
            ciphertext_b64=request.ciphertext,
            secret_key_b64=request.secret_key,
            variant=request.variant
        )
        
        return DecapsulateResponse(
            shared_secret=shared_secret,
            variant=request.variant,
            kem_method="Kyber-KEM"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Decapsulation failed: {str(e)}"
        )


@router.post("/variant-info", response_model=Dict)
async def get_variant_info(request: VariantInfoRequest):
    """
    Get information about a Kyber variant.
    
    Returns metadata about the Kyber variant including key sizes,
    security levels, and recommendations.
    
    Args:
        request: Request with variant name
        
    Returns:
        Variant information dictionary
    """
    try:
        variant_info = KyberService.get_variant_info(request.variant)
        return variant_info
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get variant info: {str(e)}"
        )


@router.post("/hybrid-encrypt", response_model=HybridEncryptResponse)
async def hybrid_encrypt(request: HybridEncryptRequest):
    """
    Hybrid encryption using Kyber + AES.
    
    This demonstrates the complete post-quantum encryption workflow:
    1. Encapsulate shared secret using Kyber (post-quantum KEM)
    2. Use shared secret as AES key
    3. Encrypt message with AES-256-GCM (symmetric encryption)
    
    This combines the quantum resistance of Kyber with the efficiency of AES.
    
    Args:
        request: Hybrid encryption request with plaintext and Kyber public key
        
    Returns:
        Kyber ciphertext, AES ciphertext, nonce, and auth tag
    """
    try:
        # Step 1: Encapsulate shared secret using Kyber
        kyber_ciphertext, shared_secret_b64 = KyberService.encapsulate(
            public_key_b64=request.public_key,
            variant=request.variant
        )
        
        # Step 2: Use shared secret as AES key
        shared_secret = base64.b64decode(shared_secret_b64)
        
        # Step 3: Encrypt message with AES-256-GCM
        aes_result = AESService.encrypt(
            plaintext=request.plaintext,
            key=shared_secret
        )
        
        return HybridEncryptResponse(
            kyber_ciphertext=kyber_ciphertext,
            aes_ciphertext=aes_result["ciphertext"],
            aes_nonce=aes_result["nonce"],
            aes_auth_tag=aes_result["auth_tag"],
            encryption_method=f"Kyber-{request.variant} + AES-256-GCM"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hybrid encryption failed: {str(e)}"
        )


@router.post("/hybrid-decrypt", response_model=HybridDecryptResponse)
async def hybrid_decrypt(request: HybridDecryptRequest):
    """
    Hybrid decryption using Kyber + AES.
    
    This demonstrates the complete post-quantum decryption workflow:
    1. Decapsulate shared secret using Kyber
    2. Use shared secret as AES key
    3. Decrypt message with AES-256-GCM
    
    Args:
        request: Hybrid decryption request with all necessary components
        
    Returns:
        Decrypted plain text message
    """
    try:
        # Step 1: Decapsulate shared secret using Kyber
        shared_secret_b64 = KyberService.decapsulate(
            ciphertext_b64=request.kyber_ciphertext,
            secret_key_b64=request.secret_key,
            variant=request.variant
        )
        
        # Step 2: Use shared secret as AES key
        shared_secret = base64.b64decode(shared_secret_b64)
        
        # Step 3: Decrypt message with AES-256-GCM
        plaintext = AESService.decrypt(
            ciphertext_b64=request.aes_ciphertext,
            key=shared_secret,
            nonce_b64=request.aes_nonce,
            auth_tag_b64=request.aes_auth_tag
        )
        
        return HybridDecryptResponse(
            plaintext=plaintext,
            decryption_method=f"Kyber-{request.variant} + AES-256-GCM"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Hybrid decryption failed: {str(e)}"
        )


@router.get("/lwe-basis", response_model=Dict)
async def get_lwe_basis():
    """
    Get information about the Learning With Errors (LWE) problem.
    
    Explains the mathematical foundation of Kyber and why it's
    quantum-resistant.
    
    Returns:
        Detailed explanation of LWE problem
    """
    return KyberService.explain_lwe_basis()


@router.get("/kem-architecture", response_model=Dict)
async def get_kem_architecture():
    """
    Get information about Key Encapsulation Mechanism architecture.
    
    Explains how KEM works and its advantages over traditional key exchange.
    
    Returns:
        Detailed explanation of KEM architecture
    """
    return KyberService.explain_kem_architecture()


@router.get("/installation-instructions", response_model=Dict)
async def get_installation_instructions():
    """
    Get installation instructions for production oqs-python.
    
    Provides instructions for installing the actual Open Quantum Safe
    Python bindings for production use with real post-quantum security.
    
    Returns:
        Installation instructions
    """
    return KyberService.get_installation_instructions()
