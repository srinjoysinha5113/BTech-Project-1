from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.database import Base


class Log(Base):
    """Log model for tracking system events and errors."""
    
    __tablename__ = "logs"
    
    id = Column(Integer, primary_key=True, index=True)
    level = Column(String(20), nullable=False)  # 'INFO', 'WARNING', 'ERROR', 'DEBUG'
    module = Column(String(50), nullable=False)  # 'auth', 'crypto', 'api', etc.
    message = Column(Text, nullable=False)
    user_id = Column(Integer, nullable=True)  # User ID if applicable
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Log(id={self.id}, level='{self.level}', module='{self.module}')>"
