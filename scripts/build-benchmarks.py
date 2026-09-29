#!/usr/bin/env python3
"""Versioned benchmark snapshot -> public site data.

Scores are reviewed against the linked primary leaderboard before changing
benchmarks.json. This script validates structure; it does not invent scores or
pretend that running daily means the source itself changed daily.
"""
import datetime as dt
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "benchmarks.json"
TARGET = ROOT / "site-pages" / "data" / "benchmarks.json"


def date(value: str) -> None:
    dt.date.fromisoformat(value)


def https(value: str) -> None:
    if not isinstance(value, str) or not value.startswith("https://"):
        raise ValueError(f"HTTPS source required: {value!r}")


def main() -> None:
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    date(data["as_of"])
    https(data["benchmark"]["source"])
    seen = set()
    for row in data["results"]:
        key = (row["agent"], row["model"], data["benchmark"]["id"])
        if key in seen:
            raise ValueError(f"duplicate result: {key}")
        seen.add(key)
        if not 0 <= row["score"] <= 100:
            raise ValueError(f"score outside 0-100: {key}")
        date(row["observed"])
        https(row["source"])
    for row in data["tracked"]:
        https(row["source"])
    if not TARGET.parent.is_dir():
        raise FileNotFoundError(f"site data directory missing: {TARGET.parent}")
    TARGET.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"  benchmarks.json 갱신: {len(data['results'])}개 점수 · {len(data['tracked'])}개 별도 추적")


if __name__ == "__main__":
    main()
