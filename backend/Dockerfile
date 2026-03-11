# backend/Dockerfile - FastAPI + Uvicorn (production-ready)
FROM python:3.11-slim AS base
WORKDIR /app

# Install system deps required for some Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies for caching
COPY requirements.txt ./requirements.txt
RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code into container
COPY . .

# Use PORT env var if provided by hosting (default 8000)
ENV PORT=8000
EXPOSE 8000

# Run Uvicorn. Adjust module path if your FastAPI app is elsewhere.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]