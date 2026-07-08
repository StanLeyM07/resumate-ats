import os
import json
import asyncio
import logging
from pathlib import Path
from typing import List, Dict

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, WebSocket, WebSocketDisconnect, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .schemas import JobCreate, CandidateScore
from .file_parser import extract_text_from_file
from .scorer import score_candidate

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI ATS API (Stateless)",
    description="Stateless Backend for the AI Applicant Tracking System.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8000"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# WEBSOCKET MANAGER FOR REAL-TIME PROGRESS
# ---------------------------------------------------------------------------
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, client_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]

    async def send_progress(self, client_id: str, message: str, status: str = "info"):
        """Sends a JSON update to a specific client."""
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_json({"status": status, "message": message})
            except Exception:
                self.disconnect(client_id)

manager = ConnectionManager()

@app.websocket("/ws/progress/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(client_id, websocket)
    try:
        while True:
            # Keep connection open
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(client_id)

# ---------------------------------------------------------------------------
# HTTP ENDPOINTS
# ---------------------------------------------------------------------------

@app.post("/api/score_candidates")
async def score_candidates(
    client_id: str = Form(...),
    job_title: str = Form(...),
    job_skills: str = Form(...),
    job_experience: int = Form(...),
    job_education: str = Form(...),
    job_context: str = Form(None),
    files: List[UploadFile] = File(...), 
    x_ai_provider_type: str | None = Header(None),
    x_ai_provider_name: str | None = Header(None),
    x_ai_base_url: str | None = Header(None),
    x_ai_model_name: str | None = Header(None),
    x_ai_api_key: str | None = Header(None)
):
    """
    Stateless endpoint for scoring resumes against a provided job description.
    Processes each resume using AI and returns the evaluated JSON objects directly.
    Streams progress via WebSockets specific to the client_id.
    """
    MAX_FILES = 500
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    if len(files) > MAX_FILES:
        raise HTTPException(status_code=400, detail=f"Maximum {MAX_FILES} files allowed per batch.")

    job_create_model = JobCreate(
        title=job_title,
        required_skills=job_skills,
        min_experience_years=job_experience,
        education=job_education,
        additional_context=job_context
    )

    await manager.send_progress(client_id, f"Received {len(files)} resumes for batch processing...", "info")
    
    processed_candidates = []

    for idx, file in enumerate(files, 1):
        filename = file.filename
        await manager.send_progress(client_id, f"[{idx}/{len(files)}] Parsing file: {filename}", "processing")
        
        try:
            # 1. Read & Extract Text
            file_bytes = await file.read()
            if len(file_bytes) > MAX_FILE_SIZE:
                await manager.send_progress(client_id, f"[{idx}/{len(files)}] Skipped {filename}: exceeds 10MB size limit.", "error")
                continue
            raw_text = extract_text_from_file(file_bytes, filename)
            
            if not raw_text.strip():
                raise ValueError("Extracted text is empty. Might be an image/scanned PDF.")

            await manager.send_progress(client_id, f"[{idx}/{len(files)}] AI Analyzing: {filename}", "processing")
            
            # 2. Score with AI
            ai_config = {
                "provider_type": x_ai_provider_type,
                "provider_name": x_ai_provider_name,
                "base_url": x_ai_base_url,
                "model_name": x_ai_model_name,
                "api_key": x_ai_api_key
            }
            score_data = await score_candidate(job_create_model, raw_text, ai_config)
            
            # 3. Append to memory response
            processed_candidates.append({
                "id": str(idx), # Dummy ID for React frontend mapping
                "filename": filename,
                "score_data": score_data.model_dump()
            })
            
            await manager.send_progress(client_id, f"[{idx}/{len(files)}] Done: {score_data.candidate_name} scored {score_data.match_score}/100", "success")
            
        except Exception as e:
            logger.error(f"Failed to process {filename}: {str(e)}")
            await manager.send_progress(client_id, f"[{idx}/{len(files)}] Error on {filename}: {str(e)}", "error")

    await manager.send_progress(client_id, "Batch processing complete!", "complete")
    
    # Sort locally before returning
    processed_candidates.sort(key=lambda x: x["score_data"]["match_score"], reverse=True)
    return processed_candidates

# Serve Frontend last so it doesn't intercept API routes
app.mount("/", StaticFiles(directory=Path(__file__).parent.parent / "frontend" / "dist", html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    logger.info("Extraction Agent API starting up (Stateless)...")
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
