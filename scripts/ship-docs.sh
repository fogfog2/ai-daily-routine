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

echo "── 5. 카탈로그 ↔ 문서 정합성"
# 2026-08-14 사고: 사이트에는 HDR 편이 올라갔는데 루틴 저장소 커밋이 빠져
# catalog.py 에 등록되지 않았다. artifacts.json 은 DOCS 만 보고 새로 쓰므로
# 그 문서는 목록·필터·네비 어디에도 나오지 않는다 (파일은 남아 있다).
# 직링크를 아는 사람만 볼 수 있는 상태 — 조용히 사라진 것과 같다.
python3 - "$ROOT" "$PAGES/docs" <<'PY' || fail "카탈로그와 문서가 어긋납니다"
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(sys.argv[1]) / "scripts"))
from catalog import DOCS

docs = pathlib.Path(sys.argv[2])
cat = {d[3] for d in DOCS}
html = {p.stem for p in docs.glob("*.html")}

missing = sorted(cat - html)     # 카탈로그에 있는데 파일이 없다
orphan = sorted(html - cat)      # 파일은 있는데 카탈로그에 없다 ← 08-14 사고

for s in missing:
    print(f"  ✗ 카탈로그에 있으나 HTML 없음: {s}")
for s in orphan:
    print(f"  ✗ HTML 은 있으나 카탈로그 미등록: {s}  (목록에 안 나온다)")
if orphan:
    print("     → scripts/catalog.py 의 DOCS 에 등록하고 다시 실행하세요.")
if missing or orphan:
    sys.exit(1)
print(f"  카탈로그 {len(cat)}편 · HTML {len(html)}편 — 일치")
PY

echo "── 6. 유출 스캔 (공개 저장소이므로 반드시)"
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

echo "── 7. 커밋 · 푸시 (사이트)"
cd "$PAGES"
# 사이트에 변경이 없어도 여기서 빠져나가면 안 된다.
# 루틴 저장소(8단계)만 바뀐 경우가 실제로 있다 — 스크립트·카탈로그 수정 등.
# 예전엔 여기서 exit 0 했다가 루틴 저장소가 통째로 안 밀렸다.
if [[ -z "$(git status --porcelain)" ]]; then
    echo "  변경 없음 — 커밋 건너뜀"
else
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

    # HEAD:main 으로 민다. 'origin main' 이 아니라 'HEAD:main' 인 것이 중요하다.
    #
    # 클라우드 세션은 main 이 아니라 작업 브랜치에 체크아웃된 채로 돈다.
    # 그 상태에서 `git push origin main` 은 방금 만든 커밋이 아니라
    # **로컬 main 참조**(클론 시점에 멈춰 있는)를 밀어서 non-fast-forward 로 거부된다.
    # 2026-08-12·08-13 회차의 문서가 브랜치에 남고 사이트에 반영되지 않은 원인이다.
    git merge-base --is-ancestor origin/main HEAD \
        || fail "HEAD 가 origin/main 을 fast-forward 하지 않습니다 — 수동 확인 필요"
    git push -q origin HEAD:main

    # 세션 브랜치도 같이 밀어 둔다. 사이트는 main 이 서지만,
    # 브랜치가 남아 있어야 어느 세션이 무엇을 올렸는지 추적된다.
    BRANCH="$(git rev-parse --abbrev-ref HEAD)"
    if [[ "$BRANCH" != "HEAD" && "$BRANCH" != "main" ]]; then
        git push -q -u origin "$BRANCH" || echo "  (세션 브랜치 푸시 실패 — main 은 반영됨)"
    fi
    echo "  $(git log --oneline -1)"
fi

# ─────────────────────────────────────────────────────────────
# 8. 루틴 저장소도 같이 민다 — 여기를 빼먹어서 08-14 회차를 잃었다.
#
# 사이트만 밀면 HTML 은 올라가는데 catalog.py 등록이 남지 않는다.
# 그러면 다음 회차의 sync 가 artifacts.json 을 DOCS 기준으로 새로 써서
# 그 문서를 목록에서 빠뜨린다. 5단계가 이제 그걸 잡지만,
# 애초에 두 저장소가 갈라지지 않게 하는 것이 근본 해결이다.
#
# 사람이 "둘 다 커밋해야 함"을 기억하는 데 기대지 않는다.
# ─────────────────────────────────────────────────────────────
echo "── 8. 커밋 · 푸시 (루틴)"
cd "$ROOT"
if [[ -z "$(git status --porcelain)" ]]; then
    echo "  변경 없음 — 커밋 건너뜀"
else
    git stash -q
    if ! git pull -q --rebase origin main 2>/dev/null; then
        git rebase --abort 2>/dev/null || true
        git stash pop -q 2>/dev/null || true
        fail "루틴 저장소가 원격과 충돌 — 수동 정리 필요 (사이트는 이미 반영됨)"
    fi
    git stash pop -q 2>/dev/null || true

    git add -A
    git commit -q -m "$MSG

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"

    # 사이트와 같은 이유로 HEAD:main 을 쓴다 (작업 브랜치에서 도는 세션 대비)
    if git merge-base --is-ancestor origin/main HEAD 2>/dev/null; then
        git push -q origin HEAD:main
        echo "  $(git log --oneline -1)"
    else
        fail "루틴 저장소 HEAD 가 origin/main 을 fast-forward 하지 않습니다 (사이트는 이미 반영됨)"
    fi
fi

echo
echo "  https://fogfog2.github.io/ai-concepts/  (반영까지 1~2분)"
