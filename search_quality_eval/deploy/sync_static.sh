#!/usr/bin/env bash
# ============================================================
# 정적 대시보드 파일을 repo(dashboard/) → nginx 웹 루트로 동기화.
# index.html/app.js/style.css 3개를 dashboard/ 에서 웹 루트로 그대로 복사(flatten)한다.
# app.js는 데이터를 상대경로 dashboard/data/ 로 참조하므로, 웹 루트 밑에
# dashboard/data/ 가 실제로 존재해야 한다(report_generator.py가 거기 직접 기록).
# 캐시 버전(?v=...)을 타임스탬프로 갱신해 브라우저 캐시를 확실히 무력화.
#
# 사용법 (EC2에서, dashboard/ 수정 또는 git pull 후):
#   ./deploy/sync_static.sh
#   # 경로를 직접 줄 수도 있음:
#   ./deploy/sync_static.sh ~/search_quality_eval/search_quality_eval/dashboard /var/www/qa-reports
#
# 참고: data/ 는 이 스크립트가 다루지 않는다. 웹 루트의 data(심볼릭 링크 → dashboard/data)는
#       과거 코드 호환용으로 남겨둔 것이라 정리 시점에 확인할 것.
#       csrag/ 는 별도 코드베이스라 이 스크립트 대상이 아니다.
# ============================================================
set -euo pipefail

SRC="${1:-$HOME/search_quality_eval/search_quality_eval/dashboard}"
DST="${2:-/var/www/qa-reports}"

for f in index.html app.js style.css; do
  [ -f "$SRC/$f" ] || { echo "ERROR: $SRC/$f 없음"; exit 1; }
done
[ -d "$DST" ] || { echo "ERROR: 웹 루트 $DST 없음"; exit 1; }

cp "$SRC/index.html" "$SRC/app.js" "$SRC/style.css" "$DST/"

# index.html 내 ?v=... 를 현재 epoch 로 일괄 치환 (매 배포마다 유니크 → 캐시 무력화)
ver="$(date +%s)"
sed -i -E "s/\?v=[A-Za-z0-9._-]+/?v=${ver}/g" "$DST/index.html"

echo "synced static → $DST  (cache ?v=${ver})"
echo "  브라우저 새로고침하면 최신 버전이 반영됩니다."
