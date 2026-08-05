"""
2단계 집계: 1단계 raw 평가 결과(jsonl)를 받아서
KPI 수치, 카테고리 그레이드, 대표 케이스 등 결정론적 통계를 만든다.
LLM 호출 없음.
"""
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from typing import Any


# ─────────────────────────────────────────────
# 임계값 (200건 분포 기반)
# ─────────────────────────────────────────────
VERDICT_TONE = {
    "적합": "good",
    "경고": "warn",
    "위험": "bad",
    "역질문/상품 미반환": "warn",
    "검색 결과 없음": "warn",
}

# health_score 임계값
HEALTHY_THRESHOLD = 80
DEGRADED_THRESHOLD = 60   # 이 아래는 BROKEN

# KPI 카드 tone 임계값 (적합률 %)
RELEVANCE_GOOD = 70
RELEVANCE_WARN = 50

# 대표 케이스 추출 개수
TOP_RISK_CASES_N = 10


# ─────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────
def load_raw_evals(jsonl_path: Path) -> list[dict]:
    """jsonl 파일을 읽어서 dict 리스트로 반환. 에러 항목은 별도 보관."""
    items = []
    for line in jsonl_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        items.append(json.loads(line))
    return items


def aggregate(raw_evals: list[dict]) -> dict:
    """
    1단계 결과 리스트를 받아 Tier 1+2 집계 결과를 반환.
    LLM에 넘길 통계 묶음 + 대시보드 KPI 카드 + sections 일부를 모두 포함.
    """
    # 멀티턴 시나리오는 각 turn을 펼쳐서 단위 평가로 변환
    flat_evals = _flatten_multi_scenarios(raw_evals)

    # 에러/정상 분리
    errors = [r for r in flat_evals if "error" in r]
    valid = [r for r in flat_evals if "error" not in r]

    return {
        "totals": _compute_totals(valid, errors),
        "verdict_distribution": _compute_verdict_distribution(valid),
        "score_stats": _compute_score_stats(valid),
        "relevance_stats": _compute_relevance_stats(valid),
        "quality_stats": _compute_quality_stats(valid),
        "language_stats": _compute_language_stats(valid),
        "category_breakdown": _compute_category_breakdown(valid),
        "top_risk_cases": _extract_top_risk_cases(valid, raw_evals),
        "low_confidence_zero_cases": _extract_low_confidence_zero(valid),
        "kpi_cards": _build_kpi_cards(valid, raw_evals),
        "health_score": _compute_health_score(valid),
        "verdict": _derive_overall_verdict(valid),
    }


# ─────────────────────────────────────────────
# 멀티턴 평탄화 — scenario_summary는 별도 보존
# ─────────────────────────────────────────────
def _flatten_multi_scenarios(raw_evals: list[dict]) -> list[dict]:
    """
    멀티턴 시나리오 객체는 turns[] 안에 단위 평가가 들어있음.
    각 turn을 독립 평가 항목으로 펼쳐서 통계 계산이 일관되게 처리되도록 함.
    """
    flat = []
    for r in raw_evals:
        if "error" in r:
            flat.append(r)
            continue
        if r.get("turn_type") == "multi" and "turns" in r:
            # scenario 메타를 각 턴에 주입 (case_id 보존 위해)
            for t in r["turns"]:
                enriched = dict(t)
                enriched.setdefault("case_id", f"{r['case_id']}-T{t.get('turn')}")
                enriched.setdefault("category", r.get("category"))
                enriched.setdefault("session_id", r.get("session_id"))
                enriched["_scenario_id"] = r["case_id"]
                flat.append(enriched)
        else:
            flat.append(r)
    return flat


# ─────────────────────────────────────────────
# 개별 집계 함수
# ─────────────────────────────────────────────
def _compute_totals(valid: list[dict], errors: list[dict]) -> dict:
    return {
        "total": len(valid) + len(errors),
        "valid": len(valid),
        "errors": len(errors),
        "general_track": sum(1 for r in valid if r.get("track") == "general"),
        "zero_track":    sum(1 for r in valid if r.get("track") == "zero_result"),
    }


def _compute_verdict_distribution(valid: list[dict]) -> dict:
    counter = Counter(r.get("verdict") for r in valid)
    return {v: c for v, c in counter.most_common() if v is not None}


def _compute_score_stats(valid: list[dict]) -> dict:
    scores = [r["final_score"] for r in valid
              if r.get("track") == "general" and r.get("final_score") is not None]
    if not scores:
        return {"n": 0}
    buckets = {"0-1": 0, "1-2": 0, "2-3": 0, "3-4": 0, "4-5": 0}
    for s in scores:
        if s < 1:   buckets["0-1"] += 1
        elif s < 2: buckets["1-2"] += 1
        elif s < 3: buckets["2-3"] += 1
        elif s < 4: buckets["3-4"] += 1
        else:       buckets["4-5"] += 1
    return {
        "n": len(scores),
        "min":  round(min(scores), 2),
        "max":  round(max(scores), 2),
        "mean": round(mean(scores), 2),
        "buckets": buckets,
    }


def _compute_relevance_stats(valid: list[dict]) -> dict:
    """
    Top-10 / Top-30 적합 비율. 분모는 실제 평가된 상품 수.
    """
    top10_relevant, top10_total = 0, 0
    top30_relevant, top30_total = 0, 0

    for r in valid:
        if r.get("track") != "general":
            continue
        for p in (r.get("products_top10") or []):
            top10_total += 1
            top30_total += 1
            if p.get("relevance_score", 0) >= 3:
                top10_relevant += 1
                top30_relevant += 1
        for p in (r.get("products_top30_extra") or []):
            top30_total += 1
            if p.get("relevance_score", 0) >= 3:
                top30_relevant += 1

    return {
        "top10": {
            "total_products": top10_total,
            "relevant_products": top10_relevant,
            "rate": round(top10_relevant / top10_total * 100, 1) if top10_total else 0,
        },
        "top30": {
            "total_products": top30_total,
            "relevant_products": top30_relevant,
            "rate": round(top30_relevant / top30_total * 100, 1) if top30_total else 0,
        },
    }


def _compute_quality_stats(valid: list[dict]) -> dict:
    """A~F 항목별 평균 (general 트랙)."""
    keys = ["rel", "pers", "acc", "comp", "ctx", "ctx_drift"]
    sums = defaultdict(list)
    for r in valid:
        if r.get("track") != "general":
            continue
        scores = r.get("scores") or {}
        for k in keys:
            v = scores.get(k)
            if v is not None:
                sums[k].append(v)
    return {k: round(mean(vs), 2) if vs else None for k, vs in sums.items()}


def _compute_language_stats(valid: list[dict]) -> dict:
    matched, total = 0, 0
    by_lang = Counter()
    for r in valid:
        lm = r.get("language_match")
        if lm is None:
            continue
        total += 1
        if lm:
            matched += 1
        by_lang[r.get("query_language")] += 1
    return {
        "total": total,
        "matched": matched,
        "mismatch": total - matched,
        "mismatch_rate": round((total - matched) / total * 100, 1) if total else 0,
        "by_language": dict(by_lang),
    }


def _compute_category_breakdown(valid: list[dict]) -> dict:
    """
    카테고리별 verdict 분포 + 평균 score + 그레이드.
    sections[grade_matrix]로 그대로 변환 가능한 형태.
    """
    by_cat = defaultdict(lambda: {
        "verdict_dist": Counter(),
        "scores": [],
        "total": 0,
    })
    for r in valid:
        cat = r.get("category", "unknown")
        by_cat[cat]["verdict_dist"][r.get("verdict")] += 1
        by_cat[cat]["total"] += 1
        if r.get("final_score") is not None:
            by_cat[cat]["scores"].append(r["final_score"])

    result = {}
    for cat, d in by_cat.items():
        avg = round(mean(d["scores"]), 2) if d["scores"] else None
        result[cat] = {
            "total": d["total"],
            "verdict_dist": dict(d["verdict_dist"]),
            "avg_score": avg,
            "grade": _score_to_grade(avg),
        }
    return result


def _score_to_grade(score: float | None) -> str:
    """final_score → A~F 매핑."""
    if score is None: return "-"
    if score >= 4.5: return "A"
    if score >= 3.5: return "B"
    if score >= 2.5: return "C"
    if score >= 1.5: return "D"
    return "F"


def _extract_top_risk_cases(valid: list[dict],
                            all_raw: list[dict]) -> list[dict]:
    """
    위험 케이스 추출. 멀티턴은 시나리오 전체(전후 턴 포함)를 묶어서 반환.
    싱글턴은 단독.
    """
    # 1) 단위 평가에서 위험 추출 (final_score 낮은 순)
    risk = [r for r in valid
            if r.get("verdict") == "위험" and r.get("final_score") is not None]
    risk.sort(key=lambda r: r["final_score"])

    # 2) 멀티턴 시나리오 dict 미리 구성: {scenario_id: scenario_obj}
    scenarios_by_id = {
        r["case_id"]: r
        for r in all_raw
        if r.get("turn_type") == "multi" and "turns" in r
    }

    # 3) 표시용으로 변환 — 멀티턴은 전체 시나리오 묶음으로
    result = []
    seen_scenarios = set()

    for r in risk[:TOP_RISK_CASES_N]:
        scenario_id = r.get("_scenario_id")  # 평탄화 시 주입한 메타

        if scenario_id and scenario_id not in seen_scenarios:
            # 멀티턴 — 시나리오 전체 추가
            scenario = scenarios_by_id.get(scenario_id)
            if scenario:
                result.append({
                    "kind": "multi_scenario",
                    "case_id": scenario_id,
                    "category": scenario.get("category"),
                    "session_id": scenario.get("session_id"),
                    "risk_turns": [r["turn"] for r in scenario["turns"]
                                   if r.get("verdict") == "위험"],
                    "turns": [{
                        "turn": t.get("turn"),
                        "query": t.get("query"),
                        "verdict": t.get("verdict"),
                        "final_score": t.get("final_score"),
                        "intent_match": t.get("intent_match"),
                        "noise_level": t.get("noise_level"),
                        "issue_types": t.get("issue_types", []),
                        "improvement_notes": t.get("improvement_notes"),
                    } for t in scenario["turns"]],
                })
                seen_scenarios.add(scenario_id)
        elif not scenario_id:
            # 싱글턴 — 단독
            result.append({
                "kind": "single",
                "case_id": r["case_id"],
                "category": r.get("category"),
                "query": r.get("query"),
                "final_score": r["final_score"],
                "verdict": r["verdict"],
                "intent_match": r.get("intent_match"),
                "noise_level": r.get("noise_level"),
                "issue_types": r.get("issue_types", []),
                "improvement_notes": r.get("improvement_notes"),
            })
        # 같은 시나리오의 다른 위험 턴은 스킵 (이미 시나리오 통째로 들어감)

    return result

def _extract_low_confidence_zero(valid: list[dict]) -> list[dict]:
    """zero_result_confidence: low인 케이스. 사람 검토 필요 표시용."""
    return [{
        "case_id": r["case_id"],
        "query": r.get("query"),
        "zero_result_type": r.get("zero_result_type"),
        "zero_result_reason": r.get("zero_result_reason"),
    } for r in valid
       if r.get("track") == "zero_result"
       and r.get("zero_result_confidence") == "low"]


def _build_kpi_cards(valid: list[dict], raw_evals: list[dict]) -> list[dict]:
    """대시보드 상단 KPI 카드 5개."""
    rel = _compute_relevance_stats(valid)
    q = _compute_quality_stats(valid)
    vd = _compute_verdict_distribution(valid)
    totals = _compute_totals(valid, [])

    # 싱글턴/멀티턴 단위 평가 개수 분리
    single_cnt = 0
    multi_turn_cnt = 0
    multi_scenario_cnt = 0
    for r in raw_evals:
        if "error" in r:
            continue
        if r.get("turn_type") == "single":
            single_cnt += 1
        elif r.get("turn_type") == "multi":
            multi_scenario_cnt += 1
            multi_turn_cnt += len(r.get("turns", []))
    total_cnt = single_cnt + multi_turn_cnt

    def tone_rel(rate: float) -> str:
        if rate >= RELEVANCE_GOOD: return "good"
        if rate >= RELEVANCE_WARN: return "warn"
        return "bad"

    def tone_score(s: float | None) -> str:
        if s is None: return "muted"
        if s >= 3.5: return "good"
        if s >= 2.5: return "warn"
        return "bad"
    
    risk_cnt = vd.get('위험', 0)
    warn_cnt = vd.get('경고', 0)
    reverse_q  = vd.get('역질문/상품 미반환', 0)
    no_result  = vd.get('검색 결과 없음', 0)

    acc = q.get('acc')
    comp = q.get('comp')

    return [
        # 1) 총 질문 수
        {
            "label": "총 질문 수",
            "type": "primary",
            "tone": "muted",
            "value": f"{total_cnt}",
            "footer": f"싱글턴 {single_cnt} / 멀티턴 {multi_turn_cnt} (시나리오 {multi_scenario_cnt} 건)",
        },
        # 2) 상품 적합 비율 (Top-10, Top-30)
        {
            "label": "상품 적합 비율",
            "type": "split",
            "tone": tone_rel(rel['top10']['rate']),
            "items": [
                {"sublabel": "상위 10", "value": f"{rel['top10']['rate']}%"},
                {"sublabel": "상위 30", "value": f"{rel['top30']['rate']}%"},
            ],
        },
        # 3) 답변 품질 지표 (Acc, Comp)
        {
            "label": "답변 품질 지표",
            "type": "split",
            "tone": tone_score(acc),
            "items": [
                {"sublabel": "답변 품질 (Acc)", "value": f"{acc:.2f}" if acc else "—"},
                {"sublabel": "정합성 (Comp)",   "value": f"{comp:.2f}" if comp else "—"},
            ],
        },
        # 4) 위험 / 경고
        {
            "label": "위험 / 경고",
            "type": "split",
            "tone": "bad" if risk_cnt > 0 else ("warn" if warn_cnt > 0 else "good"),
            "items": [
                {"sublabel": "위험", "value": f"{risk_cnt}건"},
                {"sublabel": "경고", "value": f"{warn_cnt}건"},
            ],
        },
        # 5) 0건 분류
        {
            "label": "0건 분류",
            "type": "split",
            "tone": "warn" if (reverse_q + no_result) > 0 else "good",
            "items": [
                {"sublabel": "역질문·상품 미반환", "value": f"{reverse_q}건"},
                {"sublabel": "검색 결과 없음",      "value": f"{no_result}건"},
            ],
        },
    ]


def _compute_health_score(valid: list[dict]) -> int:
    """
    종합 health_score 0-100.
    relevance_rate (top-10) 60% + answer_quality 30% + zero_rate 10%
    """
    rel = _compute_relevance_stats(valid)
    q = _compute_quality_stats(valid)
    total = len(valid)
    zero = sum(1 for r in valid if r.get("track") == "zero_result")
    zero_rate = zero / total if total else 0

    rel_score = rel['top10']['rate']                            # 0-100
    qual_score = (q.get('acc') or 0) * 20                       # 0-5 → 0-100
    zero_penalty = max(0, 100 - zero_rate * 200)                # zero 비율이 50%면 0점

    score = rel_score * 0.6 + qual_score * 0.3 + zero_penalty * 0.1
    return max(0, min(100, round(score)))


def _derive_overall_verdict(valid: list[dict]) -> str:
    """health_score 기반 HEALTHY/DEGRADED/BROKEN."""
    hs = _compute_health_score(valid)
    if hs >= HEALTHY_THRESHOLD: return "HEALTHY"
    if hs >= DEGRADED_THRESHOLD: return "DEGRADED"
    return "BROKEN"