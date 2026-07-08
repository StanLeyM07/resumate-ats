from pydantic import BaseModel, Field
from typing import List, Optional

"""
=============================================================================
LEARNING MODULE: Pydantic Data Validation
=============================================================================
Pydantic is a library used heavily in FastAPI for data parsing and validation.
We define classes (schemas) that inherit from `BaseModel`.

Why use Pydantic?
1. Type Hinting: It uses Python type hints (`int`, `str`, `List`) to guarantee 
   that incoming/outgoing data is the correct type.
2. Structured LLM Output: We pass these exact schemas to the NVIDIA NIM/OpenAI 
   SDK. The LLM uses the `Field(description="...")` metadata to understand 
   exactly how to format its JSON response, ensuring we never get broken JSON.
=============================================================================
"""

# --- JOB DESCRIPTION SCHEMAS (Input from Recruiter) ---

class JobCreate(BaseModel):
    title: str = Field(..., description="The job title, e.g., 'Senior Backend Engineer'")
    required_skills: str = Field(..., description="Comma-separated list of required skills")
    min_experience_years: int = Field(..., description="Minimum years of experience required")
    education: str = Field(..., description="Degree or education requirements")
    additional_context: Optional[str] = Field(None, description="Any other details, like 'Looking for leadership potential'")

class JobResponse(JobCreate):
    id: int

# --- AI SCORING SCHEMAS (Output from Gemini) ---

class CandidateScore(BaseModel):
    candidate_name: str = Field(..., description="The name of the candidate extracted from the resume")
    match_score: int = Field(..., ge=0, le=100, description="A score from 0 to 100 representing how well the candidate matches the job description")
    verdict: str = Field(..., description="A short 2-3 word verdict (e.g., 'Strong Match', 'Lacks Experience', 'High Potential')")
    extracted_skills: List[str] = Field(..., description="A list of the core skills extracted from the resume")
    years_experience: float = Field(..., description="Estimated total years of professional experience")
    key_strengths: List[str] = Field(..., description="2-3 bullet points highlighting why they fit the role based on projects/experience")
    concerns: List[str] = Field(..., description="1-2 bullet points highlighting missing skills or red flags")

# --- API RESPONSE SCHEMAS ---

class CandidateResponse(BaseModel):
    id: int
    job_id: int
    filename: str
    score_data: CandidateScore


