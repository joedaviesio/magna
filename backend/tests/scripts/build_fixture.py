#!/usr/bin/env python3
"""
build_fixture.py

Builds a small, deduplicated retrieval fixture (embeddings.npy + metadata.json +
config.json) from a full (embeddings, metadata) pair, restricted to a list of
act titles.

The source metadata.json is ~2 GB, so it is parsed as a *stream* of JSON objects
rather than with json.load() (which needs ~8 GB of RAM). Embedding rows are read
from the .npy through a memory map, so only the selected rows are materialised.

Rows are deduplicated on (act_title, section_number, text) — the same key the
runtime dedupe in search_similar() uses. See NOTES-duplication.md for why the
source corpus contains ~10x duplicates.

Usage (from the repo root):

    backend/venv/bin/python backend/tests/scripts/build_fixture.py \
        --embeddings data/embeddings/embeddings.npy \
        --metadata   data/embeddings/metadata.json \
        --out        backend/tests/fixtures/mini \
        --acts-file  backend/tests/scripts/mini_acts.txt

`--acts` may be given instead of `--acts-file` to pass titles on the command line.
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np

READ_CHUNK = 8 << 20  # 8 MB


def stream_json_array(path: Path):
    """Yield (index, object) for every element of a top-level JSON array.

    Handles files far larger than RAM: only a small sliding buffer is held.
    """
    decoder = json.JSONDecoder()
    with open(path, "r", encoding="utf-8") as fh:
        buf = fh.read(READ_CHUNK)
        if not buf:
            return
        start = buf.find("[")
        if start < 0:
            raise ValueError(f"{path} does not start with a JSON array")
        pos = start + 1
        index = 0

        while True:
            # Skip separators, refilling the buffer if we run out.
            while True:
                while pos < len(buf) and buf[pos] in " \t\r\n,":
                    pos += 1
                if pos < len(buf):
                    break
                more = fh.read(READ_CHUNK)
                if not more:
                    return
                buf = more
                pos = 0

            if buf[pos] == "]":
                return

            # Decode one object, extending the buffer while it is truncated.
            while True:
                try:
                    obj, end = decoder.raw_decode(buf, pos)
                    break
                except ValueError:
                    more = fh.read(READ_CHUNK)
                    if not more:
                        raise
                    buf += more

            yield index, obj
            index += 1
            pos = end

            # Compact the buffer so it does not grow without bound.
            if pos > READ_CHUNK:
                buf = buf[pos:]
                pos = 0


def build(embeddings_path: Path, metadata_path: Path, out_dir: Path,
          act_titles: list[str], max_rows_per_act: int | None = None) -> dict:
    wanted = {t.strip().lower() for t in act_titles if t.strip()}
    if not wanted:
        raise SystemExit("No act titles given")

    print(f"Streaming {metadata_path} ({metadata_path.stat().st_size / 1e9:.2f} GB)...")

    selected_rows: list[dict] = []
    selected_indices: list[int] = []
    seen: set[tuple[str, str, str]] = set()
    per_act: dict[str, int] = {}
    scanned = 0
    dupes_skipped = 0

    for index, row in stream_json_array(metadata_path):
        scanned += 1
        if scanned % 500_000 == 0:
            print(f"  scanned {scanned:,} rows, kept {len(selected_rows):,}", flush=True)

        act_title = row.get("act_title", "")
        if act_title.lower() not in wanted:
            continue

        key = (act_title, row.get("section_number", ""), row.get("text", ""))
        if key in seen:
            dupes_skipped += 1
            continue
        if max_rows_per_act is not None and per_act.get(act_title, 0) >= max_rows_per_act:
            continue

        seen.add(key)
        per_act[act_title] = per_act.get(act_title, 0) + 1
        selected_indices.append(index)
        selected_rows.append({
            "id": row.get("id", str(index)),
            "text": row.get("text", ""),
            "act_title": act_title,
            "act_short_name": row.get("act_short_name", ""),
            "section_number": row.get("section_number", ""),
            "section_heading": row.get("section_heading", ""),
            "section_url": row.get("section_url", ""),
            "act_url": row.get("act_url", ""),
        })

    print(f"  scanned {scanned:,} rows total; kept {len(selected_rows):,}, "
          f"skipped {dupes_skipped:,} duplicates")

    if not selected_rows:
        raise SystemExit("No rows matched the requested acts — check the titles")

    source = np.load(embeddings_path, mmap_mode="r")
    if source.shape[0] != scanned:
        print(f"  WARNING: embeddings has {source.shape[0]:,} rows but metadata has "
              f"{scanned:,}; they may not be aligned", file=sys.stderr)

    print(f"Extracting {len(selected_indices):,} embedding rows from {embeddings_path}...")
    subset = np.asarray(source[np.array(selected_indices, dtype=np.int64)], dtype=np.float32)

    out_dir.mkdir(parents=True, exist_ok=True)
    np.save(out_dir / "embeddings.npy", subset)
    with open(out_dir / "metadata.json", "w", encoding="utf-8") as fh:
        json.dump(selected_rows, fh, ensure_ascii=False)

    config = {
        "generated_at": __import__("datetime").datetime.now().isoformat(),
        "embedding_model": "all-MiniLM-L6-v2",
        "total_chunks": len(selected_rows),
        "embedding_dimension": int(subset.shape[1]),
        "embeddings_file": "embeddings.npy",
        "metadata_file": "metadata.json",
        "fixture": True,
        "source_embeddings": str(embeddings_path),
        "source_metadata": str(metadata_path),
        "source_rows": scanned,
        "acts": sorted(per_act),
        "rows_per_act": per_act,
        "deduplicated_on": ["act_title", "section_number", "text"],
    }
    with open(out_dir / "config.json", "w", encoding="utf-8") as fh:
        json.dump(config, fh, indent=2)

    total_bytes = sum((out_dir / n).stat().st_size
                      for n in ("embeddings.npy", "metadata.json", "config.json"))
    print(f"\nWrote {out_dir}")
    for name in ("embeddings.npy", "metadata.json", "config.json"):
        print(f"  {name:16s} {(out_dir / name).stat().st_size / 1e6:8.2f} MB")
    print(f"  {'TOTAL':16s} {total_bytes / 1e6:8.2f} MB")
    for act in sorted(per_act):
        print(f"    {per_act[act]:6d}  {act}")

    return config


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--embeddings", type=Path, required=True)
    ap.add_argument("--metadata", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--acts", nargs="*", default=[])
    ap.add_argument("--acts-file", type=Path,
                    help="File with one act title per line (# comments allowed)")
    ap.add_argument("--max-rows-per-act", type=int, default=None)
    args = ap.parse_args()

    titles = list(args.acts)
    if args.acts_file:
        for line in args.acts_file.read_text(encoding="utf-8").splitlines():
            line = line.split("#", 1)[0].strip()
            if line:
                titles.append(line)

    build(args.embeddings, args.metadata, args.out, titles, args.max_rows_per_act)


if __name__ == "__main__":
    main()
