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

# --- OPTIMIZATION START ---
# Install CPU-only PyTorch first (Reduces image size by ~2GB)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu
# --- OPTIMIZATION END ---

# Install remaining dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the Spacy model
RUN python -m spacy download en_core_web_sm

# Copy application code
COPY app /app/app

# Create directories
RUN mkdir -p /app/app/static/audio
RUN mkdir -p /app/data

# Expose port
EXPOSE 50005

# Run the server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "50005"]
