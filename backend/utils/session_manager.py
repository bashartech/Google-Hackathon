"""
Session Manager for Conversation History
Manages stateful conversations with memory across requests
"""

from typing import Dict, List, Any
from datetime import datetime, timedelta
import uuid


class ConversationSession:
    """Represents a single conversation session with history."""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.created_at = datetime.now()
        self.last_accessed = datetime.now()
        self.messages: List[Dict[str, Any]] = []
        self.context: Dict[str, Any] = {}

    def add_message(self, role: str, content: str, metadata: Dict[str, Any] = None):
        """Add a message to conversation history."""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        self.messages.append(message)
        self.last_accessed = datetime.now()

    def get_history(self, limit: int = None) -> List[Dict[str, Any]]:
        """Get conversation history, optionally limited to recent messages."""
        if limit:
            return self.messages[-limit:]
        return self.messages

    def get_context_string(self) -> str:
        """Get formatted conversation history as context string."""
        if not self.messages:
            return ""

        context_parts = ["Previous conversation:"]
        for msg in self.messages[-10:]:  # Last 10 messages for context
            role = msg["role"].capitalize()
            content = msg["content"]
            context_parts.append(f"{role}: {content}")

        return "\n".join(context_parts)

    def clear_history(self):
        """Clear conversation history."""
        self.messages = []
        self.context = {}

    def is_expired(self, timeout_minutes: int = 60) -> bool:
        """Check if session has expired."""
        expiry_time = self.last_accessed + timedelta(minutes=timeout_minutes)
        return datetime.now() > expiry_time


class SessionManager:
    """Manages multiple conversation sessions."""

    def __init__(self, session_timeout_minutes: int = 60):
        self.sessions: Dict[str, ConversationSession] = {}
        self.session_timeout_minutes = session_timeout_minutes

    def create_session(self) -> str:
        """Create a new conversation session."""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = ConversationSession(session_id)
        return session_id

    def get_session(self, session_id: str) -> ConversationSession:
        """Get existing session or create new one if not found."""
        if session_id not in self.sessions:
            self.sessions[session_id] = ConversationSession(session_id)

        session = self.sessions[session_id]

        # Check if session expired
        if session.is_expired(self.session_timeout_minutes):
            # Create new session with same ID
            self.sessions[session_id] = ConversationSession(session_id)
            return self.sessions[session_id]

        return session

    def delete_session(self, session_id: str):
        """Delete a session."""
        if session_id in self.sessions:
            del self.sessions[session_id]

    def cleanup_expired_sessions(self):
        """Remove expired sessions."""
        expired_ids = [
            sid for sid, session in self.sessions.items()
            if session.is_expired(self.session_timeout_minutes)
        ]
        for sid in expired_ids:
            del self.sessions[sid]

    def get_session_count(self) -> int:
        """Get total number of active sessions."""
        return len(self.sessions)


# Global session manager instance
session_manager = SessionManager(session_timeout_minutes=60)
