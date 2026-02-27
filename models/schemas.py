from pydantic import BaseModel


class UploadRequest(BaseModel):
    text: str


class VivaAnswerRequest(BaseModel):
    submission_id: str
    answer: str
    attention_score: float
    risk_score: float