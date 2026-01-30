FROM python:3.11-slim

WORKDIR /app

# Install curl for downloading files
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the sentence-transformers model
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Copy application code
COPY backend/ ./backend/

# Create embeddings directory and download from GitHub Release
RUN mkdir -p data/embeddings
RUN curl -L -o data/embeddings/embeddings.npy https://github.com/joedaviesio/magna/releases/download/v1.0-data/embeddings.npy
RUN curl -L -o data/embeddings/metadata.json https://github.com/joedaviesio/magna/releases/download/v1.0-data/metadata.json
RUN curl -L -o data/embeddings/config.json https://github.com/joedaviesio/magna/releases/download/v1.0-data/config.json

# Expose port
EXPOSE 8000

# Run the app
CMD uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}
