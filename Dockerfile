FROM python:3.13-slim

LABEL description="Reading sensors with python script" \
      version="1.0"

# Prevents Python from writing pyc files and buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Current working directory for the following commands
WORKDIR /script

# Install Python deps first (better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# COPY host source -> container destination (WORKDIR or /)
COPY script/ .

# Create non-root user and change ownership
RUN useradd -m appuser && \
    chown -R appuser:appuser /script

# Switch to non-root user
USER appuser

# Run the worker
CMD ["python3", "/script/sensors_moisture.py"]