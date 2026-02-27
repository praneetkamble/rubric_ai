from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uuid
import logging

from models.schemas import UploadRequest, VivaAnswerRequest
from services.ai_service import run_model
from utils.json_parser import safe_parse

app = FastAPI()

logging.basicConfig(level=logging.INFO)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

fake_db = {}

# ----------------------------
# Root
# ----------------------------

@app.get("/")
def root():
    return {"message": "Backend running 🚀"}

# ----------------------------
# Upload Submission
# ----------------------------

@app.post("/api/upload")
def upload(data: UploadRequest):

    submission_id = str(uuid.uuid4())

    fake_db[submission_id] = {
        "text": data.text,
        "evaluation": None,
        "viva_questions": None,
    }

    return {
        "submission_id": submission_id,
        "status": "uploaded"
    }

# ----------------------------
# Evaluate Submission (Ollama)
# ----------------------------

@app.post("/api/evaluate/{submission_id}")
def evaluate(submission_id: str):

    if submission_id not in fake_db:
        raise HTTPException(status_code=404, detail="Submission not found")

    submission_text = fake_db[submission_id]["text"]

    prompt = f"""
    Evaluate this academic submission and return JSON:

    {{
        "total_score": number,
        "clarity": number,
        "technical_depth": number,
        "originality": number,
        "feedback": "detailed explanation"
    }}

    Submission:
    {submission_text}
    """

    logging.info(f"Evaluating submission {submission_id}")

    output = run_model(prompt)
    result = safe_parse(output)

    fake_db[submission_id]["evaluation"] = result

    return result

# ----------------------------
# Generate Viva Questions
# ----------------------------

@app.post("/api/generate-viva/{submission_id}")
def generate_viva(submission_id: str):

    if submission_id not in fake_db:
        raise HTTPException(status_code=404, detail="Submission not found")

    submission_text = fake_db[submission_id]["text"]

    prompt = f"""
    Generate 3 deep conceptual viva questions for:

    {submission_text}

    Return JSON:
    {{
        "questions": ["q1", "q2", "q3"]
    }}
    """

    output = run_model(prompt)
    result = safe_parse(output)

    fake_db[submission_id]["viva_questions"] = result["questions"]

    return result

# ----------------------------
# Analyze Viva Answer (Scoring Logic)
# ----------------------------

@app.post("/api/analyze-viva")
def analyze_viva(data: VivaAnswerRequest):

    answer_length = len(data.answer.split())

    concept_score = min(answer_length * 1.5, 100)

    engagement_score = data.attention_score

    final_score = (concept_score * 0.6) + (engagement_score * 0.4)

    risk_level = "High" if data.risk_score > 60 else "Low"

    return {
        "concept_score": round(concept_score, 2),
        "engagement_score": round(engagement_score, 2),
        "final_score": round(final_score, 2),
        "risk_level": risk_level
    }

# ----------------------------
# Final Report
# ----------------------------

@app.get("/api/report/{submission_id}")
def get_report(submission_id: str):

    if submission_id not in fake_db:
        raise HTTPException(status_code=404, detail="Submission not found")

    return fake_db[submission_id]