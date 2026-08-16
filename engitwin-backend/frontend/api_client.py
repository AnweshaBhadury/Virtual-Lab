"""
Thin wrapper around the ENGiTwin backend REST API.

Every function here just does a requests call and raises on failure -
keeps the Streamlit pages free of raw requests/URL clutter. If you move
the backend URL (e.g. deploy it somewhere), only API_BASE needs to change.
"""
import os
import requests
import streamlit as st

API_BASE = os.environ.get("ENGITWIN_API_BASE", "http://localhost:8000")


class APIError(Exception):
    pass


def _headers():
    token = st.session_state.get("token")
    return {"Authorization": f"Bearer {token}"} if token else {}


def _handle(resp: requests.Response):
    if not resp.ok:
        try:
            detail = resp.json().get("detail", resp.text)
        except Exception:
            detail = resp.text
        raise APIError(f"{resp.status_code}: {detail}")
    return resp.json()


# ---------------- Auth ----------------

def signup(name, email, password, role, institution_code=None):
    resp = requests.post(f"{API_BASE}/auth/signup", json={
        "name": name, "email": email, "password": password, "role": role,
        "institution_code": institution_code,
    })
    return _handle(resp)


def login(email, password):
    resp = requests.post(f"{API_BASE}/auth/login", json={
        "email": email, "password": password
    })
    return _handle(resp)


def me():
    resp = requests.get(f"{API_BASE}/users/me", headers=_headers())
    return _handle(resp)


# ---------------- Labs / Experiments ----------------

def list_labs():
    resp = requests.get(f"{API_BASE}/labs", headers=_headers())
    return _handle(resp)


def create_lab(title, description, category):
    resp = requests.post(f"{API_BASE}/labs", headers=_headers(), json={
        "title": title, "description": description, "category": category
    })
    return _handle(resp)


def list_experiments(lab_id):
    resp = requests.get(f"{API_BASE}/labs/{lab_id}/experiments", headers=_headers())
    return _handle(resp)


def get_experiment(experiment_id):
    resp = requests.get(f"{API_BASE}/experiments/{experiment_id}", headers=_headers())
    return _handle(resp)


def create_experiment(lab_id, title, description, simulation_config, max_score=100.0):
    resp = requests.post(f"{API_BASE}/experiments", headers=_headers(), json={
        "lab_id": lab_id, "title": title, "description": description,
        "simulation_config": simulation_config, "max_score": max_score,
    })
    return _handle(resp)


# ---------------- Attempts ----------------

def start_attempt(experiment_id):
    resp = requests.post(f"{API_BASE}/attempts/start", headers=_headers(), json={
        "experiment_id": experiment_id
    })
    return _handle(resp)


def update_attempt(attempt_id, simulation_data):
    resp = requests.patch(f"{API_BASE}/attempts/{attempt_id}", headers=_headers(), json={
        "simulation_data": simulation_data
    })
    return _handle(resp)


def complete_attempt(attempt_id, measurements):
    resp = requests.post(f"{API_BASE}/attempts/{attempt_id}/complete", headers=_headers(), json={
        "measurements": measurements
    })
    return _handle(resp)


def my_attempts():
    resp = requests.get(f"{API_BASE}/attempts/mine", headers=_headers())
    return _handle(resp)


# ---------------- AI assistant ----------------

def ai_ask(attempt_id, student_message=None):
    resp = requests.post(f"{API_BASE}/ai/ask", headers=_headers(), json={
        "attempt_id": attempt_id, "student_message": student_message
    })
    return _handle(resp)


def ai_history(attempt_id):
    resp = requests.get(f"{API_BASE}/ai/attempts/{attempt_id}/history", headers=_headers())
    return _handle(resp)


# ---------------- Institutions ----------------

def list_institutions():
    resp = requests.get(f"{API_BASE}/institutions")
    return _handle(resp)


def create_institution(name, max_students=0):
    resp = requests.post(f"{API_BASE}/institutions", json={"name": name, "max_students": max_students})
    return _handle(resp)


def get_institution_by_code(code):
    resp = requests.get(f"{API_BASE}/institutions/by-code/{code}")
    return _handle(resp)


# ---------------- Users ----------------

def list_users():
    """Teachers / institution admins only - used to pick a student to assign to."""
    resp = requests.get(f"{API_BASE}/users", headers=_headers())
    return _handle(resp)


# ---------------- Assignments ----------------

def create_assignment(experiment_id, student_id, due_date=None):
    resp = requests.post(f"{API_BASE}/assignments", headers=_headers(), json={
        "experiment_id": experiment_id, "student_id": student_id, "due_date": due_date,
    })
    return _handle(resp)


def my_assignments():
    """Assignments for the logged-in student."""
    resp = requests.get(f"{API_BASE}/assignments/mine", headers=_headers())
    return _handle(resp)


# ---------------- Analytics ----------------

def my_analytics():
    resp = requests.get(f"{API_BASE}/analytics/me", headers=_headers())
    return _handle(resp)
