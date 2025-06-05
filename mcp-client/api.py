from typing import List, Dict, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from mcp import ClientSession
from client import MCPClient
from pydantic import BaseModel
import uuid

app = FastAPI(title="MCP Client API")

# Add CORS middleware to allow React frontend to call our API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your React app's domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    message: str

class ChatMessage:
    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content

class ChatSession:
    def __init__(self, messages: List[ChatMessage], client: MCPClient):
        self.messages = messages
        self.client = client

# Store active sessions
sessions: Dict[str, ChatSession] = {}

@app.get("/chat/start")
async def start_chat():
    """Start a new chat session. Initializes a new session with a new MCPClient"""
    session_id = str(uuid.uuid4())
    client = MCPClient()
    
    try:
        await client.connect_to_mcp_server()
        sessions[session_id] = ChatSession(messages=[], client=client)
        return {"session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/{session_id}/message")
async def send_message(session_id: str, message: Message):
    """Send a message in an existing chat session"""
    message = message.message
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    chat_session = sessions[session_id]
    client = chat_session.client
    messages = chat_session.messages
    messages.append(ChatMessage(role="user", content=message))
    
    try:
        response = await client.process_antropic_query(message)
        assistant_message = ChatMessage(role="assistant", content=response)
        messages.append(assistant_message)
        return {"response": response, "messages": messages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/chat/{session_id}/history")
async def get_chat_history(session_id: str):
    """Get the chat history for a session"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    chat_session = sessions[session_id]
    return {"messages": chat_session.messages}

@app.delete("/chat/{session_id}")
async def end_chat(session_id: str):
    """End a chat session and cleanup resources"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    chat_session = sessions[session_id]
    await chat_session.client.cleanup()
    del sessions[session_id]
    return {"status": "success"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8050)
