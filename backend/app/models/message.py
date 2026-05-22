from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Message(Base):
    """Message model for storing encrypted communications."""
    
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    encrypted_content = Column(Text, nullable=False)  # AES ciphertext
    kem_ciphertext = Column(String(4096), nullable=True)  # Kyber/RSA ciphertext for KEM
    encryption_method = Column(String(50), nullable=False)  # 'RSA', 'Kyber', etc.
    nonce = Column(String(255), nullable=True)  # For AES-GCM
    auth_tag = Column(String(255), nullable=True)  # For AES-GCM authentication
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    sender = relationship("User", foreign_keys=[sender_id], backref="sent_messages")
    receiver = relationship("User", foreign_keys=[receiver_id], backref="received_messages")
    
    def __repr__(self):
        return f"<Message(id={self.id}, sender_id={self.sender_id}, method='{self.encryption_method}')>"
