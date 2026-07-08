import os
import json
import asyncio
import logging
from pathlib import Path
from typing import List

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import io
import csv

from .schemas import JobCreate, JobResponse, CandidateResponse, CandidateScore
from .database import get_db, JobDB, CandidateDB, Base, engine
from .file_parser import extract_text_from_file
from .scorer import score_candidate

"""
=============================================================================
LEARNING MODULE: FastAPI & Backend Architecture
=============================================================================
FastAPI is a modern, fast web framework for building APIs with Python 3.8+.
It is built on top of Starlette (for web routing) and Pydantic (for data validation).

Key Concepts Used Here:
1. CORS (Cross-Origin Resource Sharing): A security feature that prevents
   websites from making requests to a different domain. We use CORSMiddleware
   to allow our React frontend to talk to our FastAPI backend.
2. Dependency Injection (`Depends(get_db)`): FastAPI allows us to "inject" 
   database sessions into our endpoints automatically. This ensures our 
   DB connections are opened and safely closed for every single API request.
=============================================================================
"""

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize DB tables (redundant but safe)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI ATS API",
    description="Backend for the AI Applicant Tracking System.",
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
"""
LEARNING MODULE: WebSockets
HTTP is "stateless" and "unidirectional" (client asks, server answers).
WebSockets provide a "full-duplex" continuous connection, allowing the server
to push live updates (like AI processing progress) to the React frontend 
without the frontend needing to constantly refresh/poll.
"""
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast_progress(self, message: str, status: str = "info"):
        """Sends a JSON update to all connected clients."""
        dead = []
        for connection in self.active_connections:
            try:
                await connection.send_json({"status": status, "message": message})
            except Exception:
                dead.append(connection)
        for connection in dead:
            self.active_connections.remove(connection)

manager = ConnectionManager()

@app.websocket("/ws/progress")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection open
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# ---------------------------------------------------------------------------
# HTTP ENDPOINTS
# ---------------------------------------------------------------------------
"""
LEARNING MODULE: RESTful API Design
We use standard HTTP methods to interact with our resources:
- POST /jobs -> Create a new job
- GET /jobs -> Retrieve all jobs
- DELETE /jobs/clear -> Delete all jobs
- POST /jobs/{job_id}/candidates -> Upload resumes for a specific job
- GET /settings -> Retrieve AI configuration
- POST /settings -> Save AI configuration
"""

from .schemas import AISettingsBase, AISettingsResponse
from .database import SettingsDB, get_cipher

@app.get("/settings", response_model=AISettingsResponse)
def get_settings(db: Session = Depends(get_db)):
    """Retrieves the current AI configuration."""
    settings = db.query(SettingsDB).first()
    if not settings:
        raise HTTPException(status_code=404, detail="Settings not configured")
    
    return AISettingsResponse(
        provider_type=settings.provider_type,
        provider_name=settings.provider_name,
        base_url=settings.base_url,
        model_name=settings.model_name,
        has_api_key=bool(settings.api_key_encrypted)
    )

@app.post("/settings", response_model=AISettingsResponse)
def update_settings(settings_data: AISettingsBase, db: Session = Depends(get_db)):
    """Updates the global AI configuration."""
    settings = db.query(SettingsDB).first()
    if not settings:
        settings = SettingsDB()
        db.add(settings)

    settings.provider_type = settings_data.provider_type
    settings.provider_name = settings_data.provider_name
    settings.base_url = settings_data.base_url
    settings.model_name = settings_data.model_name

    # Encrypt API key if provided
    if settings_data.api_key:
        cipher = get_cipher()
        encrypted_key = cipher.encrypt(settings_data.api_key.encode()).decode()
        settings.api_key_encrypted = encrypted_key
    
    db.commit()
    db.refresh(settings)

    return AISettingsResponse(
        provider_type=settings.provider_type,
        provider_name=settings.provider_name,
        base_url=settings.base_url,
        model_name=settings.model_name,
        has_api_key=bool(settings.api_key_encrypted)
    )

@app.post("/jobs", response_model=JobResponse)
def create_job(job: JobCreate, db: Session = Depends(get_db)):
    """Creates a new Job Description profile to score resumes against."""
    db_job = JobDB(**job.model_dump())
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job

@app.get("/jobs", response_model=List[JobResponse])
def get_jobs(db: Session = Depends(get_db)):
    """Retrieves all jobs."""
    return db.query(JobDB).all()

@app.delete("/jobs/clear")
def clear_database(db: Session = Depends(get_db)):
    """Clears all jobs and candidates from the database (Hard Reset)."""
    db.query(CandidateDB).delete()
    db.query(JobDB).delete()
    db.commit()
    return {"message": "Database cleared successfully."}

@app.post("/jobs/{job_id}/candidates")
async def upload_candidates(
    job_id: int, 
    files: List[UploadFile] = File(...), 
    db: Session = Depends(get_db)
):
    """
    Bulk upload endpoint for resumes.
    Processes each resume against the job description using Gemini.
    Streams progress via WebSockets.
    """
    job_db = db.query(JobDB).filter(JobDB.id == job_id).first()
    if not job_db:
        raise HTTPException(status_code=404, detail="Job not found")

    MAX_FILES = 500
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    if len(files) > MAX_FILES:
        raise HTTPException(status_code=400, detail=f"Maximum {MAX_FILES} files allowed per batch.")

    job_create_model = JobCreate(
        title=job_db.title,
        required_skills=job_db.required_skills,
        min_experience_years=job_db.min_experience_years,
        education=job_db.education,
        additional_context=job_db.additional_context
    )

    await manager.broadcast_progress(f"Received {len(files)} resumes for batch processing...", "info")
    
    processed_candidates = []

    for idx, file in enumerate(files, 1):
        filename = file.filename
        await manager.broadcast_progress(f"[{idx}/{len(files)}] Parsing file: {filename}", "processing")
        
        try:
            # 1. Read & Extract Text
            file_bytes = await file.read()
            if len(file_bytes) > MAX_FILE_SIZE:
                await manager.broadcast_progress(f"[{idx}/{len(files)}] Skipped {filename}: exceeds 10MB size limit.", "error")
                continue
            raw_text = extract_text_from_file(file_bytes, filename)
            
            if not raw_text.strip():
                raise ValueError("Extracted text is empty. Might be an image/scanned PDF.")

            await manager.broadcast_progress(f"[{idx}/{len(files)}] AI Analyzing: {filename}", "processing")
            
            # 2. Score with Gemini / AI
            score_data = await score_candidate(job_create_model, raw_text, db)
            
            # 3. Save to DB
            candidate_db = CandidateDB(
                job_id=job_id,
                filename=filename,
                score_data_json=score_data.model_dump_json()
            )
            db.add(candidate_db)
            db.commit()
            db.refresh(candidate_db)
            
            processed_candidates.append(candidate_db)
            await manager.broadcast_progress(f"[{idx}/{len(files)}] Done: {score_data.candidate_name} scored {score_data.match_score}/100", "success")
            
        except Exception as e:
            logger.error(f"Failed to process {filename}: {str(e)}")
            await manager.broadcast_progress(f"[{idx}/{len(files)}] Error on {filename}: {str(e)}", "error")

    await manager.broadcast_progress("Batch processing complete!", "complete")
    return {"message": f"Processed {len(processed_candidates)} candidates"}

@app.get("/jobs/{job_id}/candidates")
def get_candidates(job_id: int, db: Session = Depends(get_db)):
    """Returns all candidates for a job, ranked by match score descending."""
    candidates = db.query(CandidateDB).filter(CandidateDB.job_id == job_id).all()
    
    # Parse JSON strings back into Pydantic models for the response
    results = []
    for c in candidates:
        score_data = CandidateScore.model_validate_json(c.score_data_json)
        results.append({
            "id": c.id,
            "job_id": c.job_id,
            "filename": c.filename,
            "score_data": score_data
        })
    
    # Sort by score descending
    results.sort(key=lambda x: x["score_data"].match_score, reverse=True)
    return results

@app.get("/jobs/{job_id}/export")
def export_candidates_csv(job_id: int, db: Session = Depends(get_db)):
    """Exports ranked candidates as a CSV file."""
    candidates = db.query(CandidateDB).filter(CandidateDB.job_id == job_id).all()
    
    results = []
    for c in candidates:
        score_data = CandidateScore.model_validate_json(c.score_data_json)
        results.append({
            "filename": c.filename,
            "candidate_name": score_data.candidate_name,
            "match_score": score_data.match_score,
            "verdict": score_data.verdict,
            "years_experience": score_data.years_experience,
            "extracted_skills": ", ".join(score_data.extracted_skills),
            "key_strengths": " | ".join(score_data.key_strengths),
            "concerns": " | ".join(score_data.concerns)
        })
    
    results.sort(key=lambda x: x["match_score"], reverse=True)

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=[
        "candidate_name", "match_score", "verdict", "years_experience", 
        "extracted_skills", "key_strengths", "concerns", "filename"
    ])
    
    writer.writeheader()
    writer.writerows(results)
    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=job_{job_id}_candidates.csv"}
    )

# Serve Frontend last so it doesn't intercept API routes
app.mount("/", StaticFiles(directory=Path(__file__).parent.parent / "frontend" / "dist", html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    logger.info("Extraction Agent API starting up...")
    logger.info("Docs available at: http://localhost:8000/docs")
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
