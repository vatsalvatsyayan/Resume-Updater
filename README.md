# Resume Updater

A full-stack web application for building professional profiles and generating tailored resumes for specific job applications.

## Tech Stack

**Frontend:** React 19, TypeScript, Vite, Tailwind CSS, Zustand, React Hook Form, Zod, Framer Motion, Radix UI

**Backend:** Python, FastAPI, MongoDB (Motor async driver), Pydantic

## Features

- 8-section profile builder (personal info, education, work experience, projects, skills, certifications, volunteer, leadership)
- Auto-save drafts to local storage
- Form validation with real-time feedback
- Resume tailoring modal for job-specific customization
- Application tracking with match score indicators
- Responsive design

## Prerequisites

- Node.js >= 20
- Python 3.11 or 3.12
- MongoDB (local or Atlas)

## Getting Started

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python main.py
```

The API server starts at `http://localhost:8000`. API docs are available at `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The dev server starts at `http://localhost:5173`. API requests are proxied to the backend automatically.

See [frontend/readme.md](frontend/readme.md) and [backend/readme.md](backend/readme.md) for detailed setup instructions, troubleshooting, and development guides.

## Environment Variables

See `backend/.env.example` for available configuration:

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST` | `0.0.0.0` | Server host |
| `PORT` | `8000` | Server port |
| `DEBUG` | `True` | Enable debug mode / hot reload |
| `MONGODB_URL` | `mongodb://localhost:27017` | MongoDB connection string |
| `MONGODB_DB_NAME` | `resume_updater` | Database name |
| `CORS_ORIGINS` | `http://localhost:3000,http://localhost:5173` | Allowed origins (comma-separated) |

## Project Structure

```
backend/
  api/              # Route handlers (health, user, resumes)
  core/             # App configuration
  db/               # MongoDB connection
  models/           # Database models
  schemas/          # Pydantic schemas
  services/         # Business logic
  keyword-extractor/# Keyword extraction utility + job description dataset
  main.py           # Entry point

frontend/src/
  components/
    ui/             # Reusable UI primitives
    form/           # Form field components
    sections/       # Profile form sections
    modals/         # Dialog components
    layout/         # Header, navigation
  pages/            # LandingPage, ProfileFormPage, ApplicationsPage, SuccessPage
  stores/           # Zustand state management
  lib/              # API client, validation schemas, utilities
  types/            # TypeScript type definitions
```

## Scripts

### Frontend

| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server |
| `npm run build` | Type check and build for production |
| `npm run preview` | Preview production build |
| `npm run lint` | Run ESLint |
