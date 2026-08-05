"""
core/yamato_scoring.py — YAMATO(genser_discovery / report_type: yamato) 전용 수치 계산 엔진.

설계(C안: LLM 정성 + 코드 수치)
────────────────────────────────
  · LLM 출력 → relevance_score(0~4), 야마토 segment_tags, filter_evaluation 라벨,
                A/B/E/F 라벨·이유, keyword_relevance_check, summary  (schemas.LLMQueryEvalYamato)
  · 코드 계산 → relevance_label(적합/애매/유해), 산지·가격 게이트(matched/violated/100g당 단가),
                100점 score_detail, noise/top-k, zero_result 분류·대안유도 탐지,
                verdict·final_judgement, function_breakdown / type_breakdown, KPI

prompt/evaluate.py(프로토타입)의 순수 함수를 이식했다. CSV·~/Downloads·main() 의존은 제거하고
입력은 sheet_parser 가 만든 eval_input(dict)으로 통일한다. 공통 기계 항목(phoenix_evidence,
phoenix_checks, answer_length_check 등)은 core/scoring.py 를 재사용한다.

산출물(queries[] 객체)은 dashboard(app.js)가 이미 소비하는 야마토 스키마와 1:1로 맞춘다.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from typing import Any, Optional

from . import scoring as S


# ═════════════════════════════════════════════════════════════
# 상수 (prompt/evaluate.py 이식 — 단일 관리 지점)
# ═════════════════════════════════════════════════════════════
# 일본 광역 산지 + 동치 매핑
PREFECTURES = ['北海道','青森','岩手','宮城','秋田','山形','福島','茨城','栃木','群馬','埼玉','千葉','東京','神奈川',
 '新潟','富山','石川','福井','山梨','長野','岐阜','静岡','愛知','三重','滋賀','京都','大阪','兵庫','奈良','和歌山',
 '鳥取','島根','岡山','広島','山口','徳島','香川','愛媛','高知','福岡','佐賀','長崎','熊本','大分','宮崎','鹿児島','沖縄']
REGION_MAP = {'魚沼':'新潟','北見':'北海道','オホーツク':'北海道','知床':'北海道','十勝':'北海道','信州':'長野',
 '讃岐':'香川','近江':'滋賀','多摩':'東京','石巻':'宮城'}

# 대안유도(대안 추천 위반) 패턴 — 권유형(추천) 표현만
ALT_PATTERNS = ['代わりに','かわりに','いかがでしょうか','いかがですか','おすすめいたします',
 'おすすめします','お勧めします','をご提案します','はどうでしょう','代替商品をご提案',
 '別の商品をおすすめ','こちらもおすすめ','もおすすめです']
# 거절/불가 표현이 함께 있으면 권유가 아니라 거절 → 위반 아님
ALT_NEG = ['できません','特定できません','不明','対応しておりません','機能はございません','お答えすることができません']
# 0건 명시(검색 결과 없음) 표현
NORESULT_PATTERNS = ['見つかりません','見つかりませんでした','該当する商品','該当商品','商品がありません',
 '現在ありません','取り扱いがありません','検索結果がありません','在庫がありません','ございません']
# 역질문 표현
ASKBACK_PATTERNS = ['どのような','ご希望','教えてください','お聞かせ','用途','条件','もう少し','具体的','お探しでしょうか']

# 기능분류(類型/検索基準) 한국어 매핑
FUNC_KO = {
    '配送条件':'배송 조건','属性具体':'속성 구체화','産地指定':'산지 지정','価格条件':'가격 조건',
    '季節提案':'계절 제안','複合条件':'복합 조건','検索の言い換え揺れ':'검색어 표현 변형',
    '数値条件つき質問':'수치 조건 질문','失敗回避系の質問':'실패 회피 질문','希少提案':'희소 상품 제안',
    '用途曖昧':'용도 모호','安全性・証明・トレーサビリティ':'안전성·인증·추적성',
    '歩留まり・仕込み効率':'수율·전처리 효율','比較・代替・欠品対応':'비교·대체·결품 대응',
    '発注運用':'발주 운용','運用効率':'운용 효율','メニュー開発':'메뉴 개발',
}

# 1식(1인분) 표준 중량(g) — 후생노동성·농림수산성 식사밸런스가이드 기준
SERVING_G_MAIN = 60      # 主菜: 고기·생선 약 60g
SERVING_G_VEG  = 140     # 副菜: 채소·버섯·해조 약 140g
SERVING_G_STAPLE = 200   # 主食: 밥·면·곡물 약 200g
SERVING_G_DEFAULT = SERVING_G_MAIN

PRICE_RE = re.compile(r'(\d[\d,]*)\s*円(以内|以下|まで|前後|台|以上)?')
PER_SERVING_RE = re.compile(r'(\d[\d,]*)\s*円')
WEIGHT_RE = re.compile(r'(\d+(?:[.,]\d+)?)\s*(kg|ｋｇ|キロ|kｇ|g|ｇ|グラム|gr)', re.I)

# 100점 배점 (prompt Step 10: 조건인식25·필터변환25·결과적합25·제외준수15·완성도10)
SC_COND   = {'PASS': 25, 'PARTIAL': 17, 'FAIL': 8}     # condition_recognition (A 라벨)
SC_FILTER = {'PASS': 25, 'PARTIAL': 13, 'FAIL': 0}     # filter_conversion (filter_evaluation)
SC_COMP   = {'GOOD': 10, 'ACCEPTABLE': 7, 'POOR': 4}   # completeness (B 라벨)
SC_RESULT_MAX = 25                                     # result_match = (1-noise)*25
SC_EXCLUDE_FULL = 15                                   # 제외 조건 준수


# ═════════════════════════════════════════════════════════════
# 소형 유틸
# ═════════════════════════════════════════════════════════════
def to_int(v, d=0):
    try: return int(float(v))
    except Exception: return d

def to_float(v, d=None):
    try: return float(v)
    except Exception: return d

def func_ko(v):
    if not v: return v
    return FUNC_KO.get(str(v).strip(), str(v).strip())


# ═════════════════════════════════════════════════════════════
# 산지 / 가격 파싱 (prompt/evaluate.py 이식)
# ═════════════════════════════════════════════════════════════
def extract_origin(text):
    if not text: return []
    found = []
    if '国産' in text: found.append('国産')
    for r, p in REGION_MAP.items():
        if r in text: found.append(p)
    for p in PREFECTURES:
        if p in text: found.append(p)
    if '瀬戸内' in text: found.append('瀬戸内')
    return list(dict.fromkeys(found))

def norm_origin(o):
    if not o: return ''
    return re.sub(r'(県|府|都|産)$', '', o)

def query_origin(query):
    """쿼리에서 요구 산지 추출(연도표기 제외)."""
    q = re.sub(r'(令和\d+年産|R\d+年産|\d{4}年産|\d+年産)', '', query or '')
    return extract_origin(q)

def query_price(query):
    if not query: return None
    m = PRICE_RE.search(query)
    if m:
        val = int(m.group(1).replace(',', ''))
        kind = m.group(2) or ''
        if kind in ('以内', '以下', 'まで', '台', ''):
            return {'op': '<=', 'val': val, 'raw': m.group(0)}
        if kind == '以上':
            return {'op': '>=', 'val': val, 'raw': m.group(0)}
        if kind == '前後':
            return {'op': '~', 'val': val, 'raw': m.group(0)}
    if any(k in query for k in ['高価格', '高級']):
        return {'op': 'high', 'val': None, 'raw': '高価格帯'}
    if any(k in query for k in ['安い', '低単価', '単価の低い', '格安']):
        return {'op': 'low', 'val': None, 'raw': '低価格'}
    return None

def serving_g_for(category, query):
    """카테고리/쿼리로 1식 중량(g) 결정. 채소140 / 곡물200 / 主菜60."""
    text = (category or '') + ' ' + (query or '')
    if re.search(r'野菜|青果|葉茎|根菜|きのこ|キノコ|茸|海藻|いも類|いも|芋', text):
        return SERVING_G_VEG
    if re.search(r'米|麦|穀物|麺|めん|パン|ごはん|ご飯|白米|玄米', text):
        return SERVING_G_STAPLE
    if re.search(r'肉|牛|豚|鶏|精肉|魚|鮮魚|水産|刺身|切り身|甲殻|エビ|海老|カニ', text):
        return SERVING_G_MAIN
    return SERVING_G_DEFAULT

def per_serving_threshold(query, serving_g):
    """'N円/食'·'一人前N円' per-serving 가격을 100g당 임계값으로 환산."""
    if not query: return None
    if not re.search(r'(/?\s*食|一人前|人前|/\s*人)', query): return None
    m = PER_SERVING_RE.search(query)
    if not m: return None
    yen = int(m.group(1).replace(',', ''))
    return round(yen * 100.0 / serving_g)

def parse_weight_g(title):
    """상품명에서 무게(g) 추출. kg→g 환산. 없으면 None."""
    if not title: return None
    best = None
    for m in WEIGHT_RE.finditer(title):
        raw = m.group(1)
        val = float(raw.replace(',', '.')) if raw.count(',') == 1 and '.' not in raw else float(raw.replace(',', ''))
        unit = m.group(2).lower()
        g = val * 1000 if unit in ('kg', 'ｋｇ', 'キロ', 'kｇ') else val
        if best is None or g > best:
            best = g
    return best

def price_per_100g(price, grams):
    if not price or not grams or grams <= 0: return None
    return price * 100.0 / grams


# ═════════════════════════════════════════════════════════════
# 0건 분류 / 대안유도
# ═════════════════════════════════════════════════════════════
def classify_zero(answer, tools_used):
    """역질문/상품 미반환 vs 검색 결과 없음."""
    tu = tools_used or []
    if isinstance(tu, str):
        tu = S._safe_json(tu, default=[]) or []
    has_search = bool(tu)
    a = answer or ''
    if has_search:
        return '검색 결과 없음', 'json.tools_used'
    if any(p in a for p in NORESULT_PATTERNS) and not any(p in a for p in ASKBACK_PATTERNS):
        return '검색 결과 없음', 'answer_text_fallback'
    return '역질문/상품 미반환', 'answer_text_fallback'

def detect_altpush(answer):
    a = answer or ''
    hits = [p for p in ALT_PATTERNS if p in a]
    if not hits:
        return []
    if any(neg in a for neg in ALT_NEG):
        return []
    return hits


# ═════════════════════════════════════════════════════════════
# 상품 산지·가격 게이트 (점수는 LLM, 조건 충족/위반·단가는 코드)
# ═════════════════════════════════════════════════════════════
def product_gate(product, q_origins, q_price, max_per_100g=None, max_price_abs=None):
    """C안: relevance_score는 LLM이 부여. 코드는 산지·가격 조건의 충족/위반과
    100g당 단가·무게 등 '사실/수치'만 산출해 근거로 부착한다."""
    title = product.get('title') or product.get('product_name') or ''
    origin = product.get('origin')
    price = to_float(product.get('selling_price'))
    grams = parse_weight_g(title)
    p100 = price_per_100g(price, grams)
    matched, violated = [], []
    price_unknown = False

    q_norm = [norm_origin(o) for o in q_origins]
    if q_norm:
        name_origins = extract_origin(title)
        cand = []
        if origin:
            cand += extract_origin(origin) or [origin]
        cand += name_origins
        GENERIC = ('国産', '国')
        cand_has_generic = any(x == '国産' for x in cand)
        cand_specific = [norm_origin(x) for x in cand if x != '国産' and norm_origin(x) not in GENERIC]
        q_specific = [c for c in q_norm if c not in GENERIC]
        q_generic = ('国産' in q_origins)
        if q_specific:
            if any(c in q_specific for c in cand_specific):
                matched.append('원산지')
            elif cand_specific:
                violated.append('원산지 조건 위반')
            # generic/불명 → UNKNOWN(채점 제외)
        elif q_generic:
            if cand_specific or cand_has_generic:
                matched.append('원산지')

    # 가격 게이트 — 100g당 단가 > 절대 상한 > 쿼리 단순값
    if max_per_100g is not None:
        if price is None or grams is None:
            price_unknown = True
        elif p100 is not None:
            if p100 > max_per_100g:
                violated.append(f'100g당 단가 위반(¥{p100:.0f}/100g > ¥{max_per_100g})')
            else:
                matched.append(f'100g당 ¥{p100:.0f} ≤ ¥{max_per_100g}')
    elif max_price_abs is not None and price is not None:
        if price > max_price_abs:
            violated.append(f'가격 상한 위반(¥{price:.0f} > ¥{max_price_abs})')
        else:
            matched.append('가격')
    elif q_price and price is not None and q_price.get('val'):
        if q_price['op'] == '<=' and price > q_price['val']:
            violated.append('가격 조건 위반')
        elif q_price['op'] == '>=' and price < q_price['val']:
            violated.append('가격 조건 위반')
        elif q_price['op'] == '<=' and price <= q_price['val']:
            matched.append('가격')

    return {
        'weight_g': grams,
        'price_per_100g': round(p100, 1) if p100 is not None else None,
        'price_unknown': price_unknown,
        'matched_conditions': matched,
        'violated_conditions': violated,
    }


def relevance_label_yamato(score: int) -> str:
    if score >= 3: return '적합'
    if score == 2: return '애매'
    return '유해'


def filter_eval_code(tool_input, q_origins, q_price):
    """LLM filter_evaluation 미제공 시 폴백: 검색 조건 반영 여부 → PASS/PARTIAL/FAIL."""
    ti = tool_input if isinstance(tool_input, dict) else (S._safe_json(tool_input, {}) or {})
    blob = json.dumps(ti, ensure_ascii=False)
    missing = []
    if q_origins:
        if not any(norm_origin(o) in blob or o in blob or '国産' in blob for o in q_origins):
            missing.append('원산지')
    if q_price and q_price.get('val'):
        if not re.search(r'price', blob, re.I):
            missing.append('가격')
    if not q_origins and not q_price:
        return 'PASS', []
    if not missing:
        return 'PASS', []
    n_req = (1 if q_origins else 0) + (1 if q_price else 0)
    if len(missing) >= n_req:
        return ('PARTIAL' if len(missing) == 1 else 'FAIL'), missing
    return 'PARTIAL', missing


# ═════════════════════════════════════════════════════════════
# 메인: 한 쿼리/턴의 야마토 data.json 객체 조립
# ═════════════════════════════════════════════════════════════
def compute_query_yamato(eval_input: dict, llm: dict) -> dict:
    """
    eval_input : sheet_parser 입력(query/products/phoenix/function_category/...)
    llm        : LLMQueryEvalYamato(.model_dump()) — 정성 판단
    Returns    : data.json queries[] 한 객체 (야마토 스키마)
    """
    is_multi = eval_input.get("track_hint") == "multi" or eval_input.get("turn_number")
    turn_number = eval_input.get("turn_number")
    scenario_id = eval_input.get("scenario_id")
    product_count = int(eval_input.get("product_count") or 0)
    answer = eval_input.get("answer_text") or ""
    query = eval_input.get("query") or ""
    products = eval_input.get("products") or []
    ph = eval_input.get("phoenix") or {}

    language = llm.get("language") or S.detect_language(answer or query)
    func_cat = func_ko(eval_input.get("function_category"))
    llm_seg = llm.get("segment_tags") or {}
    krc_in = llm.get("keyword_relevance_check") or {}
    llm_eval = llm.get("evaluation") or {}
    llm_ph = llm.get("phoenix_judgments") or {}
    llm_summary = llm.get("summary") or {}
    llm_fe = llm.get("filter_evaluation") or {}

    # tool_input 정규화 파라미터
    tool_input = S._safe_json(ph.get("tool_input"), default={})
    ti = tool_input if isinstance(tool_input, dict) else {}
    max_per_100g = ti.get("max_price_per_100g")
    max_price_abs = ti.get("max_price")
    tools_used = S._safe_json(ph.get("tools_used"), default=[]) or []

    # 쿼리 조건 추출
    q_origins = query_origin(query)
    q_price = query_price(query)
    serving_note = None
    cat_for_serving = ti.get("category_path") or ti.get("category_paths") or query
    serving_g = serving_g_for(cat_for_serving, query)
    ps_thr = per_serving_threshold(query, serving_g)
    if ps_thr is not None:
        max_per_100g = ps_thr
        cat_label = '채소' if serving_g == SERVING_G_VEG else ('곡물' if serving_g == SERVING_G_STAPLE else '主菜(고기·생선)')
        serving_note = f'per-serving(円/食) → {cat_label} 1식 {serving_g}g 가정으로 ¥{ps_thr}/100g 환산 평가'
    per_unit = bool(re.search(r'(/?\s*kg|キロ|100\s*g|円/kg|/\s*100g)', query))
    if per_unit and max_per_100g is None and max_price_abs is None:
        q_price = None

    # PRICE 표기 (LLM 우선, 없으면 코드 산출)
    if max_per_100g is not None:
        price_tag = f'max_price_per_100g ≤ ¥{max_per_100g}/100g' + (f' ({serving_note})' if serving_note else '')
    elif max_price_abs is not None:
        price_tag = f'max_price ≤ ¥{max_price_abs}'
    elif q_price:
        price_tag = q_price['raw']
    else:
        price_tag = None
    price_filter = (f'max_price_per_100g <= {max_per_100g}' if max_per_100g is not None
                    else (f'max_price <= {max_price_abs}' if max_price_abs is not None else None))

    is_filter_query = bool(q_origins or q_price or max_per_100g is not None or max_price_abs is not None)
    # segment_tags: LLM 출력 우선, null 인 키만 코드 산출로 보강
    seg = {
        "ORIGIN": llm_seg.get("ORIGIN") or ('・'.join(q_origins) if q_origins else (ti.get("origin") or None)),
        "PRICE": llm_seg.get("PRICE") or price_tag,
        "PRICE_FILTER": llm_seg.get("PRICE_FILTER") or price_filter,
        "PRODUCT_KEYWORD": llm_seg.get("PRODUCT_KEYWORD"),
        "CATEGORY": llm_seg.get("CATEGORY") or ti.get("category_path") or ti.get("category_paths"),
        "BRAND": llm_seg.get("BRAND"),
        "SIZE_OR_UNIT": llm_seg.get("SIZE_OR_UNIT"),
        "EXCLUDE": llm_seg.get("EXCLUDE"),
        "INTENT": llm_seg.get("INTENT") or ('filter_search' if is_filter_query else 'recommend'),
    }

    # query_type / eval_type
    eval_type = "멀티턴" if is_multi else "싱글턴"
    if is_filter_query:
        query_type = "필터 쿼리 멀티턴" if is_multi else "필터 쿼리 싱글턴"
    else:
        query_type = "공통 쿼리"

    latency_summary = ""
    tlat = ph.get("tool_latency_ms"); flat = ph.get("final_llm_latency_ms")
    if tlat or flat:
        latency_summary = f'tool {tlat}ms / final LLM {flat}ms'

    case = {
        "case_id": eval_input.get("case_id") or (f"{scenario_id}-{turn_number}" if scenario_id else query[:8]),
        "query_id": eval_input.get("query_id") or scenario_id,
        "session_id": eval_input.get("session_id"),
        "chat_request_id": eval_input.get("chat_request_id"),
        "query": query,
        "query_type": query_type,
        "eval_type": eval_type,
        "function_category": func_cat,
        "language": language,
        "reasoning": llm.get("reasoning") or "",
        "segment_tags": seg,
        "answer_text": answer,
        "latency_ms": S.round_trip_ms(eval_input),   # e2e 라운드트립(ms) — latency 추적 메인 지표
        "product_count": product_count,
        "previous_turn_queries": eval_input.get("previous_turn_queries") or [],
    }
    if scenario_id:
        case["scenario_id"] = scenario_id
    if turn_number:
        case["turn_number"] = turn_number

    # ─────────────────────────────────────────
    # 0건 케이스
    # ─────────────────────────────────────────
    if product_count == 0:
        zt, src = classify_zero(answer, tools_used)
        alt = detect_altpush(answer) if zt == '검색 결과 없음' else []
        evidence = S.phoenix_evidence(ph, answer)
        case["zero_result_type"] = zt
        case["zero_result"] = {
            "product_count": 0, "zero_result_type": zt, "zero_result_source": src,
            "tools_used": tools_used, "has_alternative_recommendation": bool(alt),
            "alternative_recommendation_evidence": ('「' + answer[:80] + '…」 — ' + '/'.join(alt)) if alt else None,
        }
        case["product_scores"] = []
        case["filter_evaluation"] = {"judgement": llm_fe.get("judgement") or "PASS",
                                     "missing_conditions": llm_fe.get("missing_conditions") or [],
                                     "incorrect_conditions": llm_fe.get("incorrect_conditions") or [],
                                     "reason": llm_fe.get("reason") or ""}
        case["phoenix_checks"] = None
        case["keyword_relevance_check"] = {"result": krc_in.get("result", "해당없음"),
                                           "keywords": krc_in.get("keywords") or [], "reason": krc_in.get("reason") or ""}
        case["answer_length_check"] = S.answer_length_check(answer, language)
        if alt:
            case["has_alternative_recommendation"] = True
            case["evaluation"] = {
                "Rel": 0.0, "Acc": 0.3, "Comp": 0.3, "Score": 0.25, "D_noise_pct": 0.0,
                "verdict": "Fail", "llm_initial_judgement": "Fail", "phoenix_judgement": "Fail",
                "final_judgement": "Fail", "judgement_changed": False, "is_outlier": False,
                "human_review": True, "test_priority": 1,
                "root_cause": ["답변 근거 불일치"], "issue_types": ["대안유도"],
                "issue_detail": "검색 결과 0건인데 답변이 다른 상품을 추천·유도함.",
                "phoenix_evidence": evidence,
            }
            case["summary"] = {"strengths": "없음", "weaknesses": "결과 없음에도 다른 상품 권유",
                               "recommendations": "결과 없음만 안내하도록 수정", "notes": "대안 추천 위반"}
        else:
            case["evaluation"] = {
                "Rel": 0.0, "Acc": 0.3, "Comp": 0.3, "Score": 0.3, "D_noise_pct": 0.0,
                "verdict": "zero_result", "llm_initial_judgement": "zero_result",
                "phoenix_judgement": "zero_result", "final_judgement": "zero_result",
                "judgement_changed": False, "is_outlier": False, "human_review": False,
                "test_priority": "해당없음",
                "issue_types": ["NO_RESULT_VALID" if zt == "검색 결과 없음" else "NONE"],
                "root_cause": ["없음"], "phoenix_evidence": evidence,
            }
            case["summary"] = {"comment_skipped": True}
        return case

    # ─────────────────────────────────────────
    # 상품 있는 케이스
    # ─────────────────────────────────────────
    raw_by_rank = {p.get("rank"): p for p in products if p.get("rank") is not None}
    scored = []
    for ps in (llm.get("product_scores") or [])[:30]:
        rank = ps.get("rank")
        s = int(ps.get("relevance_score", 0))
        raw = raw_by_rank.get(rank, {})
        gate = product_gate(raw, q_origins, q_price, max_per_100g, max_price_abs) if raw else {
            "weight_g": None, "price_per_100g": None, "price_unknown": False,
            "matched_conditions": [], "violated_conditions": []}
        # matched/violated: 코드 게이트 우선, LLM 출력으로 보강
        matched = gate["matched_conditions"] or (ps.get("matched_conditions") or [])
        violated = gate["violated_conditions"] or (ps.get("violated_conditions") or [])
        scored.append({
            "rank": rank,
            "title": raw.get("title") or ps.get("title"),
            "brand": raw.get("brand_name") or raw.get("brand"),
            "image_url": raw.get("cdn_main_url") or raw.get("image_url"),
            "selling_price": to_float(raw.get("selling_price")),
            "currency": raw.get("currency") or "JPY",
            "origin": raw.get("origin"),
            "availability": raw.get("availability"),
            "_g": (raw.get("custom") or {}).get("_g"),
            "relevance_score": s,
            "relevance_label": relevance_label_yamato(s),
            "weight_g": gate["weight_g"],
            "price_per_100g": gate["price_per_100g"],
            "price_unknown": gate["price_unknown"],
            "matched_conditions": matched,
            "violated_conditions": violated,
            "description": ps.get("description"),
            "exposure_reason": ps.get("exposure_reason"),
            "reason": ps.get("reason") or ('; '.join(violated) if violated else ''),
        })

    n = len(scored) or 1
    scores = [p["relevance_score"] for p in scored]
    c_avg = sum(scores) / (4 * n)
    noise_n = sum(1 for s in scores if s <= 1)
    noise_ratio = noise_n / n
    top3 = scored[:3]
    top3_acc = sum(1 for p in top3 if p["relevance_score"] >= 3) / max(len(top3), 1)
    top3_bad = any(p["relevance_score"] <= 1 for p in top3)
    c_label = "HIGH" if c_avg >= S.C_HIGH else ("LOW" if c_avg < S.C_LOW else "MEDIUM")

    # filter_evaluation: LLM 우선, 없으면 코드 폴백
    if llm_fe.get("judgement"):
        fe_j = llm_fe["judgement"]
        fe_missing = llm_fe.get("missing_conditions") or []
        fe_incorrect = llm_fe.get("incorrect_conditions") or []
        fe_reason = llm_fe.get("reason") or ""
    else:
        fe_j, fe_missing = filter_eval_code(tool_input, q_origins, q_price)
        fe_incorrect, fe_reason = [], ""

    # 이슈 분류
    issues = []
    if fe_j in ("PARTIAL", "FAIL"):
        issues.append("FILTER_MISMATCH")
    if any(p["violated_conditions"] for p in scored) and fe_j == "PASS":
        issues.append("RESULT_MISMATCH")

    # ── 100점 score_detail ──
    a_label = llm_eval.get("A_query_intent", "FAIL")
    b_label = llm_eval.get("B_text_quality", "POOR")
    e_label = llm_eval.get("E_diversity", "POOR")
    cond_sc = SC_COND.get(a_label, 8)
    filt_sc = SC_FILTER.get(fe_j, 0)
    result_sc = round((1 - min(noise_ratio, 1)) * SC_RESULT_MAX)
    if seg.get("EXCLUDE"):
        excl_sc = SC_EXCLUDE_FULL if not any(p["violated_conditions"] for p in scored) else 7
    else:
        excl_sc = SC_EXCLUDE_FULL
    comp_sc = SC_COMP.get(b_label, 4)
    total = max(0, min(100, cond_sc + filt_sc + result_sc + excl_sc + comp_sc))
    score_detail = {
        "condition_recognition_score": cond_sc, "filter_conversion_score": filt_sc,
        "result_match_score": result_sc, "exclusion_score": excl_sc,
        "completeness_score": comp_sc, "total_score": total,
    }

    # ── verdict (100점 + top3) ──
    if total >= 90 and not top3_bad:
        verdict = "Hard Pass"
    elif total >= 70:
        verdict = "Conditional Pass"
    else:
        verdict = "Fail"
    initial = {"Hard Pass": "Pass", "Conditional Pass": "Warning", "Fail": "Fail"}[verdict]

    # ── Phoenix 검증 (scoring.py 재사용) ──
    final_lat = S._safe_int(ph.get("final_llm_latency_ms"))
    params_fallback = {"PASS": "OK", "PARTIAL": "PARTIAL", "FAIL": "FAIL"}.get(fe_j)
    checks, log_connected = S.phoenix_checks(
        ph, eval_input, product_count, c_label, krc_in.get("result", "해당없음"),
        llm_ph.get("params_ok") or params_fallback, llm_ph.get("grounding_ok"),
        bool(is_multi), turn_number, llm_eval.get("context_retention"),
    )
    # Phoenix 수집을 의도적으로 끈 경우: '연결 실패'가 아니라 '평가 안 함'으로 처리
    # (scoring.py compute_query 와 동일 정책)
    if eval_input.get("phoenix_skipped"):
        checks = {k: None for k in checks}
        ph_judge = "Phoenix 미수집"
        final = S.final_judgement(verdict, initial, ph_judge, checks, product_count)
        root_cause = S.build_root_cause(checks, True, product_count, b_label, final_lat)
    else:
        ph_judge = S.phoenix_judgement(checks, log_connected, product_count)
        final = S.final_judgement(verdict, initial, ph_judge, checks, product_count)
        root_cause = S.build_root_cause(checks, log_connected, product_count, b_label, final_lat)
    evidence = S.phoenix_evidence(ph, answer)

    # ── 보조 지표(evaluate.py 연속성 유지) ──
    rel = 0.5 + c_avg * 0.3 + (1 - noise_ratio) * 0.2
    acc = round(min(1, total / 100 + 0.05), 2)
    score01 = round(total / 100, 2)
    outlier = S.is_outlier(acc, top3_acc)
    human_review = (initial in ("Warning", "Fail")) or outlier
    priority, priority_reason = S.test_priority(final, acc, outlier)
    changed = S._level(initial) != S._level(final)

    evaluation = {
        "A_query_intent": a_label, "B_text_quality": b_label, "E_diversity": e_label,
        "Rel": round(rel, 2), "Acc": acc, "Comp": 0.8, "Score": score01,
        "score_detail": score_detail, "D_noise_pct": round(noise_ratio, 2),
        "verdict": verdict, "llm_initial_judgement": initial, "phoenix_judgement": ph_judge,
        "final_judgement": final, "judgement_changed": changed,
        "is_outlier": outlier, "human_review": human_review, "test_priority": priority,
        "root_cause": root_cause, "issue_types": issues or ["NONE"],
        "filter_evaluation_judgement": fe_j,
        "issue_detail": ("필터 변환: " + fe_j + (" (누락: " + ", ".join(fe_missing) + ")" if fe_missing else "")) if issues else None,
        "phoenix_evidence": evidence,
    }
    if priority_reason:
        evaluation["priority_reason"] = priority_reason

    is_pass = verdict == "Hard Pass"
    case["filter_evaluation"] = {"judgement": fe_j, "missing_conditions": fe_missing,
                                 "incorrect_conditions": fe_incorrect, "reason": fe_reason}
    case["product_scores"] = scored
    case["top_k_check"] = {"top_3_acc_avg": round(top3_acc, 2), "is_top_k_bad": top3_acc < 0.5}
    case["keyword_relevance_check"] = {
        "result": krc_in.get("result") or ('일치' if c_avg >= 0.75 else ('부분 일치' if c_avg >= 0.5 else '불일치')),
        "keywords": krc_in.get("keywords") or [], "reason": krc_in.get("reason") or ""}
    case["answer_length_check"] = S.answer_length_check(answer, language)
    case["phoenix_checks"] = checks
    case["evaluation"] = evaluation
    case["unevaluated_products"] = eval_input.get("unevaluated_products") or []
    case["summary"] = ({"comment_skipped": True} if is_pass else {
        "strengths": llm_summary.get("strengths") or "검색 결과가 카테고리 의도에 대체로 부합",
        "weaknesses": llm_summary.get("weaknesses") or ('; '.join(sorted({c for p in scored for c in p["violated_conditions"]})) or "경미한 노이즈"),
        "recommendations": llm_summary.get("recommendations") or (("필터 보강: " + ", ".join(fe_missing)) if fe_missing else "노이즈 상품 정제"),
        "notes": llm_summary.get("notes") or "",
    })
    return case


# ═════════════════════════════════════════════════════════════
# data.json 최상위 (meta + kpi + function_breakdown + queries)
# ═════════════════════════════════════════════════════════════
_TYPE_KEYS = ["공통 쿼리", "필터 쿼리 싱글턴", "필터 쿼리 멀티턴"]


def build_data_json_yamato(queries: list[dict], meta_info: dict) -> dict:
    """compute_query_yamato 결과 → 야마토 data.json 최상위."""
    vd = {"hard_pass": 0, "conditional_pass": 0, "warning": 0, "fail": 0, "high_risk": 0, "zero_result": 0}
    counter_q = no_result = alt_push = attention = 0
    tot_prod = disp = 0

    def _type_rec():
        return {"total": 0, "risk": 0, "warning": 0, "clarification_or_no_product": 0,
                "search_no_result": 0, "alternative_push": 0}
    type_breakdown = {k: _type_rec() for k in _TYPE_KEYS}
    fb: dict[str, dict] = {}

    for q in queries:
        ev = q.get("evaluation") or {}
        final = ev.get("final_judgement") or ""
        key = {"Hard Pass": "hard_pass", "Conditional Pass": "conditional_pass",
               "Warning": "warning", "Fail": "fail", "High Risk": "high_risk",
               "zero_result": "zero_result"}.get(final)
        if key:
            vd[key] += 1

        zt = q.get("zero_result_type")
        if zt == "역질문/상품 미반환":
            counter_q += 1
        if zt == "검색 결과 없음" and not q.get("has_alternative_recommendation"):
            no_result += 1
        if "대안유도" in (ev.get("issue_types") or []):
            alt_push += 1
        if ev.get("human_review") or final in ("Warning", "Fail", "High Risk"):
            attention += 1
        tot_prod += int(q.get("product_count") or 0)
        disp += len(q.get("product_scores") or [])

        # type_breakdown
        qt = q.get("query_type")
        if qt in type_breakdown:
            t = type_breakdown[qt]
            t["total"] += 1
            if final in ("Fail", "High Risk"):
                t["risk"] += 1
            elif final == "Warning":
                t["warning"] += 1
            if zt == "역질문/상품 미반환":
                t["clarification_or_no_product"] += 1
            if zt == "검색 결과 없음":
                t["search_no_result"] += 1
            if "대안유도" in (ev.get("issue_types") or []):
                t["alternative_push"] += 1

        # function_breakdown
        fc = q.get("function_category") or "미분류"
        rec = fb.setdefault(fc, {"name": fc, "total": 0, "fail": 0, "pass": 0, "issue": 0, "issue_types": {}})
        rec["total"] += 1
        if final in ("Fail", "High Risk"):
            rec["fail"] += 1
        elif final.lower().startswith("hard") or final == "Conditional Pass":
            rec["pass"] += 1
        its = [t for t in (ev.get("issue_types") or []) if t not in ("NONE", "없음")]
        if its:
            rec["issue"] += 1
        for t in its:
            rec["issue_types"][t] = rec["issue_types"].get(t, 0) + 1

    function_breakdown = sorted(fb.values(), key=lambda r: (-r["fail"], -r["issue"], -r["total"]))

    meta = {
        "dataset": meta_info.get("dataset", "YAMATO"),
        "report_title": meta_info.get("report_title", "Yamato 검색 품질 평가 결과"),
        "subtitle": meta_info.get("subtitle", f"v3 통합 판정 (LLM × Phoenix) · 전체 {len(queries)}건"),
        "generated_at": meta_info.get("generated_at", ""),
        "label": meta_info.get("label", "라벨링 없음"),
        "prompt_file": meta_info.get("prompt_file", ""),
        "evaluator_version": "v3",
        "total_queries": len(queries),
        "total_product_count": tot_prod,
        "display_product_count": disp,
    }
    kpi = {
        "verdict_distribution": vd,
        "counter_question_count": counter_q,
        "no_result_count": no_result,
        "alternative_push_count": alt_push,
        "attention_queries": attention,
        "type_breakdown": type_breakdown,
    }
    return {"meta": meta, "kpi": kpi, "function_breakdown": function_breakdown, "queries": queries}
