"""
2단계 집계 LLM 호출. aggregator의 결정론 통계 + 대표 케이스를 받아서
정성 종합(overall_assessment, findings, action_items, sections)을 생성한다.
LLM 호출 1회.
"""
import json
import time
from pathlib import Path

from google import genai
from google.genai import types
from google.oauth2 import service_account

from .schemas import AggregateAnalysis


MODEL = "gemini-3.1-flash-lite"
MAX_RETRIES = 3
RETRY_BACKOFF = 2.0

_VERTEX_SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]


def run_aggregate_llm(  vertex_config: dict, prompt_path: Path,
                        aggregator_result: dict, meta: dict,) -> dict:
    """
    Args:
        vertex_config: get_vertex_config() 반환값
                       {"project_id", "location", "credentials_file"}
        prompt_path: 2단계 프롬프트 md 경로 (prompt_aggregate_v1.md)
        aggregator_result: aggregator.aggregate() 반환값
        meta: {"date": "20260526", "env": "mizuno_prod-ja"}

    Returns:
        AggregateAnalysis dict (overall_assessment, findings, action_items, sections)
    """
    if not prompt_path.exists():
        raise FileNotFoundError(f"2단계 프롬프트 없음: {prompt_path}")

    prompt_text = prompt_path.read_text(encoding="utf-8")

    # LLM에 넘길 입력 구성 — 너무 큰 통계는 잘라서 토큰 절약
    llm_input = _build_llm_input(aggregator_result, meta)

    creds_file = vertex_config.get("credentials_file", "")
    credentials = None
    if creds_file and Path(creds_file).exists():
        credentials = service_account.Credentials.from_service_account_file(
            creds_file, scopes=_VERTEX_SCOPES,
        )

    client_kwargs = dict(
        vertexai=True,
        project=vertex_config["project_id"],
        location=vertex_config["location"],
    )
    if credentials:
        client_kwargs["credentials"] = credentials
    client = genai.Client(**client_kwargs)
    last_err = None

    for attempt in range(MAX_RETRIES):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=[
                    {"role": "user", "parts": [{"text": json.dumps(llm_input, ensure_ascii=False)}]}
                ],
                config=types.GenerateContentConfig(
                    system_instruction=prompt_text,
                    response_mime_type="application/json",
                    response_schema=AggregateAnalysis,
                    temperature=0.3,
                    max_output_tokens=16384,
                ),
            )
            return json.loads(response.text)
        except Exception as e:
            last_err = e
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_BACKOFF * (2 ** attempt))

    raise RuntimeError(f"2단계 LLM 호출 실패 (재시도 {MAX_RETRIES}회): {last_err}")


def _build_llm_input(aggregator_result: dict, meta: dict) -> dict:
    """LLM에 넘길 입력 JSON. 통계 묶음 + 대표 케이스."""
    return {
        "meta": meta,
        "stats": {
            "totals": aggregator_result["totals"],
            "verdict_distribution": aggregator_result["verdict_distribution"],
            "score_stats": aggregator_result["score_stats"],
            "relevance_stats": aggregator_result["relevance_stats"],
            "quality_stats": aggregator_result["quality_stats"],
            "language_stats": aggregator_result["language_stats"],
            "category_breakdown": aggregator_result["category_breakdown"],
            "health_score": aggregator_result["health_score"],
            "verdict": aggregator_result["verdict"],
        },
        "top_risk_cases": aggregator_result["top_risk_cases"],
        "low_confidence_zero_cases": aggregator_result["low_confidence_zero_cases"],
    }