FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the sentence-transformers model (avoids download at runtime)
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Copy application code
COPY backend/ ./backend/
COPY data/ ./data/

# Expose port
EXPOSE 8000

# Run the app
CMD uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}
