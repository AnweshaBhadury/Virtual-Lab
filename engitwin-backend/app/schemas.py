import datetime as dt
from typing import Optional, Any

from pydantic import BaseModel, EmailStr

from app.models import UserRole, AttemptStatus


# ---------------- Auth / Users ----------------

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.independent_user
    # Students/teachers/admins joining an institution provide the code the
    # institution admin generated when creating the institution.
    institution_code: Optional[str] = None


class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: UserRole
    institution_id: Optional[int] = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ---------------- Institutions ----------------

class InstitutionCreate(BaseModel):
    name: str
    max_students: int = 0  # 0 = unlimited


class InstitutionOut(BaseModel):
    id: int
    name: str
    code: str
    max_students: int
    student_count: int = 0
    seats_remaining: Optional[int] = None

    class Config:
        from_attributes = True


# ---------------- Labs / Experiments / Assignments ----------------

class LabCreate(BaseModel):
    title: str
    description: str = ""
    category: str = "general"


class LabOut(BaseModel):
    id: int
    title: str
    description: str
    category: str
    created_by_id: Optional[int]

    class Config:
        from_attributes = True


class ExperimentCreate(BaseModel):
    lab_id: int
    title: str
    description: str = ""
    simulation_config: dict[str, Any] = {}
    max_score: float = 100.0


class ExperimentOut(BaseModel):
    id: int
    lab_id: int
    title: str
    description: str
    simulation_config: dict[str, Any]
    max_score: float

    class Config:
        from_attributes = True


class AssignmentCreate(BaseModel):
    experiment_id: int
    student_id: int
    due_date: Optional[dt.datetime] = None


class AssignmentOut(BaseModel):
    id: int
    experiment_id: int
    teacher_id: int
    student_id: int
    due_date: Optional[dt.datetime]

    class Config:
        from_attributes = True


# ---------------- Attempts / Results ----------------

class AttemptStart(BaseModel):
    experiment_id: int


class AttemptUpdate(BaseModel):
    simulation_data: dict[str, Any]


class AttemptComplete(BaseModel):
    measurements: dict[str, Any] = {}


class ResultOut(BaseModel):
    id: int
    attempt_id: int
    measurements: dict[str, Any]
    score: float
    max_score: float
    ai_feedback: str

    class Config:
        from_attributes = True


class AttemptOut(BaseModel):
    id: int
    experiment_id: int
    student_id: int
    status: AttemptStatus
    simulation_data: dict[str, Any]
    started_at: dt.datetime
    completed_at: Optional[dt.datetime]
    result: Optional[ResultOut] = None

    class Config:
        from_attributes = True


# ---------------- AI assistant ----------------

class AIAskRequest(BaseModel):
    attempt_id: int
    student_message: Optional[str] = None  # None on first call, then their reply each turn


class AIMessageOut(BaseModel):
    role: str
    content: str
    created_at: dt.datetime

    class Config:
        from_attributes = True


# ---------------- Analytics ----------------

class StudentAnalytics(BaseModel):
    student_id: int
    total_attempts: int
    completed_attempts: int
    average_score: float
    best_score: float
    per_experiment: list[dict[str, Any]]
