# Multi-stage Dockerfile for WikiFetch
# Supports both development and production targets

# Base stage - common for both dev and prod
FROM python:3.11-slim AS base

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py database.py ./
COPY templates/ ./templates/

# Create data directory for database
RUN mkdir -p /app/data

# Development stage
FROM base AS development

ENV FLASK_ENV=development
ENV PORT=5000
ENV DATABASE_PATH=/app/data/wikifetch.db

EXPOSE 5000

CMD ["python", "app.py"]

# Production stage
FROM base AS production

ENV FLASK_ENV=production
ENV PORT=8000
ENV DATABASE_PATH=/app/data/wikifetch.db

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "app:app"]
