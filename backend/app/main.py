from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import os

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AI Assistant Backend")

# Enable CORS so VS Code webview can call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can replace "*" with allowed origins for more security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama-service:11434")

# Optional: Add /health endpoint to satisfy liveness/readiness probes
@app.get("/health")
async def health_check():
    return {"status": "ok"}

# Request model
class Query(BaseModel):
    session_id: str
    question: str
    model: str = "qwen2.5:1.5b"

@app.post("/query")
async def handle_query(query: Query):
    """
    Receives user queries, sends them to the AI model (Ollama), and returns the response.
    """
    try:
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
            
            # Return the JSON response from Ollama
            return response.json()
            
    except httpx.RequestError as exc:
        raise HTTPException(status_code=503, detail=f"An error occurred while requesting {exc.request.url!r}.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
