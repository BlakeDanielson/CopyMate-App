# Use Python 3.11 as the base image
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Install poetry
RUN pip install poetry

# Copy only pyproject.toml
COPY pyproject.toml /app/

# Configure poetry to not create a virtual environment
RUN poetry config virtualenvs.create false

# Install dependencies without using the lock file
RUN poetry install --no-interaction --no-ansi --no-root

# Copy application code
COPY . /app/

# Expose port for FastAPI
EXPOSE 8000

# Command is defined in docker-compose.yml