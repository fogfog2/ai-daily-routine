#!/usr/bin/env bash
# 카탈로그(catalog.py)를 공개 사이트에 반영한다.
#
#   catalog.py ──> site-pages/data/artifacts.json  (GitHub Pages 목록)
#              └─> site-pages/docs/*.html          (상단 네비 주입)
#
# 배포 대상은 GitHub Pages 하나뿐이다.
# 집 서버·로컬 서버·Tailscale·앱 내장 사본은 더 이상 쓰지 않는다.
#
# 문서를 추가할 때는 catalog.py 의 DOCS 에 한 줄 넣고 이 스크립트를 돌린다.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PAGES="$ROOT/site-pages"

cd "$ROOT/scripts"

# 1) 카탈로그 검증 (중복 slug·미정의 단계·빈 단계를 여기서 잡는다)
python3 catalog.py

# 2) 공개 사이트 목록 데이터
#    문서 본문을 직접 수록하므로 목록은 내부 경로(docs/<slug>.html)를 가리킨다.
[[ -d "$PAGES/data" ]] || { echo "  site-pages/data 가 없습니다: $PAGES" >&2; exit 1; }

python3 - "$PAGES" <<'PY'
import json, pathlib, sys
from catalog import STAGES, TAGS, DOCS, url, href, validate

validate()
pages = pathlib.Path(sys.argv[1])
docs_dir = pages / "docs"

items = []
for row in DOCS:
    t, sub, uid, slug, stage, summ, d = row[:7]
    tags = row[7] if len(row) > 7 else []
    local = (docs_dir / f"{slug}.html").exists()
    items.append({
        "title": t, "subtitle": sub, "stage": stage, "summary": summ,
        "updated": d, "slug": slug, "tags": tags,
        "url": href(slug) if local else url(uid, slug),
        "local": local,
    })

# 실제로 쓰인 태그만 내보낸다 — 0편짜리 필터 버튼이 생기면 혼란스럽다
used = {t for i in items for t in i["tags"]}
data = {
    "note": "catalog.py 가 단일 출처 — 이 파일을 직접 편집하지 말 것.",
    "stages": [{k: s[k] for k in ("id", "no", "name", "tagline", "desc")} for s in STAGES],
    "tags": [{k: t[k] for k in ("id", "group", "name", "desc")}
             for t in TAGS if t["id"] in used],
    "items": items,
}
(pages / "data" / "artifacts.json").write_text(
    json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
n = sum(1 for i in items if i["local"])
print(f"  artifacts.json 갱신: {len(items)}편 (내부 {n} / 외부 {len(items)-n})")
PY

# 3) 뉴스 데이터 (archive/*.md → news.json)
python3 build-news.py

# 4) 문서 페이지에 상단 네비게이션 주입
python3 build-docs.py | tail -1

echo
echo "  배포: ./scripts/ship-docs.sh \"메시지\"  → https://fogfog2.github.io/ai-concepts/"
