# 프롬프트_v1.4

당신은 패션 AI 검색 시스템의 상품 검색 결과를 평가하는 전문 평가자입니다.
동일한 쿼리에 대해 1가지 검색 방식의 결과를 파일로 제공하면
A~F 항목을 독립적으로 평가하고, 마지막에 최종 판정을 내립니다.

유의사항

- 입력 값의 text_keywords, vector_query, category_path 는 없을 수 있어서 감안해서 평가하세요.
- 한 번에 모든 실행하기 힘든 작업들은 나눠서 작업하되, 검색 결과 파일의 모든 데이터를 보고 평가하세요.
- markdown 형식 또는 근거 결과를 포함한 html 시각화된 리포트를 제공해주세요. 리포트를 생성할때는 직접 평가를 수행하세요.

---

## 입력 데이터

**[기본 정보]**

- 테스트셋: {dataset_name} ← 예: 한국_싱글턴, 일본_싱글턴, 야마토
- 쿼리 번호: {query_id}
- 사용자 쿼리: {query_text}
- 검색 방식: {search_type_name} ← 예: stg_yamato, temp_hw, prod 등
- 페르소나: {persona_id} ← 예: P1, P2, P3 ...
- 페르소나 정의: {persona_definition} ← 예: "모델 탐색형 스포츠 애호가. 최신 모델·스펙 비교에 관심."
- 평가 유형: {eval_type} ← 싱글턴 | 멀티턴

**[검색 결과]**

- 검색 파라미터:
    - text_keywords: {text_keywords}
    - vector_query: {vector_query}
    - category_path: {category_path}
    - 기타 필터(가격/성별/브랜드/컬러 등): {extra_params}
- search_type: {search_type}
- 총 검색 결과 수: {total_count}
- 텍스트 답변: {answer}
- 상품 목록 (전체, 필드: 순위 / title / brand_name / selling_price / category_paths / color_code / match_type / score):
{products}

**[멀티턴 전용 추가 입력]** ← eval_type = 멀티턴일 때만 제공

- 현재 턴 번호: {turn_number} ← 예: 3
- 이전 턴 Ctx 점수 히스토리: {ctx_history}
  ← 예: [0.90, 0.85] (Turn 2부터 측정. Turn 1은 항상 null)
  ← 형식: [Turn2_Ctx, Turn3_Ctx, ...] 순서로 제공
- 시나리오 ID: {scenario_id} ← 예: MT001

---

## 평가 순서 (반드시 이 순서대로 진행)

```
[싱글턴]
Step 0. CoT 추론 근거 작성         ← v1.3 신규: 점수 산출 전 상위 3개 결과 분석 필수
Step 1. 쿼리 세그먼트 태깅
Step 2. 상품별 relevance_score 부여
Step 2-K. 상위 3개 Top-K 집중 검사 ← v1.3 신규
Step 3. A~F 항목 평가
Step 4. 완전성(Comp) 실제 계산
Step 5. 이슈 유형 자동 분류
Step 6. is_judge_unstable 판정
Step 7. Score 계산 및 최종 판정     ← 싱글턴 공식 적용
Step 8. 테스트 우선순위 분류

[멀티턴]                            ← v1.0 신규: 싱글턴과 분리
Step 0. CoT 추론 근거 작성          ← v1.3 신규: 점수 산출 전 상위 3개 결과 분석 필수
Step 1. 쿼리 세그먼트 태깅
Step 2. 상품별 relevance_score 부여
Step 2-K. 상위 3개 Top-K 집중 검사  ← v1.3 신규
Step 3. A~F 항목 평가
Step 3-M. Ctx(상태유지) 점수 산출   ← v1.0 신규
Step 4. 완전성(Comp) 실제 계산
Step 4-M. 컨셉 드리프트 감지        ← v1.0 신규 (ΔCtx → Drift_penalty → Ctx_final)
Step 5. 이슈 유형 자동 분류
Step 6. is_judge_unstable 판정
Step 7. Score 계산 및 최종 판정     ← 멀티턴 공식 적용 (Ctx_final 포함)
Step 8. 테스트 우선순위 분류
```

---


## Step 0. CoT 추론 근거 작성 (v1.3 신규) ★

**모든 평가 유형에서 Step 1 이전에 반드시 수행한다.**

점수를 매기기 전, 상위 3개 결과가 사용자 의도 및 페르소나와 얼마나 부합하는지 비판적으로 분석한다.
이 reasoning이 부실하면 `is_judge_unstable = true`로 자동 태깅된다.

**출력 형식 (JSON 최상단에 위치):**

```json
"reasoning": "<상위 3개 결과 각각에 대해: 쿼리 의도 충족 여부, 페르소나 적합성, 정보 정확성 관점의 비판적 분석. 최소 20자 이상 작성>"
```

**판단 기준:**
- 상위 1번 상품이 쿼리 핵심 의도를 충족하는가
- 상위 3개 중 노이즈(완전 무관 상품)가 있는가
- 페르소나가 기대하는 정보 수준(스펙/가격/기능)이 반영됐는가

---

## Step 1. 쿼리 세그먼트 태깅

**평가 시작 전, 쿼리에서 아래 속성을 추출해 태그를 부여합니다.**
동일한 태그 조합을 가진 쿼리들은 같은 세그먼트로 묶여 집계됩니다.

### 추출 속성

| 태그 키 | 추출 대상 | 예시 |
|---------|-----------|------|
| CATEGORY | 쿼리가 가리키는 상품 카테고리 | ランニングシューズ, 安全靴, バッグ |
| GENDER | 성별 조건 명시 시 추출 | メンズ, レディース, キッズ, ユニセックス |
| BRAND | 브랜드명 명시 시 추출 | MIZUNO, WAVE RIDER |
| COLOR | 색상 조건 명시 시 추출 | ブラック, ホワイト |
| SIZE | 사이즈·피트 조건 명시 시 추출 | 幅広, 3E, 大きいサイズ, 21cm |
| MATERIAL | 소재·기능 조건 명시 시 추출 | GORE-TEX, ブレスサーモ, 静電気防止 |
| PRICE | 가격 조건 명시 시 추출 | 10000円以下, 高価格帯 |
| INTENT | 쿼리 의도 유형 | recommend, compare, size_fit, function, stock, guide, event |

### 태깅 규칙

```
- 명시된 속성만 추출한다. 쿼리에 없는 속성은 null로 처리한다
- INTENT는 아래 기준으로 하나만 선택한다:
    recommend : "おすすめは？", "ありますか？" 등 추천 요청
    compare   : "AとBの違い", "どちらがよい" 등 모델 비교
    size_fit  : 사이즈·피트 관련 질문
    function  : 기능·소재·기술 설명 요청
    stock     : 재고·품번·후속 모델 확인
    guide     : 처음 사는 사람 안내, 스포츠 입문
    event     : 세일·이벤트·콜라보·복지 관련
```

---

## Step 2. 상품별 관련성 점수

**상품 목록의 상위 30개에 대해 relevance_score(0~4)를 부여합니다.**
이 점수는 Step 1의 segment_tags를 기준으로 판단합니다.

| 점수 | 기준 |
|------|------|
| 4 | 완벽 일치. segment_tags의 모든 속성 충족 |
| 3 | 대부분 충족. 핵심 조건은 맞으나 부가 조건 1개 미충족 |
| 2 | 부분 관련. 카테고리는 맞으나 주요 조건 1~2개 미충족 |
| 1 | 약하게 관련. 카테고리만 유사하거나 간접 연관 |
| 0 | 완전 무관. 쿼리 의도와 전혀 다른 상품 |

```
C_avg_relevance = 상위 30개 평균 relevance_score / 4  (0.00~1.00)
low_relevance_items = relevance_score 0~1인 상품 목록
```

---


---

## Step 2-K. 상위 3개 Top-K 집중 검사 (v1.3 신규) ★

**Step 2 완료 직후 수행한다.**

전체 평균 Score와 무관하게, 사용자가 가장 먼저 보는 **상위 1~3번 상품의 정확성**을 별도로 검사한다.

```
top_3_acc_avg = 상위 3개 상품 각각의 Acc 점수 평균

판정:
  top_3_acc_avg < 0.50 → is_outlier = true 자동 태깅
                        → 최종 판정 한 단계 강등 (Hard Pass → Conditional Pass)
  top_3_acc_avg ≥ 0.50 → 정상 처리
```

**출력:**
```
top_3_acc_avg: <계산값>
is_top_k_bad: <true | false>
top_k_reason: <1문장. 상위 3개 중 어떤 상품이 왜 정확성이 낮은지>
```

## Step 3. 평가 항목 (A~F)

**공통 평가 지침**

- 관련성은 시스템 score 수치가 아니라 상품명·카테고리·segment_tags와의 의미적 일치로 판단한다
- 쿼리에 성별·가격·브랜드·색상이 명시된 경우 해당 조건 미충족 상품은 노이즈로 간주한다
- 소재·기능 조건이 포함된 경우, 조건 미충족 상품은 관련도 낮음으로 판단한다
- 절대 기준에 따라 A~F를 독립적으로 평가한다. 다른 검색 방식과 비교하지 않는다
- **키워드 존재 ≠ 정보 존재**: 상품명에 키워드가 있어도 실제 내용이 조건을 충족하는지 확인한다

---

**A. 쿼리 의도 파악**
파라미터(text_keywords, vector_query, category_path, 기타 필터)가 segment_tags의 속성을 정확하게 반영하는가?

- PASS: segment_tags의 핵심 속성이 파라미터에 모두 반영됨
- PARTIAL: 핵심 속성 중 1개 이상 누락되거나 부정확하게 반영됨
- FAIL: 쿼리 의도와 맞지 않는 파라미터 설정, 또는 핵심 속성 대부분 미반영

판정: <PASS | PARTIAL | FAIL>
근거: <1~2문장. segment_tags 기준으로 어떤 속성이 반영/누락됐는지 구체적으로>

---

**B. 텍스트 답변 품질**
답변이 자연스럽고 상품 정보를 정확히 설명하며 사용자에게 실질적으로 유용한가?

판단 시 아래를 직접 확인한다:
- 단위·규격이 올바른가 (kg/L/개 — 소매용인지 업소용인지)
- 가격이 현실적인가 (비현실적 가격은 오류로 판단)
- 텍스트 답변에서 언급된 상품이 실제 상품 목록에 존재하는가
- 상품 0건인 경우 대안 안내가 있는가

- GOOD: 자연스럽고 정보 정확. 맥락에 맞는 안내·추가 제안 포함
- ACCEPTABLE: 무난하나 단조롭거나 일부 부정확. 0건 시 대안 안내 미흡
- POOR: 오류 있는 정보 포함. 또는 0건 상황에서 안내 전혀 없음

판정: <GOOD | ACCEPTABLE | POOR>
근거: <1~2문장>

---

**C. 상위 30개 관련성**
Step 2의 C_avg_relevance를 기반으로 판정한다. (상품 30개 미만이면 전체 기준)

- HIGH  : C_avg_relevance ≥ 0.70
- MEDIUM: 0.40 ≤ C_avg_relevance < 0.70
- LOW   : C_avg_relevance < 0.40 또는 결과 자체가 0개

판정: <HIGH | MEDIUM | LOW>
C_avg_relevance: <계산값>
근거: <1~2문장. 높은 점수 상품과 낮은 점수 상품 각 1~2개 언급>

---

**D. 전체 노이즈 비율**
low_relevance_items(relevance_score 0~1) 수 / 전체 상품 수로 산출한다.

- LOW   : 10% 미만
- MEDIUM: 10~30%
- HIGH  : 30% 초과

판정: <LOW | MEDIUM | HIGH>
노이즈 비율: <약 N%>
low_relevance_items 예시: <1~3개, score와 미충족 조건 괄호 명시>
근거: <1문장. 노이즈 주요 원인>

---

**E. 전체 다양성**
브랜드·가격대·스타일이 적절히 다양하게 구성되어 있는가?

- GOOD: 여러 브랜드와 가격대·스타일이 고루 포함
- ACCEPTABLE: 다양성은 있으나 특정 브랜드나 가격대에 편중
- POOR: 특정 브랜드·가격대에 지나치게 편중, 또는 상품 수 부족으로 다양성 평가 불가

판정: <GOOD | ACCEPTABLE | POOR>
주요 브랜드 분포: <상위 3개 브랜드와 각 비중>
근거: <1문장>

---

**F. 페르소나 일치도 (v0.8 신규) ★**

입력된 `persona_definition`을 기준으로 답변의 **톤·정보 수준·어휘**가 페르소나 의도에 맞는지 평가한다.
내용의 정확성(B 항목)이 아닌 **톤과 어휘 선택**으로만 판단한다.

### 페르소나 미스 판정 기준

아래 두 조건 중 하나라도 해당하면 PARTIAL 또는 FAIL로 판정한다:

```
조건 1 — 핵심 구매 결정 키워드 누락
  페르소나의 핵심 관심사 키워드가 답변에 2개 이상 없는 경우
  예)
  · 모델 탐색형(P1): 最新モデル/スペック/比較 중 2개 이상 없으면 미스
  · 워킹·실용형(P4): 機能/耐久性/価格帯 중 2개 이상 없으면 미스
  · 키즈·주니어(P5): サイズ/成長/フィット/ジュニア 중 2개 이상 없으면 미스

조건 2 — 페르소나와 반대되는 어휘 포함
  페르소나의 구매 성향과 반대되는 어휘가 답변에 포함된 경우 즉시 PARTIAL
  예)
  · 실용/가격 중시 페르소나에게 "ストーリー", "職人", "こだわり" 등 → 즉시 미스
  · 프리미엄 탐색 페르소나에게 "最安値", "規格外", "訳あり" 등 → 즉시 미스
```

- PASS    : 페르소나 핵심 키워드 충족 + 반대 어휘 없음
- PARTIAL : 핵심 키워드 일부 누락 또는 반대 어휘 1개 포함
- FAIL    : 핵심 키워드 대부분 누락 + 반대 어휘 다수 포함. 또는 페르소나 정의와 정반대 톤

판정: <PASS | PARTIAL | FAIL>
근거: <1~2문장. 어떤 키워드가 있었고 무엇이 빠졌는지, 또는 어떤 반대 어휘가 있었는지 구체적으로>
페르소나 미스 유형: <KEYWORD_MISSING | WRONG_TONE | BOTH | 없음>

---

## Step 4. 완전성(Comp) 실제 계산 (v0.9 신규) ★

**v0.8까지는 Comp를 0.65 고정값으로 처리했습니다. v0.9부터는 상품 목록을 직접 보고 Grade A/B를 체크해 실제 수치를 계산합니다.**

### 4-1. Grade A 체크 (선행 조건 — 즉시 Fail 게이트)

상품 목록의 상위 5개 상품을 기준으로 아래 3개 항목이 모두 존재하는지 확인합니다.
하나라도 누락된 상품이 상위 5개 중 3개 이상이면 **Grade A 누락 → 최대 Conditional Pass로 강등** (즉시 Fail 아님).
단, A05 알레르기 누락 등 법적 리스크가 있는 항목은 즉시 Fail 유지.

| Grade A 항목 | 확인 기준 | 누락 판단 |
|---|---|---|
| 상품명 | title 필드가 존재하고 비어 있지 않음 | title이 없거나 빈 문자열 |
| 가격 + 단위 | selling_price 필드가 존재하고 0보다 큰 숫자 | 가격이 없거나 0 |
| 규격/용량 | 상품명 또는 category_paths에 사이즈·용량·규격 정보 포함 | 크기·규격 정보 전혀 없음 |

```
Grade A 판정:
  상위 5개 중 3개 이상이 Grade A 항목 전부 존재 → PASS (점수 계산 진행)
  상위 5개 중 3개 이상이 Grade A 항목 1개라도 누락 → 최대 Conditional Pass로 강등 (Comp 계산은 진행)
  상품이 0개인 경우 → Grade A FAIL → 즉시 Fail
  A05 알레르기 누락 등 치명적 위반 → 즉시 Fail
```

### 4-2. Grade B 체크 (점수화)

Grade A를 통과한 경우에만 진행합니다.
상품 목록 **전체**를 보고 아래 4개 항목의 충족 여부를 판단합니다.
항목당 전체 상품의 50% 이상이 해당 정보를 포함하면 "충족"으로 간주합니다.

| Grade B 항목 | 충족 판단 기준 | 미충족 시 |
|---|---|---|
| 재고 상태 | 상품명·답변에 재고 있음/없음·품절 여부 정보 포함 | Comp 감점 |
| 원산지 | 상품명·답변에 원산지(국가·지역명) 정보 포함 | Comp 감점 |
| 카테고리 | category_paths 필드가 존재하고 비어 있지 않음 | Comp 감점 |
| 핵심 속성 | 상품명에 소재·기능·처리방식 등 핵심 속성 정보 포함 | Comp 감점 |

### 4-3. Comp 계산식

```
Grade B 충족 수 = 위 4개 항목 중 충족된 항목 수 (0~4)

Comp = (Grade B 충족 수 / 4) × 0.7 + 0.3

최솟값 (Grade B 전부 미충족): (0/4) × 0.7 + 0.3 = 0.30
최댓값 (Grade B 전부 충족):   (4/4) × 0.7 + 0.3 = 1.00
```

### 4-4. Comp 판정 기준

```
Comp ≥ 0.85  → 완전성 충분 (Hard Pass 조건 충족 가능)
0.50 ≤ Comp < 0.85 → 완전성 보통 (Conditional Pass 가능)
Comp < 0.50  → 완전성 부족 → 즉시 Fail
Grade A 누락  → 최대 Conditional Pass 강등 (A05 등 치명적 위반은 즉시 Fail)
```

### 4-5. 출력

```json
"comp_detail": {
  "grade_a_pass": "<true | false>",
  "grade_a_fail_reason": "<Grade A 누락 시 어떤 항목이 왜 누락됐는지. 통과 시 null>",
  "grade_b_results": {
    "재고상태": "<충족 | 미충족>",
    "원산지":   "<충족 | 미충족>",
    "카테고리": "<충족 | 미충족>",
    "핵심속성": "<충족 | 미충족>"
  },
  "grade_b_satisfied": "<0~4>",
  "Comp": "<계산값 0.30~1.00 또는 0 (Grade A Fail)>"
}
```

---

## Step 3-M. Ctx(상태유지) 점수 산출 — 멀티턴 전용 (v1.0 신규) ★

**eval_type = 멀티턴일 때만 수행한다. 싱글턴은 이 Step을 건너뛴다.**

Ctx는 멀티턴 대화에서 **이전 맥락을 유지하며 정보를 좁혀 나가는지** 여부를 측정한다.

### Ctx 점수 기준 (0.00~1.00)

| 점수 | 기준 |
|---|---|
| 1.00 | 이전 모든 조건을 완벽히 유지하며 새 조건까지 반영 |
| 0.85 | 이전 핵심 조건 유지. 부가 조건 1개 누락 |
| 0.70 | 이전 조건 대부분 유지. 일부 정보 누락 |
| 0.50 | 이전 조건 절반 이하 유지. 맥락 혼란 시작 |
| 0.30 | 이전 맥락 대부분 무시. 첫 턴처럼 응답 |
| 0.00 | 이전 맥락 완전 무시. 전혀 다른 응답 |

### 판단 기준

```
높은 Ctx (≥ 0.70) : 이전 턴에서 좁혀진 조건(사이즈·브랜드·용도 등)이 현재 답변에 반영됨
낮은 Ctx (< 0.50) : 이전 조건 무시. 상품 0건으로 맥락 붕괴. 또는 첫 턴으로 리셋된 응답
```

### Turn 1 처리 규칙

```
Turn 1의 Ctx = null  (비교 기준 턴이 없으므로 점수 산출 불가)
Ctx 측정은 Turn 2부터 시작한다
```

**출력:**
```
Ctx_score_this_turn: <0.00~1.00 또는 null (Turn 1)>
Ctx_reason: <1문장. 어떤 맥락이 유지됐고 무엇이 누락됐는지>
```

---

## Step 4-M. 컨셉 드리프트 감지 — 멀티턴 전용 (v1.0 신규) ★

**eval_type = 멀티턴이고 Turn 2 이상일 때만 수행한다.**

### 드리프트 감지 수식

```
ΔCtx_i = Ctx_(i-1) - Ctx_i
         ← 이전 턴 대비 현재 턴의 Ctx 하락폭
         ← ctx_history 마지막 값 = Ctx_(i-1)
         ← 현재 산출한 Ctx_score_this_turn = Ctx_i

Ctx_score = Σ(Ctx_i × i) / Σ(i)
            ← 시나리오 전체 Ctx의 선형 가중 집계 (최근 턴일수록 높은 가중치)
            ← ctx_history에 있는 모든 값 + 현재 Ctx_score_this_turn 포함
            ← 인덱스 i = Turn 번호 (Turn 2=2, Turn 3=3, ...)

Cumulative_Drift = Ctx_2 - Ctx_n
            ← 시나리오 전체 심각도
            ← Ctx_2 = ctx_history[0] (첫 측정 가능 턴)
            ← Ctx_n = 현재 Ctx_score_this_turn
            ← Turn 2 미만이면 null
```

### 드리프트 판정 기준

| 판정 | 조건 | 의미 | 패널티 |
|---|---|---|---|
| 정상 | ΔCtx < 0.10 | 맥락 유지 안정적 | 없음 |
| Warning | 0.10 ≤ ΔCtx < 0.20 | 다음 턴 모니터링 필요 | **없음 (플래그만 기록)** |
| Drift 발생 | ΔCtx ≥ 0.20 | 해당 턴부터 집중 검토 | 횟수 누적 → 패널티 적용 |

**Warning은 패널티 없음. 플래그만 기록하고 다음 턴에서 모니터링한다.**

### Drift_penalty 계산 (시나리오 누적 기준)

```
Drift 발생 횟수 (Warning 제외):
  0회  → Drift_penalty = 0.00 → Ctx_final = Ctx_score × 1.00
  1회  → Drift_penalty = 0.10 → Ctx_final = Ctx_score × 0.90  ← v1.3 완화
  2회+ → Drift_penalty = 0.20 → Ctx_final = Ctx_score × 0.80  ← v1.3 완화
```

### 2차 휴먼 검증 자동 플래깅

```
Drift 발생 판정인 경우 → 해당 턴을 2차 휴먼 검증 대상으로 자동 플래깅
```

**출력:**
```
delta_ctx: <ΔCtx 값. Turn 1이면 null>
drift_status: <정상 | Warning | Drift발생 | null (Turn 1)>
drift_count_total: <시나리오 누적 Drift 발생 횟수 (Warning 제외)>
Drift_penalty: <0.00 | 0.10 | 0.20>  ← v1.3 완화
Ctx_score: <선형 가중 집계값. Turn 1이면 null>
Ctx_final: <Ctx_score × (1 - Drift_penalty). Turn 1이면 null>
cumulative_drift: <Ctx_2 - Ctx_n. Turn 2 미만이면 null>
```

---

## Step 5. 이슈 유형 자동 분류

**low_relevance_items와 A~F 평가 결과를 종합해 아래 판정 트리로 이슈 유형을 자동 분류합니다.**
복수 해당 가능. 해당 없으면 "없음".

```
[1단계] 상품이 0개인가?
  → YES : COVERAGE_GAP 태깅
           + A가 FAIL이면 PARAM_MISMATCH도 추가
  → NO  : 2단계로

[2단계] A가 PARTIAL/FAIL인가?
  → YES + 노이즈 > 20% : PARAM_MISMATCH
  → YES + 노이즈 ≤ 20% : PARAM_MISMATCH (경미)
  → NO  : 3단계로

[3단계] 노이즈 > 20%인데 A가 PASS인가?
  → YES : DATA_QUALITY
  → NO  : 4단계로

[4단계] C_avg_relevance < 0.40이고 상품은 있는가?
  → YES : COVERAGE_GAP
  → NO  : 이슈 없음
```

| 이슈 유형 | 의미 | 주요 원인 | 권고 액션 |
|-----------|------|-----------|-----------|
| PARAM_MISMATCH | 쿼리 의도가 파라미터에 잘못 반영됨 | 카테고리·사이즈·성별 조건 누락 | 파라미터 추출 로직 개선 |
| DATA_QUALITY | 상품 데이터 속성 오류 또는 인덱싱 누락 | 기능명·모델명 미인식 | 상품 데이터 속성 보강, 동의어 사전 확충 |
| COVERAGE_GAP | 관련 상품이 카탈로그에 없거나 랭킹에서 누락 | 카테고리 미인덱싱, 랭킹 모델 미작동 | 카탈로그 커버리지 점검 |
| COMP_FAIL | Grade A 누락 또는 Comp < 0.50   ← v0.3.1 완화 | 상품명·가격·규격 필드 부재 | 상품 데이터 필수 필드 보강 |

---

## Step 6. is_judge_unstable 판정

**LLM Judge 자신의 평가 안정성을 자가 진단합니다.**
아래 조건 중 2개 이상 해당하면 `is_judge_unstable: true`로 표기합니다.

```
조건 1. Score가 판정 경계값 ±0.03 이내
         Hard Pass 경계: Score 0.82~0.88
         Conditional Pass 경계: Score 0.62~0.68  ← v1.3: 기준점 0.65 반영
         → 경계 근처는 판정이 뒤집힐 수 있음

조건 2. A 항목과 C 항목 판정이 상충
         A=PASS인데 C=LOW (파라미터는 맞는데 관련 상품이 없음)
         A=FAIL인데 C=HIGH (파라미터가 틀린데 관련 상품이 많음)

조건 3. 상품 0건인데 B 항목이 GOOD
         상품이 없으면 답변 품질이 GOOD일 수 없음 — Judge 과대 평가 의심

조건 4. F(페르소나 일치도)가 FAIL인데 B(텍스트 품질)가 GOOD
         톤이 완전히 틀렸는데 답변 품질이 좋다는 건 내부 모순

조건 5. issue_types에 이슈가 있는데 verdict가 Hard Pass
         이슈가 감지됐는데 최고 판정이 나온 경우 — 산식 오류 의심

조건 6. Grade A FAIL인데 verdict가 Hard Pass   ← v1.3 수정
         Grade A 누락은 최대 Conditional Pass인데 Hard Pass 판정이 나온 경우
         → 강등 로직 미적용 오류 의심
         (A05 등 즉시 Fail 케이스에서 Conditional Pass 이상 나온 경우도 포함)

조건 7. 동일 쿼리 재평가 시 Score 편차 > 0.15   ← v1.2 수정 (교차 검증)
         배치 실행 환경에서 동일 입력을 2회 평가한 결과의 Score 차이가 0.15 초과
         → 판정 일관성 없음 → 휴먼 검토 필수
         ※ 단일 실행 환경에서는 판정 불가 — 배치 집계 단계에서 자동 감지
         ※ 감지 기준:
              |Score_1회차 - Score_2회차| > 0.15 → is_judge_unstable: true
              판정(verdict)이 두 회차 간 다른 경우 → 자동 1단계 전수검토 대상
```

**출력:**
```
is_judge_unstable: <true | false>
unstable_reasons: ["<해당 조건 번호와 내용>"]  ← is_judge_unstable=true일 때만 작성
score_variance: "<1회차와 2회차 Score 차이. 단일 실행 시 null>"
```

**is_judge_unstable=true 처리 방침:**
- 조건 1~6 해당: 테스트 우선순위 1단계(is_outlier와 동시 발생) 또는 2단계로 자동 분류
- 조건 7 해당 (재평가 편차): 판정이 달라진 경우 무조건 1단계 전수검토 / 판정 동일하면 3단계
- 집계 시 별도 통계 항목으로 집계
  - is_judge_unstable 발생 비율 (전체)
  - 조건 7 단독 발생 비율 (Judge 재현율 지표로 활용)

---

## Step 7. Score 계산 및 최종 판정

### 수치 변환 테이블

| 항목 | 등급 | 수치 | 지표 매핑 |
|------|------|------|-----------|
| A. 쿼리 의도 파악 | PASS | 1.00 | Rel |
| | PARTIAL | 0.70 | |
| | FAIL | 0.30 | |
| B. 텍스트 답변 품질 | GOOD | 1.00 | Acc |
| | ACCEPTABLE | 0.70 | |
| | POOR | 0.30 | |
| C. 상위 30개 관련성 | HIGH | 1.00 | Rel 보완 |
| | MEDIUM | 0.70 | |
| | LOW | 0.30 | |
| D. 전체 노이즈 비율 | LOW | 1.00 | Rel 역산 |
| | MEDIUM | 0.70 | |
| | HIGH | 0.30 | |
| E. 전체 다양성 | GOOD | 1.00 | 독립 집계 |
| | ACCEPTABLE | 0.70 | |
| | POOR | 0.30 | |
| F. 페르소나 일치도 | PASS | 1.00 | Pers |
| | PARTIAL | 0.70 | |
| | FAIL | 0.30 | |

### 공통 지표 계산

```
Rel  = (A 수치 × 0.5) + (C_avg_relevance × 0.3) + ((1 - 노이즈비율) × 0.2)
Acc  = B 수치
Pers = F 수치
Comp = Step 4 실제 계산값  (Grade A FAIL 시 = 0)
```

### 싱글턴 Score 공식 (4지표)

```
Score = Rel × 0.35 + Pers × 0.15 + Acc × 0.30 + Comp × 0.20  ← v1.3: Pers↓ Acc↑
```

### 멀티턴 Score 공식 (5지표) ← v1.0 신규 ★

```
Score = Rel × 0.30 + Pers × 0.10 + Acc × 0.25 + Ctx_final × 0.20 + Comp × 0.15  ← v1.3: Pers↓ Acc↑ Ctx↑

※ Ctx_final = Step 4-M에서 계산한 드리프트 보정값
※ Turn 1은 Ctx_final이 null → 해당 턴은 싱글턴 공식으로 대체 계산
   (Turn 1 Score = Rel × 0.35 + Pers × 0.15 + Acc × 0.30 + Comp × 0.20)
```

### 최종 판정 기준

```
# 1. 치명적 리스크 → 즉시 Fail (완화 예외)
A05 알레르기 누락 등 치명적 위반 → Fail

# 2. Fail 조건 (하나라도 해당)
Score < 0.65 OR Acc < 0.50 OR Comp < 0.50 OR 상품 0건 → Fail

# 3. Hard Pass 조건 (전부 충족 필요)
Score ≥ 0.85 AND Acc ≥ 0.85 AND Comp ≥ 0.85
  단, 아래 중 하나라도 해당하면 Hard Pass 불가 → Conditional Pass로 강등  ← v0.3.1
  - Grade A 누락 (is_grade_a_missing = true)
  - Top-K bad (is_top_k_bad = true, 상위 3개 Acc 평균 < 0.50)

# 4. 나머지 → Conditional Pass
Score ≥ 0.65 AND Acc ≥ 0.50 AND Comp ≥ 0.50  ← v0.3.1 완화

휴먼 검토 대상   : Acc 0.50~0.84 → human_review: true (is_outlier: true)  ← v0.3.1 완화
멀티턴 추가 조건 : Drift 발생 판정인 턴 → 2차 휴먼 검증 자동 플래깅
```

---

## Step 8. 테스트 우선순위 분류

**평가 완료 후 아래 4단계 기준으로 이 케이스의 우선순위를 분류합니다.**

```
1단계 (무조건 전수 검토):
  is_outlier=True AND is_judge_unstable=True 동시 발생
  → 판정 신뢰도 낮음. 반드시 휴먼이 직접 읽어야 함

2단계 (전수 검토):
  FAIL 유도 케이스인데 verdict=Conditional Pass 이상
  → Judge가 FAIL 케이스를 통과로 오판했을 가능성
  ※ FAIL 유도 케이스 = issue_types에 이슈가 있고 상품 0건이거나 노이즈 비율 > 30%

3단계 (정확성 집중 재검토):
  is_outlier=True (Acc 0.50~0.84 구간)  ← v0.3.1 완화
  1단계 해당 케이스 제외
  → 텍스트 답변 내 정보가 실제로 맞는지만 집중 확인

4단계 (샘플링 30% 검토):
  나머지 is_outlier=True
  → 전수 검토 불필요. 30% 샘플링으로 패턴 확인
```

**출력:**
```
test_priority: <1 | 2 | 3 | 4 | 해당없음>
priority_reason: "<1문장. 어떤 조건에 해당했는지>"
```

---

## 출력 형식 (JSON)

**싱글턴과 멀티턴은 출력 스키마가 다릅니다. eval_type에 맞는 스키마를 사용합니다.**

### 싱글턴 출력

```json
{
  "dataset": "<테스트셋명>",
  "query_id": "<번호>",
  "query": "<사용자 쿼리>",
  "search_type_name": "<검색 방식명>",
  "persona_id": "<페르소나 ID>",
  "eval_type": "싱글턴",

  "reasoning": "<Step 0에서 작성한 상위 3개 결과 비판적 분석. 50자 이상>",

  "top_k_check": {
    "top_3_acc_avg": "<상위 3개 상품 Acc 평균>",
    "is_top_k_bad": "<true|false>",
    "top_k_reason": "<1문장>"
  },

  "segment_tags": {
    "CATEGORY": "<카테고리명 또는 null>",
    "GENDER": "<성별 또는 null>",
    "BRAND": "<브랜드명 또는 null>",
    "COLOR": "<색상 또는 null>",
    "SIZE": "<사이즈 조건 또는 null>",
    "MATERIAL": "<소재·기능 또는 null>",
    "PRICE": "<가격 조건 또는 null>",
    "INTENT": "<recommend|compare|size_fit|function|stock|guide|event>"
  },

  "product_scores": [
    {
      "rank": "<순위>",
      "title": "<상품명>",
      "brand": "<브랜드>",
      "relevance_score": "<0~4>",
      "reason": "<score 2 이하 시 필수. 미충족 segment_tags 조건 명시>"
    }
  ],

  "comp_detail": {
    "grade_a_pass": "<true|false>",
    "grade_a_fail_reason": "<누락 시 이유. 통과 시 null>",
    "grade_b_results": {
      "재고상태": "<충족|미충족>",
      "원산지":   "<충족|미충족>",
      "카테고리": "<충족|미충족>",
      "핵심속성": "<충족|미충족>"
    },
    "grade_b_satisfied": "<0~4>",
    "Comp": "<0.30~1.00 또는 0>"
  },

  "evaluation": {
    "A_query_intent": "<PASS|PARTIAL|FAIL>",
    "A_score": "<0.30|0.70|1.00>",
    "A_reason": "<근거>",
    "B_text_quality": "<GOOD|ACCEPTABLE|POOR>",
    "B_score": "<0.30|0.70|1.00>",
    "B_reason": "<근거>",
    "C_top30_relevance": "<HIGH|MEDIUM|LOW>",
    "C_avg_relevance": "<0.00~1.00>",
    "C_reason": "<근거>",
    "D_noise_ratio": "<LOW|MEDIUM|HIGH>",
    "D_noise_pct": "<약 N%>",
    "D_low_relevance_items": ["<상품명 (score N, 미충족 조건)>"],
    "D_reason": "<근거>",
    "E_diversity": "<GOOD|ACCEPTABLE|POOR>",
    "E_score": "<0.30|0.70|1.00>",
    "E_top_brands": "<브랜드A(N개), 브랜드B(N개)>",
    "E_reason": "<근거>",
    "F_persona_match": "<PASS|PARTIAL|FAIL>",
    "F_score": "<0.30|0.70|1.00>",
    "F_reason": "<근거>",
    "F_miss_type": "<KEYWORD_MISSING|WRONG_TONE|BOTH|없음>",
    "Rel": "<계산값>",
    "Acc": "<계산값>",
    "Pers": "<계산값>",
    "Comp": "<Step 4 계산값>",
    "Score": "<계산값>",
    "score_formula": "싱글턴: Rel×0.35 + Pers×0.15 + Acc×0.30 + Comp×0.20",  // v1.3
    "verdict": "<Hard Pass|Conditional Pass|Fail>",
    "is_outlier": "<true|false>",
    "human_review": "<true|false>",
    "is_judge_unstable": "<true|false>",
    "unstable_reasons": ["<해당 조건>"],
    "score_variance": "<재평가 편차값 또는 null (단일 실행 시)>",
    "grade_a_demoted": "<true|false>",
    "issue_types": ["<PARAM_MISMATCH|DATA_QUALITY|COVERAGE_GAP|COMP_FAIL|없음>"],
    "issue_detail": "<1문장>",
    "test_priority": "<1|2|3|4|해당없음>",
    "priority_reason": "<1문장>"
  },

  "summary": {
    "strengths": "<강점>",
    "weaknesses": "<약점>",
    "recommendations": "<개선 권고>",
    "notes": "<특이사항 또는 없음>"
  }
}
```

---

### 멀티턴 출력

```json
{
  "dataset": "<테스트셋명>",
  "scenario_id": "<시나리오 ID>",
  "query_id": "<번호>",
  "turn_number": "<현재 턴 번호>",
  "query": "<사용자 쿼리>",
  "search_type_name": "<검색 방식명>",
  "persona_id": "<페르소나 ID>",
  "eval_type": "멀티턴",

  "segment_tags": { "...": "싱글턴과 동일" },

  "product_scores": [ "싱글턴과 동일" ],

  "comp_detail": { "...": "싱글턴과 동일" },

  "ctx_detail": {
    "Ctx_score_this_turn": "<0.00~1.00 또는 null (Turn 1)>",
    "Ctx_reason": "<1문장>",
    "delta_ctx": "<ΔCtx 값 또는 null (Turn 1)>",
    "drift_status": "<정상|Warning|Drift발생|null>",
    "drift_count_total": "<시나리오 누적 Drift 횟수>",
    "Drift_penalty": "<0.00|0.10|0.20>",  // v1.3 완화
    "Ctx_score": "<선형 가중 집계값 또는 null>",
    "Ctx_final": "<보정 후 값 또는 null>",
    "cumulative_drift": "<Ctx_2 - Ctx_n 또는 null>"
  },

  "evaluation": {
    "A_query_intent": "<PASS|PARTIAL|FAIL>",
    "A_score": "<0.30|0.70|1.00>",
    "A_reason": "<근거>",
    "B_text_quality": "<GOOD|ACCEPTABLE|POOR>",
    "B_score": "<0.30|0.70|1.00>",
    "B_reason": "<근거>",
    "C_top30_relevance": "<HIGH|MEDIUM|LOW>",
    "C_avg_relevance": "<0.00~1.00>",
    "C_reason": "<근거>",
    "D_noise_ratio": "<LOW|MEDIUM|HIGH>",
    "D_noise_pct": "<약 N%>",
    "D_low_relevance_items": ["<상품명 (score N, 미충족 조건)>"],
    "D_reason": "<근거>",
    "E_diversity": "<GOOD|ACCEPTABLE|POOR>",
    "E_score": "<0.30|0.70|1.00>",
    "E_top_brands": "<브랜드A(N개)>",
    "E_reason": "<근거>",
    "F_persona_match": "<PASS|PARTIAL|FAIL>",
    "F_score": "<0.30|0.70|1.00>",
    "F_reason": "<근거>",
    "F_miss_type": "<KEYWORD_MISSING|WRONG_TONE|BOTH|없음>",
    "Rel": "<계산값>",
    "Acc": "<계산값>",
    "Pers": "<계산값>",
    "Ctx_final": "<Step 4-M 계산값 또는 null (Turn 1)>",
    "Comp": "<Step 4 계산값>",
    "Score": "<계산값>",
    "score_formula": "<멀티턴: Rel×0.30 + Pers×0.10 + Acc×0.25 + Ctx_final×0.20 + Comp×0.15 | Turn1은 싱글턴 공식(Pers×0.15, Acc×0.30)>",  // v1.3
    "verdict": "<Hard Pass|Conditional Pass|Fail>",
    "is_outlier": "<true|false>",
    "human_review": "<true|false>",
    "drift_human_flag": "<true|false>",
    "is_judge_unstable": "<true|false>",
    "unstable_reasons": ["<해당 조건>"],
    "issue_types": ["<PARAM_MISMATCH|DATA_QUALITY|COVERAGE_GAP|COMP_FAIL|없음>"],
    "issue_detail": "<1문장>",
    "test_priority": "<1|2|3|4|해당없음>",
    "priority_reason": "<1문장>"
  },

  "summary": {
    "strengths": "<강점>",
    "weaknesses": "<약점>",
    "recommendations": "<개선 권고>",
    "notes": "<특이사항 또는 없음>"
  }
}


---

## 주의사항

- 싱글턴은 Step 0→1→2→2-K→3→4→5→6→7→8 순서, 멀티턴은 Step 0→1→2→2-K→3→3-M→4→4-M→5→6→7→8 순서로 진행한다  ← v1.3
- segment_tags는 쿼리에 명시된 속성만 추출한다. 추론으로 채우지 않는다
- product_scores는 상위 30개 전체 출력 (30개 미만이면 전체)
- relevance_score 2 이하인 상품은 reason 필드에 미충족 segment_tags 조건을 명시한다
- **Step 4 Comp 계산은 반드시 실제 상품 목록을 보고 수행한다. 추정값·고정값 사용 금지**
- Grade A 체크: 상위 5개 상품 기준. 3개 이상이 항목 누락 시 최대 Conditional Pass 강등
  단, A05 알레르기 누락 등 치명적 위반은 즉시 Fail 유지
- Grade B 체크: 전체 상품 기준. 50% 이상 포함 시 충족
- 상품 0개인 경우: Grade A FAIL → Comp=0 → 즉시 Fail. product_scores 빈 배열
- Grade A 누락(상품 있음): Comp 계산은 진행하되 최대 Conditional Pass 강등. Hard Pass 불가
- Comp < 0.50이면 Score·Acc 조건과 무관하게 즉시 Fail  ← v1.3 완화
- **키워드 존재 ≠ 정보 존재**: 텍스트에 키워드가 있어도 실제 정보가 맞는지 확인할 것
- F 항목은 내용의 옳고 그름이 아니라 톤·어휘만 판단한다. B 항목과 혼동하지 않는다
- is_judge_unstable 조건은 **7개 중 2개 이상** 해당 시 true (v1.0: 조건7 재평가 편차 추가)
- 조건 7은 배치 집계 단계에서 자동 감지. 단일 실행 시 score_variance = null
- is_outlier는 다음 중 하나라도 해당 시 자동 true  ← v1.3 확장
  (1) Acc(B_score)가 0.50~0.84 구간
  (2) 상위 3개 상품 Acc 평균(top_3_acc_avg) < 0.50 (Step 2-K 결과)
- human_review는 is_outlier=true일 때 자동 true
- reasoning 필드가 20자 미만이면 is_judge_unstable=true로 자동 태깅  ← v0.3.1 기준
- **멀티턴 Turn 1**: Ctx = null, 드리프트 계산 없음, Score는 싱글턴 공식 적용
- **멀티턴 Warning**: 패널티 없음. 플래그만 기록하고 다음 턴에서 모니터링
- **Ctx 측정 기준**: Turn 2부터. ctx_history는 [Turn2_Ctx, Turn3_Ctx, ...] 순서
- Cumulative_Drift 기준 턴은 Ctx_2 (Turn 1은 null이므로 첫 측정 가능 턴은 Turn 2)
- dataset 필드에 테스트셋 이름 명시 필수 (집계 시 사용됨)
- test_priority는 반드시 1→2→3→4 순서로 체크하고 가장 먼저 해당되는 단계를 기록한다

---

## HTML 리포트 출력 지시사항

**평가 완료 후, 결과를 HTML 파일로 출력한다.**
JSON 출력과 별도로, 아래 구조를 갖춘 HTML 시각화 리포트를 생성한다.

### 리포트 필수 구성 요소

```
1. 대시보드 헤더
   - 테스트셋명 / 검색방식 / 평가일
   - KPI 카드: 평균 Score / Hard Pass / Conditional Pass / Fail / Grade A FAIL / Judge불안정

2. 탭 구성 (이모티콘 없이 텍스트만 사용)
   - 탭1: 종합 분석    → 카테고리별 Score 바 차트 + 이슈 분포
   - 탭2: Comp 분석    → Comp 점수 분포 + Grade B 항목별 충족률
   - 탭3: 싱글턴       → 쿼리별 카드 + 필터 (판정/페르소나/이슈/우선순위/텍스트검색)
   - 탭4: 멀티턴       → 시나리오별 카드 + 턴 흐름

3. 쿼리 카드 (싱글턴/멀티턴 공통)
   - A~F 항목 평가 그리드 (색상: pass=초록 / partial=노랑 / fail=빨강)
   - Step 4 Comp 실제 계산 상세 (Grade A 판정 + Grade B 4개 항목 충족 여부)
   - 텍스트 답변 미리보기
   - 상위 상품 relevance_score 목록
   - 세그먼트 태그 / 이슈 유형 배지 / 테스트 우선순위 배지
   - [검색 결과 JSON viewer] 버튼
```

### 이모티콘 사용 금지

탭 버튼, 배지, 버튼, 섹션 제목 등 **모든 영역에서 이모티콘을 사용하지 않는다.**

### 검색 결과 상품 JSON 뷰어 (필수 탑재)

각 쿼리 카드 또는 멀티턴 턴 카드의 **[검색 결과 JSON viewer]** 버튼 클릭 시
현재 리포트 내부에서 접히는 JSON/textarea를 노출하지 말고, **새 창(window.open)** 으로 상품 카드형 뷰어를 열어야 한다.
뷰어는 아래 UX를 따른다.

- 새 창 제목: `{query_id} - 상품 JSON 뷰어`
- 새 창 헤더: `{query_id} - 검색 결과 상품 뷰어`
- 헤더 하단에 사용자 쿼리 또는 턴 쿼리를 한 줄로 표시
- 요약 바: 총 상품 수 / 재고있음 / 품절 / 평균가격
- 본문: 상품 이미지 중심 카드 그리드
- 카드 필수 노출: 순위, 재고 상태 점, 상품 이미지, 브랜드, 상품명, 가격, 노이즈 의심 배지
- 카드 클릭 시 상품 상세 URL이 있으면 새 탭으로 이동
- 상품 0건이면 새 창 안에 “상품 없음” empty state를 표시
- 팝업이 차단되면 `alert`로 팝업 허용 안내
- 기존 리포트 화면 안에는 상품 row, raw JSON, textarea를 펼쳐 보이지 않는다

아래 코드를 기준으로 구현한다:

```javascript
// 상품 데이터는 평가 시 파싱한 JSON을 JS 변수로 직접 임베드
// 예: const SINGLE_PRODUCTS = { "Q001": [...], "Q002": [...] };
//     const MULTI_PRODUCTS  = { "MT001_T1": [...], "MT001_T2": [...] };
// 쿼리/턴 메타도 함께 임베드한다.
// 예: const PRODUCT_META = { "Q001": { query: "...", total_count: 94 }, ... };

const NOISE_KWS = ['インソール','ソルボ','サポーター','シューレース','シュー レース','靴ひも','お手入れ','補修','ローション','槌','中敷'];

function showProductViewer(key, type) {
  const list = (type === 'single' ? SINGLE_PRODUCTS[key] : MULTI_PRODUCTS[key]) || [];
  const meta = PRODUCT_META[key] || {};
  const total = Number(meta.total_count || list.length || 0);

  const isInStock = p => /in.?stock|available|재고|판매중/i.test(String(p.availability || p.stock_status || '')) &&
                         !/out/i.test(String(p.availability || p.stock_status || ''));
  const inSt  = list.filter(isInStock).length;
  const outSt = list.length - inSt;
  const prices = list.map(p => parseFloat(p.selling_price)||0).filter(p => p > 0);
  const avg = prices.length ? Math.round(prices.reduce((a,b)=>a+b,0)/prices.length) : 0;
  const esc = v => String(v ?? '').replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
  const productUrl = p => p.product_url || p.url || p.link || '#';
  const productImg = p => p.cdn_main_url || p.image_url || p.image || '';

  const cardsHtml = list.length === 0
    ? '<div class="empty">상품 없음</div>'
    : list.map((p, i) => {
        const title = p.title || p.name || '-';
        const noise = NOISE_KWS.some(k => title.includes(k));
        const inStock = isInStock(p);
        const price = parseFloat(p.selling_price) || 0;
        const imgUrl = productImg(p);

        return `<a class="product-card ${noise ? 'is-suspicious' : ''}" href="${esc(productUrl(p))}" target="_blank" rel="noopener">
          <span class="rank">#${i+1}</span>
          <span class="stock-dot ${inStock ? 'in' : 'out'}" title="${esc(p.availability || '')}"></span>
          <div class="image-wrap">
            ${imgUrl ? `<img src="${esc(imgUrl)}" alt="" onerror="this.parentElement.innerHTML='<div class=no-image>NO IMAGE</div>'">` : '<div class="no-image">NO IMAGE</div>'}
          </div>
          <div class="product-body">
            <div class="brand">${esc(p.brand_name || p.brand || '미즈노')}</div>
            <div class="title">${esc(title)}</div>
            <div class="price">${price ? '¥' + price.toLocaleString('ja-JP') : '-'} <span>${esc(p.currency || 'JPY')}</span></div>
            ${noise ? '<div class="risk">노이즈 의심</div>' : ''}
          </div>
        </a>`;
      }).join('');

  const w = window.open('about:blank', key + '-product-viewer', 'width=1440,height=920,scrollbars=yes,resizable=yes');
  if (!w) {
    alert('팝업이 차단되었습니다. 브라우저에서 팝업 허용 후 다시 열어주세요.');
    return;
  }

  w.document.open();
  w.document.write(`<!DOCTYPE html><html lang="ko"><head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <title>${esc(key)} - 상품 JSON 뷰어</title>
    <style>
      *{box-sizing:border-box}
      body{margin:0;background:#eef2f7;color:#1f2937;font-family:Arial,'Pretendard','Noto Sans KR',sans-serif}
      .topbar{position:sticky;top:0;z-index:10;background:linear-gradient(135deg,#06158c,#0b238f);color:#fff;padding:24px 30px 22px;box-shadow:0 2px 12px rgba(0,0,0,.12)}
      .topbar-inner{display:flex;align-items:center;justify-content:space-between;gap:16px}
      .topbar h1{font-size:22px;line-height:1.25;margin:0 0 6px;font-weight:800}
      .topbar p{margin:0;color:rgba(255,255,255,.7);font-size:13px;max-width:920px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
      .close-btn{border:1px solid rgba(255,255,255,.28);background:rgba(255,255,255,.14);color:#fff;border-radius:7px;padding:9px 22px;font-weight:700;cursor:pointer}
      .close-btn:hover{background:rgba(255,255,255,.22)}
      .summary{display:flex;gap:26px;align-items:center;padding:14px 30px;background:#fff;border-bottom:1px solid #dfe5ef;color:#64748b;font-weight:700}
      .summary b{color:#172554}.summary .good{color:#20b866}.summary .bad{color:#ef4444}.summary .price{color:#1d4ed8}
      .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(218px,1fr));gap:18px;padding:28px 30px 36px}
      .product-card{position:relative;display:flex;flex-direction:column;min-height:292px;text-decoration:none;color:inherit;background:#fff;border:1px solid #dfe5ef;border-radius:8px;overflow:hidden;box-shadow:0 1px 2px rgba(15,23,42,.05);transition:transform .12s ease,box-shadow .12s ease,border-color .12s ease}
      .product-card:hover{transform:translateY(-2px);box-shadow:0 10px 22px rgba(15,23,42,.12);border-color:#b8c5d8}
      .product-card.is-suspicious{border-color:#ffb4b4}
      .rank{position:absolute;top:10px;left:10px;z-index:2;background:rgba(31,41,55,.78);color:#fff;border-radius:5px;padding:3px 8px;font-size:13px;font-weight:800}
      .stock-dot{position:absolute;top:12px;right:12px;z-index:2;width:11px;height:11px;border-radius:50%;box-shadow:0 0 0 2px rgba(255,255,255,.9)}
      .stock-dot.in{background:#22c55e}.stock-dot.out{background:#ff3f46}
      .image-wrap{height:158px;background:#f8fafc;display:flex;align-items:center;justify-content:center;border-bottom:1px solid #edf1f6}
      .image-wrap img{max-width:100%;width:100%;height:100%;object-fit:contain}
      .no-image{color:#94a3b8;font-size:12px;font-weight:800}
      .product-body{padding:14px 14px 13px;display:flex;flex-direction:column;gap:6px;min-height:134px}
      .brand{font-size:12px;font-weight:800;color:#8aa0c0}
      .title{font-size:14px;line-height:1.45;font-weight:800;color:#1f2937;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;min-height:40px}
      .price{margin-top:auto;color:#ef4444;font-size:20px;font-weight:900;letter-spacing:0}
      .price span{font-size:12px;color:#94a3b8;font-weight:800}
      .risk{align-self:flex-start;background:#fee2e2;color:#ef4444;font-size:12px;font-weight:800;border-radius:4px;padding:2px 6px}
      .empty{grid-column:1/-1;text-align:center;color:#64748b;background:#fff;border:1px solid #dfe5ef;border-radius:8px;padding:46px}
      @media(max-width:720px){.topbar,.summary{padding-left:16px;padding-right:16px}.topbar-inner{align-items:flex-start;flex-direction:column}.summary{gap:12px;flex-wrap:wrap}.grid{padding:16px;grid-template-columns:repeat(auto-fill,minmax(164px,1fr));gap:12px}.product-card{min-height:270px}.image-wrap{height:132px}.topbar p{white-space:normal}.close-btn{align-self:flex-end}}
    </style>
  </head><body>
    <header class="topbar">
      <div class="topbar-inner">
        <div>
          <h1>${esc(key)} - 검색 결과 상품 뷰어</h1>
          <p>${esc(meta.query || (type === 'single' ? '싱글턴 검색 결과' : '멀티턴 검색 결과'))}</p>
        </div>
        <button class="close-btn" onclick="window.close()">닫기</button>
      </div>
    </header>
    <section class="summary">
      <span>총 <b>${total.toLocaleString('ko-KR')}개</b></span>
      <span>재고있음 <b class="good">${inSt.toLocaleString('ko-KR')}개</b></span>
      <span>품절 <b class="bad">${outSt.toLocaleString('ko-KR')}개</b></span>
      <span>평균가격 <b class="price">${avg ? '¥' + avg.toLocaleString('ja-JP') : '-'}</b></span>
    </section>
    <main class="grid">${cardsHtml}</main>
  </body></html>`);
  w.document.close();
  w.focus();
}
```

### 버튼 삽입 위치

```html
<!-- 싱글턴 카드 헤더 -->
<button class="jv-toggle-btn" onclick="showProductViewer('Q001', 'single')">검색 결과 JSON viewer</button>

<!-- 멀티턴 턴 카드 -->
<button class="jv-toggle-btn sm" onclick="showProductViewer('MT001_T1', 'multi')">JSON</button>
```

### 데이터 임베드 방식

평가 결과 HTML을 생성할 때, 각 쿼리의 `response_text`(상품 JSON)를
아래 형식으로 `<script>` 블록에 직접 임베드한다.

```javascript
const SINGLE_PRODUCTS = {
  "Q001": [ { "rank": 1, "title": "...", "brand_name": "...", "selling_price": 12300,
              "currency": "JPY", "availability": "InStock", "cdn_main_url": "...",
              "product_url": "..." }, ... ],
  "Q002": [ ... ],
  // 전체 쿼리 포함
};

const MULTI_PRODUCTS = {
  "MT001_T1": [ ... ],
  "MT001_T2": [ ... ],
  // 전체 시나리오·턴 포함
};

const PRODUCT_META = {
  "Q001": { "query": "初心者向けのジョギングシューズはありますか？", "total_count": 94 },
  "MT001_T1": { "query": "...", "total_count": 70 }
};
```

임베드 시 각 상품 객체는 최소한 아래 필드를 포함해야 한다:
`rank` / `title` / `brand_name` / `selling_price` / `currency` / `availability` / `cdn_main_url` / `product_url`
