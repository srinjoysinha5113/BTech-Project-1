from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.message import Message
from app.models.server_keys import ServerKyberKeys
from app.services.kyber_service import KyberService
from app.services.aes_service import AESService
from app.middleware.auth import get_current_user
import base64

router = APIRouter()


# Pydantic models for request/response
class SendMessageRequest(BaseModel):
    """Request model for sending a secure message with pre-encrypted data."""
    recipient_username: Optional[str] = None
    kyber_ciphertext: str
    aes_ciphertext: str
    aes_nonce: str
    aes_auth_tag: str
    encryption_method: str = "Kyber"  # "Kyber" or "RSA"


class SendMessageResponse(BaseModel):
    """Response model for sent message."""
    message_id: int
    status: str
    encryption_method: str
    timestamp: datetime


class MessageResponse(BaseModel):
    """Response model for retrieved message."""
    id: int
    sender_id: int
    sender_username: str
    receiver_id: Optional[int]
    encrypted_content: str
    encryption_method: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class DecryptedMessageResponse(BaseModel):
    """Response model for decrypted message."""
    id: int
    sender_username: str
    plaintext: str
    encryption_method: str
    created_at: datetime


class ServerPublicKeyResponse(BaseModel):
    """Response model for server's Kyber public key."""
    public_key: str
    variant: str
    timestamp: datetime


def get_server_keypair(db: Session, variant: str = "Kyber512") -> dict:
    """
    Get or generate server's Kyber keypair from database.
    
    Args:
        db: Database session
        variant: Kyber variant (default: Kyber512)
    
    Returns:
        Dictionary with public_key, secret_key, and variant
    """
    # Try to get existing active keypair from database
    keypair = db.query(ServerKyberKeys).filter(
        ServerKyberKeys.variant == variant,
        ServerKyberKeys.is_active == 1
    ).first()
    
    if keypair:
        return {
            "public_key": keypair.public_key,
            "secret_key": keypair.secret_key,
            "variant": keypair.variant
        }
    
    # Generate new keypair
    public_key, secret_key = KyberService.generate_keypair(variant=variant)
    
    # Store in database
    new_keypair = ServerKyberKeys(
        variant=variant,
        public_key=public_key,
        secret_key=secret_key,
        is_active=1
    )
    
    db.add(new_keypair)
    db.commit()
    db.refresh(new_keypair)
    
    return {
        "public_key": new_keypair.public_key,
        "secret_key": new_keypair.secret_key,
        "variant": new_keypair.variant
    }


@router.get("/server-public-key", response_model=ServerPublicKeyResponse)
async def get_server_public_key(db: Session = Depends(get_db)):
    """
    Get server's Kyber public key for secure messaging.
    
    Clients use this public key to encapsulate a shared secret
    for encrypting messages to the server.
    
    Returns:
        Server's Kyber public key
    """
    keypair = get_server_keypair(db)
    
    return ServerPublicKeyResponse(
        public_key=keypair["public_key"],
        variant=keypair["variant"],
        timestamp=datetime.utcnow()
    )


@router.post("/send", response_model=SendMessageResponse)
async def send_secure_message(
    request: SendMessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send a secure message with pre-encrypted data.
    
    Client-side workflow (performed by client before calling this endpoint):
    1. Client fetches server's Kyber public key
    2. Client encapsulates shared secret using Kyber
    3. Client encrypts message with AES using shared secret
    
    Server-side workflow (this endpoint):
    4. Server receives pre-encrypted message
    5. Server stores encrypted message in database
    6. Server can later decapsulate and decrypt when recipient reads message
    
    Args:
        request: Pre-encrypted message data (kyber_ciphertext, aes_ciphertext, nonce, auth_tag)
        current_user: Authenticated sender
        db: Database session
        
    Returns:
        Message confirmation
    """
    try:
        # Find recipient if specified
        recipient_id = None
        if request.recipient_username:
            from app.services.auth_service import AuthService
            recipient = AuthService.get_user_by_username(db, request.recipient_username)
            if not recipient:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Recipient not found"
                )
            recipient_id = recipient.id
        
        # Store encrypted message in database using proper columns
        message = Message(
            sender_id=current_user.id,
            receiver_id=recipient_id,
            encrypted_content=request.aes_ciphertext,
            kem_ciphertext=request.kyber_ciphertext,
            encryption_method=f"{request.encryption_method}-AES256-GCM",
            nonce=request.aes_nonce,
            auth_tag=request.aes_auth_tag
        )
        
        db.add(message)
        db.commit()
        db.refresh(message)
        
        return SendMessageResponse(
            message_id=message.id,
            status="sent",
            encryption_method=message.encryption_method,
            timestamp=message.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send message: {str(e)}"
        )


@router.get("/inbox", response_model=List[MessageResponse])
async def get_inbox(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's inbox (received messages).
    
    Args:
        current_user: Authenticated user
        db: Database session
        
    Returns:
        List of received messages
    """
    messages = db.query(Message).filter(
        Message.receiver_id == current_user.id
    ).order_by(Message.created_at.desc()).all()
    
    # Add sender username to each message
    result = []
    for msg in messages:
        sender = db.query(User).filter(User.id == msg.sender_id).first()
        msg_dict = {
            "id": msg.id,
            "sender_id": msg.sender_id,
            "sender_username": sender.username if sender else "Unknown",
            "receiver_id": msg.receiver_id,
            "encrypted_content": msg.encrypted_content,
            "encryption_method": msg.encryption_method,
            "created_at": msg.created_at
        }
        result.append(MessageResponse(**msg_dict))
    
    return result


@router.get("/sent", response_model=List[MessageResponse])
async def get_sent_messages(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's sent messages.
    
    Args:
        current_user: Authenticated user
        db: Database session
        
    Returns:
        List of sent messages
    """
    messages = db.query(Message).filter(
        Message.sender_id == current_user.id
    ).order_by(Message.created_at.desc()).all()
    
    # Add sender username to each message
    result = []
    for msg in messages:
        result.append(MessageResponse(
            id=msg.id,
            sender_id=msg.sender_id,
            sender_username=current_user.username,
            receiver_id=msg.receiver_id,
            encrypted_content=msg.encrypted_content,
            encryption_method=msg.encryption_method,
            created_at=msg.created_at
        ))
    
    return result


@router.get("/{message_id}/decrypt", response_model=DecryptedMessageResponse)
async def decrypt_message(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Decrypt a secure message.
    
    Only the intended recipient (or sender) can decrypt the message.
    The server uses its private key to decapsulate the shared secret.
    
    Args:
        message_id: Message ID to decrypt
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Decrypted message content
    """
    try:
        # Get message
        message = db.query(Message).filter(Message.id == message_id).first()
        
        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found"
            )
        
        # Check authorization (only sender or recipient can decrypt)
        if message.sender_id != current_user.id and message.receiver_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to decrypt this message"
            )
        
        # Use dedicated kem_ciphertext column for Kyber ciphertext
        kyber_ciphertext = message.kem_ciphertext
        aes_ciphertext = message.encrypted_content
        
        # Use nonce and auth_tag from proper database columns
        aes_nonce = message.nonce
        aes_auth_tag = message.auth_tag
        
        # Decapsulate shared secret using server's private key
        keypair = get_server_keypair(db)
        shared_secret_b64 = KyberService.decapsulate(
            ciphertext_b64=kyber_ciphertext,
            secret_key_b64=keypair["secret_key"],
            variant=keypair["variant"]
        )
        
        # Use shared secret as AES key
        shared_secret = base64.b64decode(shared_secret_b64)
        
        # Decrypt message with AES-256-GCM
        plaintext = AESService.decrypt(
            ciphertext_b64=aes_ciphertext,
            key=shared_secret,
            nonce_b64=aes_nonce,
            auth_tag_b64=aes_auth_tag
        )
        
        # Get sender username
        sender = db.query(User).filter(User.id == message.sender_id).first()
        sender_username = sender.username if sender else "Unknown"
        
        return DecryptedMessageResponse(
            id=message.id,
            sender_username=sender_username,
            plaintext=plaintext,
            encryption_method=message.encryption_method,
            created_at=message.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to decrypt message: {str(e)}"
        )


@router.delete("/{message_id}")
async def delete_message(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a message.
    
    Only the sender can delete their own messages.
    
    Args:
        message_id: Message ID to delete
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Deletion confirmation
    """
    # Get message
    message = db.query(Message).filter(Message.id == message_id).first()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    # Check authorization (only sender can delete)
    if message.sender_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this message"
        )
    
    # Delete message
    db.delete(message)
    db.commit()
    
    return {"status": "deleted", "message_id": message_id}
