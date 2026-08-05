# -*- coding: utf-8 -*-
"""
STG-YAMATO 평가기 — prompt.md(야마토 v3) 기준 구현.
싱글턴/멀티턴 CSV를 읽어 {meta, kpi, queries} 스키마의 data.json을 생성한다.

- 0건 분류(역질문/검색 결과 없음), 대안유도 탐지, 필터 변환 정합성,
  가격·원산지 게이트, Phoenix 검증, 100점 판정을 md 규칙대로 적용.
- 상품별 relevance는 origin/price/키워드 일치 휴리스틱으로 산출(상위 30위).
"""
import csv, json, re, os, datetime

DL = os.path.expanduser('~/Downloads')
SINGLE = os.path.join(DL, 'PROD-YAMATO-260604 - 싱글턴-prod-260604-qaid35.csv')
MULTI  = os.path.join(DL, 'PROD-YAMATO-260604 - 멀티턴-prod-260604-qaid35.csv')

# ---------- 일본 광역 산지 + 동치 ----------
PREFECTURES = ['北海道','青森','岩手','宮城','秋田','山形','福島','茨城','栃木','群馬','埼玉','千葉','東京','神奈川',
 '新潟','富山','石川','福井','山梨','長野','岐阜','静岡','愛知','三重','滋賀','京都','大阪','兵庫','奈良','和歌山',
 '鳥取','島根','岡山','広島','山口','徳島','香川','愛媛','高知','福岡','佐賀','長崎','熊本','大分','宮崎','鹿児島','沖縄']
REGION_MAP = {'魚沼':'新潟','北見':'北海道','オホーツク':'北海道','知床':'北海道','十勝':'北海道','信州':'長野',
 '讃岐':'香川','近江':'滋賀','多摩':'東京','石巻':'宮城'}

# ---------- 대안유도(대안 추천 위반) 패턴 ----------
# 권유형(추천) 표현만 — 거절/역질문 오탐 방지를 위해 동작 표현으로 한정
ALT_PATTERNS = ['代わりに','かわりに','いかがでしょうか','いかがですか','おすすめいたします',
 'おすすめします','お勧めします','をご提案します','はどうでしょう','代替商品をご提案',
 '別の商品をおすすめ','こちらもおすすめ','もおすすめです']
# 거절/불가 표현이 함께 있으면 대안유도 아님(권유가 아니라 거절)
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
    # 멀티턴 検索基準은 이미 한국어 — 그대로 통과
}
def func_ko(v):
    if not v: return v
    return FUNC_KO.get(v.strip(), v.strip())

def jload(s, default=None):
    if not s: return default
    try: return json.loads(s)
    except Exception: return default

def detect_cols(fieldnames):
    """타임스탬프 접미사가 붙은 컬럼명을 prefix로 매핑."""
    m = {}
    for fn in fieldnames:
        base = re.sub(r'_2026-06-\d{2}_\d{2}:\d{2}$','',fn)
        m[base] = fn
    return m

def extract_origin(text):
    if not text: return []
    found = []
    if '国産' in text: found.append('国産')
    for r,p in REGION_MAP.items():
        if r in text: found.append(p)
    for p in PREFECTURES:
        # 年産 오탐 방지: 산지명 자체는 연도와 무관
        if p in text: found.append(p)
    if '瀬戸内' in text: found.append('瀬戸内')
    return list(dict.fromkeys(found))

def norm_origin(o):
    if not o: return ''
    o = re.sub(r'(県|府|都|産)$','',o)
    return o

def query_origin(query):
    """쿼리에서 요구 산지 추출(연도표기 제외)."""
    q = re.sub(r'(令和\d+年産|R\d+年産|\d{4}年産|\d+年産)','',query or '')
    return extract_origin(q)

PRICE_RE = re.compile(r'(\d[\d,]*)\s*円(以内|以下|まで|前後|台|以上)?')
def query_price(query):
    if not query: return None
    m = PRICE_RE.search(query)
    if m:
        val = int(m.group(1).replace(',',''))
        kind = m.group(2) or ''
        if kind in ('以内','以下','まで','台',''):
            return {'op':'<=','val':val,'raw':m.group(0)}
        if kind=='以上':
            return {'op':'>=','val':val,'raw':m.group(0)}
        if kind=='前後':
            return {'op':'~','val':val,'raw':m.group(0)}
    if any(k in query for k in ['高価格','高級']):
        return {'op':'high','val':None,'raw':'高価格帯'}
    if any(k in query for k in ['安い','低単価','単価の低い','格安']):
        return {'op':'low','val':None,'raw':'低価格'}
    return None

# 1식(1인분) 표준 중량 가정 — 일본 공식 기준(후생노동성·농림수산성 식사밸런스가이드).
# 카레라이스 예시 ごはん200g·肉約60g·野菜140~150g (mhlw.go.jp / maff.go.jp).
# 카테고리별로 1식 중량이 다르므로 분류해서 적용한다.
SERVING_G_MAIN = 60     # 主菜: 고기·생선 1인분 약 60g
SERVING_G_VEG  = 140    # 副菜: 채소·버섯·해조 1식 약 140g
SERVING_G_STAPLE = 200  # 主食: 밥·면·곡물 1식 약 200g
SERVING_G_DEFAULT = SERVING_G_MAIN  # 혼합·불명은 主菜 기준(보수적)

def serving_g_for(category, query):
    """카테고리/쿼리로 1식 중량(g) 결정. 채소 140 / 곡물 200 / 主菜(고기·생선) 60."""
    text = (category or '') + ' ' + (query or '')
    if re.search(r'野菜|青果|葉茎|根菜|きのこ|キノコ|茸|海藻|いも類|いも|芋', text):
        return SERVING_G_VEG
    if re.search(r'米|麦|穀物|麺|めん|パン|ごはん|ご飯|白米|玄米', text):
        return SERVING_G_STAPLE
    if re.search(r'肉|牛|豚|鶏|精肉|魚|鮮魚|水産|刺身|切り身|甲殻|エビ|海老|カニ', text):
        return SERVING_G_MAIN
    return SERVING_G_DEFAULT

PER_SERVING_RE = re.compile(r'(\d[\d,]*)\s*円')
def per_serving_threshold(query, serving_g):
    """'N円/食'·'一人前N円' 등 per-serving 가격 임계값을 100g당 임계값으로 환산."""
    if not query: return None
    if not re.search(r'(/?\s*食|一人前|人前|/\s*人)', query): return None
    m = PER_SERVING_RE.search(query)
    if not m: return None
    yen = int(m.group(1).replace(',', ''))
    # 1식 ≈ serving_g 가정 → per-100g = yen × 100 / serving_g
    return round(yen * 100.0 / serving_g)

WEIGHT_RE = re.compile(r'(\d+(?:[.,]\d+)?)\s*(kg|ｋｇ|キロ|kｇ|g|ｇ|グラム|gr)', re.I)
def parse_weight_g(title):
    """상품명에서 무게(g) 추출. kg→g 환산. 없으면 None."""
    if not title: return None
    best=None
    for m in WEIGHT_RE.finditer(title):
        val=float(m.group(1).replace(',', '.')) if m.group(1).count(',')==1 and '.' not in m.group(1) else float(m.group(1).replace(',', ''))
        unit=m.group(2).lower()
        g = val*1000 if unit in ('kg','ｋｇ','キロ','kｇ') else val
        # 가장 큰 단위(주 규격)를 우선
        if best is None or g>best: best=g
    return best

def price_per_100g(price, grams):
    if not price or not grams or grams<=0: return None
    return price*100.0/grams

def to_int(v, d=0):
    try: return int(float(v))
    except Exception: return d
def to_float(v, d=None):
    try: return float(v)
    except Exception: return d

def classify_zero(answer, tools_used):
    """역질문/상품 미반환 vs 검색 결과 없음."""
    tu = tools_used or []
    if isinstance(tu, str): tu = jload(tu, [])
    has_search = bool(tu)
    a = answer or ''
    if has_search:
        return '검색 결과 없음', 'json.tools_used'
    # tools_used == [] → 역질문 우선, 단 명시적 부재 표현이 강하면 검색 결과 없음
    if any(p in a for p in NORESULT_PATTERNS) and not any(p in a for p in ASKBACK_PATTERNS):
        return '검색 결과 없음', 'answer_text_fallback'
    return '역질문/상품 미반환', 'answer_text_fallback'

def detect_altpush(answer):
    a = answer or ''
    hits = [p for p in ALT_PATTERNS if p in a]
    if not hits:
        return []
    # 거절·불가 안내가 답변에 있으면 권유가 아니라 거절 → 위반 아님
    if any(neg in a for neg in ALT_NEG):
        return []
    return hits

def eval_products(products, q_origins, q_price, max_per_100g=None, max_price_abs=None):
    """상위 30위 relevance 휴리스틱. (적합4/3, 애매2, 유해0)
    max_per_100g: tool_input의 max_price_per_100g(100g당 상한). 있으면 절대가 대신 이걸로 판정.
    max_price_abs: tool_input의 max_price(절대 상한)."""
    top = products[:30]
    scored = []
    q_norm = [norm_origin(o) for o in q_origins]
    for i,p in enumerate(top):
        title = p.get('title') or ''
        origin = p.get('origin')
        price = to_float(p.get('selling_price'))
        grams = parse_weight_g(title)
        p100 = price_per_100g(price, grams)
        violated = []
        matched = []
        price_unknown = False
        rs = 3  # 검색이 반환한 카테고리 상품 → 기본 관련
        # 원산지 게이트
        if q_norm:
            src = origin if origin else None
            name_origins = extract_origin(title)
            cand = []
            if src: cand += extract_origin(src) or [src]
            cand += name_origins
            GENERIC = ('国産', '国')   # 일본 내 generic — 특정 광역 아님
            cand_has_generic = any(x == '国産' for x in cand)
            cand_specific = [norm_origin(x) for x in cand if x != '国産' and norm_origin(x) not in GENERIC]
            q_specific = [c for c in q_norm if c not in GENERIC]
            q_generic = ('国産' in q_origins)
            if q_specific:
                # 특정 광역(예: 大阪)을 요구
                if any(c in q_specific for c in cand_specific):
                    matched.append('원산지'); rs = 4              # MATCH
                elif cand_specific:
                    violated.append('원산지 조건 위반'); rs = 0     # 다른 특정 광역 명시 → MISMATCH
                # 国産(generic)뿐이거나 산지 불명 → UNKNOWN(채점 제외): 大阪일 수도 있음
            elif q_generic:
                # 国産(일본 내) 요구 → 일본 광역/국산이면 충족
                if cand_specific or cand_has_generic:
                    matched.append('원산지'); rs = 4
                # 산지 불명 → UNKNOWN
        # 가격 게이트 — 우선순위: 100g당 단가 > 절대 상한 > 쿼리 단순값
        if max_per_100g is not None:
            if price is None:
                price_unknown = True
            elif grams is None:
                price_unknown = True   # 무게 미상 → 100g당 계산 불가(UNKNOWN, 채점 제외)
            elif p100 is not None:
                if p100 > max_per_100g:
                    violated.append(f'100g당 단가 위반(¥{p100:.0f}/100g > ¥{max_per_100g})'); rs = 0
                else:
                    matched.append(f'100g당 ¥{p100:.0f} ≤ ¥{max_per_100g}')
        elif max_price_abs is not None and price is not None:
            if price > max_price_abs:
                violated.append(f'가격 상한 위반(¥{price:.0f} > ¥{max_price_abs})'); rs = 0
            else:
                matched.append('가격')
        elif q_price and price is not None and q_price.get('val'):
            if q_price['op']=='<=' and price > q_price['val']:
                violated.append('가격 조건 위반'); rs = 0
            elif q_price['op']=='>=' and price < q_price['val']:
                violated.append('가격 조건 위반'); rs = 0
            elif q_price['op']=='<=' and price <= q_price['val']:
                matched.append('가격')
        label = '적합' if rs>=3 else ('애매' if rs==2 else '유해')
        scored.append({
            'rank': i+1,
            'title': title,
            'brand': p.get('brand_name'),
            'image_url': p.get('cdn_main_url'),
            'selling_price': price,
            'currency': p.get('currency') or 'JPY',
            'origin': origin,
            'availability': p.get('availability'),
            'relevance_score': rs,
            'relevance_label': label,
            'weight_g': grams,
            'price_per_100g': round(p100,1) if p100 is not None else None,
            'price_unknown': price_unknown,
            'matched_conditions': matched,
            'violated_conditions': violated,
            'reason': ('; '.join(violated) if violated else '')
        })
    return scored

def filter_eval(tool_input, q_origins, q_price):
    """검색 조건 반영 여부 → PASS/PARTIAL/FAIL."""
    ti = tool_input if isinstance(tool_input, dict) else jload(tool_input, {}) or {}
    blob = json.dumps(ti, ensure_ascii=False)
    missing = []
    if q_origins:
        if not any(norm_origin(o) in blob or o in blob or '国産' in blob for o in q_origins):
            # origin 필터 또는 키워드에 산지 반영 안 됨
            missing.append('원산지')
    if q_price and q_price.get('val'):
        # 가격 필터 키 존재 여부
        if not re.search(r'price', blob, re.I):
            missing.append('가격')
    if not q_origins and not q_price:
        return 'PASS', []
    if not missing:
        return 'PASS', []
    if len(missing) >= (len(['o' for _ in [1] if q_origins]) + (1 if q_price else 0)):
        return ('PARTIAL' if len(missing)==1 else 'FAIL'), missing
    return 'PARTIAL', missing

def build_case(row, cols, eval_type, prev_queries=None, scenario=None, turn=None):
    g = lambda k: row.get(cols.get(k,''),'') if cols.get(k) else ''
    query = g('検索クエリ')
    answer = g('answer_text')
    pcount = to_int(g('product_count'), 0)
    products = jload(g('response_text_1'), []) or []
    tools_used = jload(g('phoenix_tools_used'), [])
    tool_input = jload(g('phoenix_tool_input'), {})
    tool_output = g('phoenix_tool_output')
    total_count = to_int(g('phoenix_total_count'), pcount)
    tool_name = g('phoenix_tool_name')
    trace_id = g('phoenix_trace_id')
    tlat = g('phoenix_tool_latency_ms'); flat = g('phoenix_final_llm_latency_ms')
    sess = g('session_id'); crid = g('chat_request_id')

    func_cat = func_ko(g('類型') or g('検索基準') or None)  # 기능분류 (싱글턴 類型 / 멀티턴 検索基準) → 한국어

    ti = tool_input if isinstance(tool_input, dict) else {}
    max_per_100g = ti.get('max_price_per_100g')
    max_price_abs = ti.get('max_price')
    q_origins = query_origin(query)
    q_price = query_price(query)
    # per-serving(円/食·一人前) 쿼리: 카테고리별 1식 중량 가정으로 100g당 임계값 환산
    serving_note = None
    cat_for_serving = ti.get('category_path') or ti.get('category_paths') or query
    serving_g = serving_g_for(cat_for_serving, query)
    ps_thr = per_serving_threshold(query, serving_g)
    if ps_thr is not None:
        max_per_100g = ps_thr  # 쿼리 의도(円/食) 기반 임계값을 우선 사용
        cat_label = '채소' if serving_g==SERVING_G_VEG else ('곡물' if serving_g==SERVING_G_STAPLE else '主菜(고기·생선)')
        serving_note = f'per-serving(円/食) → {cat_label} 1식 {serving_g}g 가정으로 ¥{ps_thr}/100g 환산 평가'
    # 단위가격(円/kg, キロ…円, /100g) 표현인데 정규화 파라미터가 없으면 절대가 비교 부정확 → 가격 채점 제외(UNKNOWN)
    per_unit = bool(re.search(r'(/?\s*kg|キロ|100\s*g|円/kg|/\s*100g)', query or ''))
    if per_unit and max_per_100g is None and max_price_abs is None:
        q_price = None

    # PRICE 세그먼트: tool_input의 정규화 파라미터 우선 표기
    if max_per_100g is not None:
        price_tag = f'max_price_per_100g ≤ ¥{max_per_100g}/100g' + (f' ({serving_note})' if serving_note else '')
    elif max_price_abs is not None:
        price_tag = f'max_price ≤ ¥{max_price_abs}'
    elif q_price:
        price_tag = q_price['raw']
    else:
        price_tag = None

    seg = {
        'ORIGIN': '・'.join(q_origins) if q_origins else (ti.get('origin') or None),
        'PRICE': price_tag,
        'PRICE_FILTER': (f'max_price_per_100g <= {max_per_100g}' if max_per_100g is not None
                         else (f'max_price <= {max_price_abs}' if max_price_abs is not None else None)),
        'CATEGORY': ti.get('category_path') or ti.get('category_paths'),
        'INTENT': 'filter_search' if (q_origins or q_price or max_per_100g is not None or max_price_abs is not None) else 'recommend'
    }

    latency_summary = ''
    if tlat or flat:
        latency_summary = f'tool {tlat}ms / final LLM {flat}ms'

    case = {
        'case_id': (scenario+'-'+str(turn)) if scenario else g('シナリオID') or query[:8],
        'query_id': g('シナリオID'),
        'session_id': sess, 'chat_request_id': crid,
        'query': query, 'eval_type': eval_type,
        'function_category': func_cat,
        'language': 'ja',
        'segment_tags': {k:v for k,v in seg.items()},
        'answer_text': answer,
        'product_count': pcount,
        'previous_turn_queries': prev_queries or [],
    }
    if scenario: case['scenario_id'] = scenario
    if turn: case['turn_number'] = turn

    # ---------- 0건 케이스 ----------
    if pcount == 0:
        zt, src = classify_zero(answer, tools_used)
        # 역질문/상품 미반환은 대안유도 검증·집계에서 제외 (검색 결과 없음 케이스만 대상)
        alt = detect_altpush(answer) if zt == '검색 결과 없음' else []
        ev = {'Rel':0,'Acc':0.3,'Comp':0.3,'root_cause':[],'issue_types':[]}
        case['zero_result_type'] = zt
        case['zero_result'] = {'product_count':0,'zero_result_type':zt,'zero_result_source':src,
            'tools_used':tools_used,'has_alternative_recommendation':bool(alt),
            'alternative_recommendation_evidence': ('「'+answer[:80]+'…」 — '+'/'.join(alt)) if alt else None}
        case['product_scores'] = []
        if alt:
            ev.update({'verdict':'Fail','llm_initial_judgement':'Fail','phoenix_judgement':'Fail',
                'final_judgement':'Fail','judgement_changed':False,'is_outlier':False,'human_review':True,
                'test_priority':1,'Score':0.25,'Acc':0.3,'Comp':0.3,
                'root_cause':['답변 근거 불일치'],'issue_types':['대안유도'],
                'issue_detail':'검색 결과 0건인데 답변이 다른 상품을 추천·유도함.'})
            case['has_alternative_recommendation'] = True
        else:
            ev.update({'verdict':'zero_result','llm_initial_judgement':'zero_result',
                'phoenix_judgement':None,'final_judgement':'zero_result','judgement_changed':False,
                'is_outlier':False,'human_review':False,
                'issue_types':['NO_RESULT_VALID' if zt=='검색 결과 없음' else 'NONE'],
                'root_cause':['없음']})
        ev['phoenix_evidence'] = {'tool_name':tool_name or '-','tool_input_summary':json.dumps(tool_input,ensure_ascii=False)[:160] if tool_input else '-',
            'total_count':total_count,'tool_output_summary':'상품 0건','llm_response_summary':answer[:60],'latency_summary':latency_summary}
        case['evaluation'] = ev
        case['phoenix_checks'] = None
        case['summary'] = ({'strengths':'없음','weaknesses':'결과 없음에도 다른 상품 권유','recommendations':'결과 없음만 안내하도록 수정','notes':'대안 추천 위반'} if alt
            else {'comment_skipped':True})
        return case

    # ---------- 상품 있는 케이스 ----------
    scored = eval_products(products, q_origins, q_price, max_per_100g=max_per_100g, max_price_abs=max_price_abs)
    n = len(scored) or 1
    viol = [s for s in scored if s['violated_conditions']]
    noise_ratio = len(viol)/n
    c_avg = sum(s['relevance_score'] for s in scored)/ (4*n)
    top3 = scored[:3]
    top3_bad = any(s['violated_conditions'] for s in top3)
    top3_acc = sum(min(s['relevance_score'],4) for s in top3)/(4*max(len(top3),1))

    fe_j, fe_missing = filter_eval(tool_input, q_origins, q_price)

    issues = []
    if fe_j in ('PARTIAL','FAIL'): issues.append('FILTER_MISMATCH')
    if viol and fe_j=='PASS': issues.append('RESULT_MISMATCH')

    # 100점 근사
    score100 = 100
    if fe_j=='FAIL': score100 -= 30
    elif fe_j=='PARTIAL': score100 -= 12
    score100 -= min(noise_ratio,1)*40
    if top3_bad: score100 -= 10
    score100 = max(0, round(score100))

    if score100>=90 and not top3_bad: verdict='Hard Pass'; fj='Hard Pass'; llm='Pass'
    elif score100>=70: verdict='Conditional Pass'; fj='Conditional Pass'; llm='Warning'
    else: verdict='Fail'; fj='Fail'; llm='Fail'
    # Warning 표기 통일(Conditional Pass는 Warning 1차)
    is_outlier = top3_acc < 0.5
    human_review = (llm in ('Warning','Fail')) or is_outlier

    # Phoenix (Warning/Fail만)
    pchecks=None; root=['없음']; phoenix_j=None; changed=False
    if llm in ('Warning','Fail'):
        params_ok = 'OK' if fe_j=='PASS' else ('PARTIAL' if fe_j=='PARTIAL' else 'FAIL')
        retrieval_ok = 'OK' if noise_ratio<0.1 else ('PARTIAL' if noise_ratio<=0.3 else 'FAIL')
        count_ok = 'OK' if abs(total_count - pcount) <= max(5, pcount*0.5) else 'PARTIAL'
        pchecks={'mapping_ok':'OK' if trace_id else 'FAIL','tool_call_ok':'OK' if tools_used else 'FAIL',
            'params_ok':params_ok,'count_ok':count_ok,'retrieval_ok':retrieval_ok,
            'grounding_ok':'OK','context_ok':None}
        rc=[]
        if params_ok in ('FAIL','PARTIAL'): rc.append('검색 조건 문제')
        if retrieval_ok in ('FAIL','PARTIAL'): rc.append('검색 결과 부적합')
        root = rc or ['없음']
        crit = any(pchecks[k]=='FAIL' for k in ('params_ok','retrieval_ok','grounding_ok'))
        phoenix_j = 'Fail' if crit else ('Warning' if any(v=='PARTIAL' for v in pchecks.values() if v) else 'Pass')

    rel = 0.5 + c_avg*0.3 + (1-noise_ratio)*0.2
    ev = {'Rel':round(rel,2),'Acc':round(min(1,score100/100+0.05),2),'Comp':0.8,
        'Score':round(score100/100,2),'verdict':verdict,'llm_initial_judgement':llm,
        'phoenix_judgement':phoenix_j if phoenix_j else '-','final_judgement':fj,
        'judgement_changed':changed,'is_outlier':is_outlier,'human_review':human_review,
        'test_priority': 1 if (is_outlier and human_review) else (3 if is_outlier else (4 if issues else None)),
        'root_cause':root,'issue_types':issues or ['NONE'],
        'D_noise_pct':round(noise_ratio,2),
        'filter_evaluation_judgement':fe_j,
        'issue_detail': ('필터 변환: '+fe_j+(' (누락: '+', '.join(fe_missing)+')' if fe_missing else '')) if issues else None,
        'phoenix_evidence':{'tool_name':tool_name or '-',
            'tool_input_summary':json.dumps(tool_input,ensure_ascii=False)[:180] if tool_input else '-',
            'total_count':total_count,'tool_output_summary':f'returned {len(products)}건 / total {total_count}',
            'llm_response_summary':answer[:60],'latency_summary':latency_summary}}
    case['evaluation']=ev
    case['filter_evaluation']={'judgement':fe_j,'missing_conditions':fe_missing,'incorrect_conditions':[],'reason':''}
    case['phoenix_checks']=pchecks
    case['product_scores']=scored
    case['top_k_check']={'top_3_acc_avg':round(top3_acc,2),'is_top_k_bad':top3_bad}
    case['keyword_relevance_check']={'result':'일치' if c_avg>=0.75 else ('부분 일치' if c_avg>=0.5 else '불일치'),
        'keywords': jload(g('keywords'),[]) or [], 'reason':''}
    case['answer_length_check']={'language':'ja','char_count':len(answer or ''),
        'result':'충분' if len(answer or '')>=80 else '보통'}
    if pcount>30:
        case['unevaluated_products']=[{'rank':31+i,'title':p.get('title'),'brand_name':p.get('brand_name'),
            'selling_price':to_float(p.get('selling_price')),'currency':p.get('currency') or 'JPY',
            'origin':p.get('origin'),'cdn_main_url':p.get('cdn_main_url')} for i,p in enumerate(products[30:])]
    isPass = verdict.lower().startswith('hard')
    case['summary']=({'comment_skipped':True} if isPass else
        {'strengths':'검색 결과가 카테고리 의도에 대체로 부합','weaknesses':('; '.join(set(sum([s['violated_conditions'] for s in viol],[]))) or '경미한 노이즈'),
         'recommendations':('필터 보강: '+', '.join(fe_missing)) if fe_missing else '노이즈 상품 정제','notes':''})
    return case

def load(name, eval_type):
    with open(name, encoding='utf-8') as f:
        rows=list(csv.DictReader(f))
        cols=detect_cols(rows[0].keys())
    return rows, cols

def main():
    queries=[]
    # 싱글턴
    rows,cols=load(SINGLE,'싱글턴')
    for row in rows:
        if not (row.get(cols.get('検索クエリ','')) or '').strip(): continue
        queries.append(build_case(row,cols,'싱글턴'))
    # 멀티턴 (시나리오별 이전 턴 누적)
    rows,cols=load(MULTI,'멀티턴')
    prev={}
    for row in rows:
        q=row.get(cols.get('検索クエリ','')) or ''
        if not q.strip(): continue
        scen=row.get(cols.get('シナリオID',''))
        turn_raw=row.get(cols.get('ターン','')) or ''
        tn=to_int(re.sub(r'\D','',turn_raw),0)
        pq=prev.get(scen,[])[:]
        case=build_case(row,cols,'멀티턴',prev_queries=pq,scenario=scen,turn=tn)
        queries.append(case)
        prev.setdefault(scen,[]).append(q)

    # KPI
    vd={'hard_pass':0,'conditional_pass':0,'warning':0,'fail':0,'high_risk':0,'zero_result':0}
    cq=nr=alt=att=0
    tot_prod=disp=0
    for q in queries:
        fj=(q['evaluation'].get('final_judgement') or '')
        if fj=='Hard Pass': vd['hard_pass']+=1
        elif fj=='Conditional Pass': vd['conditional_pass']+=1
        elif fj=='Warning': vd['warning']+=1
        elif fj=='Fail': vd['fail']+=1
        elif fj=='High Risk': vd['high_risk']+=1
        elif fj=='zero_result': vd['zero_result']+=1
        zt=q.get('zero_result_type')
        if zt=='역질문/상품 미반환': cq+=1
        if zt=='검색 결과 없음' and not q.get('has_alternative_recommendation'): nr+=1
        if '대안유도' in (q['evaluation'].get('issue_types') or []): alt+=1
        if q['evaluation'].get('human_review'): att+=1
        tot_prod += q.get('product_count',0)
        disp += len(q.get('product_scores',[]))

    # 기능분류별 집계 (이슈 추적)
    fb = {}
    for q in queries:
        fc = q.get('function_category') or '미분류'
        ev = q['evaluation']
        rec = fb.setdefault(fc, {'name':fc,'total':0,'fail':0,'pass':0,'issue':0,'issue_types':{}})
        rec['total'] += 1
        fj = ev.get('final_judgement') or ''
        if fj in ('Fail','High Risk'): rec['fail'] += 1
        elif fj.lower().startswith('hard') or fj=='Conditional Pass': rec['pass'] += 1
        its = [t for t in (ev.get('issue_types') or []) if t != 'NONE']
        if its: rec['issue'] += 1
        for t in its:
            rec['issue_types'][t] = rec['issue_types'].get(t,0)+1
    function_breakdown = sorted(fb.values(), key=lambda r:(-r['fail'], -r['issue'], -r['total']))

    data={
      'meta':{'dataset':'PROD-YAMATO-260604','report_title':'Yamato 검색 품질 평가 결과',
        'subtitle':f'v3 통합 판정 (LLM × Phoenix) · 싱글턴+멀티턴 {len(queries)}건 · 규칙 기반 자동 평가',
        'generated_at':datetime.date.today().strftime('%Y.%m.%d'),'evaluator_version':'v3',
        'total_queries':len(queries),'total_product_count':tot_prod,'display_product_count':disp},
      'kpi':{'verdict_distribution':vd,'counter_question_count':cq,'no_result_count':nr,
        'alternative_push_count':alt,'attention_queries':att},
      'function_breakdown':function_breakdown,
      'queries':queries
    }
    out=os.path.join(os.path.dirname(__file__),'data.json')
    with open(out,'w',encoding='utf-8') as f:
        json.dump(data,f,ensure_ascii=False,indent=1)
    print('cases:',len(queries))
    print('verdict:',vd,'altpush:',alt,'askback:',cq,'noresult:',nr)

if __name__=='__main__':
    main()
# -*- coding: utf-8 -*-
"""
STG-YAMATO 평가기 — prompt.md(야마토 v3) 기준 구현.
싱글턴/멀티턴 CSV를 읽어 {meta, kpi, queries} 스키마의 data.json을 생성한다.

- 0건 분류(역질문/검색 결과 없음), 대안유도 탐지, 필터 변환 정합성,
  가격·원산지 게이트, Phoenix 검증, 100점 판정을 md 규칙대로 적용.
- 상품별 relevance는 origin/price/키워드 일치 휴리스틱으로 산출(상위 30위).
"""
import csv, json, re, os, datetime

DL = os.path.expanduser('~/Downloads')
SINGLE = os.path.join(DL, 'PROD-YAMATO-260604 - 싱글턴-prod-260604-qaid35.csv')
MULTI  = os.path.join(DL, 'PROD-YAMATO-260604 - 멀티턴-prod-260604-qaid35.csv')

# ---------- 일본 광역 산지 + 동치 ----------
PREFECTURES = ['北海道','青森','岩手','宮城','秋田','山形','福島','茨城','栃木','群馬','埼玉','千葉','東京','神奈川',
 '新潟','富山','石川','福井','山梨','長野','岐阜','静岡','愛知','三重','滋賀','京都','大阪','兵庫','奈良','和歌山',
 '鳥取','島根','岡山','広島','山口','徳島','香川','愛媛','高知','福岡','佐賀','長崎','熊本','大分','宮崎','鹿児島','沖縄']
REGION_MAP = {'魚沼':'新潟','北見':'北海道','オホーツク':'北海道','知床':'北海道','十勝':'北海道','信州':'長野',
 '讃岐':'香川','近江':'滋賀','多摩':'東京','石巻':'宮城'}

# ---------- 대안유도(대안 추천 위반) 패턴 ----------
# 권유형(추천) 표현만 — 거절/역질문 오탐 방지를 위해 동작 표현으로 한정
ALT_PATTERNS = ['代わりに','かわりに','いかがでしょうか','いかがですか','おすすめいたします',
 'おすすめします','お勧めします','をご提案します','はどうでしょう','代替商品をご提案',
 '別の商品をおすすめ','こちらもおすすめ','もおすすめです']
# 거절/불가 표현이 함께 있으면 대안유도 아님(권유가 아니라 거절)
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
    # 멀티턴 検索基準은 이미 한국어 — 그대로 통과
}
def func_ko(v):
    if not v: return v
    return FUNC_KO.get(v.strip(), v.strip())

def jload(s, default=None):
    if not s: return default
    try: return json.loads(s)
    except Exception: return default

def detect_cols(fieldnames):
    """타임스탬프 접미사가 붙은 컬럼명을 prefix로 매핑."""
    m = {}
    for fn in fieldnames:
        base = re.sub(r'_2026-06-\d{2}_\d{2}:\d{2}$','',fn)
        m[base] = fn
    return m

def extract_origin(text):
    if not text: return []
    found = []
    if '国産' in text: found.append('国産')
    for r,p in REGION_MAP.items():
        if r in text: found.append(p)
    for p in PREFECTURES:
        # 年産 오탐 방지: 산지명 자체는 연도와 무관
        if p in text: found.append(p)
    if '瀬戸内' in text: found.append('瀬戸内')
    return list(dict.fromkeys(found))

def norm_origin(o):
    if not o: return ''
    o = re.sub(r'(県|府|都|産)$','',o)
    return o

def query_origin(query):
    """쿼리에서 요구 산지 추출(연도표기 제외)."""
    q = re.sub(r'(令和\d+年産|R\d+年産|\d{4}年産|\d+年産)','',query or '')
    return extract_origin(q)

PRICE_RE = re.compile(r'(\d[\d,]*)\s*円(以内|以下|まで|前後|台|以上)?')
def query_price(query):
    if not query: return None
    m = PRICE_RE.search(query)
    if m:
        val = int(m.group(1).replace(',',''))
        kind = m.group(2) or ''
        if kind in ('以内','以下','まで','台',''):
            return {'op':'<=','val':val,'raw':m.group(0)}
        if kind=='以上':
            return {'op':'>=','val':val,'raw':m.group(0)}
        if kind=='前後':
            return {'op':'~','val':val,'raw':m.group(0)}
    if any(k in query for k in ['高価格','高級']):
        return {'op':'high','val':None,'raw':'高価格帯'}
    if any(k in query for k in ['安い','低単価','単価の低い','格安']):
        return {'op':'low','val':None,'raw':'低価格'}
    return None

# 1식(1인분) 표준 중량 가정 — 일본 공식 기준(후생노동성·농림수산성 식사밸런스가이드).
# 카레라이스 예시 ごはん200g·肉約60g·野菜140~150g (mhlw.go.jp / maff.go.jp).
# 카테고리별로 1식 중량이 다르므로 분류해서 적용한다.
SERVING_G_MAIN = 60     # 主菜: 고기·생선 1인분 약 60g
SERVING_G_VEG  = 140    # 副菜: 채소·버섯·해조 1식 약 140g
SERVING_G_STAPLE = 200  # 主食: 밥·면·곡물 1식 약 200g
SERVING_G_DEFAULT = SERVING_G_MAIN  # 혼합·불명은 主菜 기준(보수적)

def serving_g_for(category, query):
    """카테고리/쿼리로 1식 중량(g) 결정. 채소 140 / 곡물 200 / 主菜(고기·생선) 60."""
    text = (category or '') + ' ' + (query or '')
    if re.search(r'野菜|青果|葉茎|根菜|きのこ|キノコ|茸|海藻|いも類|いも|芋', text):
        return SERVING_G_VEG
    if re.search(r'米|麦|穀物|麺|めん|パン|ごはん|ご飯|白米|玄米', text):
        return SERVING_G_STAPLE
    if re.search(r'肉|牛|豚|鶏|精肉|魚|鮮魚|水産|刺身|切り身|甲殻|エビ|海老|カニ', text):
        return SERVING_G_MAIN
    return SERVING_G_DEFAULT

PER_SERVING_RE = re.compile(r'(\d[\d,]*)\s*円')
def per_serving_threshold(query, serving_g):
    """'N円/食'·'一人前N円' 등 per-serving 가격 임계값을 100g당 임계값으로 환산."""
    if not query: return None
    if not re.search(r'(/?\s*食|一人前|人前|/\s*人)', query): return None
    m = PER_SERVING_RE.search(query)
    if not m: return None
    yen = int(m.group(1).replace(',', ''))
    # 1식 ≈ serving_g 가정 → per-100g = yen × 100 / serving_g
    return round(yen * 100.0 / serving_g)

WEIGHT_RE = re.compile(r'(\d+(?:[.,]\d+)?)\s*(kg|ｋｇ|キロ|kｇ|g|ｇ|グラム|gr)', re.I)
def parse_weight_g(title):
    """상품명에서 무게(g) 추출. kg→g 환산. 없으면 None."""
    if not title: return None
    best=None
    for m in WEIGHT_RE.finditer(title):
        val=float(m.group(1).replace(',', '.')) if m.group(1).count(',')==1 and '.' not in m.group(1) else float(m.group(1).replace(',', ''))
        unit=m.group(2).lower()
        g = val*1000 if unit in ('kg','ｋｇ','キロ','kｇ') else val
        # 가장 큰 단위(주 규격)를 우선
        if best is None or g>best: best=g
    return best

def price_per_100g(price, grams):
    if not price or not grams or grams<=0: return None
    return price*100.0/grams

def to_int(v, d=0):
    try: return int(float(v))
    except Exception: return d
def to_float(v, d=None):
    try: return float(v)
    except Exception: return d

def classify_zero(answer, tools_used):
    """역질문/상품 미반환 vs 검색 결과 없음."""
    tu = tools_used or []
    if isinstance(tu, str): tu = jload(tu, [])
    has_search = bool(tu)
    a = answer or ''
    if has_search:
        return '검색 결과 없음', 'json.tools_used'
    # tools_used == [] → 역질문 우선, 단 명시적 부재 표현이 강하면 검색 결과 없음
    if any(p in a for p in NORESULT_PATTERNS) and not any(p in a for p in ASKBACK_PATTERNS):
        return '검색 결과 없음', 'answer_text_fallback'
    return '역질문/상품 미반환', 'answer_text_fallback'

def detect_altpush(answer):
    a = answer or ''
    hits = [p for p in ALT_PATTERNS if p in a]
    if not hits:
        return []
    # 거절·불가 안내가 답변에 있으면 권유가 아니라 거절 → 위반 아님
    if any(neg in a for neg in ALT_NEG):
        return []
    return hits

def eval_products(products, q_origins, q_price, max_per_100g=None, max_price_abs=None):
    """상위 30위 relevance 휴리스틱. (적합4/3, 애매2, 유해0)
    max_per_100g: tool_input의 max_price_per_100g(100g당 상한). 있으면 절대가 대신 이걸로 판정.
    max_price_abs: tool_input의 max_price(절대 상한)."""
    top = products[:30]
    scored = []
    q_norm = [norm_origin(o) for o in q_origins]
    for i,p in enumerate(top):
        title = p.get('title') or ''
        origin = p.get('origin')
        price = to_float(p.get('selling_price'))
        grams = parse_weight_g(title)
        p100 = price_per_100g(price, grams)
        violated = []
        matched = []
        price_unknown = False
        rs = 3  # 검색이 반환한 카테고리 상품 → 기본 관련
        # 원산지 게이트
        if q_norm:
            src = origin if origin else None
            name_origins = extract_origin(title)
            cand = []
            if src: cand += extract_origin(src) or [src]
            cand += name_origins
            GENERIC = ('国産', '国')   # 일본 내 generic — 특정 광역 아님
            cand_has_generic = any(x == '国産' for x in cand)
            cand_specific = [norm_origin(x) for x in cand if x != '国産' and norm_origin(x) not in GENERIC]
            q_specific = [c for c in q_norm if c not in GENERIC]
            q_generic = ('国産' in q_origins)
            if q_specific:
                # 특정 광역(예: 大阪)을 요구
                if any(c in q_specific for c in cand_specific):
                    matched.append('원산지'); rs = 4              # MATCH
                elif cand_specific:
                    violated.append('원산지 조건 위반'); rs = 0     # 다른 특정 광역 명시 → MISMATCH
                # 国産(generic)뿐이거나 산지 불명 → UNKNOWN(채점 제외): 大阪일 수도 있음
            elif q_generic:
                # 国産(일본 내) 요구 → 일본 광역/국산이면 충족
                if cand_specific or cand_has_generic:
                    matched.append('원산지'); rs = 4
                # 산지 불명 → UNKNOWN
        # 가격 게이트 — 우선순위: 100g당 단가 > 절대 상한 > 쿼리 단순값
        if max_per_100g is not None:
            if price is None:
                price_unknown = True
            elif grams is None:
                price_unknown = True   # 무게 미상 → 100g당 계산 불가(UNKNOWN, 채점 제외)
            elif p100 is not None:
                if p100 > max_per_100g:
                    violated.append(f'100g당 단가 위반(¥{p100:.0f}/100g > ¥{max_per_100g})'); rs = 0
                else:
                    matched.append(f'100g당 ¥{p100:.0f} ≤ ¥{max_per_100g}')
        elif max_price_abs is not None and price is not None:
            if price > max_price_abs:
                violated.append(f'가격 상한 위반(¥{price:.0f} > ¥{max_price_abs})'); rs = 0
            else:
                matched.append('가격')
        elif q_price and price is not None and q_price.get('val'):
            if q_price['op']=='<=' and price > q_price['val']:
                violated.append('가격 조건 위반'); rs = 0
            elif q_price['op']=='>=' and price < q_price['val']:
                violated.append('가격 조건 위반'); rs = 0
            elif q_price['op']=='<=' and price <= q_price['val']:
                matched.append('가격')
        label = '적합' if rs>=3 else ('애매' if rs==2 else '유해')
        scored.append({
            'rank': i+1,
            'title': title,
            'brand': p.get('brand_name'),
            'image_url': p.get('cdn_main_url'),
            'selling_price': price,
            'currency': p.get('currency') or 'JPY',
            'origin': origin,
            'availability': p.get('availability'),
            'relevance_score': rs,
            'relevance_label': label,
            'weight_g': grams,
            'price_per_100g': round(p100,1) if p100 is not None else None,
            'price_unknown': price_unknown,
            'matched_conditions': matched,
            'violated_conditions': violated,
            'reason': ('; '.join(violated) if violated else '')
        })
    return scored

def filter_eval(tool_input, q_origins, q_price):
    """검색 조건 반영 여부 → PASS/PARTIAL/FAIL."""
    ti = tool_input if isinstance(tool_input, dict) else jload(tool_input, {}) or {}
    blob = json.dumps(ti, ensure_ascii=False)
    missing = []
    if q_origins:
        if not any(norm_origin(o) in blob or o in blob or '国産' in blob for o in q_origins):
            # origin 필터 또는 키워드에 산지 반영 안 됨
            missing.append('원산지')
    if q_price and q_price.get('val'):
        # 가격 필터 키 존재 여부
        if not re.search(r'price', blob, re.I):
            missing.append('가격')
    if not q_origins and not q_price:
        return 'PASS', []
    if not missing:
        return 'PASS', []
    if len(missing) >= (len(['o' for _ in [1] if q_origins]) + (1 if q_price else 0)):
        return ('PARTIAL' if len(missing)==1 else 'FAIL'), missing
    return 'PARTIAL', missing

def build_case(row, cols, eval_type, prev_queries=None, scenario=None, turn=None):
    g = lambda k: row.get(cols.get(k,''),'') if cols.get(k) else ''
    query = g('検索クエリ')
    answer = g('answer_text')
    pcount = to_int(g('product_count'), 0)
    products = jload(g('response_text_1'), []) or []
    tools_used = jload(g('phoenix_tools_used'), [])
    tool_input = jload(g('phoenix_tool_input'), {})
    tool_output = g('phoenix_tool_output')
    total_count = to_int(g('phoenix_total_count'), pcount)
    tool_name = g('phoenix_tool_name')
    trace_id = g('phoenix_trace_id')
    tlat = g('phoenix_tool_latency_ms'); flat = g('phoenix_final_llm_latency_ms')
    sess = g('session_id'); crid = g('chat_request_id')

    func_cat = func_ko(g('類型') or g('検索基準') or None)  # 기능분류 (싱글턴 類型 / 멀티턴 検索基準) → 한국어

    ti = tool_input if isinstance(tool_input, dict) else {}
    max_per_100g = ti.get('max_price_per_100g')
    max_price_abs = ti.get('max_price')
    q_origins = query_origin(query)
    q_price = query_price(query)
    # per-serving(円/食·一人前) 쿼리: 카테고리별 1식 중량 가정으로 100g당 임계값 환산
    serving_note = None
    cat_for_serving = ti.get('category_path') or ti.get('category_paths') or query
    serving_g = serving_g_for(cat_for_serving, query)
    ps_thr = per_serving_threshold(query, serving_g)
    if ps_thr is not None:
        max_per_100g = ps_thr  # 쿼리 의도(円/食) 기반 임계값을 우선 사용
        cat_label = '채소' if serving_g==SERVING_G_VEG else ('곡물' if serving_g==SERVING_G_STAPLE else '主菜(고기·생선)')
        serving_note = f'per-serving(円/食) → {cat_label} 1식 {serving_g}g 가정으로 ¥{ps_thr}/100g 환산 평가'
    # 단위가격(円/kg, キロ…円, /100g) 표현인데 정규화 파라미터가 없으면 절대가 비교 부정확 → 가격 채점 제외(UNKNOWN)
    per_unit = bool(re.search(r'(/?\s*kg|キロ|100\s*g|円/kg|/\s*100g)', query or ''))
    if per_unit and max_per_100g is None and max_price_abs is None:
        q_price = None

    # PRICE 세그먼트: tool_input의 정규화 파라미터 우선 표기
    if max_per_100g is not None:
        price_tag = f'max_price_per_100g ≤ ¥{max_per_100g}/100g' + (f' ({serving_note})' if serving_note else '')
    elif max_price_abs is not None:
        price_tag = f'max_price ≤ ¥{max_price_abs}'
    elif q_price:
        price_tag = q_price['raw']
    else:
        price_tag = None

    seg = {
        'ORIGIN': '・'.join(q_origins) if q_origins else (ti.get('origin') or None),
        'PRICE': price_tag,
        'PRICE_FILTER': (f'max_price_per_100g <= {max_per_100g}' if max_per_100g is not None
                         else (f'max_price <= {max_price_abs}' if max_price_abs is not None else None)),
        'CATEGORY': ti.get('category_path') or ti.get('category_paths'),
        'INTENT': 'filter_search' if (q_origins or q_price or max_per_100g is not None or max_price_abs is not None) else 'recommend'
    }

    latency_summary = ''
    if tlat or flat:
        latency_summary = f'tool {tlat}ms / final LLM {flat}ms'

    case = {
        'case_id': (scenario+'-'+str(turn)) if scenario else g('シナリオID') or query[:8],
        'query_id': g('シナリオID'),
        'session_id': sess, 'chat_request_id': crid,
        'query': query, 'eval_type': eval_type,
        'function_category': func_cat,
        'language': 'ja',
        'segment_tags': {k:v for k,v in seg.items()},
        'answer_text': answer,
        'product_count': pcount,
        'previous_turn_queries': prev_queries or [],
    }
    if scenario: case['scenario_id'] = scenario
    if turn: case['turn_number'] = turn

    # ---------- 0건 케이스 ----------
    if pcount == 0:
        zt, src = classify_zero(answer, tools_used)
        # 역질문/상품 미반환은 대안유도 검증·집계에서 제외 (검색 결과 없음 케이스만 대상)
        alt = detect_altpush(answer) if zt == '검색 결과 없음' else []
        ev = {'Rel':0,'Acc':0.3,'Comp':0.3,'root_cause':[],'issue_types':[]}
        case['zero_result_type'] = zt
        case['zero_result'] = {'product_count':0,'zero_result_type':zt,'zero_result_source':src,
            'tools_used':tools_used,'has_alternative_recommendation':bool(alt),
            'alternative_recommendation_evidence': ('「'+answer[:80]+'…」 — '+'/'.join(alt)) if alt else None}
        case['product_scores'] = []
        if alt:
            ev.update({'verdict':'Fail','llm_initial_judgement':'Fail','phoenix_judgement':'Fail',
                'final_judgement':'Fail','judgement_changed':False,'is_outlier':False,'human_review':True,
                'test_priority':1,'Score':0.25,'Acc':0.3,'Comp':0.3,
                'root_cause':['답변 근거 불일치'],'issue_types':['대안유도'],
                'issue_detail':'검색 결과 0건인데 답변이 다른 상품을 추천·유도함.'})
            case['has_alternative_recommendation'] = True
        else:
            ev.update({'verdict':'zero_result','llm_initial_judgement':'zero_result',
                'phoenix_judgement':None,'final_judgement':'zero_result','judgement_changed':False,
                'is_outlier':False,'human_review':False,
                'issue_types':['NO_RESULT_VALID' if zt=='검색 결과 없음' else 'NONE'],
                'root_cause':['없음']})
        ev['phoenix_evidence'] = {'tool_name':tool_name or '-','tool_input_summary':json.dumps(tool_input,ensure_ascii=False)[:160] if tool_input else '-',
            'total_count':total_count,'tool_output_summary':'상품 0건','llm_response_summary':answer[:60],'latency_summary':latency_summary}
        case['evaluation'] = ev
        case['phoenix_checks'] = None
        case['summary'] = ({'strengths':'없음','weaknesses':'결과 없음에도 다른 상품 권유','recommendations':'결과 없음만 안내하도록 수정','notes':'대안 추천 위반'} if alt
            else {'comment_skipped':True})
        return case

    # ---------- 상품 있는 케이스 ----------
    scored = eval_products(products, q_origins, q_price, max_per_100g=max_per_100g, max_price_abs=max_price_abs)
    n = len(scored) or 1
    viol = [s for s in scored if s['violated_conditions']]
    noise_ratio = len(viol)/n
    c_avg = sum(s['relevance_score'] for s in scored)/ (4*n)
    top3 = scored[:3]
    top3_bad = any(s['violated_conditions'] for s in top3)
    top3_acc = sum(min(s['relevance_score'],4) for s in top3)/(4*max(len(top3),1))

    fe_j, fe_missing = filter_eval(tool_input, q_origins, q_price)

    issues = []
    if fe_j in ('PARTIAL','FAIL'): issues.append('FILTER_MISMATCH')
    if viol and fe_j=='PASS': issues.append('RESULT_MISMATCH')

    # 100점 근사
    score100 = 100
    if fe_j=='FAIL': score100 -= 30
    elif fe_j=='PARTIAL': score100 -= 12
    score100 -= min(noise_ratio,1)*40
    if top3_bad: score100 -= 10
    score100 = max(0, round(score100))

    if score100>=90 and not top3_bad: verdict='Hard Pass'; fj='Hard Pass'; llm='Pass'
    elif score100>=70: verdict='Conditional Pass'; fj='Conditional Pass'; llm='Warning'
    else: verdict='Fail'; fj='Fail'; llm='Fail'
    # Warning 표기 통일(Conditional Pass는 Warning 1차)
    is_outlier = top3_acc < 0.5
    human_review = (llm in ('Warning','Fail')) or is_outlier

    # Phoenix (Warning/Fail만)
    pchecks=None; root=['없음']; phoenix_j=None; changed=False
    if llm in ('Warning','Fail'):
        params_ok = 'OK' if fe_j=='PASS' else ('PARTIAL' if fe_j=='PARTIAL' else 'FAIL')
        retrieval_ok = 'OK' if noise_ratio<0.1 else ('PARTIAL' if noise_ratio<=0.3 else 'FAIL')
        count_ok = 'OK' if abs(total_count - pcount) <= max(5, pcount*0.5) else 'PARTIAL'
        pchecks={'mapping_ok':'OK' if trace_id else 'FAIL','tool_call_ok':'OK' if tools_used else 'FAIL',
            'params_ok':params_ok,'count_ok':count_ok,'retrieval_ok':retrieval_ok,
            'grounding_ok':'OK','context_ok':None}
        rc=[]
        if params_ok in ('FAIL','PARTIAL'): rc.append('검색 조건 문제')
        if retrieval_ok in ('FAIL','PARTIAL'): rc.append('검색 결과 부적합')
        root = rc or ['없음']
        crit = any(pchecks[k]=='FAIL' for k in ('params_ok','retrieval_ok','grounding_ok'))
        phoenix_j = 'Fail' if crit else ('Warning' if any(v=='PARTIAL' for v in pchecks.values() if v) else 'Pass')

    rel = 0.5 + c_avg*0.3 + (1-noise_ratio)*0.2
    ev = {'Rel':round(rel,2),'Acc':round(min(1,score100/100+0.05),2),'Comp':0.8,
        'Score':round(score100/100,2),'verdict':verdict,'llm_initial_judgement':llm,
        'phoenix_judgement':phoenix_j if phoenix_j else '-','final_judgement':fj,
        'judgement_changed':changed,'is_outlier':is_outlier,'human_review':human_review,
        'test_priority': 1 if (is_outlier and human_review) else (3 if is_outlier else (4 if issues else None)),
        'root_cause':root,'issue_types':issues or ['NONE'],
        'D_noise_pct':round(noise_ratio,2),
        'filter_evaluation_judgement':fe_j,
        'issue_detail': ('필터 변환: '+fe_j+(' (누락: '+', '.join(fe_missing)+')' if fe_missing else '')) if issues else None,
        'phoenix_evidence':{'tool_name':tool_name or '-',
            'tool_input_summary':json.dumps(tool_input,ensure_ascii=False)[:180] if tool_input else '-',
            'total_count':total_count,'tool_output_summary':f'returned {len(products)}건 / total {total_count}',
            'llm_response_summary':answer[:60],'latency_summary':latency_summary}}
    case['evaluation']=ev
    case['filter_evaluation']={'judgement':fe_j,'missing_conditions':fe_missing,'incorrect_conditions':[],'reason':''}
    case['phoenix_checks']=pchecks
    case['product_scores']=scored
    case['top_k_check']={'top_3_acc_avg':round(top3_acc,2),'is_top_k_bad':top3_bad}
    case['keyword_relevance_check']={'result':'일치' if c_avg>=0.75 else ('부분 일치' if c_avg>=0.5 else '불일치'),
        'keywords': jload(g('keywords'),[]) or [], 'reason':''}
    case['answer_length_check']={'language':'ja','char_count':len(answer or ''),
        'result':'충분' if len(answer or '')>=80 else '보통'}
    if pcount>30:
        case['unevaluated_products']=[{'rank':31+i,'title':p.get('title'),'brand_name':p.get('brand_name'),
            'selling_price':to_float(p.get('selling_price')),'currency':p.get('currency') or 'JPY',
            'origin':p.get('origin'),'cdn_main_url':p.get('cdn_main_url')} for i,p in enumerate(products[30:])]
    isPass = verdict.lower().startswith('hard')
    case['summary']=({'comment_skipped':True} if isPass else
        {'strengths':'검색 결과가 카테고리 의도에 대체로 부합','weaknesses':('; '.join(set(sum([s['violated_conditions'] for s in viol],[]))) or '경미한 노이즈'),
         'recommendations':('필터 보강: '+', '.join(fe_missing)) if fe_missing else '노이즈 상품 정제','notes':''})
    return case

def load(name, eval_type):
    with open(name, encoding='utf-8') as f:
        rows=list(csv.DictReader(f))
        cols=detect_cols(rows[0].keys())
    return rows, cols

def main():
    queries=[]
    # 싱글턴
    rows,cols=load(SINGLE,'싱글턴')
    for row in rows:
        if not (row.get(cols.get('検索クエリ','')) or '').strip(): continue
        queries.append(build_case(row,cols,'싱글턴'))
    # 멀티턴 (시나리오별 이전 턴 누적)
    rows,cols=load(MULTI,'멀티턴')
    prev={}
    for row in rows:
        q=row.get(cols.get('検索クエリ','')) or ''
        if not q.strip(): continue
        scen=row.get(cols.get('シナリオID',''))
        turn_raw=row.get(cols.get('ターン','')) or ''
        tn=to_int(re.sub(r'\D','',turn_raw),0)
        pq=prev.get(scen,[])[:]
        case=build_case(row,cols,'멀티턴',prev_queries=pq,scenario=scen,turn=tn)
        queries.append(case)
        prev.setdefault(scen,[]).append(q)

    # KPI
    vd={'hard_pass':0,'conditional_pass':0,'warning':0,'fail':0,'high_risk':0,'zero_result':0}
    cq=nr=alt=att=0
    tot_prod=disp=0
    for q in queries:
        fj=(q['evaluation'].get('final_judgement') or '')
        if fj=='Hard Pass': vd['hard_pass']+=1
        elif fj=='Conditional Pass': vd['conditional_pass']+=1
        elif fj=='Warning': vd['warning']+=1
        elif fj=='Fail': vd['fail']+=1
        elif fj=='High Risk': vd['high_risk']+=1
        elif fj=='zero_result': vd['zero_result']+=1
        zt=q.get('zero_result_type')
        if zt=='역질문/상품 미반환': cq+=1
        if zt=='검색 결과 없음' and not q.get('has_alternative_recommendation'): nr+=1
        if '대안유도' in (q['evaluation'].get('issue_types') or []): alt+=1
        if q['evaluation'].get('human_review'): att+=1
        tot_prod += q.get('product_count',0)
        disp += len(q.get('product_scores',[]))

    # 기능분류별 집계 (이슈 추적)
    fb = {}
    for q in queries:
        fc = q.get('function_category') or '미분류'
        ev = q['evaluation']
        rec = fb.setdefault(fc, {'name':fc,'total':0,'fail':0,'pass':0,'issue':0,'issue_types':{}})
        rec['total'] += 1
        fj = ev.get('final_judgement') or ''
        if fj in ('Fail','High Risk'): rec['fail'] += 1
        elif fj.lower().startswith('hard') or fj=='Conditional Pass': rec['pass'] += 1
        its = [t for t in (ev.get('issue_types') or []) if t != 'NONE']
        if its: rec['issue'] += 1
        for t in its:
            rec['issue_types'][t] = rec['issue_types'].get(t,0)+1
    function_breakdown = sorted(fb.values(), key=lambda r:(-r['fail'], -r['issue'], -r['total']))

    data={
      'meta':{'dataset':'PROD-YAMATO-260604','report_title':'Yamato 검색 품질 평가 결과',
        'subtitle':f'v3 통합 판정 (LLM × Phoenix) · 싱글턴+멀티턴 {len(queries)}건 · 규칙 기반 자동 평가',
        'generated_at':datetime.date.today().strftime('%Y.%m.%d'),'evaluator_version':'v3',
        'total_queries':len(queries),'total_product_count':tot_prod,'display_product_count':disp},
      'kpi':{'verdict_distribution':vd,'counter_question_count':cq,'no_result_count':nr,
        'alternative_push_count':alt,'attention_queries':att},
      'function_breakdown':function_breakdown,
      'queries':queries
    }
    out=os.path.join(os.path.dirname(__file__),'data.json')
    with open(out,'w',encoding='utf-8') as f:
        json.dump(data,f,ensure_ascii=False,indent=1)
    print('cases:',len(queries))
    print('verdict:',vd,'altpush:',alt,'askback:',cq,'noresult:',nr)

if __name__=='__main__':
    main()
