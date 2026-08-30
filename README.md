# Virtual Lab

A web-based Virtual Laboratory platform designed to provide students with an interactive environment for exploring and learning through virtual experiments.

The project consists of a React-based frontend and a Python backend.

## 1. Project Structure

```text
Virtual-Lab/
│
├── engtwin-backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── security.py
│   │   └── seed.py
│   └── requirements.txt
│
├── frontend-react/
│   ├── src/
│   ├── public/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── ...
│
└── .gitignore
```

## 2. Technology Stack

### Frontend

* React
* Vite
* JavaScript
* Tailwind CSS
* HTML/CSS
* npm

### Backend

* Python
* FastAPI
* Database integration
* REST APIs
* Authentication and security

## 3. Prerequisites

Before running the project, install:

* Node.js
* npm
* Python 3.x
* Git

Verify the installations:

```bash
node --version
npm --version
python --version
git --version
```

## 4. Clone the Repository

Clone the project using:

```bash
git clone https://github.com/AnweshaBhadury/Virtual-Lab.git
```

Move into the project directory:

```bash
cd Virtual-Lab
```

## 5. Frontend Setup

Open the frontend directory:

```bash
cd frontend-react
```

Install the frontend dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

Vite will provide a local development URL, normally similar to:

```text
http://localhost:5173
```

Open this URL in a browser to access the Virtual Lab frontend.

## 6. Frontend Production Build

To create a production build:

```bash
cd frontend-react
npm run build
```

The production files are generated in:

```text
frontend-react/dist/
```

To test the production build locally:

```bash
npm run preview
```

## 7. Backend Setup

Open a separate terminal and move to the backend:

```bash
cd engtwin-backend
```

Create a Python virtual environment:

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Linux/macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

Install the backend dependencies:

```bash
pip install -r requirements.txt
```

## 8. Run the Backend

From the `engtwin-backend` directory, start the FastAPI application using the application entry point defined in `app/main.py`.

A typical development command is:

```bash
uvicorn app.main:app --reload
```

The backend will normally be available at:

```text
http://127.0.0.1:8000
```

FastAPI's interactive API documentation can normally be accessed at:

```text
http://127.0.0.1:8000/docs
```

## 9. Running Frontend and Backend Together

The frontend and backend should be run in separate terminals.

### Terminal 1 — Backend

```bash
cd Virtual-Lab/engtwin-backend
```

Activate the Python environment and run:

```bash
uvicorn app.main:app --reload
```

### Terminal 2 — Frontend

```bash
cd Virtual-Lab/frontend-react
npm install
npm run dev
```

The frontend communicates with the backend through the configured API endpoints.

## 10. Environment Variables

If environment variables are required, create the appropriate `.env` file based on the provided `.env.example` configuration.

Do not commit passwords, API keys, database credentials, or other secrets to GitHub.

For production deployment, environment variables should be configured through the hosting platform's environment-variable settings.

## 11. Production Deployment

### Frontend Deployment on Vercel

The frontend is located inside the `frontend-react` directory.

The Vercel project should therefore use:

```text
Root Directory: frontend-react
Framework Preset: Vite
Build Command: npm run build
Output Directory: dist
```

The deployment process is:

1. Push the project to GitHub.
2. Import the GitHub repository into Vercel.
3. Select the `main` branch for production.
4. Set the Root Directory to `frontend-react`.
5. Select Vite as the Framework Preset.
6. Use `npm run build` as the build command.
7. Use `dist` as the output directory.
8. Configure required environment variables.
9. Deploy the project.
10. Verify the generated production URL.

The production frontend is currently deployed at:

https://virtual-lab-lac.vercel.app/

## 12. Backend Deployment

The backend is located separately in:

```text
engtwin-backend/
```

The backend can be deployed independently on a Python-compatible hosting platform.

The backend deployment must:

1. Use Python as the runtime.
2. Install dependencies from `requirements.txt`.
3. Start the FastAPI application from `app/main.py`.
4. Configure the required environment variables.
5. Make the backend API publicly accessible.
6. Update the frontend API configuration to use the deployed backend URL.

## 13. Database

The backend contains database-related files and application models.

Before production deployment:

1. Configure the production database.
2. Set the database connection information using environment variables.
3. Ensure required tables are created.
4. Run any required seed/setup operation.
5. Verify that the backend can connect to the production database.

Database credentials must never be committed to the repository.

## 14. API Integration

The frontend communicates with the backend using HTTP API requests.

For production deployment, ensure that:

```text
Frontend → Production Backend API
```

is configured correctly.

If the frontend is still pointing to:

```text
localhost
127.0.0.1
```

the application will work locally but will not be able to communicate with the backend after deployment.

The production API URL should therefore be configured through the frontend environment configuration.

## 15. Deployment Verification

After deployment, verify the following:

### Frontend

* Homepage loads successfully.
* Navigation works.
* Assets load correctly.
* JavaScript contains no runtime errors.
* API requests are sent to the production backend.

### Backend

* API server starts successfully.
* API endpoints respond correctly.
* Database connection works.
* Authentication/security functionality works.
* CORS configuration allows the deployed frontend.

## 16. Troubleshooting

### Vercel shows `404 NOT_FOUND`

Check:

```text
Root Directory = frontend-react
Framework Preset = Vite
Output Directory = dist
```

Then redeploy the project.

### Frontend builds but API requests fail

Check:

* Backend deployment URL.
* Frontend environment variables.
* CORS configuration.
* API endpoint configuration.
* Browser developer-console errors.

### Backend does not start

Check:

```bash
pip install -r requirements.txt
```

Then verify that the FastAPI application entry point in `app/main.py` matches the deployment start command.

## 17. Development Workflow

For making changes:

```bash
git pull origin main
```

Make the required changes and test locally.

For the frontend:

```bash
cd frontend-react
npm run build
```

After successful testing:

```bash
git add .
git commit -m "Update Virtual Lab"
git push origin main
```

The Vercel production deployment is connected to the `main` branch, so pushing changes to `main` triggers a new production deployment.

## 18. Deployment Architecture

The project follows a separated frontend/backend architecture:

```text
                    GitHub Repository
                           |
             +-------------+-------------+
             |                           |
             v                           v
      frontend-react               engtwin-backend
             |                           |
             v                           v
          Vercel                  Python/FastAPI Host
             |                           |
             +------------+--------------+
                          |
                          v
                     Database/API
```

This architecture allows the React frontend and Python backend to be developed and deployed independently.

## 19. Current Production Frontend

Production URL:

https://virtual-lab-lac.vercel.app/

GitHub Repository:

https://github.com/AnweshaBhadury/Virtual-Lab

## 20. Summary

The Virtual Lab project is deployable using a separated frontend/backend architecture.

The frontend is a Vite React application located in `frontend-react/` and can be deployed to Vercel.

The backend is a Python FastAPI application located in `engtwin-backend/` and can be deployed on a Python-compatible server.

For successful production deployment, the frontend must use the correct Vercel root directory and must be configured to communicate with the deployed backend API.
