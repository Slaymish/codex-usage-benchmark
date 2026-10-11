#!/usr/bin/env python3
"""Strict, offline validation of a Codex aggregate usage report."""
from __future__ import annotations
import argparse
from datetime import date
import json
from pathlib import Path
import re
import sys

MAX_BYTES = 256_000
MAX_BUCKETS = 240
FIELDS = {"month", "model", "sessions", "input_tokens", "cached_input_tokens", "output_tokens", "reasoning_output_tokens", "total_tokens"}
SUMMARY = {"filesInspected", "usableSessions", "snapshotsFound", "skippedFiles"}
ROOT = {"schemaVersion", "collectorVersion", "dataType", "privacy", "summary", "buckets"}
MODEL = re.compile(r"^[A-Za-z0-9._-]{1,80}$")
VERSION = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")


class InvalidReport(ValueError):
    pass


def integer(value: object) -> bool:
    return type(value) is int and 0 <= value <= 2**53 - 1


def keys(value: object, expected: set[str], where: str) -> None:
    if not isinstance(value, dict) or set(value) != expected:
        raise InvalidReport(f"{where}: expected exactly {sorted(expected)}")


def validate(data: object) -> dict:
    keys(data, ROOT, "report")
    if data["schemaVersion"] != 1 or type(data["schemaVersion"]) is not int:
        raise InvalidReport("unsupported schemaVersion")
    if not isinstance(data["collectorVersion"], str) or not VERSION.fullmatch(data["collectorVersion"]):
        raise InvalidReport("invalid collectorVersion")
    if data["dataType"] != "aggregate_token_usage" or data["privacy"] != "monthly-model-aggregates":
        raise InvalidReport("unsupported report type")
    keys(data["summary"], SUMMARY, "summary")
    for field in SUMMARY:
        if not integer(data["summary"][field]):
            raise InvalidReport(f"invalid summary.{field}")
    buckets = data["buckets"]
    if not isinstance(buckets, list) or not 1 <= len(buckets) <= MAX_BUCKETS:
        raise InvalidReport("expected 1 to 240 aggregate buckets")
    seen = set()
    sessions = 0
    for index, row in enumerate(buckets):
        keys(row, FIELDS, f"buckets[{index}]")
        month = row["month"]
        if not isinstance(month, str) or not re.fullmatch(r"\d{4}-\d{2}", month):
            raise InvalidReport("invalid month")
        try:
            date.fromisoformat(month + "-01")
        except ValueError as exc:
            raise InvalidReport("invalid calendar month") from exc
        if not isinstance(row["model"], str) or not MODEL.fullmatch(row["model"]):
            raise InvalidReport("invalid model")
        identifier = (month, row["model"])
        if identifier in seen:
            raise InvalidReport("duplicate month/model bucket")
        seen.add(identifier)
        for field in FIELDS - {"month", "model"}:
            if not integer(row[field]):
                raise InvalidReport(f"invalid {field}")
        if row["sessions"] < 1:
            raise InvalidReport("empty bucket")
        if row["cached_input_tokens"] > row["input_tokens"]:
            raise InvalidReport("cached tokens exceed input tokens")
        if row["reasoning_output_tokens"] > row["output_tokens"]:
            raise InvalidReport("reasoning tokens exceed output tokens")
        if row["total_tokens"] and row["total_tokens"] < row["input_tokens"] + row["output_tokens"]:
            raise InvalidReport("total tokens less than input plus output")
        sessions += row["sessions"]
    if sessions != data["summary"]["usableSessions"]:
        raise InvalidReport("session count mismatch")
    if data["summary"]["filesInspected"] < sessions or data["summary"]["skippedFiles"] > data["summary"]["filesInspected"]:
        raise InvalidReport("inconsistent file counts")
    return data


def load(path: Path) -> dict:
    if path.stat().st_size > MAX_BYTES:
        raise InvalidReport("report exceeds 256 KB")
    with path.open("r", encoding="utf-8") as handle:
        return validate(json.load(handle))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    args = parser.parse_args()
    try:
        report = load(args.report)
    except (OSError, ValueError, UnicodeError) as exc:
        print(f"Invalid report: {exc}", file=sys.stderr)
        return 1
    print(f"Valid v1 report: {report['summary']['usableSessions']} sessions, {len(report['buckets'])} buckets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
