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
    language: Optional[str] = 'en-US'

class ChatResponse(BaseModel):
    reply: str
    data: dict

app = FastAPI()

ai_service = AIService()

# ✅ CORS - Allow ALL origins (simplified)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=False,  # Must be False when using "*"
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the AI Trip Planner API", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/api/gemini/models")
async def list_gemini_models():
    try:
        return await ai_service.list_gemini_models()
    except Exception as e:
        return {"error": str(e), "models": []}

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
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
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return ChatResponse(
            reply=f"Sorry, an error occurred: {str(e)}",
            data={"error": str(e)}
        )