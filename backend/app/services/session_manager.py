import time
import secrets
from typing import Dict, Optional, Any
from datetime import datetime, timedelta


class SessionManager:
    """
    In-memory manager for ephemeral cryptographic sessions.
    
    This manager stores sensitive session data (like derived AES keys)
    in memory only. It handles session creation, retrieval, and expiration.
    """
    
    def __init__(self, session_expiry_minutes: int = 30):
        # Dictionary to store sessions: {session_id: session_data}
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self.session_expiry_minutes = session_expiry_minutes

    def create_session(self, data: Dict[str, Any]) -> str:
        """
        Create a new ephemeral session and return its ID.
        
        Args:
            data: Session data (e.g., derived_key, user_id, metadata)
            
        Returns:
            A unique session_id (32-byte hex string)
        """
        session_id = secrets.token_hex(32)
        expiry_time = datetime.now() + timedelta(minutes=self.session_expiry_minutes)
        
        self._sessions[session_id] = {
            "data": data,
            "expiry": expiry_time,
            "created_at": datetime.now()
        }
        
        # Periodically clean up expired sessions
        self._cleanup_expired()
        
        return session_id

    def get_session_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve data for a given session ID if it exists and hasn't expired.
        
        Args:
            session_id: The ID of the session to retrieve
            
        Returns:
            The session data or None if not found/expired
        """
        session = self._sessions.get(session_id)
        
        if not session:
            return None
        
        # Check for expiration
        if datetime.now() > session["expiry"]:
            self.delete_session(session_id)
            return None
            
        return session["data"]

    def delete_session(self, session_id: str) -> bool:
        """Delete a session manually."""
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False

    def _cleanup_expired(self):
        """Remove all expired sessions from memory."""
        now = datetime.now()
        expired_ids = [
            sid for sid, sinfo in self._sessions.items() 
            if now > sinfo["expiry"]
        ]
        
        for sid in expired_ids:
            del self._sessions[sid]


# Global session manager instance
session_manager = SessionManager()
