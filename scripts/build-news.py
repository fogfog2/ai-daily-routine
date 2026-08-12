#!/usr/bin/env python3
"""archive/YYYY-MM-DD.md → site-pages/data/news.json

뉴스는 사람이 읽기 좋은 마크다운으로 쓰고, 사이트가 읽을 JSON 은 여기서 만든다.
한 곳에만 쓰면 되도록 마크다운을 단일 출처로 둔다.

항목 형식 (ROUTINE.md 참조):

    ## 제목
    - 분류: `모델`
    - 출처: https://...

    사실 1
    사실 2

    그래서: 한 줄 해석
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).parent.parent
ARCHIVE = ROOT / "archive"
OUT = ROOT / "site-pages" / "data" / "news.json"

# 최근 며칠치를 사이트에 싣는가. 오래된 것은 파일로만 남는다.
KEEP_DAYS = 30


def parse_day(path: pathlib.Path) -> list:
    """하루치 마크다운에서 항목들을 뽑는다."""
    text = path.read_text(encoding="utf-8")
    items = []

    # '## ' 로 시작하는 블록마다 하나의 항목
    for block in re.split(r"^## ", text, flags=re.M)[1:]:
        lines = block.strip().split("\n")
        title = lines[0].strip()
        if not title:
            continue

        body = "\n".join(lines[1:])
        cat = re.search(r"분류:\s*`?([^`\n]+)`?", body)
        src = re.search(r"출처:\s*<?(https?://[^\s>）)]+)", body)
        takeaway = re.search(r"그래서:\s*(.+)", body)

        # 사실 줄 — 목록 표시가 있든 없든, 메타 줄이 아닌 본문 줄을 모은다
        facts = []
        for ln in body.split("\n"):
            s = ln.strip().lstrip("-*· ").strip()
            if not s:
                continue
            if re.match(r"^(분류|출처|그래서)\s*:", s):
                continue
            if s.startswith("<!--") or s.startswith(">"):
                continue
            facts.append(s)

        items.append({
            "title": title,
            "category": (cat.group(1).strip() if cat else ""),
            "url": (src.group(1) if src else ""),
            "facts": facts[:4],
            "takeaway": (takeaway.group(1).strip() if takeaway else ""),
        })
    return items


def main() -> None:
    if not ARCHIVE.exists():
        print("archive/ 가 없습니다")
        return

    days = []
    for p in sorted(ARCHIVE.glob("*.md"), reverse=True):
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", p.stem):
            continue
        items = parse_day(p)
        if not items:          # 뼈대만 있고 내용이 없는 날은 싣지 않는다
            continue
        days.append({"date": p.stem, "items": items})

    days = days[:KEEP_DAYS]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps({
            "note": "archive/*.md 가 단일 출처 — 이 파일을 직접 편집하지 말 것.",
            "days": days,
        }, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")

    total = sum(len(d["items"]) for d in days)
    print(f"  news.json 갱신: {len(days)}일 · {total}건")
    warn_repeats(days)


def _key_terms(title: str) -> set:
    """제목에서 고유명사스러운 토큰만 남긴다 (조사·일반어 제거)."""
    toks = re.findall(r"[A-Za-z][A-Za-z0-9.\-]{2,}|[가-힣]{2,}", title)
    stop = {"발표", "공개", "출시", "시행", "강화", "선임", "확보", "개편",
            "그리고", "위한", "관련", "이후", "대한", "최대", "규모"}
    return {t.lower() for t in toks if t not in stop}


def warn_repeats(days: list) -> None:
    """전날과 겹치는 항목을 경고한다. 막지는 않는다 — 판단은 사람이 한다."""
    hits = []
    for cur, prev in zip(days, days[1:]):          # days 는 최신순
        prev_urls = {i["url"] for i in prev["items"] if i["url"]}
        for it in cur["items"]:
            if it["url"] and it["url"] in prev_urls:
                hits.append((cur["date"], it["title"], "출처 동일"))
                continue
            a = _key_terms(it["title"])
            if not a:
                continue
            for p in prev["items"]:
                b = _key_terms(p["title"])
                if not b:
                    continue
                shared = a & b
                overlap = len(shared) / min(len(a), len(b))
                # 고유명사(라틴 문자 토큰)가 2개 이상 겹치면 비율이 낮아도 같은 사건일 공산이 크다.
                # 'Jeff Dean 퇴사' 와 'Jeff Dean, Discovery Loop 창업' 이 25% 로 새어나간 적이 있다.
                proper = {t for t in shared if re.match(r"^[a-z]", t)}
                if overlap >= 0.5 or len(proper) >= 2:
                    why = (f"고유명사 {'·'.join(sorted(proper))} 공유"
                           if len(proper) >= 2 else f"{overlap:.0%} 겹침")
                    hits.append((cur["date"], it["title"],
                                 f"'{p['title'][:30]}' 와 {why}"))
                    break

    if not hits:
        return
    print(f"\n  ⚠ 전날과 겹치는 항목 {len(hits)}건 — 확인 필요")
    for date, title, why in hits:
        print(f"    {date}  {title[:38]}  ({why})")
    print("  같은 사건이면 archive 에서 빼고 build-news.py 를 다시 돌린다.")


if __name__ == "__main__":
    main()
