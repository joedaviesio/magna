FROM python:3.11-slim

WORKDIR /app

# Install git and git-lfs for pulling large files
RUN apt-get update && apt-get install -y git git-lfs && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the sentence-transformers model
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Copy application code (excluding LFS files initially)
COPY backend/ ./backend/

# Clone just the data with LFS
# We need to pull LFS files separately since COPY doesn't handle LFS
COPY .git/ ./.git/
COPY data/ ./data/
RUN git lfs install && git lfs pull

# Clean up .git to reduce image size
RUN rm -rf .git

# Expose port
EXPOSE 8000

# Run the app
CMD uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}
