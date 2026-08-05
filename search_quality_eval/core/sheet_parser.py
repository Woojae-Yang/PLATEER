"""Google Sheets row를 1단계 평가용 입력 JSON으로 변환."""
import json
import re
from collections import defaultdict
from typing import Any


PRODUCT_EVAL_TOP_N = 30  # v2.0: 상위 30개 정밀 평가 (31위 이후는 unevaluated_products)

# Phoenix 로그 컬럼 (날짜 suffix 제외한 베이스 이름)
PHOENIX_FIELDS = (
    "trace_id", "tool_name", "tools_used", "total_count",
    "tool_input", "tool_output", "llm_response",
    "tool_latency_ms", "final_llm_latency_ms", "error",
)


def extract_phoenix(row: dict, date_suffix: str) -> dict:
    """
    phoenix_* 컬럼을 eval 입력용 dict 로 추출한다.
    컬럼명 형태: phoenix_<field>_<date_suffix>  (예: phoenix_tool_name_2026-06-01_13:11)
    값이 비어 있으면 키는 None.
    """
    out = {}
    for f in PHOENIX_FIELDS:
        v = row.get(f"phoenix_{f}_{date_suffix}")
        out[f] = None if (v is None or v == "" or v == "None") else v
    return out


def parse_all_products(row: dict, date_suffix: str) -> list[dict]:
    """response_text_1~5 전체를 이어붙여 가능한 모든 상품을 파싱(최대 200개)."""
    return parse_products(row, date_suffix, max_n=200, num_parts=5)


def parse_products(row: dict, date_suffix: str, max_n: int = 30,
                   num_parts: int = 3) -> list[dict]:
    """
    response_text_1/2/3을 이어붙여 상품 리스트로 파싱. 최대 max_n개 반환.

    Sheets 셀 50K자 제한 때문에 상품 JSON이 1/2/3로 분할 저장됨.
    이어붙이고 raw_decode로 한 객체씩 추출 (마지막에 잘려있어도 앞부분은 보존).
    """
    parts = []
    for i in range(1, num_parts + 1):
        v = row.get(f"response_text_{i}_{date_suffix}")
        if v and v != "None":
            parts.append(str(v))
    if not parts:
        return []

    raw = "".join(parts).strip()
    if raw.startswith("["):
        raw = raw[1:]

    decoder = json.JSONDecoder()
    products, idx = [], 0
    s = raw.lstrip()
    while s and len(products) < max_n:
        try:
            obj, end = decoder.raw_decode(s)
            obj["rank"] = len(products) + 1
            products.append(obj)
            s = s[end:].lstrip().lstrip(",").lstrip()
            if s.startswith("]"):
                break
        except json.JSONDecodeError:
            break
    return products


def extract_date_suffix(row: dict) -> str:
    """첫 product_count_* 컬럼에서 날짜 접미사 추출 (compute_stats와 동일 패턴)."""
    return next(
        k.replace("product_count_", "")
        for k in row
        if k.startswith("product_count_")
    )


def build_single_input(row: dict, date_suffix: str,
                       report_type: str | None = None) -> dict:
    """싱글턴 row → 1단계 평가 입력 JSON."""
    all_products = parse_all_products(row, date_suffix)
    products_top30 = all_products[:PRODUCT_EVAL_TOP_N]
    unevaluated = all_products[PRODUCT_EVAL_TOP_N:]
    case_id = (row.get("シナリオID") or row.get("scenario_id")
               or row.get("質問ID") or row.get("질문ID"))
    return {
        "track_hint": "single",
        "case_id": case_id,
        "query_id": case_id,
        "scenario_id": None,
        "turn_number": None,
        "previous_turn_queries": [],
        "report_type": report_type,
        # 야마토 기능분류: 싱글턴 類型 / 멀티턴 検索基準 (원문 유지, 한국어 매핑은 yamato_scoring에서)
        "function_category": row.get("類型") or row.get("検索基準") or None,
        "category": row.get("カテゴリ") or row.get("카테고리") or row.get("大分類") or row.get("category") or "unknown",
        "persona": row.get("ペルソナ") or row.get("페르소나ID"),
        "query": row.get("検索クエリ") or row.get("검색쿼리"),
        "session_id": row.get(f"session_id_{date_suffix}"),
        "chat_request_id": row.get(f"chat_request_id_{date_suffix}"),
        "answer_text": row.get(f"answer_text_{date_suffix}") or "",
        "keywords": _safe_json(row.get(f"keywords_{date_suffix}"), default=[]),
        "latency": _safe_float(row.get(f"latency_{date_suffix}")),
        "product_count": _safe_int(row.get(f"product_count_{date_suffix}")),
        "error": row.get(f"error_{date_suffix}"),
        "products": products_top30,
        "unevaluated_products": unevaluated,
        "phoenix": extract_phoenix(row, date_suffix),
    }


def group_multi_scenarios(rows: list[dict], date_suffix: str,
                          report_type: str | None = None) -> list[dict]:
    """
    멀티턴 rows를 시나리오 단위(같은 シナリオID)로 그룹핑.
    각 시나리오 → 1단계 평가 입력 JSON.
    """
    by_scenario = defaultdict(list)
    for row in rows:
        by_scenario[row.get("シナリオID") or row.get("시나리오ID") 
                    or row.get("scenario_id")].append(row)

    scenarios = []
    for case_id, scenario_rows in by_scenario.items():
        # ターン 번호 순 정렬 (없는 행은 0으로 → 안정정렬로 원래 순서 유지)
        scenario_rows.sort(key=lambda r: _parse_turn_value(_turn_raw(r)) or 0)

        first = scenario_rows[0]
        turns = []
        prior_queries: list[str] = []
        for seq, r in enumerate(scenario_rows, start=1):
            # 턴 컬럼(ターン/턴/Turn)의 값은 'T1' / '1' / 'ターン 1' 등 다양 →
            # 숫자만 추출해 파싱. 못 읽으면 정렬된 행 순번(1-based)으로 폴백.
            turn_no = _parse_turn_value(_turn_raw(r))
            if not turn_no or turn_no <= 0:
                turn_no = seq
            query = r.get("検索クエリ") or r.get("검색쿼리") or r.get("query") or r.get("질문")
            all_products = parse_all_products(r, date_suffix)
            turns.append({
                "turn_number": turn_no,
                "query": query,
                "function_category": r.get("類型") or r.get("検索基準") or None,
                "previous_turn_queries": list(prior_queries),
                "chat_request_id": r.get(f"chat_request_id_{date_suffix}"),
                "session_id": first.get(f"session_id_{date_suffix}"),
                "answer_text": r.get(f"answer_text_{date_suffix}") or "",
                "keywords": _safe_json(r.get(f"keywords_{date_suffix}"), default=[]),
                "latency": _safe_float(r.get(f"latency_{date_suffix}")),
                "product_count": _safe_int(r.get(f"product_count_{date_suffix}")),
                "error": r.get(f"error_{date_suffix}"),
                "products": all_products[:PRODUCT_EVAL_TOP_N],
                "unevaluated_products": all_products[PRODUCT_EVAL_TOP_N:],
                "phoenix": extract_phoenix(r, date_suffix),
            })
            if query:
                prior_queries.append(query)

        scenarios.append({
            "track_hint": "multi",
            "case_id": case_id,
            "report_type": report_type,
            "category": first.get("カテゴリ") or first.get("카테고리") or row.get("大分類") or first.get("category") or "unknown",
            "persona": first.get("ペルソナ") or first.get("페르소나ID") or first.get("persona"),
            "session_id": first.get(f"session_id_{date_suffix}"),
            "turns": turns,
        })
    return scenarios


def scenario_turn_inputs(scenario: dict) -> list[dict]:
    """
    group_multi_scenarios 가 만든 시나리오 객체를 scoring.compute_query 가
    바로 먹을 수 있는 '턴 단위' eval 입력 리스트로 펼친다.
    각 턴에 case_id(예: MT003-T2), scenario_id, phoenix, products 등을 주입.
    """
    out = []
    scen_id = scenario.get("case_id")
    for t in scenario.get("turns", []):
        tn = t.get("turn_number")
        out.append({
            "track_hint": "multi",
            "case_id": f"{scen_id}-T{tn}" if tn is not None else scen_id,
            "query_id": scen_id,
            "scenario_id": scen_id,
            "turn_number": tn,
            "report_type": scenario.get("report_type"),
            "function_category": t.get("function_category"),
            "previous_turn_queries": t.get("previous_turn_queries") or [],
            "category": scenario.get("category"),
            "persona": scenario.get("persona"),
            "query": t.get("query"),
            "session_id": t.get("session_id") or scenario.get("session_id"),
            "chat_request_id": t.get("chat_request_id"),
            "answer_text": t.get("answer_text") or "",
            "keywords": t.get("keywords") or [],
            "latency": t.get("latency"),
            "product_count": t.get("product_count") or 0,
            "error": t.get("error"),
            "products": t.get("products") or [],
            "unevaluated_products": t.get("unevaluated_products") or [],
            "phoenix": t.get("phoenix") or {},
            "phoenix_skipped": t.get("phoenix_skipped", False),
        })
    return out


# --- 작은 유틸 ---
def _safe_int(v: Any) -> int:
    try: return int(float(v))
    except (TypeError, ValueError): return 0


def _turn_raw(row: dict) -> Any:
    """멀티턴 시트의 턴 컬럼 값을 컬럼명 변형(ターン/턴/Turn/turn)에 무관하게 가져온다."""
    return row.get("ターン") or row.get("턴") or row.get("Turn") or row.get("turn")


def _parse_turn_value(raw: Any) -> int | None:
    """'T1' / '1' / 'ターン 1' / 'Turn 2' 등에서 숫자만 추출. 없으면 None."""
    if raw is None:
        return None
    m = re.search(r"\d+", str(raw))
    return int(m.group()) if m else None

def _safe_float(v: Any) -> float | None:
    try: return float(v)
    except (TypeError, ValueError): return None

def _safe_json(v: Any, default=None):
    if not v or v == "None": return default
    try: return json.loads(v)
    except (TypeError, json.JSONDecodeError): return default