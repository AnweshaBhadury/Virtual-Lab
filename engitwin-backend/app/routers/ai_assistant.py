from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.security import get_current_user
from app.services.ai_service import ai_service

router = APIRouter(prefix="/ai", tags=["ai assistant"])


@router.post("/ask", response_model=schemas.AIMessageOut)
def ask(
    payload: schemas.AIAskRequest,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    """
    Call this once when a lab attempt starts (student_message=null) to get
    the assistant's opening question, then again after each student reply
    to keep the conversation going.
    """
    attempt = db.query(models.ExperimentAttempt).filter(models.ExperimentAttempt.id == payload.attempt_id).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")
    if attempt.student_id != user.id:
        raise HTTPException(status_code=403, detail="Not your attempt")

    # log the student's message, if any
    if payload.student_message:
        db.add(models.AIMessage(attempt_id=attempt.id, role="student", content=payload.student_message))
        db.commit()

    history = (
        db.query(models.AIMessage)
        .filter(models.AIMessage.attempt_id == attempt.id)
        .order_by(models.AIMessage.created_at)
        .all()
    )
    conversation = [{"role": m.role, "content": m.content} for m in history]

    experiment = attempt.experiment
    reply_text = ai_service.ask(
        experiment_context={
            "title": experiment.title,
            "description": experiment.description,
            "simulation_data": attempt.simulation_data,
        },
        conversation=conversation,
    )

    reply = models.AIMessage(attempt_id=attempt.id, role="assistant", content=reply_text)
    db.add(reply)
    db.commit()
    db.refresh(reply)
    return reply


@router.get("/attempts/{attempt_id}/history", response_model=list[schemas.AIMessageOut])
def get_history(attempt_id: int, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    attempt = db.query(models.ExperimentAttempt).filter(models.ExperimentAttempt.id == attempt_id).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")
    if attempt.student_id != user.id:
        raise HTTPException(status_code=403, detail="Not your attempt")

    return (
        db.query(models.AIMessage)
        .filter(models.AIMessage.attempt_id == attempt_id)
        .order_by(models.AIMessage.created_at)
        .all()
    )
