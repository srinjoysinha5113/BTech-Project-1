from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional, Dict

from app.services.kyber_service import KyberService
from app.services.aes_service import AESService
from app.services.session_manager import session_manager
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


class SecureSessionRequest(BaseModel):
    """Request model for creating a PQC-secured session."""
    public_key: str
    variant: Optional[str] = "Kyber512"


class SecureSessionResponse(BaseModel):
    """Response model for created session."""
    session_id: str
    kyber_ciphertext: str
    expires_at: str


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


@router.post("/generate-keypair", response_model=KeypairResponse)
async def generate_keypair(request: KeypairGenerateRequest):
    """Generate Kyber keypair for post-quantum key encapsulation."""
    try:
        public_key, secret_key = KyberService.generate_keypair(variant=request.variant)
        variant_info = KyberService.get_variant_info(request.variant)
        return KeypairResponse(public_key=public_key, secret_key=secret_key, variant_info=variant_info)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/create-session", response_model=SecureSessionResponse)
async def create_secure_session(request: SecureSessionRequest):
    """
    Establish a PQC-secured ephemeral session.
    
    1. Encapsulate a shared secret using the provided Kyber public key.
    2. Store the shared secret in the in-memory session manager.
    3. Return the session_id and Kyber ciphertext to the client.
    """
    try:
        # Step 1: Encapsulate shared secret using Kyber
        kyber_ciphertext, shared_secret_b64 = KyberService.encapsulate(
            public_key_b64=request.public_key,
            variant=request.variant
        )
        
        # Step 2: Store the session data in-memory
        # We store the base64 encoded shared secret for later use as an AES key
        session_id = session_manager.create_session({
            "shared_secret": shared_secret_b64,
            "variant": request.variant
        })
        
        # Get expiration time for the response
        session = session_manager._sessions[session_id]
        expires_at = session["expiry"].isoformat()
        
        return SecureSessionResponse(
            session_id=session_id,
            kyber_ciphertext=kyber_ciphertext,
            expires_at=expires_at
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Session establishment failed: {str(e)}"
        )


@router.post("/encapsulate", response_model=EncapsulateResponse)
async def encapsulate(request: EncapsulateRequest):
    """Encapsulate shared secret using Kyber public key."""
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
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/decapsulate", response_model=DecapsulateResponse)
async def decapsulate(request: DecapsulateRequest):
    """Decapsulate shared secret using Kyber private key."""
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
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# ... keep other endpoints if needed, but these are the core ones for the new architecture
