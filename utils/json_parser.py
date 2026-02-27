import json
from fastapi import HTTPException

def safe_parse(output: str):
    try:
        start = output.find("{")
        end = output.rfind("}") + 1
        return json.loads(output[start:end])
    except:
        raise HTTPException(status_code=500, detail="Invalid JSON from model")