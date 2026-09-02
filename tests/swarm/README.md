# Test swarm runner

Runs the charter (`../SWARM-CHARTER.md`) against a LOCAL stubbed backend using a local Ollama model. Never against production.

```
# 1. backend on the registered port, stubbed LLM, mini fixture
EMBEDDINGS_DIR=backend/tests/fixtures/mini BOWEN_STUB_LLM=1 HF_HUB_OFFLINE=1 LOGS_DIR=~/.cache/bowen-swarm/logs \
  backend/venv/bin/python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8105
# 2. swarm
python3 tests/swarm/swarm_run.py --repo . --backend http://localhost:8105 \
  --acts-file tests/swarm/acts_mini.json --golden backend/tests/golden/retrieval.json \
  --model qwen2.5-coder:32b --per-act 4 --max-acts 10
```

Digest lands in `~/.cache/bowen-swarm/runs/<date>/DIGEST.md`; the director triages it into `hq`.
