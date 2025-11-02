from fastapi import FastAPI
from pydantic import BaseModel
from core.ai_service import AIService

# Pydantic models for data validation
class ChatRequest(BaseModel):
    message: str
    session_id: str

class ChatResponse(BaseModel):
    reply: str
    data: dict

app = FastAPI()
ai_service = AIService() # Initialize the AI service

@app.get("/")
def read_root():
    return {"message": "Welcome to the AI Trip Planner API"}

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    ai_reply = await ai_service.get_ai_response(request.message, request.session_id)
    return ChatResponse(
        reply=ai_reply,
        data={}
    )
