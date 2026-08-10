#!/usr/bin/env bash
# 카탈로그(catalog.py)를 두 도입 페이지에 반영한다.
#
#   catalog.py  ──┬──> game/public/ai/data/artifacts.json   (게임 서버 /ai/)
#                 └──> archive.html                          (claude.ai Archive)
#
# 문서를 추가할 때는 catalog.py 의 DOCS 에 한 줄 넣고 이 스크립트를 돌린다.
# archive.html 은 생성만 되므로, 발행은 Claude 에게 Artifact 갱신을 요청한다.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# 집 서버(게임 저장소) 경로. 환경변수로 덮어쓸 수 있다.
GAME="${1:-${AI_DAILY_GAME_DIR:-$HOME/src/game}}"
DST="$GAME/public/ai/data"

# 집 서버는 있으면 갱신하고 없으면 건너뛴다.
# 클라우드(Claude Code routines)에서는 게임 저장소가 없으므로 여기서 멈추면 안 된다.
HAVE_GAME=1
[[ -d "$GAME/public/ai" ]] || { HAVE_GAME=0; echo "  집 서버 경로 없음 — 공개 사이트만 갱신합니다 ($GAME)"; }

cd "$ROOT/scripts"

# 1) 카탈로그 검증 (중복 UUID·미정의 단계·빈 단계를 여기서 잡는다)
python3 catalog.py

# 2) 게임 서버용 JSON
if [[ $HAVE_GAME -eq 1 ]]; then
python3 - "$DST" <<'PY'
import json, pathlib, sys
from catalog import STAGES, DOCS, url, validate

validate()
data = {
    "note": "파이프라인 단계별 분류. catalog.py 가 단일 출처 — 이 파일을 직접 편집하지 말 것.",
    "stages": [{"id": s["id"], "no": s["no"], "name": s["name"],
                "tagline": s["tagline"], "desc": s["desc"]} for s in STAGES],
    "items": [{"title": t, "subtitle": sub, "url": url(u, slug), "stage": st,
               "summary": summ, "updated": d}
              for t, sub, u, slug, st, summ, d in DOCS],
}
out = pathlib.Path(sys.argv[1]) / "artifacts.json"
out.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"  artifacts.json 갱신: {len(data['items'])}편")
PY
fi

# 3) Archive 페이지 HTML
python3 build-archive.py

# 4) 공개 사이트(GitHub Pages)
#    문서 본문을 직접 수록하므로, 목록은 내부 경로(docs/<slug>.html)를 가리킨다.
#    아직 회수하지 못한 문서만 원본 아티팩트 링크로 폴백한다.
PAGES="$ROOT/site-pages"
if [[ -d "$PAGES/data" ]]; then
    # 뉴스 날짜 목록은 집 서버 쪽이 원본이다. 없으면 기존 것을 그대로 둔다.
    [[ $HAVE_GAME -eq 1 && -f "$DST/index.json" ]] && cp "$DST/index.json" "$PAGES/data/"
    python3 - "$PAGES" <<'PY'
import json, pathlib, sys
from catalog import STAGES, DOCS, url, href, validate

validate()
pages = pathlib.Path(sys.argv[1])
docs_dir = pages / "docs"

items = []
for t, sub, uid, slug, stage, summ, d in DOCS:
    local = (docs_dir / f"{slug}.html").exists()
    items.append({
        "title": t, "subtitle": sub, "stage": stage, "summary": summ,
        "updated": d, "slug": slug,
        "url": href(slug) if local else url(uid, slug),
        "local": local,
    })

data = {
    "note": "catalog.py 가 단일 출처 — 이 파일을 직접 편집하지 말 것.",
    "stages": [{k: s[k] for k in ("id", "no", "name", "tagline", "desc")} for s in STAGES],
    "items": items,
}
(pages / "data" / "artifacts.json").write_text(
    json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
n = sum(1 for i in items if i["local"])
print(f"  site-pages 갱신: {len(items)}편 (내부 {n} / 외부 {len(items)-n})")
PY
    # 문서 페이지에 네비게이션·내부 링크 적용
    python3 build-docs.py | tail -1
fi

echo
echo "  집   : http://<서버주소>:8080/ai/  → 🧩 기술문서 탭"
echo "  앱   : $GAME/tools/bundle-web.sh 실행 시 오프라인 사본도 갱신"
echo "  공개 : cd $PAGES && git add -A && git commit -m '문서 갱신' && git push"
echo "  Archive: scripts/archive.html 을 Claude 에게 Artifact 갱신 요청"
