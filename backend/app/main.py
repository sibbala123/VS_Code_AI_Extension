from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="AI Assistant Backend")

# Request model
class Query(BaseModel):
    session_id: str
    question: str

@app.post("/query")
async def handle_query(query: Query):
    # For now, just echo the question
    return {"response": f"Echo: {query.question}"}