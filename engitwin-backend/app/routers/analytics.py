from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.security import get_current_user, require_role

router = APIRouter(prefix="/analytics", tags=["analytics"])


def _build_student_analytics(db: Session, student_id: int) -> schemas.StudentAnalytics:
    attempts = db.query(models.ExperimentAttempt).filter(models.ExperimentAttempt.student_id == student_id).all()
    completed = [a for a in attempts if a.status == models.AttemptStatus.completed and a.result]

    scores = [a.result.score for a in completed]
    average = round(sum(scores) / len(scores), 2) if scores else 0.0
    best = max(scores) if scores else 0.0

    per_experiment = []
    for a in completed:
        per_experiment.append({
            "experiment_id": a.experiment_id,
            "experiment_title": a.experiment.title,
            "attempt_id": a.id,
            "score": a.result.score,
            "max_score": a.result.max_score,
            "completed_at": a.completed_at.isoformat() if a.completed_at else None,
        })

    return schemas.StudentAnalytics(
        student_id=student_id,
        total_attempts=len(attempts),
        completed_attempts=len(completed),
        average_score=average,
        best_score=best,
        per_experiment=per_experiment,
    )


@router.get("/me", response_model=schemas.StudentAnalytics)
def my_analytics(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    return _build_student_analytics(db, user.id)


@router.get("/students/{student_id}", response_model=schemas.StudentAnalytics)
def student_analytics(
    student_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(require_role(models.UserRole.teacher, models.UserRole.institution_admin)),
):
    """Teachers/admins can pull analytics for any student to track progress."""
    target = db.query(models.User).filter(models.User.id == student_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Student not found")
    return _build_student_analytics(db, student_id)
