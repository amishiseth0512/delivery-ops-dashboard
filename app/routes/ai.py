from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.schemas import AssistantRequest, AssistantResponse
from app.services.ai_assistant import AIAssistantError, ask_assistant

router = APIRouter(prefix="/api/ai", tags=["ai"])


@router.post("/assistant", response_model=AssistantResponse)
def assistant(
    body: AssistantRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    question = body.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        answer = ask_assistant(question, db)
    except AIAssistantError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    return {"answer": answer, "generated_at": datetime.now(timezone.utc)}
