# ENGiTwin Backend

A working, testable backend for your ENGiTwin virtual lab platform, built to
match your diagram:

```
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
```

It runs fully on your own machine (SQLite file, no external database
server). The **AI lab assistant currently calls the Anthropic API online** -
see "Going offline later" below for how to switch it to a local model
without changing any other code.

## 1. Setup (one time)

You need Python 3.10+ installed.

**Important: use two separate virtual environments** - one for the
backend, one for the frontend. They pin different, incompatible versions
of a shared dependency (Starlette), so installing both into one
environment will break one of them.

### Backend

```bash
cd engitwin-backend
python -m venv venv
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
```

Open `.env` and set:

```
ANTHROPIC_API_KEY=sk-ant-...your real key...
```

(Get a key at https://console.anthropic.com/ if you don't have one. The AI
assistant endpoints won't work without it, but every other endpoint - auth,
labs, experiments, attempts, scoring, analytics - works with zero setup.)

### Frontend

In a **separate terminal**, with a **separate** virtual environment:

```bash
cd engitwin-backend/frontend
python -m venv venv
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

pip install -r requirements.txt
```

## 2. Run it

Terminal 1 - backend (from the `engitwin-backend/` folder, backend venv active):

```bash
uvicorn app.main:app --reload
```

Terminal 2 - frontend (from the `engitwin-backend/frontend/` folder, frontend venv active):

```bash
streamlit run app.py
```

The API is live at `http://localhost:8000` (docs at `/docs`), and the
Streamlit app opens automatically at `http://localhost:8501`.

Sign up as a **teacher**, create a lab and an experiment, then sign up a
second account as a **student** (or use a private/incognito window) to try
the full student flow: browse labs -> start an experiment -> chat with the
AI assistant -> submit results -> see analytics.

## 3. How the pieces map to your diagram

| Diagram box | Where it lives |
|---|---|
| Independent User / Institution / Teacher / Student | `User` model, `role` field, `POST /auth/signup` |
| Labs | `Lab` model, `POST /labs`, `GET /labs` |
| Experiments | `Experiment` model, `POST /experiments` (each experiment holds a `simulation_config` JSON blob - put whatever parameters/expected values your simulation needs in there) |
| Assignments | `Assignment` model, `POST /assignments` (teacher assigns an experiment to a student) |
| Simulation / Experiment Attempt | `ExperimentAttempt` model. Flow: `POST /attempts/start` -> `PATCH /attempts/{id}` (call repeatedly while the student interacts with the sim, to autosave) -> `POST /attempts/{id}/complete` (submit final measurements) |
| Results / Measurements / Score | `Result` model, created automatically when an attempt completes. Scoring logic is in `app/routers/attempts.py::_score_attempt` - it compares submitted measurements against an `expected` dict you set in the experiment's `simulation_config`, with a 5% tolerance. Customize this function per lab type as needed. |
| Analytics | `GET /analytics/me` (student's own stats), `GET /analytics/students/{id}` (teacher view) |
| AI Feedback | Generated automatically when an attempt completes, stored on the `Result.ai_feedback` field |
| AI Assistant asking lab questions | `POST /ai/ask` - call once when the attempt starts to get the opening question, then again after each student reply. Full transcript: `GET /ai/attempts/{id}/history` |

## 4. Typical flow your frontend will follow

1. `POST /auth/signup` or `/auth/login` -> get a JWT `access_token`
2. Send `Authorization: Bearer <token>` on every other request
3. `GET /labs` -> show list of labs
4. `GET /labs/{id}/experiments` -> show experiments in a lab
5. `POST /attempts/start` with the experiment id -> get an `attempt_id`
6. As the student interacts with your simulation UI:
   - `PATCH /attempts/{id}` to autosave simulation state
   - `POST /ai/ask` with `{"attempt_id": ..., "student_message": "..."}` each time the student replies to the AI assistant
7. When the student finishes: `POST /attempts/{id}/complete` with their final `measurements` -> get back score + AI feedback
8. `GET /analytics/me` -> show a progress dashboard

## 4a. Starter labs are seeded automatically

On first backend startup (only if the `labs` table is empty), `app/seed.py`
automatically creates the subject categories your landing page shows -
Physics, Electrical, Computer Networks, DBMS - each with a starter lab.
**Electrical** gets a real experiment ("Digital Storage Oscilloscope &
Function Generator") whose `simulation_config` is `{"bench": "dso"}`,
which is what tells the Simulation page to load the real `dso_lab.py`
bench (guided tutorial included) instead of a "coming soon" placeholder.
The other subjects start with empty labs - add experiments to them the
same way, giving each a `bench` value on the Labs page's "Simulator"
dropdown once a real simulator exists for it (add the matching branch in
`frontend/pages/2_Simulation.py`).

This only runs once per database. Nothing to run by hand.

**If you already ran the app before this update:** delete
`engitwin.db` before starting the backend again. SQLite doesn't
auto-migrate schema changes (the `Institution` table gained `code` and
`max_students` columns), so an old DB file will crash on startup - and
the auto-seed above only fires on a genuinely empty `labs` table.

## 5. Going offline later

Everything except the AI assistant already runs 100% offline (SQLite,
no external calls). When you're ready to make the AI assistant offline
too:

1. Install [Ollama](https://ollama.com) and pull a model: `ollama pull llama3`
2. Run `ollama serve`
3. In `.env`, set `AI_PROVIDER=local`

That's it - `app/services/ai_service.py` already has the local code path
wired up (`_ask_local` / `_call_local`), and every router only ever calls
`ai_service.ask(...)` / `ai_service.feedback(...)`, so nothing else in the
app needs to change.

## 6. Project layout

```
engitwin-backend/
├── requirements.txt         backend Python packages
├── .env.example             backend config template
├── README.md
├── app/                       <- BACKEND (FastAPI)
│   ├── main.py                  FastAPI app, wires up all routers
│   ├── config.py                  settings, read from .env
│   ├── database.py                  SQLite engine/session setup
│   ├── models.py                      all database tables
│   ├── schemas.py                       request/response shapes
│   ├── security.py                        password hashing + JWT auth
│   ├── services/
│   │   └── ai_service.py                    AI assistant (Anthropic now, local later)
│   └── routers/
│       ├── auth.py                            signup / login
│       ├── users.py                             users + institutions
│       ├── labs.py                                labs / experiments / assignments
│       ├── attempts.py                              simulation attempts + scoring
│       ├── ai_assistant.py                            AI lab assistant conversation
│       └── analytics.py                                 student progress stats
│
└── frontend/                <- FRONTEND (Streamlit)
    ├── requirements.txt        frontend Python packages
    ├── api_client.py             thin wrapper around every backend endpoint
    ├── app.py                      entry point: login/signup + landing page
    └── pages/                        Streamlit auto-builds sidebar nav from these
        ├── 1_Labs.py                   browse labs, create labs/experiments, start an attempt
        ├── 2_Simulation.py               run the active attempt - THIS is where your
        │                                  dso_lab.py bench (BENCH_HTML) plugs in, plus
        │                                  the AI assistant chat and result submission
        └── 3_Analytics.py                 student progress dashboard
```

## 7. Plugging in your existing `dso_lab.py` bench

Open `frontend/pages/2_Simulation.py` and find the block marked
`PLUG IN YOUR SIMULATION HERE`. Replace the placeholder `components.html(...)`
call with your real one, e.g.:

```python
from dso_lab import BENCH_HTML   # your existing file, copied into frontend/
components.html(BENCH_HTML, height=1500, scrolling=True)
```

Two things worth doing as you wire it up:

1. **Feed the bench experiment-specific config.** Right now `BENCH_HTML` is
   probably one big fixed string. Consider making it a function
   `build_bench_html(config)` that takes `experiment["simulation_config"]`
   (whatever you stored when creating the experiment) so each experiment
   can configure the bench differently, without editing `dso_lab.py` per lab.

2. **Send live readings back to the backend.** Have your bench's JS
   `postMessage` its state to the parent window, and forward that into
   `api.update_attempt(attempt_id, data)` for autosave, and into the
   `measurements` dict on the "Complete Attempt" form for scoring.

Everything else on that page (AI chat, submit form, score/feedback
display) already works and is wired to the backend - you're only replacing
the placeholder simulation box.

## 8. Talking to the backend directly (if not using the Streamlit frontend)

`frontend/api_client.py` is a good reference for the exact calls, but in short:

```python
import requests

API = "http://localhost:8000"
token = requests.post(f"{API}/auth/login", json={
    "email": "student@test.com", "password": "pass123"
}).json()["access_token"]

headers = {"Authorization": f"Bearer {token}"}
attempt = requests.post(f"{API}/attempts/start",
    json={"experiment_id": 1}, headers=headers).json()
```
