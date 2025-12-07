"""
Chatbot State Manager
Session store & TTL hooks for chatbot functionality
"""

import asyncio
import threading
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import time
import logging

from backend_app.chatbot.models.session_model import UserRole, ConversationState


@dataclass
class SessionData:
    """Session data structure"""
    id: str
    user_id: str
    platform: str
    platform_user_id: str
    user_role: UserRole
    state: ConversationState
    context: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    last_activity: datetime
    ttl_seconds: int


class StateManager:
    """Session store with TTL and thread-safe operations"""
    
    def __init__(self, default_ttl: int = 3600):  # 1 hour default TTL
        self.sessions: Dict[str, SessionData] = {}
        self.lock = threading.RLock()
        self.default_ttl = default_ttl
        self.cleanup_interval = 300  # 5 minutes
        self._cleanup_task = None
        self.logger = logging.getLogger(__name__)
        
        # Start cleanup task
        self._start_cleanup_task()
    
    def _start_cleanup_task(self):
        """Start background cleanup task"""
        if self._cleanup_task is None:
            self._cleanup_task = threading.Thread(
                target=self._cleanup_expired_sessions,
                daemon=True
            )
            self._cleanup_task.start()
    
    def create_session(
        self,
        session_id: str,
        user_id: str,
        platform: str,
        platform_user_id: str,
        user_role: UserRole,
        state: ConversationState = ConversationState.INITIALIZED,
        context: Optional[Dict[str, Any]] = None,
        ttl_seconds: Optional[int] = None
    ) -> SessionData:
        """Create a new session"""
        with self.lock:
            now = datetime.utcnow()
            session = SessionData(
                id=session_id,
                user_id=user_id,
                platform=platform,
                platform_user_id=platform_user_id,
                user_role=user_role,
                state=state,
                context=context or {},
                created_at=now,
                updated_at=now,
                last_activity=now,
                ttl_seconds=ttl_seconds or self.default_ttl
            )
            self.sessions[session_id] = session
            self.logger.info(f"Created session {session_id} for user {user_id}")
            return session
    
    def get_session(self, session_id: str) -> Optional[SessionData]:
        """Get session by ID"""
        with self.lock:
            session = self.sessions.get(session_id)
            if session:
                # Check if session is expired
                if self._is_expired(session):
                    self.delete_session(session_id)
                    return None
                
                # Update last activity
                session.last_activity = datetime.utcnow()
                return session
            return None
    
    def update_session(
        self,
        session_id: str,
        state: Optional[ConversationState] = None,
        context: Optional[Dict[str, Any]] = None,
        ttl_seconds: Optional[int] = None
    ) -> Optional[SessionData]:
        """Update session state and context"""
        with self.lock:
            session = self.sessions.get(session_id)
            if not session:
                return None
            
            # Check if session is expired
            if self._is_expired(session):
                self.delete_session(session_id)
                return None
            
            # Update session
            if state is not None:
                session.state = state
            if context is not None:
                session.context.update(context)
            if ttl_seconds is not None:
                session.ttl_seconds = ttl_seconds
            
            session.updated_at = datetime.utcnow()
            session.last_activity = datetime.utcnow()
            
            self.logger.debug(f"Updated session {session_id}")
            return session
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        with self.lock:
            if session_id in self.sessions:
                del self.sessions[session_id]
                self.logger.info(f"Deleted session {session_id}")
                return True
            return False
    
    def touch_session(self, session_id: str) -> bool:
        """Update last activity time for session"""
        with self.lock:
            session = self.sessions.get(session_id)
            if session and not self._is_expired(session):
                session.last_activity = datetime.utcnow()
                return True
            return False
    
    def get_user_sessions(self, user_id: str) -> List[SessionData]:
        """Get all active sessions for a user"""
        with self.lock:
            active_sessions = []
            now = datetime.utcnow()
            
            for session in list(self.sessions.values()):
                if (session.user_id == user_id and 
                    not self._is_expired(session)):
                    active_sessions.append(session)
                elif self._is_expired(session):
                    self.delete_session(session.id)
            
            return active_sessions
    
    def get_session_count(self) -> int:
        """Get total number of sessions"""
        with self.lock:
            return len(self.sessions)
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions and return count of removed sessions"""
        with self.lock:
            now = datetime.utcnow()
            expired_sessions = []
            
            for session_id, session in self.sessions.items():
                if self._is_expired(session):
                    expired_sessions.append(session_id)
            
            for session_id in expired_sessions:
                del self.sessions[session_id]
                self.logger.info(f"Cleaned up expired session {session_id}")
            
            return len(expired_sessions)
    
    def _cleanup_expired_sessions(self):
        """Background task to clean up expired sessions"""
        while True:
            try:
                removed_count = self.cleanup_expired_sessions()
                if removed_count > 0:
                    self.logger.info(f"Cleaned up {removed_count} expired sessions")
                time.sleep(self.cleanup_interval)
            except Exception as e:
                self.logger.error(f"Error in cleanup task: {e}")
                time.sleep(self.cleanup_interval)
    
    def _is_expired(self, session: SessionData) -> bool:
        """Check if session is expired"""
        now = datetime.utcnow()
        time_since_activity = now - session.last_activity
        return time_since_activity.total_seconds() > session.ttl_seconds
    
    def extend_session(self, session_id: str, additional_seconds: int) -> bool:
        """Extend session TTL by additional seconds"""
        with self.lock:
            session = self.sessions.get(session_id)
            if session and not self._is_expired(session):
                session.ttl_seconds += additional_seconds
                session.last_activity = datetime.utcnow()
                return True
            return False
    
    def get_session_ttl(self, session_id: str) -> Optional[int]:
        """Get remaining TTL for session in seconds"""
        with self.lock:
            session = self.sessions.get(session_id)
            if session and not self._is_expired(session):
                time_since_activity = datetime.utcnow() - session.last_activity
                remaining = session.ttl_seconds - time_since_activity.total_seconds()
                return max(0, int(remaining))
            return None
    
    def list_all_sessions(self) -> List[SessionData]:
        """List all active sessions"""
        with self.lock:
            active_sessions = []
            for session in list(self.sessions.values()):
                if not self._is_expired(session):
                    active_sessions.append(session)
                else:
                    self.delete_session(session.id)
            return active_sessions
    
    def clear_all_sessions(self) -> int:
        """Clear all sessions and return count"""
        with self.lock:
            count = len(self.sessions)
            self.sessions.clear()
            self.logger.info(f"Cleared {count} sessions")
            return count
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics"""
        with self.lock:
            total_sessions = len(self.sessions)
            active_sessions = 0
            expired_sessions = 0
            now = datetime.utcnow()
            
            for session in self.sessions.values():
                if self._is_expired(session):
                    expired_sessions += 1
                else:
                    active_sessions += 1
            
            return {
                "total_sessions": total_sessions,
                "active_sessions": active_sessions,
                "expired_sessions": expired_sessions,
                "cleanup_interval": self.cleanup_interval,
                "default_ttl": self.default_ttl
            }


# Global state manager instance
state_manager = StateManager()


# Redis backend (optional - for production use)
class RedisStateManager(StateManager):
    """Redis-based session store for production use"""
    
    def __init__(self, redis_url: str, default_ttl: int = 3600):
        try:
            import redis
            self.redis_client = redis.from_url(redis_url)
            self.redis_enabled = True
        except ImportError:
            self.redis_client = None
            self.redis_enabled = False
            logging.warning("Redis not available, falling back to in-memory store")
        
        super().__init__(default_ttl)
    
    def create_session(self, *args, **kwargs) -> SessionData:
        """Create session and store in Redis"""
        session = super().create_session(*args, **kwargs)
        if self.redis_enabled:
            self._store_in_redis(session)
        return session
    
    def get_session(self, session_id: str) -> Optional[SessionData]:
        """Get session from Redis or fallback to memory"""
        if self.redis_enabled:
            session = self._get_from_redis(session_id)
            if session:
                return session
        return super().get_session(session_id)
    
    def update_session(self, *args, **kwargs) -> Optional[SessionData]:
        """Update session in Redis and memory"""
        session = super().update_session(*args, **kwargs)
        if session and self.redis_enabled:
            self._store_in_redis(session)
        return session
    
    def delete_session(self, session_id: str) -> bool:
        """Delete session from Redis and memory"""
        result = super().delete_session(session_id)
        if self.redis_enabled:
            self._delete_from_redis(session_id)
        return result
    
    def _store_in_redis(self, session: SessionData):
        """Store session data in Redis"""
        try:
            import json
            session_data = {
                "id": session.id,
                "user_id": session.user_id,
                "platform": session.platform,
                "platform_user_id": session.platform_user_id,
                "user_role": session.user_role.value,
                "state": session.state.value,
                "context": session.context,
                "created_at": session.created_at.isoformat(),
                "updated_at": session.updated_at.isoformat(),
                "last_activity": session.last_activity.isoformat(),
                "ttl_seconds": session.ttl_seconds
            }
            key = f"session:{session.id}"
            self.redis_client.setex(
                key,
                session.ttl_seconds,
                json.dumps(session_data)
            )
        except Exception as e:
            logging.error(f"Failed to store session in Redis: {e}")
    
    def _get_from_redis(self, session_id: str) -> Optional[SessionData]:
        """Get session data from Redis"""
        try:
            import json
            key = f"session:{session_id}"
            data = self.redis_client.get(key)
            if data:
                session_data = json.loads(data)
                return SessionData(
                    id=session_data["id"],
                    user_id=session_data["user_id"],
                    platform=session_data["platform"],
                    platform_user_id=session_data["platform_user_id"],
                    user_role=UserRole(session_data["user_role"]),
                    state=ConversationState(session_data["state"]),
                    context=session_data["context"],
                    created_at=datetime.fromisoformat(session_data["created_at"]),
                    updated_at=datetime.fromisoformat(session_data["updated_at"]),
                    last_activity=datetime.fromisoformat(session_data["last_activity"]),
                    ttl_seconds=session_data["ttl_seconds"]
                )
        except Exception as e:
            logging.error(f"Failed to get session from Redis: {e}")
        return None
    
    def _delete_from_redis(self, session_id: str):
        """Delete session from Redis"""
        try:
            key = f"session:{session_id}"
            self.redis_client.delete(key)
        except Exception as e:
            logging.error(f"Failed to delete session from Redis: {e}")