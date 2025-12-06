from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import os
import logging

from fastapi.middleware.cors import CORSMiddleware
from .database import get_database_service
from .models import (
    CreateSessionRequest, 
    CreateSessionResponse, 
    SaveMessageRequest,
    GetMessagesResponse,
    SessionMetadata
)
from .config import get_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Assistant Backend")

# Enable CORS so VS Code webview can call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can replace "*" with allowed origins for more security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration from Key Vault or environment
config = get_config()
OLLAMA_URL = config.ollama_url

# Initialize database service
try:
    db_service = get_database_service()
    logger.info("Database service initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize database service: {e}")
    db_service = None

# Optional: Add /health endpoint to satisfy liveness/readiness probes
@app.get("/health")
async def health_check():
    return {"status": "ok", "database": "connected" if db_service else "disconnected"}

# ==================== Session Endpoints ====================

@app.post("/sessions", response_model=CreateSessionResponse)
async def create_session(request: CreateSessionRequest):
    """Create a new user session"""
    if not db_service:
        raise HTTPException(status_code=503, detail="Database service unavailable")
    
    try:
        session = db_service.create_session(
            user_id=request.user_id,
            device_info=request.device_info
        )
        
        # Initialize metadata
        db_service.update_metadata(session.session_id)
        
        return CreateSessionResponse(
            session_id=session.session_id,
            created_at=session.created_at
        )
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """Retrieve session information"""
    if not db_service:
        raise HTTPException(status_code=503, detail="Database service unavailable")
    
    try:
        session = db_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return session
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Message Endpoints ====================

@app.post("/messages")
async def save_message(request: SaveMessageRequest):
    """Save a chat message"""
    if not db_service:
        raise HTTPException(status_code=503, detail="Database service unavailable")
    
    try:
        message = db_service.save_message(
            session_id=request.session_id,
            role=request.role,
            message_text=request.message_text,
            tokens_used=request.tokens_used,
            model_version=request.model_version
        )
        
        # Update last_active timestamp
        db_service.update_last_active(request.session_id)
        
        return message
    except Exception as e:
        logger.error(f"Error saving message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sessions/{session_id}/messages", response_model=GetMessagesResponse)
async def get_messages(session_id: str, limit: int = 100, offset: int = 0):
    """Retrieve messages for a session"""
    if not db_service:
        raise HTTPException(status_code=503, detail="Database service unavailable")
    
    try:
        messages = db_service.get_messages(session_id, limit=limit, offset=offset)
        total_count = db_service.get_message_count(session_id)
        
        return GetMessagesResponse(
            session_id=session_id,
            messages=messages,
            total_count=total_count
        )
    except Exception as e:
        logger.error(f"Error retrieving messages: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Metadata Endpoints ====================

@app.put("/sessions/{session_id}/metadata")
async def update_metadata(session_id: str, extension_version: str = None, cluster_used: str = None):
    """Update session metadata"""
    if not db_service:
        raise HTTPException(status_code=503, detail="Database service unavailable")
    
    try:
        metadata = db_service.update_metadata(
            session_id=session_id,
            extension_version=extension_version,
            cluster_used=cluster_used
        )
        return metadata
    except Exception as e:
        logger.error(f"Error updating metadata: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sessions/{session_id}/metadata")
async def get_metadata(session_id: str):
    """Retrieve session metadata"""
    if not db_service:
        raise HTTPException(status_code=503, detail="Database service unavailable")
    
    try:
        metadata = db_service.get_metadata(session_id)
        if not metadata:
            raise HTTPException(status_code=404, detail="Metadata not found")
        return metadata
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving metadata: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Query Endpoint (Updated) ====================

# Request model
class Query(BaseModel):
    session_id: str
    question: str
    model: str = "qwen2.5:1.5b"
    extension_version: str = None

@app.post("/query")
async def handle_query(query: Query):
    """
    Receives user queries, sends them to the AI model (Ollama), and returns the response.
    Now also persists messages and updates metadata.
    """
    try:
        # Save user message to database
        if db_service:
            try:
                db_service.save_message(
                    session_id=query.session_id,
                    role="user",
                    message_text=query.question,
                    model_version=query.model
                )
                
                # Update metadata
                if query.extension_version:
                    db_service.update_metadata(
                        session_id=query.session_id,
                        extension_version=query.extension_version,
                        cluster_used=OLLAMA_URL
                    )
            except Exception as e:
                logger.error(f"Error saving user message: {e}")
        
        # Construct the payload for Ollama
        payload = {
            "model": query.model,
            "prompt": query.question,
            "stream": False
        }
        
        # Call Ollama service
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=60.0)
            
            # Check if the request was successful
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=f"Ollama Error: {response.text}")
            
            # Get the response from Ollama
            ollama_response = response.json()
            
            # Save model response to database
            if db_service:
                try:
                    db_service.save_message(
                        session_id=query.session_id,
                        role="model",
                        message_text=ollama_response.get("response", ""),
                        tokens_used=ollama_response.get("eval_count"),
                        model_version=query.model
                    )
                    
                    # Update last_active
                    db_service.update_last_active(query.session_id)
                except Exception as e:
                    logger.error(f"Error saving model response: {e}")
            
            # Return the JSON response from Ollama
            return ollama_response
            
    except httpx.RequestError as exc:
        raise HTTPException(status_code=503, detail=f"An error occurred while requesting {exc.request.url!r}.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Utility Endpoints ====================

@app.get("/sessions")
async def get_recent_sessions(limit: int = 10):
    """Get recent sessions"""
    if not db_service:
        raise HTTPException(status_code=503, detail="Database service unavailable")
    
    try:
        sessions = db_service.get_recent_sessions(limit=limit)
        return sessions
    except Exception as e:
        logger.error(f"Error retrieving recent sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a session and all associated data"""
    if not db_service:
        raise HTTPException(status_code=503, detail="Database service unavailable")
    
    try:
        db_service.delete_session_data(session_id)
        return {"message": "Session deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

