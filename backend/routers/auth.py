from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os

router = APIRouter()

class CodeRequest(BaseModel):
    code: str

@router.post("/verify-code")
def verify_code(req: CodeRequest):
    valid_codes = os.getenv("INVITE_CODES", "").split(",")
    valid_codes = [c.strip() for c in valid_codes if c.strip()]
    if req.code not in valid_codes:
        raise HTTPException(status_code=401, detail="Code invalide")
    return {"valid": True}
