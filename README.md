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
- AI-powered cover letter generation from an optimized resume using Gemini
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
| `GEMINI_API_KEY` | — | Google Gemini API key (required for cover letter generation) |

## Project Structure

```
backend/
  api/              # Route handlers (health, user, resumes, cover_letter)
  core/             # App configuration
  db/               # MongoDB connection
  models/           # Database models
  schemas/          # Pydantic schemas (includes CoverLetterRequest/Response)
  services/         # Business logic (cover_letter_service, llm_client)
  keyword-extractor/# Keyword extraction utility + job description dataset
  tests/
    test_cover_letter.py  # Integration test runner for cover letter generation
    test-data/            # Per-job fixture directories (optimized_resume.json + job_description.txt)
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

### Backend

| Command | Description |
|---------|-------------|
| `python main.py` | Start the API server |
| `python -m tests.test_cover_letter` | Run cover letter generation against all test-data fixtures |
| `python -m tests.test_cover_letter job1` | Run cover letter generation for a specific job fixture only |

### Frontend

| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server |
| `npm run build` | Type check and build for production |
| `npm run preview` | Preview production build |
| `npm run lint` | Run ESLint |
