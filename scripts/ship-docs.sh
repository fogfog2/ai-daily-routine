#!/usr/bin/env bash
# 기술문서 검증 → 동기화 → 커밋 → 푸시.
#
# 자동 실행되는 루틴이 쓰는 스크립트라, 사람이 눈으로 확인하지 않는다는 전제로 짰다.
# 그래서 "의심스러우면 멈춘다". 검증 하나라도 실패하면 커밋하지 않고 빠져나온다.
#
#   ./scripts/ship-docs.sh "커밋 메시지"
#   ./scripts/ship-docs.sh --dry-run "커밋 메시지"   # 검증까지만
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PAGES="$ROOT/site-pages"
DRY=0

if [[ "${1:-}" == "--dry-run" ]]; then DRY=1; shift; fi
MSG="${1:-기술문서 갱신}"

cd "$ROOT"
fail() { echo "  ✗ $1" >&2; exit 1; }

# 공개 사이트는 별도 저장소(fogfog2/ai-concepts)다.
# 클라우드에서 루틴 저장소만 체크아웃된 경우 여기 없으므로 받아온다.
if [[ ! -d "$PAGES/.git" ]]; then
    echo "── 0. 공개 사이트 저장소 준비 (없어서 clone)"
    # 안전장치: 지울 대상이 정말 ROOT 아래의 site-pages 인지 확인한 뒤에만 건드린다.
    [[ "$PAGES" == "$ROOT/site-pages" ]] || fail "예상치 못한 경로: $PAGES"
    if [[ -e "$PAGES" ]]; then
        mv "$PAGES" "$PAGES.bak.$$"   # 지우지 않고 옆으로 치운다
        echo "  기존 폴더를 $PAGES.bak.$$ 로 옮겼습니다"
    fi
    git clone -q git@github.com:fogfog2/ai-concepts.git "$PAGES" \
        || fail "공개 사이트 저장소를 받지 못했습니다 (SSH 키 확인)"
fi

echo "── 1. 카탈로그 검증"
python3 scripts/catalog.py || fail "카탈로그 검증 실패"

echo "── 2. 동기화 (artifacts.json · 네비 주입)"
./scripts/sync-catalog.sh >/dev/null || fail "동기화 실패"

echo "── 3. 문서 점검 (태그·테마·SVG 접근성·미정의 변수)"
( cd scripts/docs && python3 check.py ../../site-pages/docs/*.html >/tmp/ai-docs-check.txt 2>&1 ) || {
    grep "^\[FAIL" /tmp/ai-docs-check.txt >&2 || true
    fail "문서 점검 실패 — 위 항목을 고칠 것"
}
echo "  전부 통과: $(grep -c '^\[OK' /tmp/ai-docs-check.txt)편"

echo "── 4. 내부 상호링크"
python3 - "$PAGES/docs" <<'PY' || fail "깨진 내부 링크"
import pathlib, re, sys
d = pathlib.Path(sys.argv[1]); bad = []
for p in sorted(d.glob("*.html")):
    for m in re.finditer(r'href="([a-z0-9-]+\.html)"', p.read_text(encoding="utf-8")):
        if not (d / m.group(1)).exists():
            bad.append(f"{p.name} → {m.group(1)}")
for b in bad: print(f"  {b}")
print(f"  깨진 링크 {len(bad)}건")
sys.exit(1 if bad else 0)
PY

echo "── 5. 유출 스캔 (공개 저장소이므로 반드시)"
if grep -rInE '100\.64\.[0-9]+\.[0-9]+|192\.168\.[0-9]+\.[0-9]+|/home/[a-z]+/|BEGIN [A-Z ]*PRIVATE KEY|(api[_-]?key|secret|password)[[:space:]]*[:=]' \
       "$PAGES" 2>/dev/null | grep -v '\.git/' | head -5; then
    fail "민감 정보로 보이는 문자열 발견 — 위 줄 확인"
fi
echo "  깨끗함"

if [[ $DRY -eq 1 ]]; then
    echo
    echo "  [dry-run] 여기서 멈춘다. 커밋·푸시 안 함."
    cd "$PAGES" && git status -s | head -20
    exit 0
fi

echo "── 6. 커밋 · 푸시"
cd "$PAGES"
if [[ -z "$(git status --porcelain)" ]]; then
    echo "  변경 없음 — 커밋 건너뜀"
    exit 0
fi

# 집 PC 와 클라우드가 같은 저장소에 푸시할 수 있으므로 먼저 원격을 반영한다.
# 문서는 파일 단위로 갈리므로 rebase 로 충돌 없이 얹히는 것이 보통이다.
git stash -q
if ! git pull -q --rebase origin main 2>/dev/null; then
    git rebase --abort 2>/dev/null || true
    git stash pop -q 2>/dev/null || true
    fail "원격과 충돌 — 수동으로 정리해야 합니다"
fi
git stash pop -q 2>/dev/null || true

git add -A
git commit -q -m "$MSG

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
git push -q origin main
echo "  $(git log --oneline -1)"
echo
echo "  https://fogfog2.github.io/ai-concepts/  (반영까지 1~2분)"
