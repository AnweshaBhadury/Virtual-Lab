# ENGiTwin — React + Tailwind Frontend

This folder replaces the old Streamlit UI with a React + Tailwind UI while
keeping your existing FastAPI backend and SQLite database.

## Architecture

Browser
  -> React/Vite (`localhost:5173`)
  -> FastAPI (`localhost:8000`)
  -> SQLite (`engitwin.db`)

The React frontend uses the existing backend endpoints:
- `/auth/login`
- `/auth/signup`
- `/users/me`
- `/labs`
- `/labs/{id}/experiments`
- `/experiments/{id}`
- `/attempts/*`
- `/assignments*`
- `/analytics/me`
- `/ai/*`
- `/institutions*`

## Run

From this `frontend-react` directory:

```bash
npm install
npm run dev
```

Open:

http://localhost:5173

In another terminal, run the backend from the existing backend root:

```bash
python -m venv venv
# Windows PowerShell:
venv\Scripts\Activate.ps1
# Windows Git Bash:
# source venv/Scripts/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## API URL

By default React calls:

`http://localhost:8000`

To change it, create `.env`:

```env
VITE_API_BASE=http://localhost:8000
```

## Offline note

The UI itself has no CDN, remote fonts, remote images, analytics or external
browser services.

The backend already uses SQLite locally.

The current backend AI service defaults to Anthropic in `.env.example`, which
is online. For a completely offline AI assistant, change the backend to
`AI_PROVIDER=local` and run a local model server such as Ollama. The rest of
the React UI does not change.

## DSO simulator

The existing `frontend/dso_lab.py` simulator was carried into
`src/assets/dso.html` and is rendered locally through an iframe. No external
asset is required.

## Important

The old Streamlit frontend is intentionally left untouched in the backend
project. Once this React frontend is working, you can remove the old
`frontend/` directory if you no longer need Streamlit.