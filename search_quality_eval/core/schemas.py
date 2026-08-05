"""
GELATTO Common KR/JP 검색 품질 평가 스키마 (v2.0).

설계 원칙
─────────
v2.0에서는 "수치 계산은 전부 코드(core/scoring.py)"가 책임진다.
따라서 LLM이 출력해야 하는 것은 **정성 판단(라벨 + 이유)** 뿐이다.

  · LLM 출력  → 아래 LLM* 스키마 (Gemini response_schema로 강제)
                  segment_tags, 상품별 relevance_score(0~4), A/B/E 라벨,
                  keyword_relevance_check 라벨, Phoenix params/grounding 판단,
                  reasoning, summary 코멘트
  · 코드 계산 → scoring.py 가 A/B/E_score, C_avg_relevance, D_noise_pct,
                  Rel/Acc/Comp/Ctx_final/Score, verdict, final_judgement,
                  phoenix_checks(기계적 항목), root_cause, phoenix_evidence,
                  is_outlier, human_review, test_priority, answer_length_check,
                  zero_result_type, relevance_label/comment_skipped 등

최종 산출물(data.json)의 queries[] 객체 형태는 gelatto_report/App.js 와
gelatto_report/data.example.json 이 기대하는 스키마와 1:1로 맞춘다.
검증용 Pydantic 타입(Final*)도 함께 둔다.
"""
from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Literal, Optional


# ═════════════════════════════════════════════════════════════
# 공통 리터럴
# ═════════════════════════════════════════════════════════════
Language        = Literal["ko", "ja", "en", "mixed"]
RelevanceLabel  = Literal["적합", "부분 적합", "부적합"]
RelevanceLabelYamato = Literal["적합", "애매", "유해"]   # 야마토 전용 라벨(코드가 score→label 도출)
IntentType      = Literal[
    "recommend", "compare", "size_fit", "function", "stock", "guide", "event"
]
ABEPass         = Literal["PASS", "PARTIAL", "FAIL"]
BEQuality       = Literal["GOOD", "ACCEPTABLE", "POOR"]
KeywordResult   = Literal["일치", "부분 일치", "불일치", "해당없음"]
CheckStatus     = Literal["OK", "FAIL", "PARTIAL"]
ContextRetention = Literal["ok", "partial", "broken"]

FinalJudgement = Literal[
    "Hard Pass", "Conditional Pass", "Warning", "Fail", "High Risk", "zero_result"
]
ZeroResultType = Literal["역질문/상품 미반환", "검색 결과 없음"]


# ═════════════════════════════════════════════════════════════
# 1) LLM 출력 스키마 — 정성 판단만
# ═════════════════════════════════════════════════════════════
class LLMSegmentTags(BaseModel):
    """쿼리에서 명시된 속성만 추출. 없으면 null."""
    CATEGORY: Optional[str] = None
    GENDER:   Optional[str] = None
    BRAND:    Optional[str] = None
    COLOR:    Optional[str] = None
    SIZE:     Optional[str] = None
    MATERIAL: Optional[str] = None
    PRICE:    Optional[str] = None
    INTENT:   IntentType = "recommend"


class LLMKeywordCheck(BaseModel):
    """키워드 칩 정합성 판단(라벨 + 이유). char_count 등 수치는 코드가 계산."""
    result: KeywordResult
    keywords: list[str] = Field(default_factory=list)
    reason: Optional[str] = Field(default=None, max_length=240)


class LLMProductScore(BaseModel):
    """
    상위 30개 상품 정성 판단 — **rank + relevance_score + 코멘트만**.
    제목/브랜드/가격/통화/이미지/카테고리 등 메타데이터는 LLM이 출력하지 않는다.
    (코드가 입력 products[]에서 rank로 매칭해 채움 → 토큰 절약 + 통화/URL 정확성)
    relevance_label / comment_skipped 도 코드가 score 로부터 도출.
    """
    rank: int
    relevance_score: int = Field(ge=0, le=4)
    # 아래 코멘트는 score ≤ 2 일 때만 작성. score ≥ 3 이면 생략.
    matched_conditions: list[str] = Field(default_factory=list)   # 야마토: 충족 조건(산지·가격 등)
    violated_conditions: list[str] = Field(default_factory=list)
    description: Optional[str] = Field(default=None, max_length=200)
    exposure_reason: Optional[str] = Field(default=None, max_length=200)
    reason: Optional[str] = Field(default=None, max_length=200)


class LLMBrandCount(BaseModel):
    brand: str
    count: int


class LLMEvaluation(BaseModel):
    """A/B/E 라벨 + 이유, 이슈 분류. C/D/Rel/Acc/Comp/Score 는 코드가 계산."""
    A_query_intent: ABEPass
    A_reason: Optional[str] = Field(default=None, max_length=240)
    B_text_quality: BEQuality
    B_reason: Optional[str] = Field(default=None, max_length=240)
    E_diversity: BEQuality
    E_top_brands: list[LLMBrandCount] = Field(default_factory=list)
    E_reason: Optional[str] = Field(default=None, max_length=240)

    issue_types: list[str] = Field(default_factory=list)
    issue_detail: Optional[str] = Field(default=None, max_length=400)

    # ── 멀티턴 전용(Turn ≥ 2) ──
    context_retention: Optional[ContextRetention] = None
    drift_detected: Optional[bool] = None


class LLMPhoenixJudgments(BaseModel):
    """
    Phoenix 검증 중 '판단'이 필요한 항목만 LLM이 채운다.
    mapping/tool_call/count/retrieval/context 는 코드가 기계적으로 도출.
    """
    params_ok: Optional[CheckStatus] = None     # 검색 조건이 질문과 맞는가
    grounding_ok: Optional[CheckStatus] = None  # 답변이 검색된 상품을 근거로 했는가


class LLMSummary(BaseModel):
    """Warning/Fail 케이스에서만 작성(코드가 Pass 케이스는 비움)."""
    strengths: Optional[str] = Field(default=None, max_length=400)
    weaknesses: Optional[str] = Field(default=None, max_length=400)
    recommendations: Optional[str] = Field(default=None, max_length=400)
    notes: Optional[str] = Field(default=None, max_length=400)


class LLMQueryEval(BaseModel):
    """싱글턴 1쿼리 또는 멀티턴 1턴에 대한 LLM 정성 출력."""
    reasoning: str = Field(min_length=20, max_length=600)
    language: Language
    segment_tags: LLMSegmentTags
    keyword_relevance_check: LLMKeywordCheck
    product_scores: list[LLMProductScore] = Field(default_factory=list)
    evaluation: LLMEvaluation
    phoenix_judgments: LLMPhoenixJudgments = Field(default_factory=LLMPhoenixJudgments)
    summary: LLMSummary = Field(default_factory=LLMSummary)


class LLMTurnEval(LLMQueryEval):
    """멀티턴 턴 단위 — 턴 번호 포함."""
    turn_number: int


class LLMScenarioEval(BaseModel):
    """멀티턴 시나리오 전체 LLM 출력."""
    turns: list[LLMTurnEval]


class LLMProductScoreList(BaseModel):
    """상품 점수 누락 보완(gap-fill) 전용 — 누락 rank만 재질의할 때 사용."""
    product_scores: list[LLMProductScore] = Field(default_factory=list)


# ═════════════════════════════════════════════════════════════
# 1-Y) YAMATO 전용 LLM 출력 스키마 (report_type: yamato / genser_discovery)
#   · GELATTO와 세그먼트 키·필터 변환 평가가 달라 별도 정의.
#   · relevance_score(0~4)·라벨·이유는 LLM이, 100점·노이즈·top-k·
#     function_breakdown·zero_result 집계는 yamato_scoring.py(코드)가 계산.
# ═════════════════════════════════════════════════════════════
class LLMSegmentTagsYamato(BaseModel):
    """야마토 쿼리 세그먼트 — 쿼리에 명시된 속성만. 없으면 null."""
    PRICE:           Optional[str] = None
    PRICE_FILTER:    Optional[str] = None
    ORIGIN:          Optional[str] = None
    PRODUCT_KEYWORD: Optional[str] = None
    CATEGORY:        Optional[str] = None
    BRAND:           Optional[str] = None
    SIZE_OR_UNIT:    Optional[str] = None
    EXCLUDE:         Optional[str] = None
    INTENT:          Optional[str] = "recommend"   # 야마토 INTENT는 자유 서술(filter_search 등)


class LLMFilterEvaluation(BaseModel):
    """Step 2. 검색 파라미터(필터) 변환 정합성 — 라벨 + 누락/오변환 + 이유."""
    judgement: ABEPass                                          # PASS | PARTIAL | FAIL
    missing_conditions:   list[str] = Field(default_factory=list)
    incorrect_conditions: list[str] = Field(default_factory=list)
    reason: Optional[str] = Field(default=None, max_length=240)


class LLMEvaluationYamato(LLMEvaluation):
    """A/B/E + 야마토 F(페르소나·사용 맥락 일치) 라벨. 점수·Score는 코드가 계산."""
    F_context_match: Optional[ABEPass] = None
    F_reason: Optional[str] = Field(default=None, max_length=240)


class LLMQueryEvalYamato(BaseModel):
    """야마토 싱글턴 1쿼리 / 멀티턴 1턴에 대한 LLM 정성 출력."""
    reasoning: str = Field(min_length=20, max_length=600)
    language: Language
    segment_tags: LLMSegmentTagsYamato
    filter_evaluation: LLMFilterEvaluation
    keyword_relevance_check: LLMKeywordCheck
    product_scores: list[LLMProductScore] = Field(default_factory=list)
    evaluation: LLMEvaluationYamato
    phoenix_judgments: LLMPhoenixJudgments = Field(default_factory=LLMPhoenixJudgments)
    summary: LLMSummary = Field(default_factory=LLMSummary)


class LLMTurnEvalYamato(LLMQueryEvalYamato):
    """야마토 멀티턴 턴 단위 — 턴 번호 포함."""
    turn_number: int


class LLMScenarioEvalYamato(BaseModel):
    """야마토 멀티턴 시나리오 전체 LLM 출력."""
    turns: list[LLMTurnEvalYamato]


# 하위 호환 별칭 (per_query_evaluator 등 기존 import 보호)
SingleEvaluation = LLMQueryEval
MultiEvaluation = LLMScenarioEval


# ═════════════════════════════════════════════════════════════
# 2) 최종 data.json 스키마 — 코드가 완성하는 형태 (검증용)
# ═════════════════════════════════════════════════════════════
class FinalProductScore(BaseModel):
    rank: int
    title: str
    brand: Optional[str] = None
    image_url: Optional[str] = None
    selling_price: Optional[float] = None
    currency: Optional[Literal["KRW", "JPY"]] = None
    category_path: Optional[str] = None
    stock_status: Optional[str] = None
    relevance_score: int
    relevance_label: RelevanceLabel
    violated_conditions: list[str] = Field(default_factory=list)
    description: Optional[str] = None
    exposure_reason: Optional[str] = None
    reason: Optional[str] = None
    comment_skipped: bool = False


class FinalSegmentTags(LLMSegmentTags):
    pass


class FinalTopKCheck(BaseModel):
    top_3_acc_avg: float
    is_top_k_bad: bool
    top_k_reason: Optional[str] = None


class FinalAnswerLengthCheck(BaseModel):
    language: Language
    char_count: int
    result: Literal["충분", "보통", "부족"]


class FinalKeywordCheck(BaseModel):
    result: KeywordResult
    keywords: list[str] = Field(default_factory=list)
    reason: Optional[str] = None


class FinalPhoenixChecks(BaseModel):
    mapping_ok:   Optional[CheckStatus] = None
    tool_call_ok: Optional[CheckStatus] = None
    params_ok:    Optional[CheckStatus] = None
    count_ok:     Optional[CheckStatus] = None
    retrieval_ok: Optional[CheckStatus] = None
    grounding_ok: Optional[CheckStatus] = None
    context_ok:   Optional[CheckStatus] = None


class FinalPhoenixEvidence(BaseModel):
    tool_name: Optional[str] = None
    tool_input_summary: Optional[str] = None
    total_count: Optional[int] = None
    tool_output_summary: Optional[str] = None
    llm_response_summary: Optional[str] = None
    latency_summary: Optional[str] = None


class FinalEvaluation(BaseModel):
    A_query_intent: ABEPass
    A_score: float
    A_reason: Optional[str] = None
    B_text_quality: BEQuality
    B_score: float
    B_reason: Optional[str] = None
    C_relevance: Literal["HIGH", "MEDIUM", "LOW"]
    C_avg_relevance: float
    C_reason: Optional[str] = None
    D_noise_ratio: Literal["LOW", "MEDIUM", "HIGH"]
    D_noise_pct: float
    D_low_relevance_items: list[str] = Field(default_factory=list)
    D_reason: Optional[str] = None
    E_diversity: BEQuality
    E_score: float
    E_top_brands: list[dict] = Field(default_factory=list)
    E_reason: Optional[str] = None

    Rel: float
    Acc: float
    Comp: float
    Ctx_final: Optional[float] = None
    Score: float
    score_formula: str

    verdict: Literal["Hard Pass", "Conditional Pass", "Fail"]
    is_outlier: bool
    human_review: bool
    is_judge_unstable: bool
    unstable_reasons: list[str] = Field(default_factory=list)
    drift_human_flag: Optional[bool] = None

    issue_types: list[str] = Field(default_factory=list)
    issue_detail: Optional[str] = None

    llm_initial_judgement: Literal["Pass", "Warning", "Fail"]
    phoenix_judgement: Literal[
        "Pass", "Warning", "Fail", "zero_result", "Phoenix 로그 연결 안 됨"
    ]
    final_judgement: FinalJudgement
    judgement_changed: bool
    root_cause: list[str] = Field(default_factory=list)
    phoenix_evidence: FinalPhoenixEvidence

    test_priority: Literal["1", "2", "3", "4", "해당없음", 1, 2, 3, 4]
    priority_reason: Optional[str] = None
    comment_skipped: bool = False


class FinalSummary(BaseModel):
    strengths: Optional[str] = None
    weaknesses: Optional[str] = None
    recommendations: Optional[str] = None
    notes: Optional[str] = None
    comment_skipped: bool = False


class FinalQuery(BaseModel):
    case_id: str
    query_id: Optional[str] = None
    session_id: Optional[str] = None
    chat_request_id: Optional[str] = None
    query: Optional[str] = None
    search_type_name: Optional[str] = None
    eval_type: Literal["싱글턴", "멀티턴"]
    scenario_id: Optional[str] = None
    turn_number: Optional[int] = None
    previous_turn_queries: list[str] = Field(default_factory=list)
    language: Language

    reasoning: str
    segment_tags: FinalSegmentTags
    top_k_check: FinalTopKCheck
    answer_text: Optional[str] = None
    latency_ms: Optional[float] = None   # e2e 라운드트립(ms) — latency 추적 메인 지표
    answer_length_check: FinalAnswerLengthCheck
    keyword_relevance_check: FinalKeywordCheck
    product_count: int
    zero_result_type: Optional[ZeroResultType] = None
    product_scores: list[FinalProductScore] = Field(default_factory=list)
    unevaluated_products: list[dict] = Field(default_factory=list)
    phoenix_checks: FinalPhoenixChecks
    evaluation: FinalEvaluation
    summary: FinalSummary


class FinalMeta(BaseModel):
    dataset: str
    report_title: str
    subtitle: str
    generated_at: str
    env: str = ""                  # 평가 환경 (예: mizuno_stg-ja) — 헤더 환경 뱃지
    label: str = "라벨링 없음"
    prompt_file: str = ""          # 평가에 사용된 프롬프트 파일명
    evaluator_version: str = "v2.0"
    total_queries: int
    session_count: int = 0         # 세션 수 (session_id 기준)
    total_product_count: int
    display_product_count: int


class FinalVerdictDistribution(BaseModel):
    hard_pass: int = 0
    conditional_pass: int = 0
    warning: int = 0
    fail: int = 0
    high_risk: int = 0
    zero_result: int = 0


class TurnSessionStat(BaseModel):
    """싱글턴/멀티턴 한 그룹의 세션 기준 카운트."""
    total: int = 0
    pass_count: int = 0
    warning: int = 0
    fail: int = 0


class SessionSummary(BaseModel):
    singleturn: TurnSessionStat = Field(default_factory=TurnSessionStat)
    multiturn: TurnSessionStat = Field(default_factory=TurnSessionStat)


class PassRate(BaseModel):
    """전체 통과율 — 세션 기준 (Pass + Warning) ÷ 전체."""
    value: int = 0                 # 백분율 정수
    basis: str = "pass_warning"
    numerator: int = 0
    denominator: int = 0


class FinalKpi(BaseModel):
    verdict_distribution: FinalVerdictDistribution
    counter_question_count: int = 0
    no_result_count: int = 0
    attention_queries: int = 0
    # v2.x — 세션 기준 싱글/멀티턴 집계 + 전체 통과율 (scoring_v2 계산)
    session_summary: Optional[SessionSummary] = None
    total_sessions: int = 0
    pass_rate: Optional[PassRate] = None


class FinalReport(BaseModel):
    """data.json 최상위."""
    meta: FinalMeta
    kpi: FinalKpi
    queries: list[FinalQuery]


# ═════════════════════════════════════════════════════════════
# (레거시) 2단계 집계 LLM 종합 타입 — 현재 v2.0 data.json 에는 미사용.
# aggregator_llm.py 호환을 위해 보존. 향후 서술형 총평 섹션 부활 시 재사용.
# ═════════════════════════════════════════════════════════════
Severity = Literal["critical", "warning", "positive"]
Priority = Literal["P1", "P2", "P3"]
SectionType = Literal["text", "grade_matrix", "case_list"]


class Finding(BaseModel):
    severity: Severity
    title: str
    description: str


class ActionItem(BaseModel):
    priority: Priority
    item: str
    reason: str


class Section(BaseModel):
    title: str
    type: SectionType
    content: Optional[str] = None
    categories: Optional[list[str]] = None
    grades: Optional[list[str]] = None
    avg_scores: Optional[list[float]] = None
    notes: Optional[list[str]] = None
    items: Optional[list[dict]] = None


class AggregateAnalysis(BaseModel):
    """2단계 LLM 정성 종합 (레거시)."""
    overall_assessment: str
    findings: list[Finding]
    action_items: list[ActionItem]
    sections: list[Section]
