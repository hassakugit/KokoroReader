FROM python:3.10-slim

# Set env to see logs immediately
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    espeak-ng \
    ffmpeg \
    libsndfile1 \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the Spacy model so it doesn't happen at runtime
RUN python -m spacy download en_core_web_sm

# Copy application code
COPY app /app/app

# Create directory for generated audio and history
RUN mkdir -p /app/app/static/audio
RUN mkdir -p /app/data

# Expose the requested port
EXPOSE 50005

# Run the server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "50005"]
