from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database import Base


class ServerKyberKeys(Base):
    """Server Kyber keypair storage for persistent post-quantum keys."""
    
    __tablename__ = "server_kyber_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    variant = Column(String(50), nullable=False, unique=True)  # e.g., "Kyber512"
    public_key = Column(String(4096), nullable=False)  # Base64-encoded public key
    secret_key = Column(String(4096), nullable=False)  # Base64-encoded secret key
    is_active = Column(Integer, default=1)  # 1 = active, 0 = inactive
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<ServerKyberKeys(id={self.id}, variant='{self.variant}', is_active={self.is_active})>"
