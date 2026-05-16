#!/usr/bin/env python3
"""
shard_embeddings.py

Prepare embeddings for GitHub Release delivery (2 GiB/file cap):
  1. Convert embeddings.npy float32 -> float16  (~halves size, negligible
     cosine-retrieval loss; also halves backend RAM — helps the deploy OOM)
  2. Byte-split the resulting .npy into shards < 1.9 GiB each
  3. Reassembly at deploy time is a plain `cat shard.* > embeddings.npy`
     (byte-identical to the float16 file — np.load just works, no code change)

    python backend/scripts/shard_embeddings.py            # build shards
    python backend/scripts/shard_embeddings.py --verify   # parity check only
"""
import sys, hashlib
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent
EMB = ROOT / "data/embeddings"
SRC = EMB / "embeddings.npy"
F16 = EMB / "embeddings_f16.npy"
SHARD_PREFIX = "embeddings_f16.npy.part"
SHARD_BYTES = 1_900_000_000  # ~1.77 GiB, comfortably under GitHub's 2 GiB cap


def build():
    src = np.load(SRC, mmap_mode="r")
    print(f"source : {src.shape} {src.dtype}  ({SRC.stat().st_size/1e9:.2f} GB)")

    arr16 = np.asarray(src, dtype=np.float16)
    np.save(F16, arr16)
    sz = F16.stat().st_size
    print(f"float16: {arr16.shape} {arr16.dtype}  ({sz/1e9:.2f} GB / {sz/2**30:.2f} GiB)")

    data = F16.read_bytes()
    for old in EMB.glob(SHARD_PREFIX + "*"):
        old.unlink()
    parts = []
    for i in range(0, len(data), SHARD_BYTES):
        p = EMB / f"{SHARD_PREFIX}{len(parts):02d}"
        p.write_bytes(data[i:i + SHARD_BYTES])
        parts.append(p)
        print(f"  shard {p.name}: {p.stat().st_size/2**30:.2f} GiB")
    # reassembly integrity check
    joined = b"".join(p.read_bytes() for p in parts)
    assert hashlib.md5(joined).hexdigest() == hashlib.md5(data).hexdigest(), "shard reassembly mismatch"
    print(f"reassembly verified ({len(parts)} shards, md5 matches)")
    return parts


def verify():
    """Retrieval parity on the EXACT backend path: np.dot(float16_emb, float32_query).

    Criterion is user-facing, not bit-exact: float16 passes if for every probe
    (a) the f16 #1 is still within the f32 top-5 (and vice versa) — i.e. any
    change is an intra-top-5 reshuffle of effectively-tied chunks — and
    (b) the #1 score delta is < 0.005 (well below MIN_SIMILARITY=0.25 and any
    boost threshold, so ordering after boosting is unaffected).
    """
    from sentence_transformers import SentenceTransformer
    f32 = np.load(SRC, mmap_mode="r")
    f16 = np.load(F16, mmap_mode="r")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    probes = [
        "Personal Property Securities Act security interest",
        "Land Transfer Act registration of title",
        "Maori Language Act te reo",
        "Extradition Act surrender to a foreign country",
        "Wildlife Act absolutely protected species",
    ]
    print(f"\n{'query':46} {'top1 same':>9} {'in top5':>8} {'Δscore':>8} {'top5∩':>6}")
    ok = True
    for q in probes:
        qv = model.encode(q, convert_to_numpy=True).astype(np.float32)
        s32 = np.dot(f32, qv)                 # f32 reference
        s16 = np.dot(f16, qv)                 # EXACT backend path: f16 emb · f32 query
        t32 = list(np.argsort(s32)[-5:][::-1])
        t16 = list(np.argsort(s16)[-5:][::-1])
        same1 = t32[0] == t16[0]
        cross = (t16[0] in t32) and (t32[0] in t16)   # reshuffle within top-5 both ways
        dscore = abs(float(s32[t32[0]]) - float(s16[t16[0]]))
        overlap = len(set(t32) & set(t16))
        probe_ok = (same1 or cross) and dscore < 0.005
        ok &= probe_ok
        print(f"{q[:46]:46} {('YES' if same1 else 'no'):>9} "
              f"{('YES' if cross else 'NO'):>8} {dscore:>8.4f} {overlap:>5}/5")
    print("\nPARITY: " + ("PASS — float16 retrieval is user-equivalent to float32"
                           if ok else "FAIL — material ranking change, do NOT ship"))
    return ok


if __name__ == "__main__":
    if "--verify" in sys.argv:
        sys.exit(0 if verify() else 1)
    build()
    ok = verify()
    sys.exit(0 if ok else 1)
