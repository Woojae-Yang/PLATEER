import json
import math
import platform
import re
from collections import defaultdict
from pathlib import Path
from google import genai
from google.oauth2 import service_account

from core.config_loader import YAML_CONFIG, PROJECT_ROOT, now_kst, get_vertex_config
from .sheet_parser import build_single_input, extract_date_suffix, group_multi_scenarios
from .per_query_evaluator import PerQueryEvaluator
from .aggregator import aggregate
from .aggregator_llm import run_aggregate_llm
from .scoring import build_data_json
from .yamato_scoring import build_data_json_yamato
from .report_html import write_shareable_html


# v2.0 대시보드 자산 폴더 (data.json 을 fetch 해 meta/kpi/queries 를 렌더)
# 평가 프롬프트는 defaults.yaml(default_prompt_file) / clients.yaml(prompt_file)에서 관리.
DASHBOARD_DIR = PROJECT_ROOT / "dashboard"


def _resolve_data_dir() -> Path:
    """
    EC2(Linux) → nginx 서빙 경로
    로컬(Mac/Windows) → 프로젝트 루트 하위 data/
    주석 교체 없이 환경 자동 감지
    """
    defaults = YAML_CONFIG["defaults"]
    if platform.system() == "Linux":
        return Path(defaults.get("report_data_dir_ec2", "/var/www/qa-reports/data"))
    return PROJECT_ROOT / defaults.get("report_data_dir_local", "data")

DATA_DIR = _resolve_data_dir()


def _json_safe(o):
    """
    표준 JSON이 아닌 float(Infinity/-Infinity/NaN)을 None(null)으로 치환.
    파이썬 json.dump는 기본적으로 Infinity/NaN을 그대로 쓰지만, 브라우저
    JSON.parse()는 이를 거부하므로 대시보드에서 해당 회차가 깨진다.
    저장 직전에 한 번 통과시켜 어떤 필드든 비표준 값이 새어나가지 않게 한다.
    """
    if isinstance(o, float):
        return o if math.isfinite(o) else None
    if isinstance(o, dict):
        return {k: _json_safe(v) for k, v in o.items()}
    if isinstance(o, list):
        return [_json_safe(v) for v in o]
    return o


# ============================================================
# 고객사 환경 추출
# ============================================================
def extract_client_name(lang: str) -> str:
    """
    clients.yaml 프로파일 키에서 고객사명을 추출한다.
        예:
            mizuno_stg-ja        → MIZUNO_STG
            stg-ko               → STG
    """
    return lang.split("-")[0].upper()


# ============================================================
# 통계 집계
# ============================================================
def compute_stats(rows: list[dict]) -> tuple[dict, dict]:
    """
    시트 rows를 받아 카테고리별 통계와 전체 요약을 반환한다.
        Returns:
            stats   : 카테고리별 집계 dict
            summary : 전체 건수/비율 dict
    """
    # 컬럼명에서 날짜 suffix 자동 추출 (예: "2026-05-06_02:47")
    date_suffix = next(
        k.replace("product_count_", "")
        for k in rows[0]
        if k.startswith("product_count_")
    )

    cat_stats = defaultdict(lambda: {
        "total": 0, "normal": 0, "zero": 0, "error": 0, "latencies": []
    })

    for row in rows:
        cat  = row.get("カテゴリ", "unknown")
        err  = row.get(f"error_{date_suffix}")
        prod = int(row.get(f"product_count_{date_suffix}") or 0)
        lat  = float(row.get(f"latency_{date_suffix}") or 0)

        s = cat_stats[cat]
        s["total"] += 1
        s["latencies"].append(lat)

        if err:
            s["error"] += 1
        elif prod == 0:
            s["zero"] += 1
        else:
            s["normal"] += 1

    stats = {}
    for cat, s in cat_stats.items():
        lats  = s.pop("latencies")
        total = s["total"]
        stats[cat] = {
            **s,
            "normal_rate": round(s["normal"] / total * 100, 1),
            "zero_rate":   round(s["zero"]   / total * 100, 1),
            "error_rate":  round(s["error"]  / total * 100, 1),
            "avg_latency": round(sum(lats) / len(lats), 2) if lats else 0,
        }

    total_count  = len(rows)
    normal_count = sum(s["normal"] for s in stats.values())
    zero_count   = sum(s["zero"]   for s in stats.values())
    error_count  = sum(s["error"]  for s in stats.values())

    summary = {
        "total":       total_count,
        "normal":      normal_count,
        "zero":        zero_count,
        "error":       error_count,
        "normal_rate": round(normal_count / total_count * 100, 1),
        "zero_rate":   round(zero_count   / total_count * 100, 1),
        "error_rate":  round(error_count  / total_count * 100, 1),
    }
    return stats, summary


# ============================================================
# Vertex AI 호출 (레거시 단순 분석 — run_two_stage_analysis 권장)
# ============================================================
def analyze_with_gemini(prompt_file: str,
                        stats_single: dict, summary_single: dict,
                        stats_multi: dict, summary_multi: dict,
                        env_name: str, date: str) -> dict:
    """
    프롬프트 md + 통계 데이터를 Vertex AI에 전달하고 JSON 형태의 분석 결과를 반환한다.
    (레거시. 신규 파이프라인은 run_two_stage_analysis 사용 권장)
    """
    vcfg = get_vertex_config()
    if not vcfg["project_id"]:
        raise ValueError("vertex.yaml에 vertex_project_id가 없습니다.")

    # 프롬프트 파일 로드
    prompt_path = PROJECT_ROOT / "prompt" / prompt_file
    if not prompt_path.exists():
        raise FileNotFoundError(f"프롬프트 파일을 찾을 수 없습니다: {prompt_path}")

    with open(prompt_path, encoding="utf-8") as f:
        prompt_template = f.read()

    prompt = f"""
{prompt_template}

---
## 분석 대상 데이터

- 테스트 일시: {date}
- 대상 환경: {env_name}

### 싱글턴
- 총 케이스: {summary_single["total"]}건
- 정상: {summary_single["normal"]}건 ({summary_single["normal_rate"]}%)
- Zero-result: {summary_single["zero"]}건 ({summary_single["zero_rate"]}%)
- 시스템 에러: {summary_single["error"]}건 ({summary_single["error_rate"]}%)

### 싱글턴 카테고리별 통계
{json.dumps(stats_single, ensure_ascii=False, indent=2)}

### 멀티턴
- 총 케이스: {summary_multi["total"]}건
- 정상: {summary_multi["normal"]}건 ({summary_multi["normal_rate"]}%)
- Zero-result: {summary_multi["zero"]}건 ({summary_multi["zero_rate"]}%)
- 시스템 에러: {summary_multi["error"]}건 ({summary_multi["error_rate"]}%)

### 멀티턴 카테고리별 통계
{json.dumps(stats_multi, ensure_ascii=False, indent=2)}

---
## 출력 형식
    반드시 아래 JSON 형식으로만 응답하세요.
    마크다운 코드블록(```) 없이 JSON만 출력하세요.

{{
  "overall_assessment": "전체 시스템 상태 평가 (2~3문장)",
  "health_score": 0~100 사이 정수,
  "findings": [
    {{
      "severity": "critical|warning|positive",
      "title": "발견사항 제목",
      "description": "구체적인 설명"
    }}
  ],
  "action_items": [
    {{
      "priority": "P1|P2|P3",
      "item": "개선 항목",
      "reason": "근거",
    }}
  ],
  "category_comments": {{
    "카테고리명": "한 줄 코멘트"
  }}
}}
"""

    creds_file = vcfg.get("credentials_file", "")
    credentials = None
    if creds_file and Path(creds_file).exists():
        credentials = service_account.Credentials.from_service_account_file(
            creds_file, scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )

    client_kwargs = dict(
        vertexai=True,
        project=vcfg["project_id"],
        location=vcfg["location"],
    )
    if credentials:
        client_kwargs["credentials"] = credentials
    client = genai.Client(**client_kwargs)
    response = client.models.generate_content(
        model="gemini-2.5-pro",
        contents=prompt,
    )
    raw = response.text.strip()

    # 코드블록 감싸진 경우 제거
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    return json.loads(raw.strip())



# ============================================================
# html 추출
# ============================================================
def _extract_html(ai_output: dict) -> str:
    """ai_output 구조에 따라 HTML 본문을 꺼낸다."""
    # 케이스 A: 프롬프트에서 JSON mode로 받았을 때 → {"html": "..."}
    if "html" in ai_output:
        return ai_output["html"]

    # 케이스 B: Gemini raw 응답을 그대로 dict화한 경우
    if "candidates" in ai_output:
        text = ai_output["candidates"][0]["content"]["parts"][0]["text"]
        # ```html ... ``` 코드펜스가 붙어 있으면 제거
        text = text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
            if text.endswith("```"):
                text = text[:-3]
        return text.strip()

    raise ValueError(f"HTML 키를 찾을 수 없음: {list(ai_output.keys())}")


# ============================================================
# JSON 저장 & index.json 갱신
# ============================================================
def save_report(date: str, env_name: str,
                summary_single: dict, summary_multi: dict,
                stats_single: dict, stats_multi: dict,
                ai_output: dict,) -> Path:
    """
    리포트 JSON을 DATA_DIR에 저장하고 index.json을 갱신한다.
        Returns:
            json_path
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    generated_at = now_kst().isoformat(timespec="seconds")

    # ---- JSON 저장 (기존) ----
    report_data = {
        "date":    date,
        "env":  env_name,
        "generated_at": generated_at, 
        "single": {"meta": summary_single,  "category_stats": stats_single},
        "multi": {"meta":  summary_multi, "category_stats": stats_multi},
        "ai_analysis": ai_output,
    }

    filename = f"{date}_{env_name}.json"
    report_path = DATA_DIR / filename
    report_path.write_text(
        json.dumps(_json_safe(report_data), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    _update_index(date, env_name, filename, generated_at, ai_output)
    return report_path


def _update_index(date: str, env_name: str, filename: str,
                  generated_at: str, ai_output: dict) -> None:
    """대시보드 드롭다운/카드용 인덱스. 같은 (date, env, generated_at)은 최신본으로 갱신."""
    index_path = DATA_DIR / "index.json"
    index = (
        json.loads(index_path.read_text(encoding="utf-8"))
        if index_path.exists() else []
    )

    # 같은 (date, env, generated_at) 조합만 제거 (옛날 같은 날 실행은 보존)
    index = [e for e in index
             if not (e.get("date") == date 
                     and e.get("env") == env_name 
                     and e.get("generated_at") == generated_at)]

    entry = {
        "date": date,
        "env": env_name,
        "file": filename,
        "generated_at": generated_at,
        "health_score": ai_output.get("health_score"),
        "overall_assessment": ai_output.get("overall_assessment"),
    }
    index.append(entry)
    index.sort(key=lambda e: (e["date"], e.get("generated_at") or ""), reverse=True)

    index_path.write_text(
        json.dumps(index, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


# ============================================================
# 프롬프트 파일 결정
# ============================================================
def resolve_prompt_file(lang: str) -> str:
    """
    clients.yaml 프로파일에 prompt_file 지정된 경우에는 해당 파일 사용,
    없으면 defaults.yaml의 default_prompt_file 사용.
    """
    profile      = YAML_CONFIG["clients"]["profiles"].get(lang, {})
    defaults     = YAML_CONFIG["defaults"]
    prompt_file  = profile.get("prompt_file") or defaults.get("default_prompt_file")

    if not prompt_file:
        raise ValueError(
            f"prompt_file이 설정되지 않았습니다. "
            f"clients.yaml({lang}) 또는 defaults.yaml(default_prompt_file)을 확인하세요."
        )
    return prompt_file


# ============================================================
# v2.0 파이프라인: 평가 → data.json + 공유용 HTML 저장
# ============================================================
def run_eval_v2(rows_single: list[dict], rows_multi: list[dict],
                lang: str, date: str, env_name: str,
                label: str | None = None) -> dict:
    """
    싱글턴/멀티턴 시트 rows → LLM 정성 평가 → 코드 수치 계산 → data.json(dict).
    수치·판정·Phoenix 검증은 전부 scoring.py 가 계산한다.
    """
    vcfg = get_vertex_config()
    if not vcfg["project_id"]:
        raise ValueError("vertex.yaml에 vertex_project_id가 없습니다.")

    # 평가 분기 플래그 (clients.yaml profile.report_type) — 야마토면 야마토 스키마/집계 사용
    report_type = YAML_CONFIG["clients"]["profiles"].get(lang, {}).get("report_type")
    is_yamato = report_type == "yamato"
    if is_yamato:
        print("   ▶ report_type=yamato — 야마토 전용 스키마·수치·집계로 평가")

    inputs = []
    if rows_single:
        ds_s = extract_date_suffix(rows_single[0])
        inputs += [build_single_input(r, ds_s, report_type) for r in rows_single]
    scenarios = []
    if rows_multi:
        ds_m = extract_date_suffix(rows_multi[0])
        scenarios = group_multi_scenarios(rows_multi, ds_m, report_type)
        inputs += scenarios

    print(f"   1단계: 평가 입력 {len(inputs)}건 "
          f"(싱글턴 {len(rows_single)} + 멀티턴 시나리오 {len(scenarios)})")

    prompt_file = resolve_prompt_file(lang)          # 평가에 사용된 프롬프트 파일명
    prompt_path = PROJECT_ROOT / "prompt" / prompt_file
    raw_eval_dir = DATA_DIR / "raw_eval" / f"{date}_{env_name}"

    evaluator = PerQueryEvaluator(
        vertex_config=vcfg, prompt_path=prompt_path, output_dir=raw_eval_dir,
    )
    results = evaluator.evaluate_all(inputs)

    queries = [q for q in results if "error" not in q]
    errors = [q for q in results if "error" in q]
    if errors:
        print(f"   ⚠️ 평가 실패 {len(errors)}건 (data.json 에서 제외)")
    print(f"   평가 완료: queries {len(queries)}건")

    if is_yamato:
        meta_info = {
            "dataset": env_name,
            "report_title": "Yamato 검색 품질 평가 결과",
            "subtitle": f"프롬프트: {prompt_file}",
            "generated_at": now_kst().strftime("%Y.%m.%d %H:%M"),
            "label": label or "라벨링 없음",
            "prompt_file": prompt_file,
        }
        return build_data_json_yamato(queries, meta_info)

    meta_info = {
        "dataset": env_name,
        "report_title": f"{env_name}-{date}",
        "subtitle": f"프롬프트: {prompt_file}",
        "generated_at": now_kst().strftime("%Y.%m.%d %H:%M"),
        "label": label or "라벨링 없음",
        "prompt_file": prompt_file,
    }
    return build_data_json(queries, meta_info)


def _safe_token(s: str) -> str:
    """파일명에 안전한 토큰으로 변환 (영숫자 . _ - 만 허용)."""
    return re.sub(r"[^A-Za-z0-9._-]+", "_", s).strip("_") or "nolabel"


def _update_dashboard_index(data_dir: Path, env_name: str, date: str,
                            label: str, file_name: str, data: dict) -> Path:
    """
    dashboard/data/index.json 을 갱신한다 (환경/라벨·일시 셀렉터용).
    같은 file(=env+date+label)은 최신본으로 교체. 일시(generated_at) 최신순 정렬.
    """
    import json as _json
    index_path = data_dir / "index.json"
    index = []
    if index_path.exists():
        try:
            index = _json.loads(index_path.read_text(encoding="utf-8"))
        except Exception:
            index = []

    index = [e for e in index if e.get("file") != file_name]
    vd = (data.get("kpi") or {}).get("verdict_distribution", {})
    index.append({
        "env": env_name,
        "date": date,
        "label": label,
        "file": file_name,
        "generated_at": (data.get("meta") or {}).get("generated_at", ""),
        "total_queries": (data.get("meta") or {}).get("total_queries", 0),
        "verdict_distribution": vd,
    })
    index.sort(key=lambda e: (e.get("generated_at", ""), e.get("date", "")), reverse=True)
    index_path.write_text(_json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    return index_path


def save_report_v2(data: dict, env_name: str, date: str,
                   label: str | None = None) -> dict:
    """
    (1) 회차별 data.json 을 dashboard/data/{date}_{env}_{label}.json 에 저장
    (2) dashboard/data/index.json 갱신 (환경 / 라벨·일시 셀렉터)
    (3) 외부 공유용 단일 HTML 을 reports/ 에 저장 (셀렉터 없는 단일 리포트)
    Returns: {"run_json", "index_json", "shareable_html"}
    """
    import json as _json

    label_disp = label or "라벨링 없음"
    data_dir = DATA_DIR
    data_dir.mkdir(parents=True, exist_ok=True)

    # 1) 회차별 data 파일 (라벨 포함 → 같은 날 다른 라벨 공존)
    file_name = f"{date}_{env_name}_{_safe_token(label_disp)}.json"
    run_json = data_dir / file_name
    run_json.write_text(_json.dumps(_json_safe(data), ensure_ascii=False, indent=2), encoding="utf-8")

    # 2) 인덱스 갱신
    index_json = _update_dashboard_index(data_dir, env_name, date, label_disp, file_name, data)

    # 3) 외부 공유용 단일 HTML (번들: app.js 가 topbar 제거 후 단일 렌더)
    reports_dir = PROJECT_ROOT / "reports"
    html_path = reports_dir / f"{date}_{env_name}_{_safe_token(label_disp)}_report.html"
    write_shareable_html(data, html_path, DASHBOARD_DIR)

    return {
        "run_json": run_json,
        "index_json": index_json,
        "shareable_html": html_path,
    }


# ============================================================
# 1단계 + 2단계 프롬프트 적용
# ============================================================
def run_two_stage_analysis( rows_single: list[dict], rows_multi: list[dict],
                            lang: str, date: str, env_name: str) -> dict:
    """
    1단계 (쿼리/시나리오별 평가) + 2단계 (집계 + LLM 종합)
    옛 analyze_with_gemini 자리에 들어가는 새 파이프라인.

    Returns:
        save_report의 ai_output 자리에 들어갈 dict.
        구조: { health_score, verdict, kpi_cards, overall_assessment,
                findings, action_items, sections, category_breakdown,
                score_stats, relevance_stats, ... }
    """
    vcfg = get_vertex_config()
    if not vcfg["project_id"]:
        raise ValueError("vertex.yaml에 vertex_project_id가 없습니다.")

    # ── 1단계: 평가 입력 구성 ──
    date_suffix_s = extract_date_suffix(rows_single[0])
    date_suffix_m = extract_date_suffix(rows_multi[0])

    inputs_single = [build_single_input(r, date_suffix_s) for r in rows_single]
    scenarios = group_multi_scenarios(rows_multi, date_suffix_m)
    inputs = inputs_single + scenarios

    # ── 1단계: per-query 평가 (병렬) ──
    print(f"   1단계: 쿼리별 평가 {len(inputs)}건 (싱글턴 {len(inputs_single)} + 멀티턴 시나리오 {len(scenarios)})")
    per_query_prompt = PROJECT_ROOT / "prompt" / resolve_prompt_file(lang)
    raw_eval_dir = DATA_DIR / "raw_eval" / f"{date}_{env_name}"

    evaluator = PerQueryEvaluator(
        vertex_config=vcfg,
        prompt_path=per_query_prompt,
        output_dir=raw_eval_dir,
    )
    raw_evals = evaluator.evaluate_all(inputs)
    print(f"   1단계 완료: {len(raw_evals)}건")

    # ── 2단계: 결정론 집계 ──
    print("   2단계: 결정론 집계...")
    agg = aggregate(raw_evals)
    print(f"   health_score: {agg['health_score']}, verdict: {agg['verdict']}")

    # ── 3단계: LLM 정성 종합 ──
    print("   3단계: LLM 정성 종합 호출...")
    aggregate_prompt = PROJECT_ROOT / "prompt" / YAML_CONFIG["defaults"].get(
        "aggregate_prompt_file", "prompt_aggregate_v1.md"
    )
    qual = run_aggregate_llm(
        vertex_config=vcfg,
        prompt_path=aggregate_prompt,
        aggregator_result=agg,
        meta={"date": date, "env": env_name},
    )
    print("   2단계 완료")

    # ── 최종 합본: 코드 결과 + LLM 결과 ──
    return {
        # 코드(aggregator)가 책임지는 정량
        "health_score": agg["health_score"],
        "verdict": agg["verdict"],
        "kpi_cards": agg["kpi_cards"],
        "verdict_distribution": agg["verdict_distribution"],
        "score_stats": agg["score_stats"],
        "relevance_stats": agg["relevance_stats"],
        "quality_stats": agg["quality_stats"],
        "language_stats": agg["language_stats"],
        "category_breakdown": agg["category_breakdown"],
        "top_risk_cases": agg["top_risk_cases"],
        "low_confidence_zero_cases": agg["low_confidence_zero_cases"],
        "totals": agg["totals"],

        # LLM이 책임지는 정성
        "overall_assessment": qual["overall_assessment"],
        "findings": qual["findings"],
        "action_items": qual["action_items"],
        "sections": qual["sections"],

        # 케이스 상세 디버깅용 raw 데이터
        "cases": raw_evals,
    }
