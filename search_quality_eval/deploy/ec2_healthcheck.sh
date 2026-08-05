#!/usr/bin/env bash
# ============================================================
# EC2 배포 환경 점검 스크립트 (읽기 전용 / 변경 없음)
# 검색 품질 평가: nginx(정적 대시보드) + FastAPI(uvicorn) 구성
#
# 사용법 (EC2 위에서):
#   chmod +x deploy/ec2_healthcheck.sh
#   ./deploy/ec2_healthcheck.sh
#
# 환경에 맞게 아래 변수만 수정하면 됩니다. 환경변수로 덮어쓸 수도 있습니다:
#   APP_DIR=/srv/app DOMAIN=eval.example.com ./deploy/ec2_healthcheck.sh
# ============================================================
set -uo pipefail

# ── 점검 대상 설정 (환경에 맞게 수정) ──────────────────────
APP_DIR="${APP_DIR:-$(cd "$(dirname "$0")/.." && pwd)}"   # 프로젝트 루트
APP_PORT="${APP_PORT:-8080}"                              # uvicorn 내부 포트
APP_SERVICE="${APP_SERVICE:-search-quality-eval}"        # systemd 서비스명
DOMAIN="${DOMAIN:-}"                                      # 예: eval.example.com (있으면 HTTPS까지 점검)
DASHBOARD_DIR="${DASHBOARD_DIR:-$APP_DIR/dashboard}"
SA_JSON="${GOOGLE_APPLICATION_CREDENTIALS:-}"             # Vertex/Sheets 서비스계정 JSON 경로

# 외부 egress 점검 대상 (사내망 STG 엔드포인트는 clients.yaml에서 자동 추출)
EGRESS_HOSTS=(
  "aiplatform.googleapis.com:443"      # Vertex AI (Gemini 평가)
  "sheets.googleapis.com:443"          # Google Sheets
  "oauth2.googleapis.com:443"          # 서비스계정 토큰 발급
)

# ── 출력 헬퍼 ──────────────────────────────────────────────
PASS=0; WARN=0; FAIL=0
ok()   { printf "  \033[32m[ OK ]\033[0m %s\n" "$1"; PASS=$((PASS+1)); }
warn() { printf "  \033[33m[WARN]\033[0m %s\n" "$1"; WARN=$((WARN+1)); }
bad()  { printf "  \033[31m[FAIL]\033[0m %s\n" "$1"; FAIL=$((FAIL+1)); }
hdr()  { printf "\n\033[1m== %s ==\033[0m\n" "$1"; }
have() { command -v "$1" >/dev/null 2>&1; }

echo "============================================================"
echo " EC2 배포 환경 점검  |  $(date '+%Y-%m-%d %H:%M:%S %Z')"
echo " APP_DIR=$APP_DIR  PORT=$APP_PORT  SERVICE=$APP_SERVICE  DOMAIN=${DOMAIN:-(미설정)}"
echo "============================================================"

# ── 1. 코드 / 디렉터리 ─────────────────────────────────────
hdr "1. 코드 및 디렉터리"
[ -d "$APP_DIR" ]            && ok "APP_DIR 존재: $APP_DIR"            || bad "APP_DIR 없음: $APP_DIR"
[ -f "$APP_DIR/api/main.py" ] && ok "api/main.py 존재"               || bad "api/main.py 없음 (pull/경로 확인)"
[ -d "$DASHBOARD_DIR" ]      && ok "대시보드 디렉터리 존재"            || bad "대시보드 디렉터리 없음: $DASHBOARD_DIR"
[ -f "$DASHBOARD_DIR/index.html" ] && ok "dashboard/index.html 존재" || bad "dashboard/index.html 없음"
if [ -d "$DASHBOARD_DIR/data" ] && ls "$DASHBOARD_DIR/data/"*.json >/dev/null 2>&1; then
  [ -f "$DASHBOARD_DIR/data/index.json" ] && ok "dashboard/data/index.json 존재 (셀렉터용)" || warn "data/*.json은 있으나 index.json 없음 → 셀렉터 비어보일 수 있음"
else
  warn "dashboard/data 에 회차 JSON 없음 (리포트 1회 생성 필요)"
fi
if git -C "$APP_DIR" rev-parse --short HEAD >/dev/null 2>&1; then
  ok "git HEAD: $(git -C "$APP_DIR" rev-parse --short HEAD) ($(git -C "$APP_DIR" rev-parse --abbrev-ref HEAD))"
fi

# ── 2. Python / 의존성 ─────────────────────────────────────
hdr "2. Python 및 의존성"
if have python3; then ok "python3: $(python3 -V 2>&1)"; else bad "python3 없음"; fi
PYBIN="python3"
if   [ -x "$APP_DIR/venv/bin/python" ];  then PYBIN="$APP_DIR/venv/bin/python";  ok "venv 발견: $APP_DIR/venv ($("$PYBIN" -V 2>&1))"
elif [ -x "$APP_DIR/.venv/bin/python" ]; then PYBIN="$APP_DIR/.venv/bin/python"; ok "venv 발견: $APP_DIR/.venv ($("$PYBIN" -V 2>&1))"
else warn "venv(venv/.venv) 없음 → 시스템 python 사용 가정 (코드가 3.10+ 문법 사용, 3.9면 import 실패)"; fi
"$PYBIN" - <<'PY' 2>/dev/null && ok "핵심 의존성 import 성공 (fastapi/uvicorn/gspread/google-genai)" || bad "의존성 import 실패 → pip install -r api/requirements.txt 확인"
import fastapi, uvicorn, gspread, yaml, requests
import google.genai  # noqa
PY

# ── 3. 설정 파일 / 자격 증명 ───────────────────────────────
hdr "3. 설정 파일 및 자격 증명"
for f in config/clients.yaml config/vertex.yaml config/credentials.json config/defaults.yaml; do
  [ -f "$APP_DIR/$f" ] && ok "$f 존재" || bad "$f 없음"
done
# Vertex 인증: 코드(per_query_evaluator)가 vertex.yaml의 vertex_credentials_file을 직접 로드
# (파일명이 비어있을 때만 ADC 폴백). 따라서 GOOGLE_APPLICATION_CREDENTIALS는 보통 불필요.
VCF=""
if have python3 && [ -f "$APP_DIR/config/vertex.yaml" ]; then
  VCF=$(python3 -c "import yaml; print(yaml.safe_load(open('$APP_DIR/config/vertex.yaml')).get('vertex_credentials_file','') or '')" 2>/dev/null)
fi
if [ -n "$VCF" ] && [ -f "$APP_DIR/config/$VCF" ]; then
  ok "Vertex 서비스계정 JSON 존재: config/$VCF (vertex.yaml 지정)"
elif [ -n "$VCF" ]; then
  bad "vertex.yaml가 가리키는 config/$VCF 없음 → Vertex 인증 실패"
elif [ -n "$SA_JSON" ] && [ -f "$SA_JSON" ]; then
  ok "GOOGLE_APPLICATION_CREDENTIALS 파일 존재: $SA_JSON (ADC)"
else
  warn "vertex_credentials_file 미설정 & ADC 없음 → Vertex 인증 경로 확인 필요"
fi
[ -n "${API_KEY:-}" ] && ok "API_KEY 환경변수 설정됨 (X-API-Key 인증 활성)" || warn "API_KEY 미설정 → API 인증 없이 열림 (내부망 한정이면 OK)"

# ── 4. 애플리케이션 서비스 (uvicorn) ───────────────────────
hdr "4. 애플리케이션 서비스 (uvicorn :$APP_PORT)"
if have systemctl; then
  if systemctl list-unit-files 2>/dev/null | grep -q "^${APP_SERVICE}"; then
    systemctl is-active --quiet "$APP_SERVICE" && ok "systemd '$APP_SERVICE' active" || bad "systemd '$APP_SERVICE' 비활성 → systemctl status $APP_SERVICE"
    systemctl is-enabled --quiet "$APP_SERVICE" 2>/dev/null && ok "'$APP_SERVICE' 부팅 시 자동시작 enabled" || warn "'$APP_SERVICE' enabled 아님 → 재부팅 후 안 뜸 (systemctl enable)"
  else
    warn "systemd 유닛 '$APP_SERVICE' 없음 → 서비스명 확인 또는 유닛 미등록"
  fi
fi
# 내부 포트 LISTEN 확인 + 소유 프로세스 (nginx가 점유하면 API 포트 충돌)
PORT_OWNER=$( { sudo -n ss -ltnp 2>/dev/null || ss -ltnp 2>/dev/null; } | grep ":$APP_PORT " | grep -oE 'users:\(\("[^"]+' | head -1 | sed 's/.*"//' )
if [ "$PORT_OWNER" = "nginx" ]; then
  bad "포트 $APP_PORT 를 nginx가 점유 중 → uvicorn(API)이 이 포트로 못 뜸. API용 포트를 분리하세요 (예: 8000)"
elif [ -n "$PORT_OWNER" ]; then
  ok "포트 $APP_PORT LISTEN 중 (소유 프로세스: $PORT_OWNER)"
elif (have ss && ss -ltn 2>/dev/null | grep -q ":$APP_PORT ") || (have netstat && netstat -ltn 2>/dev/null | grep -q ":$APP_PORT "); then
  ok "포트 $APP_PORT LISTEN 중"
else
  bad "포트 $APP_PORT LISTEN 안 함 → uvicorn 미기동"
fi
# /health 직접 호출
if have curl; then
  code=$(curl -s -o /dev/null -w '%{http_code}' "http://127.0.0.1:$APP_PORT/health" 2>/dev/null); code=${code:-000}
  [ "$code" = "200" ] && ok "GET 127.0.0.1:$APP_PORT/health → 200" || bad "127.0.0.1:$APP_PORT/health → $code"
fi

# ── 5. nginx ───────────────────────────────────────────────
hdr "5. nginx (리버스 프록시 + 정적 서빙)"
if have nginx; then
  ok "nginx 설치됨: $(nginx -v 2>&1 | sed 's#nginx version: ##')"
  if nginx -t >/dev/null 2>&1; then ok "nginx -t 설정 문법 정상"
  elif sudo -n nginx -t >/dev/null 2>&1; then ok "nginx -t 설정 문법 정상 (sudo)"
  else warn "nginx -t 를 비루트로 확인 불가(권한) → 'sudo nginx -t' 로 직접 확인"; fi
  if have systemctl; then systemctl is-active --quiet nginx && ok "nginx active" || bad "nginx 비활성"; fi
  # 정적 root가 dashboard를 가리키는지 추정 점검
  if nginx -T 2>/dev/null | grep -qiE "root\s+.*dashboard"; then ok "nginx 설정에 dashboard root 발견"; else warn "nginx 설정에서 dashboard root를 못 찾음 (경로 직접 확인 권장)"; fi
  if nginx -T 2>/dev/null | grep -qiE "proxy_pass\s+http://(127\.0\.0\.1|localhost):$APP_PORT"; then ok "nginx proxy_pass → :$APP_PORT 발견"; else warn "nginx에서 :$APP_PORT 로의 proxy_pass를 못 찾음 (API 프록시 경로 확인)"; fi
else
  bad "nginx 미설치"
fi

# ── 6. 로컬 엔드 투 엔드 (nginx 경유) ──────────────────────
hdr "6. nginx 경유 엔드포인트"
if have curl; then
  code=$(curl -s -o /dev/null -w '%{http_code}' "http://127.0.0.1/" 2>/dev/null); code=${code:-000}
  [ "$code" = "200" ] && ok "GET http://127.0.0.1/ (대시보드) → 200" || warn "http://127.0.0.1/ → $code (정적 root/포트 확인)"
  # API 프록시 경로는 환경마다 달라 (/api, /health 등) — 둘 다 시도
  for p in /api/health /health; do
    c=$(curl -s -o /dev/null -w '%{http_code}' "http://127.0.0.1$p" 2>/dev/null); c=${c:-000}
    [ "$c" = "200" ] && { ok "GET http://127.0.0.1$p → 200 (API 프록시 동작)"; break; }
  done
fi

# ── 7. 인바운드 보안그룹 (포트 노출) ───────────────────────
hdr "7. 인바운드 포트"
for port in 80 443; do
  if (have ss && ss -ltn 2>/dev/null | grep -q ":$port ") || (have netstat && netstat -ltn 2>/dev/null | grep -q ":$port "); then
    ok "포트 $port LISTEN 중"
  else
    [ "$port" = 443 ] && warn "포트 443 LISTEN 안 함 (TLS 미설정이면 데브옵스 티켓에 인증서 요청)" || bad "포트 80 LISTEN 안 함"
  fi
done
echo "  (주의: 외부 접속 가능 여부는 AWS 보안그룹 인바운드 규칙에도 좌우됨 — 콘솔에서 80/443 허용 확인)"

# ── 8. 아웃바운드(egress) 연결 ─────────────────────────────
hdr "8. 아웃바운드 연결 (평가·시트·챗 API)"
test_tcp() { # host:port
  local hp="$1" h="${1%%:*}" p="${1##*:}"
  if have nc; then nc -z -w3 "$h" "$p" >/dev/null 2>&1; return $?; fi
  timeout 3 bash -c ">/dev/tcp/$h/$p" >/dev/null 2>&1
}
for hp in "${EGRESS_HOSTS[@]}"; do
  test_tcp "$hp" && ok "egress $hp 도달" || bad "egress $hp 불가 → 보안그룹/NAT/방화벽 확인"
done
# 사내망 STG 챗 엔드포인트: clients.yaml의 api_base_url 추출해 점검
if [ -f "$APP_DIR/config/clients.yaml" ] && have python3; then
  while read -r host; do
    [ -z "$host" ] && continue
    test_tcp "$host:443" && ok "egress(사내망) $host:443 도달" || bad "egress(사내망) $host:443 불가 → 사내망 라우팅/VPN/피어링 필요 (데브옵스 요청)"
  done < <(python3 - "$APP_DIR/config/clients.yaml" <<'PY'
import sys,re,yaml
try:
    d=yaml.safe_load(open(sys.argv[1],encoding="utf-8"))
except Exception:
    sys.exit(0)
hosts=set()
def walk(o):
    if isinstance(o,dict):
        for k,v in o.items():
            if isinstance(v,str) and re.match(r"https?://",v) and ("base" in k.lower() or "url" in k.lower()):
                m=re.match(r"https?://([^/:]+)",v);
                if m: hosts.add(m.group(1))
            else: walk(v)
    elif isinstance(o,list):
        for v in o: walk(v)
walk(d)
print("\n".join(sorted(hosts)))
PY
)
fi

# ── 요약 ───────────────────────────────────────────────────
echo ""
echo "============================================================"
printf " 결과:  \033[32mPASS %d\033[0m  /  \033[33mWARN %d\033[0m  /  \033[31mFAIL %d\033[0m\n" "$PASS" "$WARN" "$FAIL"
echo "============================================================"
[ "$FAIL" -gt 0 ] && exit 1 || exit 0
