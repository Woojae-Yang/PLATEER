#!/usr/bin/env bash
# ============================================================
# logs/ 월별 압축 아카이브 스크립트
# core/logger.py 가 실행마다 만드는 logs/YYYYMMDD_HHMMSS/ 를 그대로 두면
# 폴더 수가 무한정 쌓여 지저분해진다. 삭제 대신 "2개월 지난 달"을 통째로
# tar.gz 하나로 묶어 logs/archive/에 보관하고 원본 폴더는 지운다
# (데이터는 안 버리고 폴더 개수만 줄이는 방식).
#
# 기본 대상월 = 실행 시점 기준 "이번달 - 2개월".
# 예: 8월 1일에 실행 → 6월 로그를 archive/202606.tar.gz 로 압축.
#     7월(직전달)은 최근 디버깅에 쓸 수 있어 이번엔 건드리지 않고 그대로 둠.
#
# 사용법 (EC2 위에서):
#   chmod +x deploy/archive_logs.sh
#   ./deploy/archive_logs.sh --dry-run          # 미리보기
#   ./deploy/archive_logs.sh                    # 실제 압축 + 원본 삭제
#   ./deploy/archive_logs.sh --month 202605     # 특정 월 수동 지정
#
# crontab 등록 (매달 1일 08:00 KST, 2개월 전 로그 압축):
#   서버 시스템 시간대가 KST가 아닐 수 있어(EC2 기본은 보통 UTC) CRON_TZ로 명시.
#   crontab -e 로 아래 두 줄을 그대로 추가 (CRON_TZ 줄은 그 아래 모든 라인에 적용됨):
#   CRON_TZ=Asia/Seoul
#   0 8 1 * * cd /home/ec2-user/search_quality_eval/search_quality_eval && ./deploy/archive_logs.sh >> logs/_archive.log 2>&1
# ============================================================
set -uo pipefail

APP_DIR="${APP_DIR:-$(cd "$(dirname "$0")/.." && pwd)}"
LOG_DIR="${LOG_DIR:-$APP_DIR/logs}"
ARCHIVE_DIR="${ARCHIVE_DIR:-$LOG_DIR/archive}"
DRY_RUN=0
TARGET_MONTH=""

while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) DRY_RUN=1; shift ;;
    --month) TARGET_MONTH="$2"; shift 2 ;;
    *) echo "알 수 없는 옵션: $1"; exit 1 ;;
  esac
done

# 대상월 = 이번달 1일을 기준으로 2개월 전 (day-of-month 오차 방지 위해 1일로 앵커링)
# 로그 폴더명(YYYYMMDD_HHMMSS)은 core/config_loader.now_kst() 기준 KST로 찍힘.
# 서버 시스템 시간대가 KST가 아니면(EC2 기본 UTC 등) "현재 월" 계산이 어긋날 수 있어
# TZ=Asia/Seoul 을 명시해 시스템 시간대와 무관하게 항상 KST 기준으로 계산한다.
if [ -z "$TARGET_MONTH" ]; then
  anchor="$(TZ=Asia/Seoul date +%Y-%m-01)"
  TARGET_MONTH=$(TZ=Asia/Seoul date -d "$anchor -2 months" +%Y%m 2>/dev/null || TZ=Asia/Seoul date -j -v-2m -f "%Y-%m-%d" "$anchor" +%Y%m 2>/dev/null)
fi

if ! [[ "$TARGET_MONTH" =~ ^[0-9]{6}$ ]]; then
  echo "ERROR: TARGET_MONTH 형식이 올바르지 않음 (YYYYMM): $TARGET_MONTH"
  exit 1
fi

if [ ! -d "$LOG_DIR" ]; then
  echo "logs 디렉토리 없음: $LOG_DIR (압축할 것 없음)"
  exit 0
fi

archive_file="$ARCHIVE_DIR/${TARGET_MONTH}.tar.gz"

echo "============================================================"
echo " logs/ 월별 아카이브  |  LOG_DIR=$LOG_DIR  TARGET_MONTH=$TARGET_MONTH  DRY_RUN=$DRY_RUN"
echo " 산출물: $archive_file"
echo "============================================================"

if [ -f "$archive_file" ]; then
  echo "WARN: $archive_file 이미 존재 — 중복 실행 방지를 위해 중단합니다. 다시 만들려면 해당 파일을 먼저 지우세요."
  exit 1
fi

# 대상 폴더 수집 (YYYYMMDD_HHMMSS 패턴 + 앞 6자리가 TARGET_MONTH 와 일치하는 것만, 안전장치)
targets=()
for dir in "$LOG_DIR"/*/; do
  [ -d "$dir" ] || continue
  name="$(basename "$dir")"
  [[ "$name" =~ ^[0-9]{8}_[0-9]{6}$ ]] || continue
  [ "${name:0:6}" = "$TARGET_MONTH" ] && targets+=("$name")
done

if [ ${#targets[@]} -eq 0 ]; then
  echo "대상 폴더 없음 ($TARGET_MONTH). 종료."
  exit 0
fi

echo "대상 ${#targets[@]}개:"
printf '  %s\n' "${targets[@]}"

total_kb=0
for name in "${targets[@]}"; do
  kb=$(du -sk "$LOG_DIR/$name" 2>/dev/null | cut -f1)
  total_kb=$((total_kb + ${kb:-0}))
done
echo "원본 합계 용량: $((total_kb / 1024))MB"

if [ "$DRY_RUN" -eq 1 ]; then
  echo "(dry-run 모드 — 압축/삭제 안 함)"
  exit 0
fi

mkdir -p "$ARCHIVE_DIR"

# tar 압축 (LOG_DIR 기준 상대경로로 묶어 압축 해제 시 구조 유지)
if ! tar -czf "$archive_file" -C "$LOG_DIR" "${targets[@]}"; then
  echo "ERROR: 압축 실패, 원본은 삭제하지 않음"
  rm -f "$archive_file"
  exit 1
fi

# 압축본이 실제로 읽히는지 검증 후에만 원본 삭제 (안전장치)
if ! tar -tzf "$archive_file" >/dev/null 2>&1; then
  echo "ERROR: 압축본 무결성 검증 실패, 원본은 삭제하지 않음: $archive_file"
  exit 1
fi

archived_size=$(du -sh "$archive_file" | cut -f1)
echo "압축 완료 및 검증됨: $archive_file ($archived_size)"

for name in "${targets[@]}"; do
  rm -rf "${LOG_DIR:?}/$name"
done
echo "원본 ${#targets[@]}개 폴더 삭제 완료"
echo "============================================================"
