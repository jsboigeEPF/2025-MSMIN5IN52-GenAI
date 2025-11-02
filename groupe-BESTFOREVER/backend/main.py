from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from core.ai_service import AIService

# Pydantic models for data validation
class ChatRequest(BaseModel):
    message: str
    session_id: str
    model_name: str # Added field for AI model selection

class ChatResponse(BaseModel):
    reply: str
    data: dict

app = FastAPI()

# Set up CORS
origins = [
    "http://localhost:5173", # Default Vite dev server
    "http://localhost:3000", # Common React dev server
    # In production, you would restrict this to your frontend's domain
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ai_service = AIService() # Initialize the AI service

@app.get("/")
def read_root():
    return {"message": "Welcome to the AI Trip Planner API"}

@app.get("/api/gemini/models")
async def list_gemini_models():
    return await ai_service.list_gemini_models()

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    ai_reply = await ai_service.get_ai_response(request.model_name, request.message, request.session_id)
    return ChatResponse(
        reply=ai_reply,
        data={}
    )
