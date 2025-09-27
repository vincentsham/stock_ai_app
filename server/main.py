from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ai_agent.graph import generate_chat_responses
from fastapi.responses import StreamingResponse
from fastapi import Query
from typing import Optional

# Initialize FastAPI app
app = FastAPI()

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Type"],
)

@app.get("/chat_stream/{message}")
async def chat_stream(message: str, checkpoint_id: Optional[str] = Query(None)):
    return StreamingResponse(
        generate_chat_responses(message, checkpoint_id), 
        media_type="text/event-stream"
    )

@app.get("/")
async def root():
    return {"message": "Welcome to the API!"}
