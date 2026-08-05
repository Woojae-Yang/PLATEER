#!/usr/bin/env bash
# ============================================================
# 로컬 Mac에서 실행하는 정적 대시보드 배포 스크립트.
#
#   dashboard/{index.html,app.js,style.css}  →  EC2 웹 루트(/var/www/qa-reports)
#   를 ssh+rsync 로 직접 전송하고, 캐시버전(?v=)을 갱신한다.
#
# 기존 워크플로(로컬 수정 → git push → EC2 git pull → /var/www 로 복붙)를
# 한 줄로 대체한다. EC2 쪽에 deploy/ 스크립트가 없어도 동작한다.
# (git push 는 이력 보존용으로 따로 하면 됨 — 배포에는 불필요)
#
# 사용법 (맥 로컬 터미널에서):
#   ./deploy/deploy_local.sh
#
# 전제:
#   - ~/.ssh/config 에 Host 'ec2dash' 가 설정돼 있음 (없으면 EC2_HOST 를 user@DNS 로 지정)
#   - ec2-user 가 /var/www/qa-reports 에 쓰기 권한 있음 (지금까지 sudo 없이 cp 해왔다면 OK)
#   - data/ 는 EC2 generate_report.py 가 자동 기록하므로 이 스크립트 대상 아님
#
# 환경변수로 덮어쓰기 가능:
#   EC2_HOST=ec2-user@ec2-43-200-3-175.ap-northeast-2.compute.amazonaws.com \
#   DST=/var/www/qa-reports  ./deploy/deploy_local.sh
# ============================================================
set -euo pipefail

# 이 스크립트 위치 기준으로 dashboard 경로 추정 (repo 어디서 실행해도 동작)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="${SRC:-$(cd "$SCRIPT_DIR/../dashboard" && pwd)}"

EC2_HOST="${EC2_HOST:-ec2dash}"
DST="${DST:-/var/www/qa-reports}"

# 1) 필수 파일 확인
for f in index.html app.js style.css; do
  [ -f "$SRC/$f" ] || { echo "ERROR: $SRC/$f 없음"; exit 1; }
done

echo "→ 전송: $SRC  ⇒  $EC2_HOST:$DST"

# 2) 정적 3파일 전송 (-c: 내용 체크섬 비교 → 진짜 바뀐 것만 보냄)
rsync -avzc \
  "$SRC/index.html" "$SRC/app.js" "$SRC/style.css" \
  "$EC2_HOST:$DST/"

# 3) 원격 index.html 의 ?v=... 를 현재 epoch 로 갱신 (브라우저 캐시 확실히 무력화)
ver="$(date +%s)"
ssh "$EC2_HOST" "sed -i -E 's/\\?v=[A-Za-z0-9._-]+/?v=${ver}/g' '$DST/index.html'"

echo "✅ 배포 완료  (cache ?v=${ver})"
echo "   확인: http://aac-qa.gelatto.io:8080/  (브라우저 강력 새로고침)"
