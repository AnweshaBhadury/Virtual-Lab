from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import random
import string

from app.database import get_db
from app import models, schemas
from app.security import get_current_user, require_role

router = APIRouter(tags=["users"])


def _generate_institution_code(db: Session) -> str:
    """Short, human-shareable, unique code like 'ACME7F2Q'."""
    alphabet = string.ascii_uppercase + string.digits
    for _ in range(20):
        code = "".join(random.choices(alphabet, k=8))
        if not db.query(models.Institution).filter(models.Institution.code == code).first():
            return code
    raise HTTPException(status_code=500, detail="Could not generate a unique institution code")


def _institution_out(db: Session, inst: models.Institution) -> schemas.InstitutionOut:
    student_count = (
        db.query(models.User)
        .filter(models.User.institution_id == inst.id, models.User.role == models.UserRole.student)
        .count()
    )
    seats_remaining = None if inst.max_students == 0 else max(inst.max_students - student_count, 0)
    return schemas.InstitutionOut(
        id=inst.id, name=inst.name, code=inst.code, max_students=inst.max_students,
        student_count=student_count, seats_remaining=seats_remaining,
    )


@router.get("/users/me", response_model=schemas.UserOut)
def get_me(user: models.User = Depends(get_current_user)):
    return user


@router.get("/users", response_model=list[schemas.UserOut])
def list_users(
    db: Session = Depends(get_db),
    user: models.User = Depends(require_role(models.UserRole.teacher, models.UserRole.institution_admin)),
):
    """Teachers/institution admins can list users (e.g. to find students to assign labs to)."""
    query = db.query(models.User)
    if user.role == models.UserRole.institution_admin:
        query = query.filter(models.User.institution_id == user.institution_id)
    return query.all()


@router.post("/institutions", response_model=schemas.InstitutionOut)
def create_institution(payload: schemas.InstitutionCreate, db: Session = Depends(get_db)):
    inst = models.Institution(
        name=payload.name,
        code=_generate_institution_code(db),
        max_students=payload.max_students,
    )
    db.add(inst)
    db.commit()
    db.refresh(inst)
    return _institution_out(db, inst)


@router.get("/institutions", response_model=list[schemas.InstitutionOut])
def list_institutions(db: Session = Depends(get_db)):
    return [_institution_out(db, i) for i in db.query(models.Institution).all()]


@router.get("/institutions/by-code/{code}", response_model=schemas.InstitutionOut)
def get_institution_by_code(code: str, db: Session = Depends(get_db)):
    """Used at signup so the frontend can validate a code (and show seats
    remaining) before the student/teacher actually submits the form."""
    inst = db.query(models.Institution).filter(models.Institution.code == code.upper()).first()
    if not inst:
        raise HTTPException(status_code=404, detail="No institution found with that code")
    return _institution_out(db, inst)
