import time
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.benchmark import BenchmarkResult
from app.services.rsa_service import RSAService
from app.services.kyber_service import KyberService
from pydantic import BaseModel
from typing import List

router = APIRouter()

class BenchmarkSummary(BaseModel):
    algorithm: str
    operation: str
    execution_time_ms: float

@router.get("/run", response_model=List[BenchmarkSummary])
async def run_benchmark(db: Session = Depends(get_db)):
    results = []
    
    # 1. RSA 2048 Keygen
    start = time.time()
    RSAService.generate_keypair(2048)
    end = time.time()
    rsa_keygen_time = (end - start) * 1000
    results.append({"algorithm": "RSA-2048", "operation": "Key Generation", "execution_time_ms": rsa_keygen_time})
    
    # 2. Kyber 512 Keygen
    start = time.time()
    KyberService.generate_keypair("Kyber512")
    end = time.time()
    kyber_keygen_time = (end - start) * 1000
    results.append({"algorithm": "Kyber-512", "operation": "Key Generation", "execution_time_ms": kyber_keygen_time})
    
    # 3. RSA Encrypt (using a small message)
    _, pub = RSAService.generate_keypair(2048)
    start = time.time()
    RSAService.encrypt_message("Test message for benchmarking", pub)
    end = time.time()
    rsa_encrypt_time = (end - start) * 1000
    results.append({"algorithm": "RSA-2048", "operation": "Encryption", "execution_time_ms": rsa_encrypt_time})
    
    # 4. Kyber Encapsulate
    pk, _ = KyberService.generate_keypair("Kyber512")
    start = time.time()
    KyberService.encapsulate(pk, "Kyber512")
    end = time.time()
    kyber_encap_time = (end - start) * 1000
    results.append({"algorithm": "Kyber-512", "operation": "Encapsulation", "execution_time_ms": kyber_encap_time})

    # Save to database
    for res in results:
        db_res = BenchmarkResult(
            algorithm=res["algorithm"],
            operation=res["operation"],
            execution_time_ms=res["execution_time_ms"],
            key_size=2048 if "RSA" in res["algorithm"] else 512
        )
        db.add(db_res)
    
    db.commit()
    return results

@router.get("/history", response_model=List[BenchmarkSummary])
async def get_benchmark_history(db: Session = Depends(get_db)):
    history = db.query(BenchmarkResult).order_by(BenchmarkResult.created_at.desc()).limit(20).all()
    return history
