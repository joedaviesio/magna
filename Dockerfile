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

# Embeddings data from a GitHub Release.
# embeddings.npy is float16 (~2 GB) shipped as <2 GiB shards because GitHub
# caps Release assets at 2 GiB. Shards are byte-concatenated back into the
# exact float16 .npy here — np.load reads it directly, no backend change.
# Bump DATA_RELEASE to publish new data (also busts this layer's cache).
ARG DATA_RELEASE=v0.4-data
RUN mkdir -p data/embeddings && cd data/embeddings \
 && BASE=https://github.com/joedaviesio/magna/releases/download/${DATA_RELEASE} \
 && curl -fL -o p00 "$BASE/embeddings_f16.npy.part00" \
 && curl -fL -o p01 "$BASE/embeddings_f16.npy.part01" \
 && cat p00 p01 > embeddings.npy && rm p00 p01 \
 && curl -fL -o metadata.json "$BASE/metadata.json" \
 && curl -fL -o config.json   "$BASE/config.json" \
 && python -c "import numpy as np; a=np.load('embeddings.npy', mmap_mode='r'); assert a.dtype=='float16' and a.ndim==2 and a.shape[1]==384 and a.shape[0]>2000000, a.shape; print('embeddings OK', a.shape, a.dtype)"

# Expose port
EXPOSE 8000

# Run the app
CMD uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}
