from sqlalchemy import Column, Integer, Float, String, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base


class BenchmarkResult(Base):
    """BenchmarkResult model for storing cryptography performance metrics."""
    
    __tablename__ = "benchmark_results"
    
    id = Column(Integer, primary_key=True, index=True)
    algorithm = Column(String(50), nullable=False)  # 'RSA', 'Kyber512', 'AES256'
    operation = Column(String(50), nullable=False)  # 'keygen', 'encrypt', 'decrypt'
    key_size = Column(Integer, nullable=False)  # in bits
    execution_time_ms = Column(Float, nullable=False)  # execution time in milliseconds
    ciphertext_size = Column(Integer, nullable=True)  # ciphertext size in bytes
    additional_metrics = Column(Text, nullable=True)  # JSON string for additional metrics
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<BenchmarkResult(id={self.id}, algorithm='{self.algorithm}', operation='{self.operation}', time={self.execution_time_ms}ms)>"
