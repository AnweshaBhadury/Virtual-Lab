from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=schemas.Token)
def signup(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    institution_id = None
    if payload.role in (models.UserRole.institution_admin, models.UserRole.teacher, models.UserRole.student):
        if not payload.institution_code:
            raise HTTPException(
                status_code=400,
                detail="Institution role requires an institution_code (create one via POST /institutions "
                       "if you're setting up a new institution).",
            )
        inst = db.query(models.Institution).filter(
            models.Institution.code == payload.institution_code.upper()
        ).first()
        if not inst:
            raise HTTPException(status_code=404, detail="No institution found with that code")

        if payload.role == models.UserRole.student and inst.max_students > 0:
            current_students = db.query(models.User).filter(
                models.User.institution_id == inst.id,
                models.User.role == models.UserRole.student,
            ).count()
            if current_students >= inst.max_students:
                raise HTTPException(
                    status_code=400,
                    detail=f"'{inst.name}' has no student seats left "
                           f"({current_students}/{inst.max_students} used). Contact the institution admin.",
                )
        institution_id = inst.id

    user = models.User(
        name=payload.name,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role=payload.role,
        institution_id=institution_id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user.id)
    return schemas.Token(access_token=token, user=user)


@router.post("/login", response_model=schemas.Token)
def login(payload: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    token = create_access_token(user.id)
    return schemas.Token(access_token=token, user=user)
