FROM python:3.10-slim

# Install ffmpeg for audio stitching (pydub)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY app /app/app

# Create storage for generated audio and history
RUN mkdir -p /app/app/static/audio
RUN mkdir -p /app/data

EXPOSE 50005

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "50005"]