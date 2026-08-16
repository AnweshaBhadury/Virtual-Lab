from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.security import get_current_user, require_role

router = APIRouter(tags=["labs"])


# ---------------- Labs ----------------

@router.post("/labs", response_model=schemas.LabOut)
def create_lab(
    payload: schemas.LabCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(require_role(models.UserRole.teacher, models.UserRole.institution_admin, models.UserRole.independent_user)),
):
    lab = models.Lab(
        title=payload.title,
        description=payload.description,
        category=payload.category,
        created_by_id=user.id,
    )
    db.add(lab)
    db.commit()
    db.refresh(lab)
    return lab


@router.get("/labs", response_model=list[schemas.LabOut])
def list_labs(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    return db.query(models.Lab).all()


@router.get("/labs/{lab_id}", response_model=schemas.LabOut)
def get_lab(lab_id: int, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    lab = db.query(models.Lab).filter(models.Lab.id == lab_id).first()
    if not lab:
        raise HTTPException(status_code=404, detail="Lab not found")
    return lab


# ---------------- Experiments ----------------

@router.post("/experiments", response_model=schemas.ExperimentOut)
def create_experiment(
    payload: schemas.ExperimentCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(require_role(models.UserRole.teacher, models.UserRole.institution_admin, models.UserRole.independent_user)),
):
    lab = db.query(models.Lab).filter(models.Lab.id == payload.lab_id).first()
    if not lab:
        raise HTTPException(status_code=404, detail="Lab not found")

    experiment = models.Experiment(
        lab_id=payload.lab_id,
        title=payload.title,
        description=payload.description,
        simulation_config=payload.simulation_config,
        max_score=payload.max_score,
    )
    db.add(experiment)
    db.commit()
    db.refresh(experiment)
    return experiment


@router.get("/labs/{lab_id}/experiments", response_model=list[schemas.ExperimentOut])
def list_experiments_for_lab(lab_id: int, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    return db.query(models.Experiment).filter(models.Experiment.lab_id == lab_id).all()


@router.get("/experiments/{experiment_id}", response_model=schemas.ExperimentOut)
def get_experiment(experiment_id: int, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    exp = db.query(models.Experiment).filter(models.Experiment.id == experiment_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return exp


# ---------------- Assignments ----------------

@router.post("/assignments", response_model=schemas.AssignmentOut)
def create_assignment(
    payload: schemas.AssignmentCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(require_role(models.UserRole.teacher)),
):
    experiment = db.query(models.Experiment).filter(models.Experiment.id == payload.experiment_id).first()
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")

    assignment = models.Assignment(
        experiment_id=payload.experiment_id,
        teacher_id=user.id,
        student_id=payload.student_id,
        due_date=payload.due_date,
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment


@router.get("/assignments/mine", response_model=list[schemas.AssignmentOut])
def my_assignments(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    """Assignments for the logged-in student."""
    return db.query(models.Assignment).filter(models.Assignment.student_id == user.id).all()
