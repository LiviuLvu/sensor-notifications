FROM python:3.13-slim

LABEL description="Reading sensors with python script" \
      version="1.0"

# Prevents Python from writing pyc files and buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /script

# Install Python deps first (better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create non-root user
RUN useradd -m appuser
USER appuser

# ensure /script files are owned by non-root before switching
COPY --chown=appuser:appuser script/ .

# Run the worker
CMD ["python3", "/script/sensors_moisture.py"]