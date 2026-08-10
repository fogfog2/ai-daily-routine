#!/usr/bin/env python3
"""archive/*.md -> public/ai/data/*.json

ROUTINE.md [4] 의 항목 형식을 그대로 파싱한다:

    ### 제목
    **출처:** [도메인](URL) · **분류:** 모델
    - 사실
    **그래서:** 해석
"""
import json
import pathlib
import re
import sys

RE_SRC = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
RE_CAT = re.compile(r"\*\*분류:\*\*\s*([^\n·|]+)")


def parse(md: str) -> list:
    items, cur = [], None

    def close():
        if cur and cur["title"]:
            items.append(cur)

    for raw in md.splitlines():
        line = raw.strip()
        if line.startswith("### "):
            close()
            cur = {"title": line[4:].strip(), "facts": []}
        elif cur is None:
            continue
        elif line.startswith("**출처:**"):
            m = RE_SRC.search(line)
            if m:
                cur["source"], cur["url"] = m.group(1), m.group(2)
            c = RE_CAT.search(line)
            if c:
                cur["category"] = c.group(1).strip()
        elif line.startswith("**그래서:**"):
            cur["takeaway"] = line.split("**", 2)[-1].lstrip(":* ").strip()
        elif line.startswith(("- ", "* ")):
            fact = line[2:].strip()
            if "(미확인)" in fact:
                cur["unverified"] = True
            cur["facts"].append(fact)

    close()
    return items


def main() -> None:
    src, dst = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    dst.mkdir(parents=True, exist_ok=True)

    dates = []
    for f in sorted(src.glob("*.md"), reverse=True):
        items = parse(f.read_text(encoding="utf-8"))
        if not items:
            print(f"  건너뜀(항목 없음): {f.name}")
            continue
        (dst / f"{f.stem}.json").write_text(
            json.dumps({"date": f.stem, "items": items}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        dates.append(f.stem)
        print(f"  {f.stem}: {len(items)}건")

    (dst / "index.json").write_text(
        json.dumps({"dates": dates}, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"==> {len(dates)}일치 내보냄 -> {dst}")


if __name__ == "__main__":
    main()
