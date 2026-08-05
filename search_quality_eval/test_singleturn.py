
from collections import defaultdict
from typing import Optional
from pathlib import Path
from core.config_loader import build_config, YAML_CONFIG
from core.args import build_parser, prompt_if_missing
from core.runners import run_api_test
from core.logger import logger, RUN_LOG_DIR
import argparse
import sys


'''[명령어 예시]
curl -N -X POST 'https://stg-gelatto-chat-780663204901.asia-northeast3.run.app/api/chat' \
  --header 'User-Id: tester_user_id-ywj-0609' \
  --header 'Vendor-Id: 0e26f03f-1fa4-4064-9ffd-ed69dd8dcc0e' \
  --header 'Lang: ja' \
  --header 'Business-Type: genser_discovery' \
  --header 'Content-Type: application/json' \
  --data '{
    "session_id": "sess-000-075aa0b5",
    "query": "大阪の魚類、今の時期いくらで仕入れられますか？"
  }'
'''

# ============================================================
# stdout을 통째로 로그 파일에 tee
# ============================================================
class TeeOutput:
    """stdout을 콘솔과 파일 양쪽에 동시 출력."""
    def __init__(self, *files):
        self.files = files
    def write(self, data):
        for f in self.files:
            f.write(data)
            f.flush()
    def flush(self):
        for f in self.files:
            f.flush()


def setup_log_file(prefix: str, run_dir: Path):
    """주어진 run_dir 안에 진행 로그 파일을 만들고 stdout을 tee 처리."""
    timestamp = run_dir.name   # "eg. 20260518_094030"
    log_path = run_dir / f"{prefix}_{timestamp}.txt"
    
    log_file = open(log_path, 'w', encoding='utf-8')
    sys.stdout = TeeOutput(sys.__stdout__, log_file)
    
    print(f"📝 로그 파일: {log_path}")
    return log_file


# ============================================================
# 인자 파싱
# ============================================================

def _format_profile_help(profile_keys: list[str]) -> str:
    """profile_key를 클라이언트 그룹별로 묶어서 정렬된 문자열로 변환."""
    groups: dict[str, list[str]] = defaultdict(list)
    for key in profile_keys:
        client = key.split("-")[0]   # "YAMATO-ja" → "YAMATO"
        groups[client].append(key)

    lines = ["사용 가능한 테스트 환경:"]
    for client in sorted(groups.keys()):
        lines.append(f"  [{client}]")
        for key in sorted(groups[client]):
            lines.append(f"    - {key}")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    return build_parser("LLM API 싱글턴 테스트 자동화").parse_args()


# ============================================================
# main
# ============================================================
if __name__ == "__main__":
    log_file = setup_log_file("singleturn", RUN_LOG_DIR)
    logger.info(f"=== Singleturn run start | logs={RUN_LOG_DIR} ===")
    try:
        args = parse_args()

        lang = prompt_if_missing(args.lang, "lang",
                         list(YAML_CONFIG["clients"].get("profiles", {}).keys()))
        spreadsheet_name = prompt_if_missing(args.spreadsheet, "spreadsheet_name")
        worksheet_name = prompt_if_missing(args.worksheet, "worksheet_name")

        config = build_config(
            lang=lang,
            spreadsheet_name=spreadsheet_name,
            worksheet_name=worksheet_name,
            max_workers=args.workers,
        )

        print("\n📋 실행 설정:")
        print(f"   profile_key    : {config['profile_key']}")
        print(f"   lang_code      : {config['lang_code']}")
        print(f"   spreadsheet    : {config['spreadsheet_name']}")
        print(f"   worksheet      : {config['worksheet_name']}")
        print(f"   user_id_prefix : {config['user_id_prefix']}")
        print(f"   api_base_url   : {config['api_base_url']}")
        _api_type = (config.get('api_type') or '').lower()
        _is_gcloud = _api_type in ('gcloud_run', 'gcloud', 'cloud_run', 'cloudrun', 'genserd', 'qa_gcloud')
        if _api_type.startswith('adk') or _is_gcloud:
            # body 라우팅 API (tab/lang/mode/search_backend) — ADK2-front / Cloud Run IAM
            print(f"   api_type       : {config['api_type']}")
            print(f"   tab            : {config.get('tab') or '(없음)'}")
            print(f"   mode           : {config.get('mode')}")
            print(f"   search_backend : {config.get('search_backend')}")
            if _is_gcloud:
                auth_mode = ('static-token' if config.get('iap_token')
                             else 'gcloud-identity-token')
                print(f"   auth           : Cloud Run IAM ({auth_mode})")
            else:
                iap_mode = ('service-account' if config.get('iap_credentials_file')
                            else 'static-token' if config.get('iap_token')
                            else 'ADC/미설정')
                print(f"   iap_audience   : {'설정됨' if config.get('iap_audience') else '(없음)'}")
                print(f"   iap_auth       : {iap_mode}")
        else:
            print(f"   business_type  : {config.get('business_type')}")
            print(f"   vendor_id      : {config.get('vendor_id') or '(없음)'}")
        print(f"   question_column: {config['question_column']}")
        print(f"   max_workers    : {config['max_workers']}")

        run_api_test(config)

        logger.info(f"=== Singleturn run done ===")

    except KeyboardInterrupt:
        print("\n\n⚠️  사용자에 의해 중단됨")
    except Exception as e:
        print(f"\n\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
    finally:
        sys.stdout = sys.__stdout__   # stdout 복원
        log_file.close()
    