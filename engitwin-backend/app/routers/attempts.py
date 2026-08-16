import datetime as dt

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.security import get_current_user
from app.services.ai_service import ai_service

router = APIRouter(tags=["attempts"])


def _score_attempt(experiment: models.Experiment, measurements: dict) -> float:
    """
    Simple scoring: compares submitted measurements against
    experiment.simulation_config['expected'] (if the lab author provided
    one), with a tolerance. Falls back to full marks if no expected
    values are configured, so this never blocks you - customize this
    function per-lab-type as needed.
    """
    expected = (experiment.simulation_config or {}).get("expected")
    if not expected:
        return experiment.max_score

    total = len(expected)
    if total == 0:
        return experiment.max_score

    points_per_item = experiment.max_score / total
    score = 0.0
    for key, target in expected.items():
        actual = measurements.get(key)
        if actual is None:
            continue
        try:
            tolerance = abs(target) * 0.05 if target else 0.05
            if abs(float(actual) - float(target)) <= tolerance:
                score += points_per_item
        except (TypeError, ValueError):
            if actual == target:
                score += points_per_item
    return round(score, 2)


@router.post("/attempts/start", response_model=schemas.AttemptOut)
def start_attempt(
    payload: schemas.AttemptStart,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    experiment = db.query(models.Experiment).filter(models.Experiment.id == payload.experiment_id).first()
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")

    attempt = models.ExperimentAttempt(
        experiment_id=payload.experiment_id,
        student_id=user.id,
        status=models.AttemptStatus.in_progress,
        simulation_data={},
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    return attempt


@router.patch("/attempts/{attempt_id}", response_model=schemas.AttemptOut)
def update_attempt(
    attempt_id: int,
    payload: schemas.AttemptUpdate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    """Called repeatedly while the student interacts with the simulation, to save live state."""
    attempt = db.query(models.ExperimentAttempt).filter(models.ExperimentAttempt.id == attempt_id).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")
    if attempt.student_id != user.id:
        raise HTTPException(status_code=403, detail="Not your attempt")

    attempt.simulation_data = payload.simulation_data
    db.commit()
    db.refresh(attempt)
    return attempt


@router.post("/attempts/{attempt_id}/complete", response_model=schemas.AttemptOut)
def complete_attempt(
    attempt_id: int,
    payload: schemas.AttemptComplete,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    attempt = db.query(models.ExperimentAttempt).filter(models.ExperimentAttempt.id == attempt_id).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")
    if attempt.student_id != user.id:
        raise HTTPException(status_code=403, detail="Not your attempt")

    experiment = attempt.experiment
    score = _score_attempt(experiment, payload.measurements)

    ai_feedback = ai_service.feedback(
        experiment_context={"title": experiment.title, "description": experiment.description},
        measurements=payload.measurements,
        score=score,
        max_score=experiment.max_score,
    )

    result = models.Result(
        attempt_id=attempt.id,
        measurements=payload.measurements,
        score=score,
        max_score=experiment.max_score,
        ai_feedback=ai_feedback,
    )
    db.add(result)

    attempt.status = models.AttemptStatus.completed
    attempt.completed_at = dt.datetime.utcnow()

    db.commit()
    db.refresh(attempt)
    return attempt


@router.get("/attempts/{attempt_id}", response_model=schemas.AttemptOut)
def get_attempt(attempt_id: int, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    attempt = db.query(models.ExperimentAttempt).filter(models.ExperimentAttempt.id == attempt_id).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")
    return attempt


@router.get("/attempts/mine", response_model=list[schemas.AttemptOut])
def my_attempts(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    return db.query(models.ExperimentAttempt).filter(models.ExperimentAttempt.student_id == user.id).all()
