# Resume Updater - Backend

Backend API for the Resume Updater application built with FastAPI and MongoDB.

## Quick Start

```bash
# Check Python version (must be 3.11 or 3.12)
python3.11 --version

# Create and activate virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env

# Start MongoDB (macOS)
brew services start mongodb-community

# Run the server
python main.py

# Test in a new terminal
curl http://localhost:8000/health
```

## Prerequisites

- **Python 3.11** (recommended - see note below about Python 3.14+)
- MongoDB (local installation or MongoDB Atlas account)
- pip (Python package installer)

**Important**: As of January 2026, Python 3.14+ may have compatibility issues with some dependencies (specifically pydantic-core). We recommend using Python 3.11 or 3.12 for this project.

## Project Structure

```
backend/
├── api/              # API route handlers (routers)
│   ├── health.py     # Health check endpoints
│   └── resumes.py    # Resume-related endpoints
├── core/             # Core application configuration
│   └── config.py     # Settings and environment variables
├── db/               # Database connections and utilities
│   └── mongodb.py    # MongoDB connection setup
├── models/           # Database models
├── schemas/          # Pydantic schemas for request/response validation
├── services/         # Business logic layer
├── main.py           # FastAPI application entry point
├── requirements.txt  # Python dependencies
└── .env.example      # Environment variables template
```

## Setup Instructions

### 1. Clone the Repository

```bash
cd backend
```

### 2. Check Python Version

Before creating the virtual environment, verify you have Python 3.11 or 3.12 installed:

#### On macOS/Linux:

```bash
# Check default Python version
python3 --version

# Check if Python 3.11 is available
which python3.11

# Check if Python 3.12 is available
which python3.12
```

#### On Windows:

```bash
# Check Python version
python --version

# Or check specific versions
py -3.11 --version
py -3.12 --version
```

**If you don't have Python 3.11 or 3.12:**
- macOS: `brew install python@3.11`
- Windows: Download from https://www.python.org/downloads/
- Linux: `sudo apt-get install python3.11` (or use your package manager)

### 3. Create Python Virtual Environment

#### On macOS/Linux:

```bash
# Create virtual environment using Python 3.11 (recommended)
python3.11 -m venv venv

# OR if Python 3.12 is your preference
# python3.12 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Verify you're using the correct Python version
python --version
```

#### On Windows:

```bash
# Create virtual environment using Python 3.11 (recommended)
py -3.11 -m venv venv

# OR if Python 3.12 is your preference
# py -3.12 -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Verify you're using the correct Python version
python --version
```

### 4. Install Dependencies

**Make sure your virtual environment is activated** (you should see `(venv)` in your terminal prompt).

```bash
# Upgrade pip first (recommended)
pip install --upgrade pip

# Install all project dependencies
pip install -r requirements.txt
```

This will install:
- FastAPI, Uvicorn (web framework and server)
- Pydantic (data validation)
- Motor, PyMongo (MongoDB drivers)
- python-dotenv, httpx, and other utilities

The installation may take 1-2 minutes.

### 5. Environment Configuration

1. Copy the example environment file:

```bash
cp .env.example .env
```

2. Edit the `.env` file and add your configuration:

```env
# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=True

# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=resume_updater

# API Keys (Add your actual API keys)
# OPENAI_API_KEY=your_openai_api_key_here
# ANTHROPIC_API_KEY=your_anthropic_api_key_here

# CORS Origins (comma-separated)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# JWT Secret (generate a secure random string)
# SECRET_KEY=your_secret_key_here
```

### 6. Install and Start MongoDB

#### On macOS:

```bash
# Install MongoDB using Homebrew
brew tap mongodb/brew
brew install mongodb-community

# Start MongoDB service
brew services start mongodb-community
```

#### On Windows:

1. Download MongoDB from https://www.mongodb.com/try/download/community
2. Install MongoDB following the installer instructions
3. Start MongoDB service from Services or run:

```bash
net start MongoDB
```

#### Using MongoDB Atlas (Cloud):

1. Create a free account at https://www.mongodb.com/cloud/atlas
2. Create a cluster
3. Get your connection string
4. Update `MONGODB_URL` in `.env` with your Atlas connection string

### 7. Run the Application

```bash
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 8. Verify Installation

Once the server is running, you should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started server process
INFO:     Application startup complete.
Connected to MongoDB at mongodb://localhost:27017
```

#### Test via Browser:

Open your browser and navigate to:

- **API Root**: http://localhost:8000/
- **API Documentation (Swagger UI)**: http://localhost:8000/docs
- **Alternative Docs (ReDoc)**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

#### Test via Command Line (curl):

Open a new terminal window (keep the server running) and test:

```bash
# Test health endpoint
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","timestamp":"2026-01-26T02:41:43.423487","service":"Resume Updater API"}

# Pretty-print JSON response
curl -s http://localhost:8000/health | python3 -m json.tool

# Test root endpoint
curl http://localhost:8000/

# Test resumes endpoint
curl http://localhost:8000/resumes
```

If you see JSON responses, your API is working correctly!

## Available Endpoints

### Health Check
- `GET /health` - Check API health status

### Resumes
- `GET /resumes` - Get all resumes
- `GET /resumes/{resume_id}` - Get a specific resume
- `POST /resumes` - Create a new resume
- `PUT /resumes/{resume_id}` - Update a resume
- `DELETE /resumes/{resume_id}` - Delete a resume

## Development

### Adding a New Router

1. Create a new file in the `api/` directory (e.g., `api/users.py`)
2. Define your router:

```python
from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("")
async def get_users():
    return {"users": []}
```

3. Import and include the router in `main.py`:

```python
from api import users

app.include_router(users.router)
```

### Stopping the Server

To stop the FastAPI server:

```bash
# If running in foreground
Press CTRL+C

# If running in background, find and kill the process
# macOS/Linux
lsof -i :8000 | grep LISTEN
kill -9 <PID>

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Deactivating Virtual Environment

When you're done working:

```bash
deactivate
```

### Useful Development Commands

```bash
# Check if server is running
curl http://localhost:8000/health

# View API documentation
open http://localhost:8000/docs  # macOS
start http://localhost:8000/docs  # Windows

# Check MongoDB connection
# In Python shell (with venv activated):
python3 -c "from pymongo import MongoClient; print(MongoClient('mongodb://localhost:27017').server_info())"

# View server logs (if running in background)
tail -f /path/to/log/file

# Format Python code (optional - install black first)
pip install black
black .

# Run with specific log level
uvicorn main:app --reload --log-level debug
```

## Common Issues

### 1. Python 3.14 Compatibility Issues

**Problem**: Error building wheel for `pydantic-core` with Python 3.14:
```
error: failed to run custom build command for `pyo3-ffi v0.22.6`
Building wheel for pydantic-core (pyproject.toml): finished with status 'error'
```

**Solution**: Use Python 3.11 or 3.12 instead:

```bash
# On macOS/Linux
rm -rf venv
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# On Windows
rmdir /s venv
py -3.11 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Port Already in Use

**Problem**: Error `Address already in use` when starting the server.

**Solution**: Find and kill the process using port 8000:

```bash
# macOS/Linux
lsof -i :8000 | grep LISTEN
kill -9 <PID>

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Or change the port in .env
PORT=8001
```

### 3. MongoDB Connection Error

**Problem**: `ServerSelectionTimeoutError` or cannot connect to MongoDB.

**Solution**: Make sure MongoDB is running:

```bash
# macOS - Check status
brew services list | grep mongodb

# macOS - Start MongoDB
brew services start mongodb-community

# Linux
sudo systemctl status mongod
sudo systemctl start mongod

# Windows
net start MongoDB
```

### 4. Module Not Found Error

**Problem**: `ModuleNotFoundError: No module named 'fastapi'` or similar.

**Solution**: Make sure your virtual environment is activated and dependencies are installed:

```bash
# Check if venv is activated (should see (venv) in prompt)
# If not, activate it:
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt

# Verify installation
pip list
```

### 5. Import Errors in IDE (VS Code, PyCharm)

**Problem**: IDE shows import errors even though code runs fine.

**Solution**: Point your IDE to the correct Python interpreter:

**VS Code**:
1. Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows)
2. Type "Python: Select Interpreter"
3. Choose the one in `./venv/bin/python`

**PyCharm**:
1. Go to Settings → Project → Python Interpreter
2. Select the venv interpreter from the project directory

### 6. CORS Errors from Frontend

**Problem**: Frontend gets blocked by CORS policy.

**Solution**: Update `CORS_ORIGINS` in `.env`:

```env
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:YOUR_FRONTEND_PORT
```

### 7. Connection Refused Error

**Problem**: `curl: (7) Failed to connect to localhost port 8000: Connection refused`

**Solution**: The server is not running. Start it:

```bash
# Make sure you're in the backend directory
cd backend

# Activate virtual environment
source venv/bin/activate  # Mac/Linux
# or
venv\Scripts\activate  # Windows

# Start server
python main.py
```

## First Time Setup Checklist

Use this checklist when setting up the project for the first time:

- [ ] Python 3.11 or 3.12 installed (`python3.11 --version`)
- [ ] MongoDB installed and running (`brew services list` on Mac)
- [ ] In the `backend` directory (`cd backend`)
- [ ] Virtual environment created with correct Python version (`python3.11 -m venv venv`)
- [ ] Virtual environment activated (see `(venv)` in terminal prompt)
- [ ] Dependencies installed (`pip install -r requirements.txt` - no errors)
- [ ] `.env` file created (`cp .env.example .env`)
- [ ] `.env` file configured with correct settings
- [ ] Server starts without errors (`python main.py`)
- [ ] Health endpoint works (`curl http://localhost:8000/health` returns JSON)
- [ ] API docs accessible (http://localhost:8000/docs loads in browser)
- [ ] Can see "Connected to MongoDB" message in server logs

If all checkboxes are checked, you're ready to develop!

## Dependencies

- **FastAPI**: Modern web framework for building APIs
- **Uvicorn**: ASGI server for running FastAPI
- **Pydantic**: Data validation using Python type hints
- **Motor**: Async MongoDB driver
- **PyMongo**: Official MongoDB driver for Python
- **python-dotenv**: Environment variable management
- **httpx**: HTTP client for making requests

## Team Collaboration

### Before Starting Work

1. **Ensure you have Python 3.11 or 3.12** installed (check: `python3.11 --version`)
2. Pull the latest changes: `git pull`
3. Activate virtual environment: `source venv/bin/activate` (Mac/Linux) or `venv\Scripts\activate` (Windows)
4. Update dependencies: `pip install -r requirements.txt`
5. Make sure MongoDB is running
6. Verify setup: `curl http://localhost:8000/health`

### After Adding New Dependencies

**IMPORTANT**: Only use `pip freeze` for dependencies you explicitly added, not all packages.

1. Install the package: `pip install package-name`
2. Add the package with version to `requirements.txt` manually, OR:
3. Use: `pip freeze | grep package-name >> requirements.txt`
4. Commit the updated `requirements.txt`
5. Notify team members to run `pip install -r requirements.txt`

**Example**:
```bash
# Install new package
pip install python-jose

# Add to requirements (choose one method):
# Method 1: Add manually to requirements.txt
echo "python-jose==3.3.0" >> requirements.txt

# Method 2: Use grep to filter
pip freeze | grep python-jose >> requirements.txt

# Commit
git add requirements.txt
git commit -m "Add python-jose dependency for JWT handling"
```

### Never Commit

- `.env` file (contains sensitive data)
- `venv/` directory (virtual environment)
- `__pycache__/` directories
- `.pyc` files

These are already in `.gitignore` but be mindful when adding files.

## License

This project is part of the Resume Updater application.
