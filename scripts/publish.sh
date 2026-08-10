#!/usr/bin/env bash
# archive/*.md 를 게임 서버(public/ai/data/)로 내보낸다.
#
# 게임 서버는 이미 public/ 을 정적 서빙하므로, JSON 만 떨궈두면
# 웹(http://<서버>:8080/ai/)과 앱 양쪽에서 바로 보인다.
#
# 사용법: ./scripts/publish.sh [게임_저장소_경로]
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GAME="${1:-/home/sj/src/game}"
DST="$GAME/public/ai/data"

[[ -d "$GAME/public" ]] || { echo "게임 저장소를 찾을 수 없습니다: $GAME" >&2; exit 1; }
mkdir -p "$DST"

python3 "$ROOT/scripts/export_json.py" "$ROOT/archive" "$DST"

echo
echo "  웹  : http://<서버주소>:8080/ai/"
echo "  앱  : 서버에 붙으면 목록에 'AI DAILY' 카드가 보입니다"
echo "  오프라인 사본까지 갱신하려면: $GAME/tools/bundle-web.sh"
