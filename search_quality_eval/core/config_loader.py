
import os
import yaml
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional



# ============================================================
# KST 헬퍼 — EC2는 UTC이므로 모든 datetime 은 이 함수로 생성
# ============================================================
KST = timezone(timedelta(hours=9))

def now_kst() -> datetime:
    """현재 시각을 KST 기준으로 반환 (외부 라이브러리 불필요)"""
    return datetime.now(tz=KST)


# ============================================================
# 프로젝트 루트 & YAML 설정 로드 (모듈 로드 시 1회)
# ============================================================
def _find_project_root() -> Path:
    """현재 파일에서 부모로 올라가며 프로젝트 루트를 찾는다."""
    current = Path(__file__).resolve().parent
    markers = (".git", "requirements.txt", "config")  # 루트에만 있는 것들

    for parent in [current, *current.parents]:
        if any((parent / m).exists() for m in markers):
            return parent

    raise RuntimeError(
        "프로젝트 루트를 찾을 수 없습니다. "
        ".git, requirements.txt, config 중 하나가 있는지 확인하세요."
    )

PROJECT_ROOT = _find_project_root()
CONFIG_DIR = PROJECT_ROOT / "config"


def _load_yaml_configs() -> dict:
    def _load(name: str, required: bool = True) -> dict:
        path = CONFIG_DIR / name
        try:
            with open(path, encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            if required:
                raise FileNotFoundError(f"설정 파일을 찾을 수 없습니다: {path}")
            return {}
        except yaml.YAMLError as e:
            raise ValueError(f"YAML 파싱 실패 ({name}): {e}")

    return {
        "defaults": _load("defaults.yaml"),
        "columns":  _load("columns.yaml"),
        "clients":  _load("clients.yaml"),
        "vertex":   _load("vertex.yaml",   required=False),
        "phoenix":  _load("phoenix.yaml",  required=False),
    }

YAML_CONFIG = _load_yaml_configs()


# ============================================================
# CONFIG 빌더
# ============================================================
def build_config(lang: str, spreadsheet_name: str, worksheet_name: str,
                 max_workers: Optional[int] = None) -> dict:
    profiles = YAML_CONFIG["clients"].get("profiles", {})
    columns = YAML_CONFIG["columns"]
    defaults = YAML_CONFIG["defaults"]
    
    if lang not in profiles:
        raise ValueError(
            f"지원하지 않는 lang: '{lang}'. 사용 가능: {list(profiles.keys())}"
        )

    profile = profiles[lang]
    lang_code = profile.get("lang_code")

    if lang_code not in columns:
        raise ValueError(
            f"'{lang}' 프로파일의 lang_code='{lang_code}'를 columns.yaml에서 찾을 수 없습니다. "
            f"사용 가능: {list(columns.keys())}"
        )

    today = now_kst().strftime("%Y%m%d")

    config = {
        **defaults,
        **columns[lang_code],
        **profile,
        "profile_key": lang,                         
        "spreadsheet_name": spreadsheet_name,
        "worksheet_name": worksheet_name,
        "user_id_prefix": f"qa-{lang}-{today}",
    }

    if max_workers is not None:
        config["max_workers"] = max_workers

    config["credentials_file"] = str(CONFIG_DIR / config["credentials_file"])

    # IAP 서비스계정 JSON 경로: 상대경로면 config/ 기준으로 해석 (adk_front 프로파일용)
    iap_cred = config.get("iap_credentials_file")
    if iap_cred and not os.path.isabs(iap_cred):
        config["iap_credentials_file"] = str(CONFIG_DIR / iap_cred)

    config["phoenix"] = get_phoenix_config(lang)

    return config


# ============================================================
# Vertex AI 설정 빌더
# ============================================================
def get_vertex_config() -> dict:
    """
    vertex.yaml의 Vertex AI 설정을 읽어 반환한다.

    vertex_project_id가 비어 있으면 credentials JSON 파일의 project_id를 자동 사용.

    Returns:
        {
            project_id,       ← GCP 프로젝트 ID
            location,         ← 리전 (예: asia-northeast1)
            credentials_file, ← 서비스 계정 JSON 절대 경로 (없으면 ADC 사용)
            model,            ← Gemini 모델 ID
            max_output_tokens ← 생성 출력 토큰 상한
            max_workers,       ← 동시 호출 수
            max_retries,       ← 재시도 횟수
            retry_backoff      ← 재시도 backoff 초
            max_eval_concurrency ← API 동시 평가 요청 상한
        }
    """
    import json as _json

    vertex = YAML_CONFIG.get("vertex") or {}
    creds_filename = vertex.get("vertex_credentials_file", "")
    creds_file = str(CONFIG_DIR / creds_filename) if creds_filename else ""

    # project_id: vertex.yaml 우선, 비어있으면 credentials JSON에서 자동 추출
    project_id = vertex.get("vertex_project_id", "")
    if not project_id and creds_file:
        try:
            with open(creds_file, encoding="utf-8") as f:
                project_id = _json.load(f).get("project_id", "")
        except Exception:
            pass

    return {
        "project_id":       project_id,
        "location":         vertex.get("vertex_location", "asia-northeast1"),
        "credentials_file": creds_file,
        "model":            vertex.get("vertex_model", "gemini-3.1-flash-lite"),
        "max_output_tokens": int(vertex.get("vertex_max_output_tokens", 4096)),
        "max_workers":      int(vertex.get("vertex_max_workers", 5)),
        "max_retries":      int(vertex.get("vertex_max_retries", 3)),
        "retry_backoff":    float(vertex.get("vertex_retry_backoff", 2.0)),
        "max_eval_concurrency": int(vertex.get("vertex_max_eval_concurrency", 8)),
        "eval_log_retention_days": int(vertex.get("vertex_eval_log_retention_days", 14)),
    }


# ============================================================
# Phoenix 설정 빌더
# ============================================================
def get_phoenix_config(lang: str) -> dict:
    """
    lang 프로파일에 맞는 Phoenix 연동 설정을 반환한다.

    Returns:
        {
            url, email, password,
            project_key, project_id,
            delay_sec, max_retries, retry_backoff,
            enabled  ← project_id가 비어 있으면 False
        }
    """
    phoenix = YAML_CONFIG.get("phoenix") or {}
    projects    = phoenix.get("projects")      or {}
    profile_map = phoenix.get("profile_project_map") or {}

    project_key = profile_map.get(lang) or phoenix.get("default_project", "GELATTO-STG")
    project_id  = projects.get(project_key, "")

    return {
        "url":           phoenix.get("url",      "http://34.47.106.52:6006"),
        "email":         os.getenv("PHOENIX_EMAIL", phoenix.get("email",    "")),
        "password":      os.getenv("PHOENIX_PASS",  phoenix.get("password", "")),
        "project_key":   project_key,
        "project_id":    project_id,
        "delay_sec":     float(phoenix.get("delay_sec",     5.0)),
        "max_retries":   int(  phoenix.get("max_retries",   3)),
        "retry_backoff": float(phoenix.get("retry_backoff", 2.0)),
        "enabled":       bool(project_id),
    }
