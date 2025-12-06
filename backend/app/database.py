from typing import Optional, List
from datetime import datetime
import logging

from .blob_client import get_blob_client
from .models import UserSession, ChatMessage, SessionMetadata

logger = logging.getLogger(__name__)


class DatabaseService:
    """Service layer for database operations"""
    
    def __init__(self):
        self.client = get_blob_client()
    
    # ==================== Session Operations ====================
    
    def create_session(self, user_id: Optional[str] = None, device_info: Optional[dict] = None) -> UserSession:
        """Create a new user session"""
        session = UserSession(
            user_id=user_id,
            device_info=device_info
        )
        
        # Convert to dict
        session_dict = session.model_dump()
        
        # Upload to blob storage
        blob_path = f"sessions/{session.session_id}.json"
        self.client.upload_json(blob_path, session_dict)
        logger.info(f"Created session: {session.session_id}")
        
        return session
    
    def get_session(self, session_id: str) -> Optional[UserSession]:
        """Retrieve a session by ID"""
        blob_path = f"sessions/{session_id}.json"
        item = self.client.download_json(blob_path)
        if item:
            return UserSession(**item)
        return None
    
    def update_session(self, session_id: str, **kwargs) -> Optional[UserSession]:
        """Update session information"""
        session = self.get_session(session_id)
        if not session:
            logger.warning(f"Session {session_id} not found for update")
            return None
        
        # Update fields
        session.updated_at = datetime.utcnow()
        for key, value in kwargs.items():
            if hasattr(session, key):
                setattr(session, key, value)
        
        # Upload updated session to blob storage
        session_dict = session.model_dump()
        blob_path = f"sessions/{session.session_id}.json"
        self.client.upload_json(blob_path, session_dict)
        logger.info(f"Updated session: {session_id}")
        
        return session
    
    # ==================== Message Operations ====================
    
    def save_message(
        self,
        session_id: str,
        role: str,
        message_text: str,
        tokens_used: Optional[int] = None,
        model_version: Optional[str] = None
    ) -> ChatMessage:
        """Save a chat message"""
        message = ChatMessage(
            session_id=session_id,
            role=role,
            message_text=message_text,
            tokens_used=tokens_used,
            model_version=model_version
        )
        
        # Convert to dict
        message_dict = message.model_dump()
        
        # Upload to blob storage
        blob_path = f"messages/{session_id}/{message.message_id}.json"
        self.client.upload_json(blob_path, message_dict)
        logger.info(f"Saved message: {message.message_id} for session: {session_id}")
        
        return message
    
    def get_messages(
        self,
        session_id: str,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[ChatMessage]:
        """Retrieve messages for a session"""
        # List all message blobs for this session
        prefix = f"messages/{session_id}/"
        blob_paths = self.client.list_blobs(prefix)
        
        # Download all messages
        messages = []
        for blob_path in blob_paths:
            item = self.client.download_json(blob_path)
            if item:
                messages.append(ChatMessage(**item))
        
        # Sort by timestamp
        messages.sort(key=lambda m: m.timestamp)
        
        # Apply pagination
        if limit:
            messages = messages[offset:offset + limit]
        
        logger.info(f"Retrieved {len(messages)} messages for session: {session_id}")
        return messages
    
    def get_message_count(self, session_id: str) -> int:
        """Get total message count for a session"""
        prefix = f"messages/{session_id}/"
        blob_paths = self.client.list_blobs(prefix)
        return len(blob_paths)
    
    def delete_message(self, message_id: str, session_id: str):
        """Delete a specific message"""
        blob_path = f"messages/{session_id}/{message_id}.json"
        self.client.delete_blob(blob_path)
        logger.info(f"Deleted message: {message_id}")
    
    # ==================== Metadata Operations ====================
    
    def update_metadata(
        self,
        session_id: str,
        extension_version: Optional[str] = None,
        cluster_used: Optional[str] = None
    ) -> SessionMetadata:
        """Update or create session metadata"""
        metadata = SessionMetadata(
            session_id=session_id,
            extension_version=extension_version,
            cluster_used=cluster_used
        )
        
        # Convert to dict
        metadata_dict = metadata.model_dump()
        
        # Upload to blob storage
        blob_path = f"metadata/{session_id}.json"
        self.client.upload_json(blob_path, metadata_dict)
        logger.info(f"Updated metadata for session: {session_id}")
        
        return metadata
    
    def get_metadata(self, session_id: str) -> Optional[SessionMetadata]:
        """Retrieve session metadata"""
        blob_path = f"metadata/{session_id}.json"
        item = self.client.download_json(blob_path)
        if item:
            return SessionMetadata(**item)
        return None
    
    def update_last_active(self, session_id: str):
        """Update the last_active timestamp for a session"""
        metadata = self.get_metadata(session_id)
        
        if metadata:
            metadata.last_active = datetime.utcnow()
            metadata_dict = metadata.model_dump()
            blob_path = f"metadata/{session_id}.json"
            self.client.upload_json(blob_path, metadata_dict)
        else:
            # Create new metadata if it doesn't exist
            self.update_metadata(session_id)
        
        logger.info(f"Updated last_active for session: {session_id}")
    
    # ==================== Utility Operations ====================
    
    def get_recent_sessions(self, limit: int = 10) -> List[UserSession]:
        """Get most recent sessions"""
        # List all session blobs
        blob_paths = self.client.list_blobs("sessions/")
        
        # Download all sessions
        sessions = []
        for blob_path in blob_paths:
            item = self.client.download_json(blob_path)
            if item:
                sessions.append(UserSession(**item))
        
        # Sort by updated_at descending
        sessions.sort(key=lambda s: s.updated_at, reverse=True)
        
        # Return top N
        sessions = sessions[:limit]
        
        logger.info(f"Retrieved {len(sessions)} recent sessions")
        return sessions
    
    def delete_session_data(self, session_id: str):
        """Delete all data associated with a session"""
        # Delete session
        session_blob = f"sessions/{session_id}.json"
        self.client.delete_blob(session_blob)
        
        # Delete all messages
        message_prefix = f"messages/{session_id}/"
        message_blobs = self.client.list_blobs(message_prefix)
        for blob_path in message_blobs:
            self.client.delete_blob(blob_path)
        
        # Delete metadata
        metadata_blob = f"metadata/{session_id}.json"
        self.client.delete_blob(metadata_blob)
        
        logger.info(f"Deleted all data for session: {session_id}")


# Singleton instance
_db_service: Optional[DatabaseService] = None


def get_database_service() -> DatabaseService:
    """Get or create the database service singleton"""
    global _db_service
    if _db_service is None:
        _db_service = DatabaseService()
    return _db_service
