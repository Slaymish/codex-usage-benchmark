#!/usr/bin/env python3
"""Offline, standard-library-only, aggregate Codex usage exporter."""
from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys

SCHEMA_VERSION = 1
MAX_LINE_BYTES = 2_000_000
MAX_FILE_BYTES = 100_000_000
TOKEN_FIELDS = ("input_tokens", "cached_input_tokens", "output_tokens", "reasoning_output_tokens", "total_tokens")


def nonnegative_int(value: object) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) and value >= 0 else None


def safe_model(value: object) -> str:
    if not isinstance(value, str) or not value or len(value) > 80:
        return "unknown"
    return value if all(c.isalnum() or c in "._-" for c in value) else "unknown"


def month_of(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            return None
        return parsed.astimezone(timezone.utc).strftime("%Y-%m")
    except ValueError:
        return None


def extract(path: Path) -> tuple[dict | None, int]:
    latest = None
    model = "unknown"
    month = None
    snapshots = 0
    try:
        if path.stat().st_size > MAX_FILE_BYTES:
            return None, 0
        with path.open("rb") as handle:
            for raw in handle:
                if len(raw) > MAX_LINE_BYTES:
                    continue
                try:
                    record = json.loads(raw)
                except (ValueError, UnicodeDecodeError):
                    continue
                if not isinstance(record, dict):
                    continue
                kind = record.get("type")
                payload = record.get("payload")
                if not isinstance(payload, dict):
                    continue
                if kind == "turn_context":
                    model = safe_model(payload.get("model")) if payload.get("model") else model
                if kind != "event_msg" or payload.get("type") != "token_count":
                    continue
                info = payload.get("info")
                if not isinstance(info, dict):
                    continue
                totals = info.get("total_token_usage")
                if not isinstance(totals, dict):
                    continue
                parsed = {key: nonnegative_int(totals.get(key)) for key in TOKEN_FIELDS}
                if any(parsed[k] is None for k in ("input_tokens", "output_tokens")):
                    continue
                # Snapshots are cumulative for a session, so never sum them.
                if latest is None or parsed.get("total_tokens", 0) >= latest.get("total_tokens", 0):
                    latest = parsed
                snapshots += 1
                month = month_of(record.get("timestamp")) or month
    except (OSError, PermissionError):
        return None, 0
    if latest is None or month is None:
        return None, snapshots
    return {"month": month, "model": model, "tokens": latest}, snapshots


def export(sessions_dir: Path) -> dict:
    aggregate = defaultdict(lambda: {"sessions": 0, **{key: 0 for key in TOKEN_FIELDS}})
    files_inspected = 0
    snapshots_found = 0
    skipped_files = 0
    if sessions_dir.is_dir():
        for path in sessions_dir.rglob("*.jsonl"):
            if path.is_symlink() or not path.is_file():
                continue
            files_inspected += 1
            session, snapshots = extract(path)
            snapshots_found += snapshots
            if session is None:
                skipped_files += 1
                continue
            bucket = aggregate[(session["month"], session["model"])]
            bucket["sessions"] += 1
            for key, value in session["tokens"].items():
                if value is not None:
                    bucket[key] += value
    buckets = [{"month": month, "model": model, **aggregate[(month, model)]}
               for month, model in sorted(aggregate)]
    return {
        "schemaVersion": SCHEMA_VERSION,
        "collectorVersion": "0.1.0",
        "dataType": "aggregate_token_usage",
        "privacy": "monthly-model-aggregates",
        "summary": {
            "filesInspected": files_inspected,
            "usableSessions": sum(row["sessions"] for row in buckets),
            "snapshotsFound": snapshots_found,
            "skippedFiles": skipped_files,
        },
        "buckets": buckets,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sessions-dir", type=Path, default=Path(os.environ.get("CODEX_HOME", "~/.codex")).expanduser() / "sessions")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not args.sessions_dir.is_dir():
        print("No Codex sessions directory found; no report written.", file=sys.stderr)
        return 2
    result = export(args.sessions_dir)
    destination = args.output.expanduser().resolve()
    if destination.exists():
        print("Output already exists. Choose a new path to avoid overwriting.", file=sys.stderr)
        return 2
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("x", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, ensure_ascii=True)
        handle.write("\n")
    print(f"Saved {destination}")
    print(json.dumps(result["summary"], indent=2))
    if not result["summary"]["usableSessions"]:
        print("No supported usage snapshots found. Do not submit an empty report.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
