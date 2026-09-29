#!/usr/bin/env python3
"""Validate the daily concept recommendation and publish its small JSON file."""
import datetime as dt
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    from catalog import DOCS
    data = json.loads((ROOT / "recommendation.json").read_text(encoding="utf-8"))
    dt.date.fromisoformat(data["date"])
    slugs = {row[3] for row in DOCS}
    if data["slug"] not in slugs:
        raise ValueError(f"unknown document slug: {data['slug']}")
    out = ROOT / "site-pages" / "data" / "recommendation.json"
    if not out.parent.is_dir():
        raise FileNotFoundError(out.parent)
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"  recommendation.json 갱신: {data['slug']}")


if __name__ == "__main__":
    main()
