#!/usr/bin/env bash
# 오늘자 리포트 뼈대를 생성한다. 이미 있으면 건드리지 않는다.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DATE="${1:-$(date +%F)}"
FILE="$ROOT/archive/$DATE.md"

mkdir -p "$ROOT/archive"

if [[ -e "$FILE" ]]; then
  echo "이미 존재함: $FILE (변경하지 않음)"
  exit 0
fi

cat > "$FILE" <<EOF
# AI Daily — $DATE

> 수집 범위: $(date -d "$DATE -1 day" +%F) ~ $DATE

<!-- 항목 형식은 ROUTINE.md [4] 요약 참조 -->

EOF

echo "생성됨: $FILE"
