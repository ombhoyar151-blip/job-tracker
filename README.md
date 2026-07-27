# Job Tracker & Sign Language Detection Project

A production-ready full-stack application with a FastAPI backend and React (Vite) frontend.

## Project Structure

```
├── backend/
│   ├── api/             # API routes, models, services, and AI integration
│   ├── core/            # Configuration, database engine, security, compatibility
│   ├── tests/           # Pytest suite
│   ├── main.py          # FastAPI application entry point
│   ├── requirements.txt # Python dependencies
│   └── Dockerfile       # Backend container definition
├── frontend/
│   ├── src/             # React components, pages, services, store
│   ├── package.json     # Node.js dependencies & build scripts
│   ├── vite.config.js   # Vite configuration
│   └── Dockerfile       # Frontend container definition
├── docker-compose.yml   # Docker Compose setup for local development
├── render.yaml          # Render Blueprint for automated deployment
└── .env.example         # Environment variable template
```

## Running Locally

### Option 1: Direct Execution (No Docker required)

1. **Backend (Python 3.10+)**:
   ```bash
   cd backend
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Linux/macOS:
   source venv/bin/activate

   pip install -r requirements.txt
   uvicorn main:app --reload --port 8000
   ```
   *Note: Defaults to SQLite automatically if `DATABASE_URL` is omitted.*

2. **Frontend (Node 18+)**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   Access the app at `http://localhost:5173`.

### Option 2: Using Docker Compose

```bash
docker-compose up --build
```

---

## Deployment on Render

This project is pre-configured with a Render Blueprint (`render.yaml`).

1. Push your repository to GitHub or GitLab.
2. In the [Render Dashboard](https://dashboard.render.com), click **New +** -> **Blueprint**.
3. Connect your repository. Render will automatically detect `render.yaml` and provision:
   - **PostgreSQL Database** (`job-tracker-db`)
   - **FastAPI Web Service** (`job-tracker-backend`)
   - **React Static Site** (`job-tracker-frontend`)
4. Click **Apply** to deploy!