from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine, SessionLocal
from app.routers import auth, users, labs, attempts, ai_assistant, analytics
from app.seed import seed_default_data

# Creates engitwin.db and all tables automatically on first run.
# Fully offline - no external DB server required.
Base.metadata.create_all(bind=engine)

# Populate default subject categories (Physics, Electrical, Computer
# Networks, DBMS) + the working DSO experiment, only if the DB is empty.
with SessionLocal() as _db:
    seed_default_data(_db)

app = FastAPI(
    title="ENGiTwin Backend",
    description="Backend for the ENGiTwin virtual lab platform",
    version="0.1.0",
)

# Wide-open CORS for now so your Streamlit / future React frontend can call
# this from anywhere during development. Tighten this before going live.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(labs.router)
app.include_router(attempts.router)
app.include_router(ai_assistant.router)
app.include_router(analytics.router)


@app.get("/")
def root():
    return {"status": "ok", "service": "ENGiTwin backend"}


@app.get("/health")
def health():
    return {"status": "healthy"}
