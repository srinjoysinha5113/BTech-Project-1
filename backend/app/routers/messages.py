from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.message import Message
from app.services.aes_service import AESService
from app.services.session_manager import session_manager
from app.middleware.auth import get_current_user
import base64

router = APIRouter()


class SendMessageRequest(BaseModel):
    recipient_username: Optional[str] = None
    kyber_ciphertext: str
    aes_ciphertext: str
    aes_nonce: str
    aes_auth_tag: str
    encryption_method: str = "Kyber"


class SessionSendMessageRequest(BaseModel):
    recipient_username: Optional[str] = None
    session_id: str
    aes_ciphertext: str
    aes_nonce: str
    aes_auth_tag: str


class SendMessageResponse(BaseModel):
    message_id: int
    status: str
    encryption_method: str
    timestamp: datetime


class MessageResponse(BaseModel):
    id: int
    sender_id: int
    sender_username: str
    receiver_id: Optional[int]
    encrypted_content: str
    encryption_method: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class DecryptRequest(BaseModel):
    session_id: str

class DecryptedMessageResponse(BaseModel):
    id: int
    plaintext: str


@router.post("/send-with-session", response_model=SendMessageResponse)
async def send_with_session(
    request: SessionSendMessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    session_data = session_manager.get_session_data(request.session_id)
    if not session_data:
        raise HTTPException(status_code=401, detail="Invalid or expired secure session")
    
    try:
        shared_secret_b64 = session_data["shared_secret"]
        shared_secret = base64.b64decode(shared_secret_b64)
        
        # Verify it can be decrypted
        AESService.decrypt(
            ciphertext_b64=request.aes_ciphertext,
            key=shared_secret,
            nonce_b64=request.aes_nonce,
            auth_tag_b64=request.aes_auth_tag
        )
        
        recipient_id = None
        if request.recipient_username:
            recipient = db.query(User).filter(User.username == request.recipient_username).first()
            if not recipient:
                raise HTTPException(status_code=404, detail="Recipient not found")
            recipient_id = recipient.id

        message = Message(
            sender_id=current_user.id,
            receiver_id=recipient_id,
            encrypted_content=request.aes_ciphertext,
            kem_ciphertext="session-managed",
            encryption_method=f"Kyber-Session-AES256-GCM",
            nonce=request.aes_nonce,
            auth_tag=request.aes_auth_tag
        )
        
        db.add(message)
        db.commit()
        db.refresh(message)
        
        return SendMessageResponse(
            message_id=message.id,
            status="sent and verified",
            encryption_method=message.encryption_method,
            timestamp=message.created_at
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{message_id}/decrypt-with-session", response_model=DecryptedMessageResponse)
async def decrypt_with_session(
    message_id: int,
    request: DecryptRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Decrypt a message using an active PQC session."""
    message = db.query(Message).filter(Message.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    # Auth check
    if message.sender_id != current_user.id and message.receiver_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    session_data = session_manager.get_session_data(request.session_id)
    if not session_data:
        raise HTTPException(status_code=401, detail="Invalid session - establish session first")

    try:
        shared_secret = base64.b64decode(session_data["shared_secret"])
        plaintext = AESService.decrypt(
            ciphertext_b64=message.encrypted_content,
            key=shared_secret,
            nonce_b64=message.nonce,
            auth_tag_b64=message.auth_tag
        )
        return DecryptedMessageResponse(id=message.id, plaintext=plaintext)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Decryption failed. Session key may not match message key.")


@router.get("/inbox", response_model=List[MessageResponse])
async def get_inbox(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    messages = db.query(Message).filter(Message.receiver_id == current_user.id).order_by(Message.created_at.desc()).all()
    result = []
    for msg in messages:
        sender = db.query(User).filter(User.id == msg.sender_id).first()
        result.append(MessageResponse(
            id=msg.id,
            sender_id=msg.sender_id,
            sender_username=sender.username if sender else "Unknown",
            receiver_id=msg.receiver_id,
            encrypted_content=msg.encrypted_content,
            encryption_method=msg.encryption_method,
            created_at=msg.created_at
        ))
    return result
