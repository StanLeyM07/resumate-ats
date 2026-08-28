"""
=============================================================================
LEARNING MODULE: LLMs, Prompts, and Structured Extraction
=============================================================================
This file handles the communication with the AI model (via NVIDIA NIM or any 
OpenAI-compatible API).

Key Concepts Used Here:
1. System Prompt vs User Prompt: 
   - System Prompt: Defines the AI's persona, rules, and constraints.
   - User Prompt: The actual data we want processed (resume + job description).
2. Structured Data Output (JSON Mode): Modern LLMs can be forced to output
   strictly formatted JSON that matches a Pydantic schema.
3. asyncio.to_thread(): The OpenAI SDK's synchronous `create()` call would 
   block the entire FastAPI event loop. We wrap it in `asyncio.to_thread()` 
   to run it in a separate thread, keeping the server responsive.
=============================================================================
"""

import os
import re
import json
import asyncio
import logging
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

from .schemas import JobCreate, CandidateScore

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You are an expert Technical Recruiter and AI ATS (Applicant Tracking System).
Your job is to deeply analyze a candidate's resume against a specific Job Description.

You must not only match keywords, but evaluate the *context* and *depth* of their experience, their potential based on past projects, and their overall fit for the role.
CRITICAL: Do NOT copy-paste bullet points from the candidate's experience or resume. You must synthesize and write your own independent analysis. When listing "key_strengths", judge how well their actual skills and accomplishments map to the Job Description's requirements.

Evaluate the resume and output a JSON object strictly matching this schema:
{
    "candidate_name": "String",
    "match_score": Integer (0 to 100),
    "verdict": "String (Short 2-3 word verdict like 'Strong Match', 'Lacks Experience')",
    "extracted_skills": ["List of strings"],
    "years_experience": Float (Estimated total years),
    "key_strengths": ["2-3 concise bullet points analyzing their specific skills and why they are a strong fit for the required role. Do NOT copy-paste from the resume."],
    "concerns": ["1-2 bullet points analyzing any missing required skills or potential red flags. Do NOT copy-paste."]
}

IMPORTANT: You must return ONLY valid JSON. Do not wrap the JSON in markdown formatting (like ```json), and do not include any other text before or after the JSON.
"""

def parse_model_json(raw_response: str) -> dict:
    """Turn a raw model response into a dict, tolerating markdown fences.

    Pure and synchronous on purpose: this is the part that breaks in production
    (models ignore "return only JSON" instructions often enough to matter), so
    it must be testable without an API key or a network call. See
    tests/test_scorer.py.

    Handles the fence variants actually observed: ```json, ```JSON, a bare
    ```, and prose before or after the block.
    """
    if raw_response is None:
        raise ValueError("Model returned no content.")

    text = raw_response.strip()

    # A fenced block anywhere in the response wins over surrounding prose.
    fence = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if fence:
        text = fence.group(1).strip()
    else:
        # No closing fence (truncated output): drop an opening fence if present.
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE).strip()
        # Otherwise fall back to the outermost braces, ignoring any prose.
        if not text.startswith("{"):
            braces = re.search(r"\{.*\}", text, re.DOTALL)
            if braces:
                text = braces.group(0)

    if not text:
        raise ValueError("Model returned an empty response.")

    return json.loads(text)


def _sync_score_candidate(prompt: str, api_key: str, base_url: str, model_name: str) -> str:
    """Synchronous helper that performs the blocking OpenAI API call using dynamic settings."""
    client = OpenAI(
        base_url=base_url,
        api_key=api_key or "dummy_key"
    )
    
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
        max_tokens=1024,
        response_format={ "type": "json_object" }
    )
    return response.choices[0].message.content

async def score_candidate(job: JobCreate, resume_text: str, ai_config: dict) -> CandidateScore:
    """
    Sends the Job Description and the Resume text to the configured AI provider to generate a CandidateScore.
    """
    # 1. Check if user provided an API Key via Headers
    api_key = ai_config.get("api_key")
    base_url = ai_config.get("base_url") or "https://integrate.api.nvidia.com/v1"
    model_name = ai_config.get("model_name") or "meta/llama-3.1-70b-instruct"

    # 2. If no API key was provided by the user, fallback to our Render environment variable!
    if not api_key:
        # Fallback to NVIDIA NIM (or Google Gemini if you prefer)
        api_key = os.getenv("NVIDIA_API_KEY")
        if not api_key:
            raise ValueError("No API key provided by user, and no fallback NVIDIA_API_KEY found in server environment.")

    prompt = f"""
    --- JOB DESCRIPTION ---
    Title: {job.title}
    Required Skills: {job.required_skills}
    Minimum Experience: {job.min_experience_years} years
    Education Requirement: {job.education or 'None specified'}
    Additional Context: {job.additional_context or 'None'}

    --- CANDIDATE RESUME ---
    {resume_text}

    Analyze the candidate against the job description and return the JSON score.
    """

    try:
        raw_response = await asyncio.to_thread(
            _sync_score_candidate, prompt, api_key, base_url, model_name
        )
        logger.info(f"AI Raw Response: {raw_response[:100]}...")

        # Parse JSON (tolerating markdown fences) and validate against the schema
        data_dict = parse_model_json(raw_response)
        score_data = CandidateScore(**data_dict)
        return score_data

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON from AI: {e}\nRaw Text: {raw_response}")
        raise ValueError("AI returned malformed JSON.")
    except Exception as e:
        logger.error(f"AI API error during scoring: {str(e)}")
        raise

