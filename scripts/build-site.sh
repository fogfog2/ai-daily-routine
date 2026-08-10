#!/usr/bin/env bash
# archive/*.md 를 모아 site/index.html 을 재생성한다.
# 외부 의존성 없음(python3만 사용). CDN·원격 폰트를 쓰지 않아 오프라인에서 열린다.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
mkdir -p "$ROOT/site"

python3 "$ROOT/scripts/render.py" "$ROOT/archive" "$ROOT/site/index.html"
echo "빌드 완료: $ROOT/site/index.html"
