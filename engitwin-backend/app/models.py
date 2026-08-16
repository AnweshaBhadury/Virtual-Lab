"""
Database models. These map directly onto the diagram you drew:

ENGiTwin
 -> Independent User / Institution
      -> Teacher / Student
 -> Common Lab System
      -> Labs / Experiments / Assignments
           -> Simulation
                -> Experiment Attempt
                     -> Results / Measurements / Score
                          -> Analytics
                               -> AI Feedback
"""
import enum
import datetime as dt

from sqlalchemy import (
    Column, Integer, String, Float, Boolean, ForeignKey, DateTime,
    Text, JSON, Enum
)
from sqlalchemy.orm import relationship

from app.database import Base


def now():
    return dt.datetime.utcnow()


# ---------------------------------------------------------------------------
# Users / Institutions
# ---------------------------------------------------------------------------

class UserRole(str, enum.Enum):
    independent_user = "independent_user"
    institution_admin = "institution_admin"
    teacher = "teacher"
    student = "student"


class Institution(Base):
    __tablename__ = "institutions"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    # Short code shared with students/teachers so they can join this
    # institution at signup (e.g. "ACME7F2Q"). Generated when the
    # institution is created.
    code = Column(String, unique=True, index=True, nullable=False)
    # How many *student* seats this institution purchased/allows. 0 = unlimited.
    max_students = Column(Integer, default=0)
    created_at = Column(DateTime, default=now)

    users = relationship("User", back_populates="institution")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.independent_user)

    institution_id = Column(Integer, ForeignKey("institutions.id"), nullable=True)
    institution = relationship("Institution", back_populates="users")

    created_at = Column(DateTime, default=now)

    labs_created = relationship("Lab", back_populates="created_by")
    attempts = relationship("ExperimentAttempt", back_populates="student")


# ---------------------------------------------------------------------------
# Common Lab System: Labs -> Experiments -> Assignments
# ---------------------------------------------------------------------------

class Lab(Base):
    __tablename__ = "labs"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(Text, default="")
    category = Column(String, default="general")  # e.g. Digital, Analog, Mechanical...

    created_by_id = Column(Integer, ForeignKey("users.id"))
    created_by = relationship("User", back_populates="labs_created")

    created_at = Column(DateTime, default=now)

    experiments = relationship("Experiment", back_populates="lab", cascade="all, delete-orphan")


class Experiment(Base):
    __tablename__ = "experiments"

    id = Column(Integer, primary_key=True)
    lab_id = Column(Integer, ForeignKey("labs.id"), nullable=False)
    lab = relationship("Lab", back_populates="experiments")

    title = Column(String, nullable=False)
    description = Column(Text, default="")

    # Free-form config describing the simulation: components, default
    # parameter values, valid ranges, expected outcomes, etc. The frontend
    # (e.g. your Streamlit bench) reads this to build the simulation UI.
    simulation_config = Column(JSON, default=dict)

    max_score = Column(Float, default=100.0)
    created_at = Column(DateTime, default=now)

    attempts = relationship("ExperimentAttempt", back_populates="experiment")
    assignments = relationship("Assignment", back_populates="experiment")


class Assignment(Base):
    """A teacher assigning an experiment/lab to a student or a whole class."""
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True)
    experiment_id = Column(Integer, ForeignKey("experiments.id"), nullable=False)
    experiment = relationship("Experiment", back_populates="assignments")

    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    due_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=now)


# ---------------------------------------------------------------------------
# Simulation -> Experiment Attempt -> Results / Measurements / Score
# ---------------------------------------------------------------------------

class AttemptStatus(str, enum.Enum):
    in_progress = "in_progress"
    completed = "completed"
    abandoned = "abandoned"


class ExperimentAttempt(Base):
    __tablename__ = "experiment_attempts"

    id = Column(Integer, primary_key=True)
    experiment_id = Column(Integer, ForeignKey("experiments.id"), nullable=False)
    experiment = relationship("Experiment", back_populates="attempts")

    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    student = relationship("User", back_populates="attempts")

    status = Column(Enum(AttemptStatus), default=AttemptStatus.in_progress)

    # Raw data captured live from the simulation (readings, control
    # settings the student changed, timestamps, etc.)
    simulation_data = Column(JSON, default=dict)

    started_at = Column(DateTime, default=now)
    completed_at = Column(DateTime, nullable=True)

    result = relationship("Result", back_populates="attempt", uselist=False,
                           cascade="all, delete-orphan")
    ai_messages = relationship("AIMessage", back_populates="attempt",
                                cascade="all, delete-orphan")


class Result(Base):
    __tablename__ = "results"

    id = Column(Integer, primary_key=True)
    attempt_id = Column(Integer, ForeignKey("experiment_attempts.id"), unique=True, nullable=False)
    attempt = relationship("ExperimentAttempt", back_populates="result")

    measurements = Column(JSON, default=dict)  # e.g. {"voltage": 4.98, "current": 0.21}
    score = Column(Float, default=0.0)
    max_score = Column(Float, default=100.0)

    ai_feedback = Column(Text, default="")  # narrative feedback from the AI assistant

    created_at = Column(DateTime, default=now)


# ---------------------------------------------------------------------------
# AI Assistant conversation log (the AI "keeps asking lab questions")
# ---------------------------------------------------------------------------

class AIMessage(Base):
    __tablename__ = "ai_messages"

    id = Column(Integer, primary_key=True)
    attempt_id = Column(Integer, ForeignKey("experiment_attempts.id"), nullable=False)
    attempt = relationship("ExperimentAttempt", back_populates="ai_messages")

    role = Column(String, nullable=False)  # "assistant" or "student"
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=now)
