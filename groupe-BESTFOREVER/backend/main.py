from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from core.ai_service import AIService
from typing import List, Optional

# Pydantic models for data validation
class Message(BaseModel):
    text: str
    isUser: bool

class ChatRequest(BaseModel):
    history: List[Message]
    session_id: str
    model_name: str
    language: Optional[str] = 'en-US' # Add language field

class ChatResponse(BaseModel):
    reply: str
    data: dict

app = FastAPI()

ai_service = AIService()

# Set up CORS
origins = [
    "http://localhost:5173", # Default Vite dev server
    "http://localhost:3000", # Common React dev server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the AI Trip Planner API"}

@app.get("/api/gemini/models")
async def list_gemini_models():
    return await ai_service.list_gemini_models()

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    ai_reply = await ai_service.get_ai_response(
        model_name=request.model_name, 
        history=request.history, 
        session_id=request.session_id,
        language=request.language
    )
    return ChatResponse(
        reply=ai_reply,
        data={}
    )
