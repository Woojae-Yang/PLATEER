"""
core/scoring.py — v2.0 코드 단 수치 계산 엔진.

LLM은 정성 판단(라벨 + 이유)만 출력한다. 이 모듈이 다음을 전부 코드로 계산한다.

  · A/B/E_score 변환, C_avg_relevance, D_noise_pct, top_3_acc_avg
  · Rel / Acc / Comp / Ctx_final / Score  (싱글턴/멀티턴 공식)
  · verdict, llm_initial_judgement, phoenix_judgement, final_judgement,
    judgement_changed
  · phoenix_checks(기계적 항목) + phoenix_evidence(전부 컬럼에서)
  · root_cause(원인명 매핑표), is_outlier, human_review,
    is_judge_unstable, test_priority
  · answer_length_check(char_count + 판정), zero_result_type
  · relevance_label / comment_skipped 도출, 코멘트 생략 정책 적용
  · build_data_json(meta + kpi + queries)

모든 임계값과 공식은 이 파일 상단 상수에 모아두어 프롬프트가 아니라
코드에서 단일 관리한다.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from typing import Any, Optional


# ═════════════════════════════════════════════════════════════
# 임계값 / 공식 상수  (단일 관리 지점)
# ═════════════════════════════════════════════════════════════
# A/B/E 라벨 → 점수
PASS_MAP = {"PASS": 1.00, "PARTIAL": 0.70, "FAIL": 0.30}
QUALITY_MAP = {"GOOD": 1.00, "ACCEPTABLE": 0.70, "POOR": 0.30}

# keyword_relevance_check 라벨 → 완성도 가중 인자
KEYWORD_FACTOR = {"일치": 1.00, "부분 일치": 0.70, "불일치": 0.40, "해당없음": 0.70}
# answer_length 판정 → 완성도 가중 인자
LENGTH_FACTOR = {"충분": 1.00, "보통": 0.70, "부족": 0.40}

# C (관련성) 라벨 임계값 — C_avg_relevance 기준
C_HIGH = 0.70
C_LOW = 0.40
# D (노이즈) 라벨 임계값 — noise_pct 기준
D_LOW = 0.10
D_HIGH = 0.30
# 노이즈로 집계하는 상품 기준 (부적합 = relevance_score ≤ 1)
NOISE_SCORE_MAX = 1
# 적합 기준 (KPI 적합 비율)
RELEVANT_SCORE_MIN = 3

# Top-K
TOP_K = 3
TOP_K_BAD_THRESHOLD = 0.50

# 최종 판정 임계값
FAIL_SCORE = 0.65
FAIL_ACC = 0.50
FAIL_COMP = 0.50
HARD_PASS_SCORE = 0.85
HARD_PASS_ACC = 0.85
HARD_PASS_COMP = 0.85

# is_outlier: Acc 구간
OUTLIER_ACC_LO = 0.50
OUTLIER_ACC_HI = 0.84

# 멀티턴 컨텍스트 유지 라벨 → 점수
CTX_MAP = {"ok": 1.00, "partial": 0.60, "broken": 0.30}

# Phoenix 지연 임계값(ms) — final LLM latency 가 이보다 크면 응답 지연 원인
LATENCY_WARN_MS = 8000

# answer_length 판정 임계값 (글자 수, 공백 포함)
LENGTH_THRESHOLDS = {
    #            충분 >        부족 ≤
    "ko": {"enough": 150, "short": 50},
    "ja": {"enough": 100, "short": 35},
    "en": {"enough": 200, "short": 80},
}

# 원인명 매핑표 (내부 분류 → 출력 문자열)
ROOT_CAUSE_NAMES = {
    "Mapping Issue": "로그 연결 문제",
    "Tool Selection Issue": "검색 도구 선택 문제",
    "Search Parameter Issue": "검색 조건 문제",
    "Zero Result Issue": "검색 결과 0건",
    "Retrieval Issue": "검색 결과 부적합",
    "Response Grounding Issue": "답변 근거 불일치",
    "Response Generation Issue": "답변 생성 문제",
    "Context Retention Issue": "이전 대화 조건 누락",
    "Performance Issue": "응답 지연/타임아웃",
    "Query Understanding Issue": "검색 조건 문제",
    "없음": "없음",
}


# ═════════════════════════════════════════════════════════════
# 소형 유틸
# ═════════════════════════════════════════════════════════════
def _round(v: Optional[float], n: int = 2) -> Optional[float]:
    return None if v is None else round(float(v), n)


def _safe_int(v: Any) -> Optional[int]:
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return None


def round_trip_ms(eval_input: dict) -> Optional[int]:
    """
    e2e 라운드트립 latency(초, chat_api 측정값)를 ms 정수로 변환.
    eval_input["latency"] 는 sheet 의 latency_{timestamp} 컬럼(초). 없으면 None.
    """
    v = eval_input.get("latency")
    if v in (None, ""):
        return None
    try:
        return int(round(float(v) * 1000))
    except (TypeError, ValueError):
        return None


def _safe_json(v: Any, default=None):
    if v in (None, "", "None"):
        return default
    if isinstance(v, (list, dict)):
        return v
    try:
        return json.loads(v)
    except (TypeError, ValueError, json.JSONDecodeError):
        return default


def _stock_status(raw: dict) -> Optional[str]:
    av = (raw.get("availability") or raw.get("stock_status") or "")
    av = str(av).lower()
    if "out" in av or "soldout" in av or "품절" in av:
        return "out_of_stock"
    if "instock" in av or "in_stock" in av or av == "true":
        return "in_stock"
    return None


def normalize_product_meta(raw: dict) -> dict:
    """원본 파싱 상품(response_text JSON) → 최종 상품 메타 필드."""
    return {
        "title": raw.get("title") or raw.get("product_name"),
        "brand": raw.get("brand_name") or raw.get("brand"),
        "image_url": raw.get("cdn_main_url") or raw.get("image_url") or raw.get("main_image"),
        "selling_price": raw.get("selling_price") if raw.get("selling_price") is not None
                         else raw.get("original_price"),
        "currency": raw.get("currency"),
        "category_path": raw.get("category_path") or raw.get("category"),
        "stock_status": _stock_status(raw),
    }


def relevance_label(score: int) -> str:
    if score >= RELEVANT_SCORE_MIN:
        return "적합"
    if score == 2:
        return "부분 적합"
    return "부적합"


# ═════════════════════════════════════════════════════════════
# 보조 지표
# ═════════════════════════════════════════════════════════════
def answer_length_check(answer_text: Optional[str], language: str) -> dict:
    text = answer_text or ""
    char_count = len(text)
    th = LENGTH_THRESHOLDS.get(language, LENGTH_THRESHOLDS["ko"])
    if char_count > th["enough"]:
        result = "충분"
    elif char_count <= th["short"]:
        result = "부족"
    else:
        result = "보통"
    lang = language if language in ("ko", "ja", "en") else "ko"
    return {"language": lang, "char_count": char_count, "result": result}


def detect_language(text: Optional[str]) -> str:
    """답변/쿼리 텍스트로 주 언어 추정 (LLM 미지정 시 폴백)."""
    if not text:
        return "ko"
    has_hangul = bool(re.search(r"[가-힣]", text))
    has_kana = bool(re.search(r"[ぁ-んァ-ヶ]", text))
    if has_hangul and not has_kana:
        return "ko"
    if has_kana and not has_hangul:
        return "ja"
    if has_hangul and has_kana:
        return "mixed"
    if re.search(r"[A-Za-z]", text):
        return "en"
    return "ko"


# ═════════════════════════════════════════════════════════════
# 상품 기반 지표 (C / D / Top-K)
# ═════════════════════════════════════════════════════════════
def product_metrics(product_scores: list[dict]) -> dict:
    """평가된 상품 점수로부터 C_avg / noise / top-K 등을 계산."""
    n = len(product_scores)
    if n == 0:
        return {
            "c_avg": 0.0, "c_label": "LOW",
            "noise_pct": 0.0, "d_label": "LOW", "low_items": [],
            "top_3_acc_avg": 0.0, "is_top_k_bad": True,
        }

    scores = [int(p.get("relevance_score", 0)) for p in product_scores]
    c_avg = sum(scores) / n / 4.0

    noise_n = sum(1 for s in scores if s <= NOISE_SCORE_MAX)
    noise_pct = noise_n / n

    low_items = []
    for p in product_scores:
        s = int(p.get("relevance_score", 0))
        if s <= NOISE_SCORE_MAX:
            cond = p.get("reason") or (", ".join(p.get("violated_conditions") or []))
            title = (p.get("title") or "")[:40]
            low_items.append(f"{title} (score {s}{', ' + cond if cond else ''})")

    topk = scores[:TOP_K]
    top_3_acc_avg = sum(1 for s in topk if s >= RELEVANT_SCORE_MIN) / len(topk)

    return {
        "c_avg": round(c_avg, 2),
        "c_label": "HIGH" if c_avg >= C_HIGH else ("LOW" if c_avg < C_LOW else "MEDIUM"),
        "noise_pct": round(noise_pct, 2),
        "d_label": "LOW" if noise_pct < D_LOW else ("HIGH" if noise_pct > D_HIGH else "MEDIUM"),
        "low_items": low_items,
        "top_3_acc_avg": round(top_3_acc_avg, 2),
        "is_top_k_bad": top_3_acc_avg < TOP_K_BAD_THRESHOLD,
    }


# ═════════════════════════════════════════════════════════════
# 점수 공식
# ═════════════════════════════════════════════════════════════
def compute_scores(
    a_label: str, b_label: str, e_label: str,
    c_avg: float, noise_pct: float,
    keyword_result: str, length_result: str, top_3_acc_avg: float,
    product_count: int,
    is_multiturn: bool, turn_number: Optional[int],
    ctx_label: Optional[str],
) -> dict:
    a = PASS_MAP.get(a_label, 0.30)
    b = QUALITY_MAP.get(b_label, 0.30)
    e = QUALITY_MAP.get(e_label, 0.30)

    rel = a * 0.5 + c_avg * 0.3 + (1 - noise_pct) * 0.2
    acc = b

    if product_count == 0:
        comp = 0.0
    else:
        kw = KEYWORD_FACTOR.get(keyword_result, 0.70)
        ln = LENGTH_FACTOR.get(length_result, 0.70)
        comp = 0.5 * kw + 0.3 * ln + 0.2 * top_3_acc_avg

    # Ctx_final: 멀티턴 Turn 2+ 에서만
    ctx_final = None
    if is_multiturn and (turn_number or 1) >= 2:
        ctx_final = CTX_MAP.get(ctx_label or "partial", 0.60)

    if ctx_final is not None:
        score = rel * 0.35 + acc * 0.30 + ctx_final * 0.20 + comp * 0.15
        formula = "멀티턴: Rel×0.35 + Acc×0.30 + Ctx_final×0.20 + Comp×0.15"
    else:
        score = rel * 0.40 + acc * 0.35 + comp * 0.25
        formula = "싱글턴: Rel×0.40 + Acc×0.35 + Comp×0.25"

    return {
        "A_score": round(a, 2), "B_score": round(b, 2), "E_score": round(e, 2),
        "Rel": round(rel, 2), "Acc": round(acc, 2), "Comp": round(comp, 2),
        "Ctx_final": _round(ctx_final), "Score": round(score, 2),
        "score_formula": formula,
    }


# ═════════════════════════════════════════════════════════════
# 판정
# ═════════════════════════════════════════════════════════════
def score_verdict(score: float, acc: float, comp: float, product_count: int) -> str:
    """Score 기반 1차 verdict (Hard Pass / Conditional Pass / Fail)."""
    if product_count == 0 or score < FAIL_SCORE or acc < FAIL_ACC or comp < FAIL_COMP:
        return "Fail"
    if score >= HARD_PASS_SCORE and acc >= HARD_PASS_ACC and comp >= HARD_PASS_COMP:
        return "Hard Pass"
    return "Conditional Pass"


def llm_initial_judgement(verdict: str) -> str:
    return {"Hard Pass": "Pass", "Conditional Pass": "Warning", "Fail": "Fail"}[verdict]


def _level(judgement: str) -> str:
    """final/initial 판정을 Pass/Warning/Fail 3단계로 정규화 (judgement_changed 비교용)."""
    j = judgement.lower()
    if "fail" in j or "high risk" in j:
        return "Fail"
    if "warning" in j:
        return "Warning"
    return "Pass"


# ═════════════════════════════════════════════════════════════
# Phoenix
# ═════════════════════════════════════════════════════════════
def phoenix_evidence(ph: dict, answer_text: Optional[str]) -> dict:
    """phoenix_* 컬럼값으로 phoenix_evidence 객체 구성 (전부 코드)."""
    tool_input = _safe_json(ph.get("tool_input"), default={})
    tool_output = _safe_json(ph.get("tool_output"), default={})
    total_count = _safe_int(ph.get("total_count"))

    # tool_input 요약: 주요 키만
    if isinstance(tool_input, dict) and tool_input:
        keys = ("category_l1", "category_l2", "category", "query", "color",
                "material", "features", "lang")
        parts = [f"{k}={tool_input[k]}" for k in keys if tool_input.get(k)]
        input_summary = ", ".join(parts) or json.dumps(tool_input, ensure_ascii=False)[:160]
    else:
        input_summary = (str(ph.get("tool_input") or "") or None)
        if input_summary:
            input_summary = input_summary[:160]

    returned = None
    if isinstance(tool_output, dict):
        returned = tool_output.get("returned_count") or tool_output.get("shown_count")
    output_summary = None
    if total_count is not None:
        output_summary = f"{total_count}건 반환"
        if returned is not None:
            output_summary += f" (노출 {returned}건)"

    tool_lat = _safe_int(ph.get("tool_latency_ms"))
    final_lat = _safe_int(ph.get("final_llm_latency_ms"))
    latency_summary = None
    if tool_lat is not None or final_lat is not None:
        latency_summary = (
            f"tool {tool_lat if tool_lat is not None else '?'}ms / "
            f"final LLM {final_lat if final_lat is not None else '?'}ms"
        )

    llm_resp = ph.get("llm_response") or answer_text or ""
    llm_resp_summary = (str(llm_resp)[:80] + "...") if llm_resp else None

    return {
        "tool_name": ph.get("tool_name") or None,
        "tool_input_summary": input_summary,
        "total_count": total_count,
        "tool_output_summary": output_summary,
        "llm_response_summary": llm_resp_summary,
        "latency_summary": latency_summary,
    }


def phoenix_checks(
    ph: dict, eval_input: dict, product_count: int,
    c_label: str, keyword_result: str,
    llm_params_ok: Optional[str], llm_grounding_ok: Optional[str],
    is_multiturn: bool, turn_number: Optional[int], ctx_label: Optional[str],
) -> tuple[dict, bool]:
    """
    phoenix_checks 7개 항목 산정.
    기계적 항목(mapping/tool_call/count/retrieval/context)은 코드가,
    판단 항목(params/grounding)은 LLM 값을 사용하되 폴백 추론.
    Returns: (checks dict, log_connected)
    """
    trace_id = ph.get("trace_id")
    tools_used = _safe_json(ph.get("tools_used"), default=[]) or []
    tool_name = ph.get("tool_name")

    log_connected = bool(trace_id or tool_name or tools_used)

    if not log_connected:
        return ({
            "mapping_ok": "FAIL", "tool_call_ok": None, "params_ok": None,
            "count_ok": None, "retrieval_ok": None, "grounding_ok": None,
            "context_ok": None,
        }, False)

    # mapping: trace 가 있고 세션이 매칭되면 OK
    mapping_ok = "OK" if trace_id else "PARTIAL"

    # tool_call: 검색 도구 호출 여부
    has_search = any("search" in str(t).lower() for t in tools_used) or \
        ("search" in str(tool_name or "").lower())
    tool_call_ok = "OK" if (tool_name or tools_used) else "FAIL"
    if not has_search and product_count > 0:
        tool_call_ok = "PARTIAL"

    # count: 수치 정합성(응답 상품 수 일치)은 판정 대상이 아니다.
    # Phoenix는 정성 판단 보조 + 개발자 트리아지 용도이므로 count_ok는 평가하지 않고,
    # total_count 자체는 phoenix_evidence에서 참고값으로만 노출한다.
    count_ok = None

    # retrieval: 검색 결과 적합도 = C 라벨에서 도출
    retrieval_ok = {"HIGH": "OK", "MEDIUM": "PARTIAL", "LOW": "FAIL"}.get(c_label)

    # params / grounding: LLM 판단 우선, 없으면 폴백
    params_ok = llm_params_ok
    grounding_ok = llm_grounding_ok or \
        {"일치": "OK", "부분 일치": "PARTIAL", "불일치": "FAIL", "해당없음": None}.get(keyword_result)

    # context: 멀티턴 Turn 2+ 에서만
    context_ok = None
    if is_multiturn and (turn_number or 1) >= 2:
        context_ok = {"ok": "OK", "partial": "PARTIAL", "broken": "FAIL"}.get(ctx_label or "partial")

    return ({
        "mapping_ok": mapping_ok, "tool_call_ok": tool_call_ok, "params_ok": params_ok,
        "count_ok": count_ok, "retrieval_ok": retrieval_ok, "grounding_ok": grounding_ok,
        "context_ok": context_ok,
    }, True)


def phoenix_judgement(checks: dict, log_connected: bool, product_count: int) -> str:
    if product_count == 0:
        return "zero_result"
    if not log_connected:
        return "Phoenix 로그 연결 안 됨"
    vals = [v for v in checks.values() if v is not None]
    fails = sum(1 for v in vals if v == "FAIL")
    partials = sum(1 for v in vals if v == "PARTIAL")
    if fails >= 2:
        return "Fail"
    if fails == 1 or partials >= 2:
        return "Warning"
    return "Pass"


def build_root_cause(
    checks: dict, log_connected: bool, product_count: int,
    b_label: str, final_lat_ms: Optional[int],
) -> list[str]:
    causes: list[str] = []

    def add(internal: str):
        name = ROOT_CAUSE_NAMES[internal]
        if name not in causes:
            causes.append(name)

    if product_count == 0:
        add("Zero Result Issue")
    if not log_connected:
        add("Mapping Issue")
    if checks.get("tool_call_ok") == "FAIL":
        add("Tool Selection Issue")
    if checks.get("params_ok") == "FAIL":
        add("Search Parameter Issue")
    if checks.get("retrieval_ok") == "FAIL":
        add("Retrieval Issue")
    if checks.get("grounding_ok") == "FAIL":
        add("Response Grounding Issue")
    if checks.get("context_ok") == "FAIL":
        add("Context Retention Issue")
    if b_label == "POOR" or b_label == "ACCEPTABLE":
        add("Response Generation Issue")
    if final_lat_ms is not None and final_lat_ms > LATENCY_WARN_MS:
        add("Performance Issue")

    return causes or ["없음"]


# ═════════════════════════════════════════════════════════════
# 종합: final_judgement / outlier / priority / instability
# ═════════════════════════════════════════════════════════════
def final_judgement(
    verdict: str, initial: str, ph_judgement: str,
    checks: dict, product_count: int,
) -> str:
    if product_count == 0:
        return "zero_result"
    if initial == "Pass":
        return "Hard Pass"
    # Phoenix 로그 미연결 → LLM 1차 유지
    if ph_judgement == "Phoenix 로그 연결 안 됨":
        return "Warning" if initial == "Warning" else "Fail"

    fails = sum(1 for v in checks.values() if v == "FAIL")
    has_issue = any(v in ("FAIL", "PARTIAL") for v in checks.values() if v is not None)

    if initial == "Fail":
        return "High Risk" if fails >= 3 else "Fail"
    # initial == Warning
    return "Warning" if has_issue else "Conditional Pass"


def is_outlier(acc: float, top_3_acc_avg: float) -> bool:
    return (OUTLIER_ACC_LO <= acc <= OUTLIER_ACC_HI) or (top_3_acc_avg < TOP_K_BAD_THRESHOLD)


def judge_instability(
    acc: float, comp: float, score: float, c_avg: float,
    noise_pct: float, top_3_acc_avg: float, is_top_k_bad: bool,
) -> tuple[bool, list[str]]:
    """7개 조건 중 2개 이상이면 불안정으로 판정."""
    reasons = []
    if abs(acc - comp) >= 0.40:
        reasons.append("Acc와 Comp 격차 큼")
    if 0.60 <= score <= 0.70:
        reasons.append("Score가 판정 경계(0.60~0.70)에 위치")
    if is_top_k_bad and c_avg >= C_HIGH:
        reasons.append("Top-K 불량이나 전체 관련성 높음")
    if noise_pct > D_HIGH and c_avg >= C_HIGH:
        reasons.append("노이즈 높으나 평균 관련성 높음")
    if 0.45 <= c_avg <= 0.55:
        reasons.append("C_avg가 경계 구간")
    if top_3_acc_avg in (0.33, 0.67) and not is_top_k_bad:
        reasons.append("Top-K 부분 적합 혼재")
    if acc <= 0.30 and score >= 0.65:
        reasons.append("답변 품질 낮으나 종합 점수 통과")
    return (len(reasons) >= 2, reasons)


def test_priority(final: str, acc: float, outlier: bool) -> tuple[Any, Optional[str]]:
    if final in ("Fail", "High Risk"):
        if outlier:
            return 1, "is_outlier=True. Fail 케이스 — 휴먼 전수 검토."
        return 2, "Fail 케이스 — 휴먼 검토 권장."
    if final in ("Warning", "Conditional Pass"):
        if OUTLIER_ACC_LO <= acc <= OUTLIER_ACC_HI:
            return 3, f"Acc {acc:.2f} (0.50~0.84 구간). 텍스트 답변 정확성 집중 재검토."
        return 4, "Warning 케이스 — 샘플 검토."
    return "해당없음", None


# ═════════════════════════════════════════════════════════════
# zero_result 분류
# ═════════════════════════════════════════════════════════════
_ASK_BACK_PAT = re.compile(
    r"(어떤|원하시는|알려주세요|말씀해|있으신가요|있나요|찾으시|용도|조건|"
    r"どのような|ご希望|教えてください|お聞かせ|もう少し|具体的|相談)"
)
_NO_RESULT_PAT = re.compile(
    r"(찾을 수 없|찾지 못|검색 결과가 없|상품이 없|재고가 없|품절|일치하는 상품이 없|"
    r"見つかりません|該当する商品|商品がありません|在庫がありません|検索結果がありません)"
)


def classify_zero_result(tools_used: list, answer_text: Optional[str]) -> Optional[str]:
    """product_count == 0 케이스 분류. tools_used 우선, answer_text 폴백."""
    if tools_used:
        has_search = any("search" in str(t).lower() for t in tools_used)
        return "검색 결과 없음" if has_search else "역질문/상품 미반환"
    text = answer_text or ""
    if _NO_RESULT_PAT.search(text):
        return "검색 결과 없음"
    if _ASK_BACK_PAT.search(text):
        return "역질문/상품 미반환"
    if not text.strip():
        return "검색 결과 없음"
    return "역질문/상품 미반환"


# ═════════════════════════════════════════════════════════════
# 메인: 한 쿼리/턴의 최종 data.json 객체 조립
# ═════════════════════════════════════════════════════════════
def compute_query(eval_input: dict, llm: dict) -> dict:
    """
    eval_input : sheet_parser 가 만든 입력(쿼리/상품/phoenix 컬럼 포함)
    llm        : LLMQueryEval(.model_dump()) — 정성 판단
    Returns    : data.json queries[] 한 객체
    """
    is_multi = eval_input.get("track_hint") == "multi" or eval_input.get("turn_number")
    turn_number = eval_input.get("turn_number")
    product_count = int(eval_input.get("product_count") or 0)
    answer_text = eval_input.get("answer_text") or ""
    ph = eval_input.get("phoenix") or {}

    language = llm.get("language") or detect_language(answer_text or eval_input.get("query"))
    seg = llm.get("segment_tags") or {}
    krc_in = llm.get("keyword_relevance_check") or {}
    llm_eval = llm.get("evaluation") or {}
    llm_ph = llm.get("phoenix_judgments") or {}
    llm_summary = llm.get("summary") or {}

    ctx_label = llm_eval.get("context_retention")
    drift_detected = llm_eval.get("drift_detected")

    # ── 상품 점수 후처리 (label + comment_skipped 도출, 코멘트 정책) ──
    # 메타데이터(제목·브랜드·이미지·가격·통화)는 원본 파싱 상품을 신뢰하고
    # rank로 매칭, LLM 출력은 폴백으로만 사용.
    raw_by_rank = {}
    for rp in (eval_input.get("products") or []):
        if rp.get("rank") is not None:
            raw_by_rank[rp["rank"]] = rp

    product_scores = []
    for p in (llm.get("product_scores") or [])[:30]:
        s = int(p.get("relevance_score", 0))
        is_pass_product = s >= RELEVANT_SCORE_MIN
        rank = p.get("rank")
        raw = raw_by_rank.get(rank, {})
        meta = normalize_product_meta(raw) if raw else {}
        item = {
            "rank": rank,
            "title": meta.get("title") or p.get("title"),
            "brand": meta.get("brand") or p.get("brand"),
            "image_url": meta.get("image_url") or p.get("image_url"),
            "selling_price": meta.get("selling_price") if meta.get("selling_price") is not None
                             else p.get("selling_price"),
            "currency": meta.get("currency") or p.get("currency"),
            "category_path": meta.get("category_path") or p.get("category_path"),
            "stock_status": meta.get("stock_status") or p.get("stock_status"),
            "_g": (raw.get("custom") or {}).get("_g"),
            "relevance_score": s,
            "relevance_label": relevance_label(s),
            "comment_skipped": is_pass_product,
        }
        if not is_pass_product:
            item["violated_conditions"] = p.get("violated_conditions") or []
            item["description"] = p.get("description")
            item["exposure_reason"] = p.get("exposure_reason")
            item["reason"] = p.get("reason")
        product_scores.append(item)

    # ── 보조 지표 ──
    alc = answer_length_check(answer_text, language)
    pm = product_metrics(product_scores)

    # ── zero_result ──
    zero_result_type = None
    if product_count == 0:
        tools_used = _safe_json(ph.get("tools_used"), default=[]) or []
        zero_result_type = classify_zero_result(tools_used, answer_text)

    # ── 점수 ──
    a_label = llm_eval.get("A_query_intent", "FAIL")
    b_label = llm_eval.get("B_text_quality", "POOR")
    e_label = llm_eval.get("E_diversity", "POOR")
    sc = compute_scores(
        a_label, b_label, e_label,
        pm["c_avg"], pm["noise_pct"],
        krc_in.get("result", "해당없음"), alc["result"], pm["top_3_acc_avg"],
        product_count, bool(is_multi), turn_number, ctx_label,
    )

    # ── 판정 ──
    verdict = score_verdict(sc["Score"], sc["Acc"], sc["Comp"], product_count)
    initial = llm_initial_judgement(verdict)

    final_lat = _safe_int(ph.get("final_llm_latency_ms"))
    checks, log_connected = phoenix_checks(
        ph, eval_input, product_count, pm["c_label"], krc_in.get("result", "해당없음"),
        llm_ph.get("params_ok"), llm_ph.get("grounding_ok"),
        bool(is_multi), turn_number, ctx_label,
    )

    # Phoenix 수집을 의도적으로 끈 경우(eval_input["phoenix_skipped"]=True):
    # '연결 실패'가 아니라 '평가 안 함'으로 처리한다. → Phoenix 항목을 N/A로 비우고
    # 판정은 LLM 단독으로, root_cause 에 '로그 연결 문제'를 넣지 않는다.
    if eval_input.get("phoenix_skipped"):
        checks = {k: None for k in checks}
        ph_judge = "Phoenix 미수집"
        final = final_judgement(verdict, initial, ph_judge, checks, product_count)
        root_cause = build_root_cause(checks, True, product_count, b_label, final_lat)
    else:
        ph_judge = phoenix_judgement(checks, log_connected, product_count)
        final = final_judgement(verdict, initial, ph_judge, checks, product_count)
        root_cause = build_root_cause(checks, log_connected, product_count, b_label, final_lat)
    evidence = phoenix_evidence(ph, answer_text)

    outlier = is_outlier(sc["Acc"], pm["top_3_acc_avg"])
    unstable, unstable_reasons = judge_instability(
        sc["Acc"], sc["Comp"], sc["Score"], pm["c_avg"],
        pm["noise_pct"], pm["top_3_acc_avg"], pm["is_top_k_bad"],
    )
    priority, priority_reason = test_priority(final, sc["Acc"], outlier)
    changed = _level(initial) != _level(final)

    # ── 코멘트 생략 정책: Hard Pass 만 생략 ──
    is_hard_pass = final == "Hard Pass"

    # ── top_k_reason ──
    top_k_reason = None
    if not is_hard_pass and (pm["is_top_k_bad"] or pm["top_3_acc_avg"] < 1.0):
        top_k_reason = f"Top-{TOP_K} 적합 비율 {pm['top_3_acc_avg']:.2f}."

    # ── evaluation 블록 ──
    evaluation = {
        "A_query_intent": a_label, "A_score": sc["A_score"],
        "B_text_quality": b_label, "B_score": sc["B_score"],
        "C_relevance": pm["c_label"], "C_avg_relevance": pm["c_avg"],
        "D_noise_ratio": pm["d_label"], "D_noise_pct": pm["noise_pct"],
        "D_low_relevance_items": pm["low_items"],
        "E_diversity": e_label, "E_score": sc["E_score"],
        "E_top_brands": llm_eval.get("E_top_brands") or [],
        "Rel": sc["Rel"], "Acc": sc["Acc"], "Comp": sc["Comp"],
        "Ctx_final": sc["Ctx_final"], "Score": sc["Score"],
        "score_formula": sc["score_formula"],
        "verdict": verdict, "is_outlier": outlier, "human_review": outlier,
        "is_judge_unstable": unstable, "unstable_reasons": unstable_reasons,
        "issue_types": llm_eval.get("issue_types") or ["없음"],
        "llm_initial_judgement": initial,
        "phoenix_judgement": ph_judge,
        "final_judgement": final,
        "judgement_changed": changed,
        "root_cause": root_cause,
        "phoenix_evidence": evidence,
        "test_priority": priority,
        "comment_skipped": is_hard_pass,
    }
    if bool(is_multi) and (turn_number or 1) >= 2:
        evaluation["drift_human_flag"] = bool(drift_detected)
    # Pass(Hard Pass)면 코멘트성 필드 생략
    if not is_hard_pass:
        evaluation["A_reason"] = llm_eval.get("A_reason")
        evaluation["B_reason"] = llm_eval.get("B_reason")
        evaluation["C_reason"] = llm_eval.get("C_reason")
        evaluation["D_reason"] = llm_eval.get("D_reason")
        evaluation["E_reason"] = llm_eval.get("E_reason")
        evaluation["issue_detail"] = llm_eval.get("issue_detail")
        if priority_reason:
            evaluation["priority_reason"] = priority_reason

    # ── summary 블록 ──
    if is_hard_pass:
        summary = {"comment_skipped": True}
    else:
        summary = {
            "strengths": llm_summary.get("strengths"),
            "weaknesses": llm_summary.get("weaknesses"),
            "recommendations": llm_summary.get("recommendations"),
            "notes": llm_summary.get("notes"),
            "comment_skipped": False,
        }

    # ── keyword_relevance_check (Pass 면 reason 비움 가능) ──
    krc = {
        "result": krc_in.get("result", "해당없음"),
        "keywords": krc_in.get("keywords") or [],
        "reason": krc_in.get("reason") or "",
    }

    return {
        "case_id": eval_input.get("case_id"),
        "query_id": eval_input.get("query_id") or eval_input.get("scenario_id") or eval_input.get("case_id"),
        "session_id": eval_input.get("session_id"),
        "chat_request_id": eval_input.get("chat_request_id"),
        "query": eval_input.get("query"),
        "search_type_name": eval_input.get("search_type_name"),
        "eval_type": "멀티턴" if is_multi else "싱글턴",
        "scenario_id": eval_input.get("scenario_id") if is_multi else None,
        "turn_number": turn_number if is_multi else None,
        "previous_turn_queries": eval_input.get("previous_turn_queries") or [],
        "language": language,
        "reasoning": llm.get("reasoning") or "",
        "segment_tags": {
            "CATEGORY": seg.get("CATEGORY"), "GENDER": seg.get("GENDER"),
            "BRAND": seg.get("BRAND"), "COLOR": seg.get("COLOR"),
            "SIZE": seg.get("SIZE"), "MATERIAL": seg.get("MATERIAL"),
            "PRICE": seg.get("PRICE"), "INTENT": seg.get("INTENT", "recommend"),
        },
        "top_k_check": {
            "top_3_acc_avg": pm["top_3_acc_avg"],
            "is_top_k_bad": pm["is_top_k_bad"],
            **({"top_k_reason": top_k_reason} if top_k_reason else {}),
        },
        "answer_text": answer_text,
        "latency_ms": round_trip_ms(eval_input),   # e2e 라운드트립(ms) — latency 추적 메인 지표
        "answer_length_check": alc,
        "keyword_relevance_check": krc,
        "product_count": product_count,
        "zero_result_type": zero_result_type,
        "product_scores": product_scores,
        "unevaluated_products": eval_input.get("unevaluated_products") or [],
        "phoenix_checks": checks,
        "evaluation": evaluation,
        "summary": summary,
    }


# ═════════════════════════════════════════════════════════════
# data.json 최상위 (meta + kpi + queries)
# ═════════════════════════════════════════════════════════════
def build_data_json(queries: list[dict], meta_info: dict) -> dict:
    """compute_query 결과 리스트 → data.json 최상위 객체."""
    dist = Counter()
    counter_q = 0
    no_result = 0
    attention = 0

    for q in queries:
        final = (q.get("evaluation") or {}).get("final_judgement", "")
        key = {
            "Hard Pass": "hard_pass", "Conditional Pass": "conditional_pass",
            "Warning": "warning", "Fail": "fail", "High Risk": "high_risk",
            "zero_result": "zero_result",
        }.get(final)
        if key:
            dist[key] += 1

        zrt = q.get("zero_result_type")
        if zrt == "역질문/상품 미반환":
            counter_q += 1
        elif zrt == "검색 결과 없음":
            no_result += 1

        ev = q.get("evaluation") or {}
        if ev.get("human_review") or final in ("Warning", "Fail", "High Risk"):
            attention += 1

    total_pc = sum(int(q.get("product_count") or 0) for q in queries)
    display_pc = sum(len(q.get("product_scores") or []) for q in queries)

    verdict_distribution = {
        "hard_pass": dist.get("hard_pass", 0),
        "conditional_pass": dist.get("conditional_pass", 0),
        "warning": dist.get("warning", 0),
        "fail": dist.get("fail", 0),
        "high_risk": dist.get("high_risk", 0),
        "zero_result": dist.get("zero_result", 0),
    }

    # ── 세션 기준 싱글턴/멀티턴 집계 + 전체 통과율 ──────────────────────
    #  · 멀티턴 판정: eval_type == "멀티턴" 또는 query_id 가 M 으로 시작
    #  · 세션 그룹핑: session_id 기준, 없으면 케이스 단위 독립 세션
    #  · 세션 판정: 하나라도 Fail/High Risk → FAIL, 없으면 Warning → WARNING,
    #              그 외(Pass·Conditional Pass·zero_result 포함) → PASS
    #  · 전체 통과율 = (Pass + Warning) ÷ 전체 세션
    session_summary, total_sessions, pass_rate = _session_kpi(queries)

    meta = {
        "dataset": meta_info.get("dataset", "STG-GELATTO_Common_KRJP"),
        "report_title": meta_info.get("report_title", meta_info.get("dataset", "GELATTO_Common_KRJP")),
        "subtitle": meta_info.get(
            "subtitle", f"v2.0 통합 판정 (LLM × Phoenix) — 전체 {len(queries)}건"
        ),
        "generated_at": meta_info.get("generated_at", ""),
        "env": meta_info.get("env", ""),
        "label": meta_info.get("label", "라벨링 없음"),
        "prompt_file": meta_info.get("prompt_file", ""),
        "evaluator_version": "v2.0",
        "total_queries": len(queries),
        "session_count": total_sessions,
        "total_product_count": total_pc,
        "display_product_count": display_pc,
    }
    kpi = {
        "verdict_distribution": verdict_distribution,
        "counter_question_count": counter_q,
        "no_result_count": no_result,
        "attention_queries": attention,
        "session_summary": session_summary,
        "total_sessions": total_sessions,
        "pass_rate": pass_rate,
    }
    return {"meta": meta, "kpi": kpi, "queries": queries}


def _is_multiturn(q: dict) -> bool:
    if q.get("eval_type") == "멀티턴":
        return True
    qid = str(q.get("query_id") or "")
    return qid[:1].upper() == "M"


def _verdict_bucket(final_judgement: str) -> str:
    """세션 판정용 버킷. zero_result/Pass 계열 → pass."""
    s = str(final_judgement or "").lower()
    if "fail" in s or "high risk" in s:
        return "fail"
    if "warning" in s:
        return "warning"
    return "pass"


def _session_kpi(queries: list[dict]) -> tuple[dict, int, dict]:
    """세션 기준 싱글턴/멀티턴 집계 + 전체 통과율((Pass+Warning)/전체)."""
    sessions: dict[str, list[dict]] = {}
    solo = 0
    for q in queries:
        sid = q.get("session_id")
        if not sid:
            sid = "__solo_" + str(q.get("case_id") or q.get("query_id") or f"n{solo}")
            solo += 1
        sessions.setdefault(sid, []).append(q)

    groups = {
        "singleturn": {"total": 0, "pass_count": 0, "warning": 0, "fail": 0},
        "multiturn":  {"total": 0, "pass_count": 0, "warning": 0, "fail": 0},
    }
    for arr in sessions.values():
        g = groups["multiturn"] if any(_is_multiturn(x) for x in arr) else groups["singleturn"]
        g["total"] += 1
        buckets = [_verdict_bucket((x.get("evaluation") or {}).get("final_judgement")) for x in arr]
        if "fail" in buckets:
            g["fail"] += 1
        elif "warning" in buckets:
            g["warning"] += 1
        else:
            g["pass_count"] += 1

    total_sessions = groups["singleturn"]["total"] + groups["multiturn"]["total"]
    pass_warn = (groups["singleturn"]["pass_count"] + groups["singleturn"]["warning"]
                 + groups["multiturn"]["pass_count"] + groups["multiturn"]["warning"])
    value = round(pass_warn / total_sessions * 100) if total_sessions else 0
    pass_rate = {
        "value": value,
        "basis": "pass_warning",
        "numerator": pass_warn,
        "denominator": total_sessions,
    }
    return groups, total_sessions, pass_rate
