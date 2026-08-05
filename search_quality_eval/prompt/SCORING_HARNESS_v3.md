# 채점 하네스 (SCORING_HARNESS)

genser-adk2 검색 에이전트 QA 채점용 **결정론적 rubric**. 목표는 단 하나:
**QA팀 AI 도구가 어떤 LLM 모델을 쓰든 같은 transcript에 같은 PASS/FAIL을 낸다.**

## 1. 목적 / 원칙

- **모델 무관 동일 결과**가 최우선. 같은 케이스를 flash-lite로 채점하든 Opus로 채점하든 결론이 같아야 한다.
- 모델별 편차의 원인은 **주관 항목**이다. flash-lite judge는 "칩이 약하다", "설명이 부자연스럽다" 같은 인상으로 과벌점한다(예: mizuno 2/15=13%). Opus 직접 심사는 ~90%. 이 격차는 거의 전부 주관 평가에서 나온다.
- 따라서 **주관(칩 자연스러움·설명 매끄러움·영업력·과장 어조)은 PASS/FAIL 판정에서 완전히 제외**한다. 필요하면 별도 `note` 메모로만 남기고, verdict에는 영향을 주지 않는다.
- PASS/FAIL은 아래 **R1~R5 결정론적 규칙**만으로 결정한다. 규칙은 transcript에 실제로 적힌 값(titles / ans / n / intent)으로 검증 가능한 것만 담는다.
- **이진 판정**: 부분점수 없음. R1~R5를 전부 만족하면 PASS, 하나라도 위반하면 FAIL.

## 2. 입력 형식

채점 입력은 `run_eval.py`가 떨군 transcript JSON
(`/tmp/eval_<iter>_<vendor>_transcripts.json`). 케이스 배열이며 두 종류다.

### 단일턴 케이스
```json
{
  "cid":   "mizuno:S:0",           // 케이스 ID (vendor:S:index)
  "q":     "安全靴を探しています。",   // 사용자 쿼리
  "intent":"正答=… 異常値=…",        // 정답 기준 (아래 규약)
  "n":     20,                      // 결과 상품 수
  "cats":  ["ブーツ","ローカット"],   // 결과 카테고리(최대 6, 참고용)
  "titles":["【ミズノ公式】… ", …],   // 결과 상품명(최대 10) — 정합 검증의 핵심 근거
  "matched":[],                     // 일치 색상(있으면)
  "chips": ["ローカット安全靴", …],   // 액션 칩(참고용, 판정 제외)
  "ans":   "ミズノの安全靴ですね…",    // 에이전트 답변 텍스트
  "product_scores": [               // 검색 결과 상품 상세 (있으면)
    {
      "rank": 1,
      "title": "【ミズノ公式】…",
      "image_url": "https://…webp",
      "selling_price": 12100.0,
      "currency": "JPY",
      "stock_status": "in_stock",
      "relevance_score": 4,         // 0~4
      "relevance_label": "적합",    // 적합 / 부분 적합 / 부적합
      "comment_skipped": true,
      "violated_conditions": [],
      "reason": null
    }
  ]
}
```

실제 레포트 생성에 사용하는 JSON(`*_report.json`)의 대응 필드:

| 채점 필드 | report JSON 필드 | 비고 |
|---|---|---|
| `cid` | `query_id` | "Q001", "MT001" 등 |
| `q` | `query` | 사용자 쿼리 텍스트 |
| `ans` | `answer_text` | 에이전트 답변 전문 |
| `chips` | `keyword_relevance_check.keywords` | 에이전트가 생성한 관련 검색어 |
| `n` | `product_count` | 결과 상품 수 (문자열) |
| `product_scores` | `product_scores` | 상품별 관련도 배열 |
| `eval_type` | `eval_type` | "싱글턴" / "멀티턴" |
| `scenario_id` | `scenario_id` | 멀티턴 시나리오 ID |
| `turn_number` | `turn_number` | 멀티턴 턴 번호 |

### 멀티턴 케이스
```json
{
  "cid":   "mizuno:M:junior_pitcher_glove",
  "intent":"…段階的に絞り込み、整合した提案に収束するか",  // 시나리오 전체 의도
  "turns": [
    {
      "q":"…", "n":0, "cats":[], "titles":[], "chips":[…], "ans":"…",
      "product_scores": []
    },
    {
      "q":"…", "n":3, "cats":[…], "titles":[…], "chips":[…], "ans":"…",
      "product_scores": [/* … */]
    }
  ]
}
```
멀티턴은 `turns` 배열을 가진다. 각 턴은 단일턴과 같은 필드(intent 제외)를 갖고,
시나리오 의도는 케이스 최상위 `intent` 하나에만 적혀 있다.

### `intent` 규약 (정답 기준이 여기 다 적혀 있음)
- `正答=…` (정답=): 결과 titles가 만족해야 하는 상품 종류·속성. **R1의 기준.**
- `異常値=…` / `…が混入したら異常値` (이상치=): titles에 섞이면 안 되는 무관 항목. **R3의 기준.**
- `text↔product整合` 명시: 답변이 든 상품이 titles에 실재해야 함. **R2가 항상 적용되나, 이 문구가 있으면 특히 엄격히.**
- 하드 제약(`price_current<=5000`, `グレー以外`, `レディース`, 사이즈, 산지 등): **R5의 기준.**

## 3. 결정론적 판정 규칙 (R1~R5)

PASS = 아래 **다섯 규칙을 모두** 만족. 하나라도 위반하면 FAIL.
모든 규칙은 transcript의 `titles` / `ans` / `n` / `intent` 값만으로 검증한다.

| 규칙 | 이름 | PASS 조건 | FAIL 예 |
|---|---|---|---|
| **R1** | 의도 충족 | `intent`의 `正答=` 조건을 titles의 **다수(과반)**가 만족 | "安全靴" 의도인데 titles 다수가 일반 러닝화 |
| **R2** | text↔product 정합 | `ans`가 언급한 **구체 상품/모델/속성**이 titles(또는 결과)에 **실재** | ans가 "○○モデルがおすすめ"라는데 titles에 그 모델 없음(환각) |
| **R3** | 카테고리 정확 | `intent`의 `異常値=` 항목이 titles에 **혼입되지 않음** | "안전화" 의도 결과에 골프화/경기화가 섞임 |
| **R4** | 0건 정직 | `n=0`이면 `ans`가 **"없음"을 정직히** 말하고 **대체 제안**을 함 | n=0인데 ans가 상품이 있는 것처럼 추천(있는 척) |
| **R5** | 하드 조건 | `intent`의 명시 제약(가격/색/사이즈/성별/산지 등)을 결과가 충족 | "5천엔 이하"인데 titles/ans에 초과품 제시, "그레이 제외"인데 그레이 혼입 |

규칙별 판정 세칙:

- **R1 — 다수 기준.** "다수"는 결과 상품의 과반(50% 초과)을 뜻한다. 소수(1~2건)의 경계성 상품은 위반으로 보지 않는다. titles가 비어도 `intent`가 결과를 요구하면(0건이 정답이 아니면) R1 위반 — 단 이때는 R4로도 본다.
- **R2 — 환각 차단.** ans가 **고유한 상품명·모델명·구체 수치(사이즈 범위, 가격 등)**를 단정하면 그것이 titles에 있거나 결과로 뒷받침돼야 한다. "様々なタイプがございます" 같은 **일반 서술은 R2 대상 아님**(검증할 구체 주장이 없으므로 통과). 답변에 든 모델명이 titles의 잘린 문자열(최대 46자)과 합치하면 실재로 본다.
- **R3 — 이상치 혼입.** `異常値=`에 적힌 카테고리/속성이 titles에 **하나라도** 분명히 들어오면 위반. 판단이 애매한(이상치인지 정답인지 모를) 1건은 위반으로 치지 않는다 — `異常値=` 문구에 명확히 해당할 때만 FAIL.
- **R4 — 0건 정직.** 적용 트리거는 `n=0`(단일턴) 또는 검색이 필요한 턴의 `n=0`(멀티턴). PASS하려면 ans가 (a) 해당 조건으로 결과가 없음을 정직히 인정하고 (b) 대체(예산 상향·관련 카테고리·근사 상품)를 제시해야 한다. 둘 중 하나라도 빠지거나, 없는데 있는 척하면 FAIL. **`intent`가 "0건은 안 됨/공백 불가"(예: `QAで0件だったが…必ず提示すべき`)라고 명시하면, n=0 자체가 R1+R4 위반.**
- **R5 — 하드 조건.** `intent`에 수치·열거형 제약이 명시된 경우만 적용. 가격은 ans/titles에 초과품이 제시되면 위반. 색·성별·사이즈·산지는 `異常値=`에서 R3와 겹칠 수 있으나, **명시 제약 위반은 R5로도 기록**한다(둘 다 적어도 됨, verdict는 어차피 FAIL).

### 멀티턴 추가 규칙
멀티턴은 위 R1~R5를 **각 턴에 적용**하되, 시나리오 전체에 다음을 더한다.

- **수렴.** 마지막 턴 결과가 **그때까지 누적된 모든 조건**(예: 포지션+이용손+가격대+색)에 부합해야 한다.
- **드리프트 금지.** 이전 턴에서 좁힌 조건이 뒤 턴에서 **사라지거나 모순**되면 FAIL(drift). 예: "왼손잡이"로 좁혔는데 이후 턴 titles에 오른손용이 다시 섞임.
- **기능 한계 정직 고백은 FAIL 아님.** 에이전트가 못 하는 걸(예: "무게로 정렬·필터하는 기능은 없습니다") 정직히 말하고 기존 결과/대안을 유지하면 PASS. 지어내서 답하면 FAIL.
- **판정 합산.** 모든 턴이 위반 없음 + 수렴/무드리프트면 케이스 PASS. **한 턴이라도 R 위반·드리프트면 케이스 FAIL.** (탐색을 점진적으로 좁히는 정상 흐름은 드리프트가 아니다.)

## 4. 점수 산출

- 케이스 단위 **이진**(PASS=1 / FAIL=0). 부분점수 없음.
- **벤더별 PASS 비율(%)** = (PASS 케이스 수) / (채점 케이스 수) × 100.
- **전체 평균** = 4벤더(mizuno / yamato / shoplist / guud) PASS 비율의 단순 평균.
- 보고 형식:
  ```
  vendor     PASS / TOTAL   rate
  mizuno       13 / 15       86.7%
  yamato       ...
  shoplist     ...
  guud         ...
  ──────────────────────────────
  전체 평균                   xx.x%
  ```
- FAIL 케이스는 `cid` + `violated`(위반 규칙) + `reason` 한 줄로 함께 보고한다.

## 5. 판정 프롬프트 템플릿

LLM에 케이스별로 아래를 준다(단일턴/멀티턴 각각). `{…}`만 치환.
온도 0, JSON만 강제.

### 단일턴
```
당신은 EC 검색 결과 채점기다. 아래 규칙 R1~R5만으로 PASS/FAIL을 정한다.
주관적 인상(칩이 매력적인가, 설명이 매끄러운가, 영업력, 어조)으로는 절대 감점하지 말 것.
R1~R5 위반이 입증될 때만 FAIL. 애매하면 PASS. 추측으로 위반을 만들지 말 것.

[R1] 의도 충족: intent의 "正答="(정답) 조건을 titles의 과반이 만족하는가.
[R2] text↔product 정합: ans가 단정한 구체 상품명·모델명·수치가 titles/결과에 실재하는가.
     (일반 서술 "様々なタイプ…"은 검증 대상 아님 → 통과.)
[R3] 카테고리 정확: intent의 "異常値="(이상치) 항목이 titles에 분명히 혼입되지 않았는가.
[R4] 0건 정직: n=0이면 ans가 없음을 정직히 인정하고 대체를 제안하는가.
     (n>0이면 R4는 자동 통과. intent가 "0건 불가/반드시 제시"라 적혀 있으면 n=0은 R1·R4 위반.)
[R5] 하드 조건: intent에 명시된 가격/색/사이즈/성별/산지 제약을 결과가 충족하는가.
     (명시 제약이 없으면 R5는 자동 통과.)

판정 시 의심스러우면 위 R 기준 문구를 그대로 인용해 근거로 삼는다.
주관 메모는 reason이 아니라 note로만 적는다(verdict에 영향 금지).

쿼리: {q}
의도(정답·이상치 기준): {intent}
결과수 n: {n}
상품명 titles: {titles}
답변 ans: {ans}

JSON만 출력:
{"verdict":"PASS|FAIL","violated":["R1"],"reason":"위반 규칙의 기준 문구 인용 + 근거 한 줄","note":"주관 메모(선택, 판정 무관)"}
PASS면 violated는 빈 배열 [].
```

### 멀티턴
```
당신은 EC 검색 멀티턴 대화 채점기다. 아래 R1~R5 + 멀티턴 규칙만으로 PASS/FAIL을 정한다.
주관적 인상(칩 매력·설명 매끄러움·영업력·어조)으로는 절대 감점하지 말 것.
R 위반·드리프트가 입증될 때만 FAIL. 애매하면 PASS.

각 턴에 R1~R5 적용:
[R1] 의도 충족  [R2] text↔product 정합  [R3] 카테고리 정확(이상치 혼입 금지)
[R4] 0건 정직(검색 턴 n=0이면 정직 인정+대체)  [R5] 하드 조건(명시 제약 충족)

시나리오 전체 규칙:
- 수렴: 마지막 턴 결과가 그때까지 누적된 모든 조건에 부합하는가.
- 드리프트 금지: 이전 턴에서 좁힌 조건이 뒤 턴에서 사라지거나 모순되면 FAIL.
  (점진적으로 좁히는 정상 흐름은 드리프트 아님.)
- 기능 한계를 정직히 고백하고 기존 결과/대안을 유지하면 FAIL 아님. 지어내면 FAIL.

한 턴이라도 R 위반·드리프트면 케이스 FAIL. 전부 통과 + 수렴이면 PASS.
의심스러우면 위 R/규칙 문구를 그대로 인용해 근거로 삼는다.

시나리오 의도: {intent}
대화(턴 배열, 각 턴 q/n/titles/ans): {turns}

JSON만 출력:
{"verdict":"PASS|FAIL","violated":["T2:R3","drift"],"reason":"위반 턴·규칙 + 근거 한 줄","note":"주관 메모(선택, 판정 무관)"}
PASS면 violated는 빈 배열 [].
```

## 6. 모델 편차 최소화 노트

같은 transcript에 모델이 달라도 같은 결론을 내게 하려면:

1. **온도 0** 고정. (run_eval.py 판정 호출과 동일: `temperature: 0`, thinking budget 0.)
2. **R1~R5 위반만이 FAIL 근거.** 칩·설명·영업력·어조 등 주관은 verdict에서 배제하고 `note`로만. 과벌점의 주원인이 여기이므로 가장 중요.
3. **의심스러우면 PASS, 그리고 R 기준 문구를 그대로 인용.** 위반을 주장하려면 `intent`의 `正答=`/`異常値=`/제약 문구를 reason에 인용해야 한다. 인용할 문구가 없으면 위반이 아니다.
4. **검증 대상은 transcript의 실제 값뿐.** titles에 없는 상품을 상상하거나, intent에 없는 제약을 추가해 감점하지 말 것.
5. **일반 서술은 R2 면제.** 구체 주장(모델명·수치)이 없으면 환각 판정 불가 → 통과. 모델마다 "이 설명이 부실하다"고 다르게 보는 것을 막는다.
6. **이진·과반 기준의 명시적 임계.** R1은 과반(50% 초과), R3는 명확한 이상치 1건 이상, R5는 명시 제약 위반 — 임계를 숫자로 고정해 모델 간 해석 흔들림을 줄인다.

> 운영 메모: flash-lite는 1차 트리아지에만 쓰고, 경계 케이스·최종 집계는 상위 모델이 transcript를 직접 R1~R5로 재심사하는 것을 권장한다. 단 어느 모델을 쓰든 **이 문서의 R1~R5와 임계가 유일한 판정 근거**다.

## 7. HTML 평가 결과서 출력 형식

채점 완료 후 결과를 HTML 파일로 내보낼 때 아래 사양을 따른다.
입력 소스는 `*_report.json` (meta / kpi / queries 배열 구조).

### 7-1. 기본 구조

```
header          — 벤더·날짜·채점 원칙 메타
section 01      — 요약 KPI (전체/PASS/FAIL/0건/위반 규칙별 카운트)
section 02      — 카테고리별 통과율 표 + 막대 시각화
section 03      — FAIL 케이스 상세 (위반 규칙 + 근거 한 줄)
section 04      — 핵심 인사이트 (패턴 분석)
section 05      — 전체 케이스 표 (단일턴 / 멀티턴 분리, details 토글)
footer          — 채점 기준·생성 시각
```

### 7-2. 전체 케이스 표 — 필수 컬럼

**단일턴 표**

| 컬럼 | report JSON 소스 | 설명 |
|---|---|---|
| 케이스 | `query_id` | 모노스페이스 강조 |
| 카테고리 | 케이스 유형 분류 | |
| **질의 / 답변 · 액션칩** | `query` + `answer_text` + `keyword_relevance_check.keywords` | 3단 인라인 셀 ← 7-3 참조 |
| n | `product_count` | 결과 상품 수, 숫자 우정렬 |
| 판정 | `evaluation.final_judgement` | PASS / FAIL 뱃지 |
| 위반 | 위반 규칙 코드 | R1~R5 / drift |
| 상품 | `product_scores` | 상품 뷰어 버튼 ← 7-4 참조 |

**멀티턴 표**는 `턴` 컬럼이 n 대신 들어가며, 질의/답변·칩 셀은 1턴 질의만 표시하고 상품 버튼은 `—`로 표시한다.

### 7-3. 질의 / 답변 · 액션칩 셀 (인라인 3단 구성)

답변과 액션칩은 별도 팝업 없이 **질의 셀 내부에 인라인으로 표시**한다.

#### 셀 내부 구조 (위→아래 순서)

```
┌─────────────────────────────────────────┐
│  ① 질의 텍스트                           │  .q-text
│                                         │
│  ② [칩1]  [칩2]  [칩3]  [칩4]           │  .q-chips  (없으면 생략)
│                                         │
│  │ ③ 답변 텍스트 (기본 3줄 접힘)          │  .q-answer.collapsed
│  │    …                                 │
│     ▾ 더보기                             │  .q-answer-toggle
└─────────────────────────────────────────┘
```

| 영역 | HTML 요소 | 소스 필드 | 렌더링 조건 |
|---|---|---|---|
| ① 질의 | `<div class="q-text">` | `query` | 항상 |
| ② 액션칩 | `<div class="q-chips">` + `<span class="q-chip">` | `keyword_relevance_check.keywords` | 배열이 1개 이상일 때만 |
| ③ 답변 | `<div class="q-answer collapsed" id="ans-{cid}">` | `answer_text` | 텍스트가 있을 때만 |
| 토글 | `<span class="q-answer-toggle">` | — | 답변이 있을 때만 |

#### 접기/펼치기 동작

- 답변 초기 상태: `collapsed` 클래스 → CSS `-webkit-line-clamp: 3`으로 3줄 표시
- **▾ 더보기** 클릭 → `collapsed` 클래스 제거, 전체 텍스트 노출, 토글 텍스트 **▴ 접기**로 변경
- **▴ 접기** 클릭 → `collapsed` 클래스 복원, 토글 텍스트 원복

```js
function toggleAns(id, btn) {
  const el = document.getElementById(id);
  if (!el) return;
  const collapsed = el.classList.toggle('collapsed');
  btn.textContent = collapsed ? '▾ 더보기' : '▴ 접기';
}
```

#### HTML 렌더링 예시

```html
<td class="q-cell">
  <!-- ① 질의 -->
  <div class="q-text">初心者向けのジョギングシューズはありますか？</div>

  <!-- ② 액션칩 (있을 때만) -->
  <div class="q-chips">
    <span class="q-chip">初心者向け定番 ウエーブライダー</span>
    <span class="q-chip">軽量で履きやすい マキシマイザー</span>
    <span class="q-chip">幅広設計のランニングシューズ</span>
    <span class="q-chip">10,000円以下のランニングシューズ</span>
  </div>

  <!-- ③ 답변 (있을 때만) -->
  <div class="q-answer collapsed" id="ans-Q001">ランニングを始められる方にぴったりのシューズをいくつかご用意しました。
ミズノのランニングシューズには…</div>
  <span class="q-answer-toggle" onclick="toggleAns('ans-Q001', this)">▾ 더보기</span>
</td>
```

### 7-4. 상품 뷰어 (Products Viewer)

검색 결과 상품을 모달 팝업으로 확인한다.

#### 버튼 규칙
- `product_scores` 배열이 1건 이상: **`상품 N건`** 버튼 (파란 테두리, 클릭 가능)
- `product_scores` 빈 배열 또는 `product_count=0`: **`0건`** 버튼 (disabled)
- 멀티턴 케이스: **`—`** (버튼 없음)

#### 모달 구성

```
┌──────────────────────────────────────────────┐
│ [Q001]  ウォーキング用でおすすめの靴は…  [JSON] [✕] │  ← 헤더
├──────────────────────────────────────────────┤
│  총 20건  적합 18  부분 2  부적합 0  평균관련도 3.90 │  ← 통계 바
├──────────────────────────────────────────────┤
│  ┌──────┐  ┌──────┐  ┌──────┐               │
│  │ 이미지│  │ 이미지│  │ 이미지│  …           │  ← 상품 카드 그리드
│  │ #1   │  │ #2   │  │ #3   │               │
│  │ 타이틀│  │ 타이틀│  │ 타이틀│               │
│  │ ¥xxx │  │ ¥xxx │  │ ¥xxx │               │
│  │[적합]│  │[적합]│  │[부분]│               │
│  └──────┘  └──────┘  └──────┘               │
│  ┌────────────────────────────────────────┐  │
│  │ JSON 패널 (토글, 기본 숨김)              │  │
│  └────────────────────────────────────────┘  │
└──────────────────────────────────────────────┘
```

**상품 카드 요소**

| 요소 | JSON 소스 | 비고 |
|---|---|---|
| 이미지 | `image_url` | `loading="lazy"`, 실패 시 "No Image" placeholder |
| 랭크 | `rank` | `#N` 모노스페이스 |
| 타이틀 | `title` | 전문 표시 |
| 가격 | `selling_price` | `¥N,NNN` 포맷 |
| 관련도 뱃지 | `relevance_label` | 적합/부분 적합/부적합 색상 구분 |
| 스코어 | `relevance_score` | `⭐N/4` |
| 사유 | `reason` | 있을 때만, 빨간 소형 텍스트 |

**카드 테두리 색상**

| `relevance_label` | 스타일 |
|---|---|
| `적합` | 기본 (neutral) |
| `부분 적합` | amber 테두리 |
| `부적합` | red-tint 배경 + 테두리 |

**JSON 패널**: `[JSON]` 버튼 토글, `<pre>` 코드 블록, max-height 320px, 기본 숨김

**닫기**: ✕ 버튼 / 배경 오버레이 클릭 / ESC 키

**0건 케이스**: 카드 그리드 대신 안내 메시지 표시
```
📭 검색 결과 0건 — 해당 케이스는 상품이 반환되지 않았습니다.
```

### 7-5. JS 데이터 주입 방식

상품 뷰어용 `PRODUCTS_DB` 만 JS 상수로 주입한다.
답변 텍스트와 액션칩은 HTML 생성 시 각 셀에 직접 삽입하므로 별도 DB 불필요.

```html
<script>
const PRODUCTS_DB = {
  "Q001": [ { "rank": 1, "title": "…", "image_url": "…", "selling_price": 12100, … }, … ],
  "Q002": [ … ],
  // product_scores 가 빈 케이스는 빈 배열 []
};
</script>
```

**키**: `query_id` 문자열 ("Q001", "MT001" 등)

버튼 `onclick` 패턴:

```html
<button class="btn-products"
        onclick="openProducts('Q001', &quot;쿼리텍스트&quot;)">상품 13건</button>
```

### 7-6. 스타일 가이드 (CSS 변수 기반)

기존 레포트 디자인 토큰(`:root` CSS 변수)을 그대로 사용한다.

```css
/* ── 질의/답변·칩 인라인 셀 ── */
.q-cell { max-width: 380px; }

.q-text {
  color: var(--ink2);
  margin-bottom: 6px;
  line-height: 1.55;
}

.q-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-bottom: 6px;
}

.q-chip {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 10.5px;
  font-weight: 500;
  background: var(--bg2);
  color: var(--accent2);
  border: 1px solid var(--line2);
  white-space: nowrap;
}

.q-answer {
  font-size: 11.5px;
  line-height: 1.65;
  color: var(--ink2);
  padding: 6px 8px;
  background: var(--bg);
  border-left: 2px solid var(--line2);
  border-radius: 0 4px 4px 0;
  white-space: pre-wrap;
  word-break: break-word;
}

.q-answer.collapsed {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  white-space: normal;   /* line-clamp와 pre-wrap 병용 불가 → normal로 override */
}

.q-answer-toggle {
  font-size: 10px;
  color: var(--accent2);
  cursor: pointer;
  margin-top: 4px;
  display: inline-block;
  user-select: none;
}
.q-answer-toggle:hover { text-decoration: underline; }

/* ── 상품 버튼 ── */
.btn-products {
  font-family: 'Spline Sans Mono', monospace;
  font-size: 10.5px;
  padding: 3px 9px;
  border-radius: 4px;
  border: 1.5px solid var(--accent2);
  background: transparent;
  color: var(--accent2);
  cursor: pointer;
  white-space: nowrap;
}
.btn-products:hover { background: var(--accent2); color: #fff; }
.btn-products.no-data { border-color: var(--line2); color: var(--ink2); cursor: default; }

/* ── 상품 모달 ── */
.modal-overlay {
  display: none; position: fixed; inset: 0;
  background: rgba(0,0,0,.55); z-index: 9000;
  align-items: center; justify-content: center;
}
.modal-overlay.open { display: flex; }
.modal-box {
  background: var(--paper); border-radius: 10px;
  width: min(960px, 94vw); max-height: 88vh;
  display: flex; flex-direction: column; overflow: hidden;
}

/* ── 반응형 ── */
@media (max-width: 720px) { .q-cell { max-width: none; } }
@media (max-width: 600px) { .product-grid { grid-template-columns: 1fr; } }
```

### 7-7. 구현 체크리스트

HTML 결과서를 생성하는 스크립트는 아래 항목을 모두 충족해야 한다.

**데이터 준비**
- [ ] `product_scores` → `PRODUCTS_DB` JS 상수로 직렬화
- [ ] `answer_text` → HTML 생성 시 셀에 직접 삽입 (JS DB 불필요)
- [ ] `keyword_relevance_check.keywords` → HTML 생성 시 셀에 직접 삽입 (JS DB 불필요)

**단일턴 표 — 질의 셀**
- [ ] 테이블 헤더: `질의 / 답변 · 액션칩` 으로 표기
- [ ] 셀 클래스: `class="q-cell"` (기존 `class="q"` 대체)
- [ ] ① `<div class="q-text">` — `query` 텍스트
- [ ] ② `<div class="q-chips">` — `keywords` 배열 → `<span class="q-chip">` 반복 렌더링, 배열이 빈 경우 div 자체 생략
- [ ] ③ `<div class="q-answer collapsed" id="ans-{query_id}">` — `answer_text`, 텍스트 없으면 div 자체 생략
- [ ] ③ `<span class="q-answer-toggle" onclick="toggleAns('ans-{query_id}', this)">▾ 더보기</span>` — 답변 있을 때만 렌더링
- [ ] `answer_text` 내 HTML 특수문자(`&`, `<`, `>`) 이스케이프 처리

**단일턴 표 — 상품 셀**
- [ ] `product_scores.length > 0` → `상품 N건` 버튼 (`btn-products`)
- [ ] `product_scores.length == 0` → `0건` 버튼 (`btn-products no-data`, disabled)

**멀티턴 표**
- [ ] 질의 셀: 1턴 질의만 표시 (답변·칩 인라인 포함)
- [ ] 상품 셀: `—` 렌더링

**상품 모달 (openProducts)**
- [ ] 헤더: cid 뱃지 + 쿼리(60자) + JSON 토글 + ✕
- [ ] 통계 바: 총 건수 / 적합·부분·부적합 카운트 / 평균 관련도
- [ ] 카드 그리드: 이미지(lazy) + 랭크 + 타이틀 + 가격(¥N,NNN) + 뱃지 + 스코어 + 사유
- [ ] 카드 테두리: `relevance_label` 3단계 색상
- [ ] JSON 패널: 토글 가능한 `<pre>` 코드 블록, max-height 320px
- [ ] 0건 케이스: 📭 안내 메시지
- [ ] 닫기: ✕ 버튼 / 배경 클릭 / ESC 키
