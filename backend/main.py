"""FastAPI backend for AI DataLab."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os
from dotenv import load_dotenv
import uuid
import asyncio
import json

from agent.graph import agent, AgentState
from agent.nodes import get_sse_events, add_sse_event

# Load environment variables
load_dotenv()

app = FastAPI(title="AI DataLab API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5175", "http://127.0.0.1:5175"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session storage (simple for MVP)
sessions: Dict[str, Dict[str, Any]] = {}


class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str


@app.get("/")
async def root():
    return {"message": "AI DataLab API", "status": "running"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(chat_message: ChatMessage):
    """Process chat message and return response."""
    
    # Get or create session
    session_id = chat_message.session_id or str(uuid.uuid4())
    
    if session_id not in sessions:
        sessions[session_id] = {
            "conversation_history": [],
            "created_at": None
        }
    
    # Add user message to history
    sessions[session_id]["conversation_history"].append({
        "role": "user",
        "content": chat_message.message
    })
    
    # Prepare agent state
    initial_state: AgentState = {
        "session_id": session_id,
        "user_message": chat_message.message,
        "conversation_history": sessions[session_id]["conversation_history"],
        "intent": {},
        "analysis_result": {},
        "dataframe": None,
        "response": ""
    }
    
    try:
        # Run the agent
        final_state = agent.invoke(initial_state)
        
        # Get response
        response_text = final_state.get("response", "Desculpe, não consegui processar sua solicitação.")
        
        # Add assistant response to history
        sessions[session_id]["conversation_history"].append({
            "role": "assistant",
            "content": response_text
        })
        
        return ChatResponse(
            response=response_text,
            session_id=session_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")


@app.get("/api/stream/{session_id}")
async def stream_events(session_id: str):
    """SSE endpoint for real-time preview updates."""
    
    async def event_generator():
        """Generate SSE events from the session's event queue."""
        try:
            while True:
                events = get_sse_events(session_id)
                
                for event in events:
                    yield {
                        "event": event["type"],
                        "data": json.dumps(event["data"])
                    }
                
                # Small delay to avoid busy waiting
                await asyncio.sleep(0.5)
        except Exception as e:
            print(f"SSE error: {e}")
            yield {
                "event": "error",
                "data": json.dumps({"message": str(e)})
            }
    
    return EventSourceResponse(event_generator())


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "openai_configured": bool(os.getenv("OPENAI_API_KEY"))
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("BACKEND_PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

