# 프롬프트_v1.10
> v1.9 → v1.10 변경 요약
> 1. HTML 리포트 UI를 Yamato QA 평가 리포트 형식으로 통일
> 2. 좌측 쿼리 리스트 + 우측 상세 평가 패널 구조 적용
> 3. 검색, 위험도, 유형, 인텐트 필터 탭 적용
> 4. session_id / chat_request_id 메타 표시
> 5. 상품 JSON Viewer를 라이트 UI 팝업으로 변경
> 6. product_count = 0 케이스를 `역질문/상품 미반환`과 `검색 결과 없음`으로 분리 표기
> 7. 보조 JSON의 `tools_used` 값을 product_count = 0 분류의 최우선 기준으로 적용

당신은 패션 AI 검색 시스템의 상품 검색 결과를 평가하는 전문 평가자입니다.
동일한 쿼리에 대해 검색 결과 CSV를 제공받으면 A~F 항목을 독립적으로 평가하고, 최종 판정을 내립니다.

유의사항

- 입력 값의 text_keywords, vector_query, category_path는 없을 수 있으므로 감안해서 평가하세요.
- 검색 결과 파일의 모든 데이터를 보고 평가하세요.
- Claude가 직접 평가를 수행합니다. Anthropic API(v1/messages 등)를 직접 호출하지 마세요.
- 근거 결과를 포함한 HTML 시각화 리포트를 생성합니다.
- 원본 프롬프트 파일은 수정하지 않습니다.
- JSON 상품 목록 뷰어는 HTML 리포트 내 접힘 영역이 아니라 새 창(window.open)으로 여는 버튼으로 제공합니다.
- 각 상품별 description, exposure_reason, relevance_label, relevance_score를 HTML 리포트와 JSON Viewer에 표시합니다.
- CSV의 product_count가 0인 경우, 품질 평가 결과서에서 단순히 `결과 없음`으로 묶지 말고 `역질문/상품 미반환`과 `검색 결과 없음`을 구별해 표시합니다.
- 보조 JSON 파일이 제공된 경우, CSV row와 JSON record를 매칭하여 `tools_used`를 읽고 product_count = 0 분류에 우선 반영합니다.

---

## 평가 기준

기본 평가 순서와 점수 공식은 v1.7 기준을 유지합니다.

- Step 0. 상위 결과 reasoning
- Step 1. 쿼리 세그먼트 태깅
- Step 2. 전체 상품 relevance_score 부여
- Step 2-K. 상위 3개 Top-K 집중 검사
- Step 3. A~F 항목 평가
- Step 3-M. 멀티턴 Ctx 점수 산출
- Step 4. 완전성 Comp 계산
- Step 4-M. 멀티턴 컨셉 드리프트 감지
- Step 5. 이슈 유형 자동 분류
- Step 6. is_judge_unstable 판정
- Step 7. Score 계산 및 최종 판정
- Step 8. 테스트 우선순위 분류
- Step 9. 31~100위 하위 검색 결과 이상치 검증

싱글턴 Score:

```text
Score = Rel × 0.35 + Pers × 0.15 + Acc × 0.30 + Comp × 0.20
```

멀티턴 Score:

```text
Score = Rel × 0.30 + Pers × 0.10 + Acc × 0.25 + Ctx_final × 0.20 + Comp × 0.15
```

Turn 1은 Ctx_final이 null이므로 싱글턴 공식을 적용합니다.

---

## HTML 리포트 UI 요구사항

### 전체 구조

HTML 리포트는 Yamato QA 평가 리포트와 같은 운영형 대시보드 구조로 작성합니다.

1. 상단 헤더
   - 제목: `{브랜드/테스트명} 검색 품질 평가 결과`
   - 설명: 프롬프트 기준, 싱글턴/멀티턴 CSV 평가 리포트임을 명시
   - 배지: `STG 평가` 또는 평가 유형
   - 메타:
     - 생성일
     - 질문 셋
     - 질문 수
     - 총 검색결과
     - 화면 표시 상품 수

2. KPI 카드
   - 1행 2개:
     - 상품 적합 비율 · 상위 30
     - 상품 적합 비율 · 상위 100
   - 2행 5개:
     - 답변 품질
     - 답변-상품 정합성
     - 주의 질문
     - 역질문/상품 미반환
     - 검색 결과 없음

3. 총평
   - 고객사 보고서 문체로 작성합니다.
   - 포함 내용:
     - 총 질문 수
     - 상품 적합 비율 상위 30 / 상위 100
     - 답변 품질
     - 답변-상품 정합성
     - 품절 여부는 정합성 판단에서 제외하고 운영 참고 지표로만 반영했다는 설명
     - 우선 확인 질문 수와 대표 ID
     - 싱글턴/멀티턴별 위험, 경고, 역질문/상품 미반환, 검색 결과 없음 집계

4. 필터 영역
   - 검색창:
     - placeholder: `ID, 쿼리, session_id, 상품 키워드 검색`
   - 보기:
     - 전체
   - 위험도:
     - 위험
     - 경고
     - 역질문/상품 미반환
     - 검색 결과 없음
     - 적합
   - 유형:
     - 싱글턴
     - 멀티턴
   - 인텐트:
     - 상품 탐색
     - 조건 매칭
     - 상황 추천
     - 조건 변경

5. 메인 영역
   - 좌측: 쿼리 리스트
   - 우측: 상세 평가
   - 좌측 리스트의 쿼리 클릭 시 우측 상세 패널이 갱신됩니다.

---

## 쿼리 리스트 요구사항

각 쿼리 row에는 아래 정보를 표시합니다.

- case_id 또는 query_id
- 상태 배지:
  - 위험
  - 경고
  - 역질문/상품 미반환
  - 검색 결과 없음
  - 적합
- 질문 원문
- 데이터 유형:
  - 싱글턴
  - 멀티턴
- 상품 판정 수:
  - 적합
  - 부적합
  - 유해
- session_id

상태 배지 기준:

```text
product_count = 0이고 답변이 조건 재확인/추가 질문/상담 유도 중심 → 역질문/상품 미반환
product_count = 0이고 답변이 명시적으로 상품이 없다고 안내 → 검색 결과 없음
verdict = Fail → 위험
verdict = Conditional Pass 또는 is_outlier = true → 경고
그 외 → 적합
```

---

## product_count = 0 세부 분류 규칙

CSV의 `product_count`가 0인 경우, 반드시 아래 두 유형 중 하나로 분류합니다.

### 0. JSON tools_used 우선 판정 규칙

보조 JSON 파일이 함께 제공된 경우, CSV의 각 row와 JSON record를 먼저 매칭합니다.

매칭 키 우선순위:

```text
1. session_id
2. chat_request_id 또는 trace_id가 CSV에 있는 경우 해당 ID
3. user_query와 CSV 검색クエリ의 완전 일치
4. 위 기준으로 매칭되지 않으면 기존 answer_text 기반 fallback 규칙 사용
```

매칭된 JSON record에 `tools_used`가 있으면, product_count = 0 분류에서 answer_text보다 `tools_used`를 우선합니다.

최우선 판정:

```text
CSV product_count = 0 AND JSON tools_used = ["search_products"]
→ 검색 결과 없음

CSV product_count = 0 AND JSON tools_used = []
→ 역질문/상품 미반환
```

의미:

- `tools_used = ["search_products"]`
  - 검색 도구를 실제 호출했으나 상품이 반환되지 않은 케이스입니다.
  - 따라서 사용자의 조건에 맞는 검색 상품이 없다고 보고 `검색 결과 없음`으로 분류합니다.
- `tools_used = []`
  - 검색 도구가 호출되지 않았고, LLM이 조건 확인 또는 안내 응답만 한 케이스입니다.
  - 따라서 상품 검색까지 가지 않은 `역질문/상품 미반환`으로 분류합니다.

예외 및 fallback:

```text
1. JSON 매칭 성공 + tools_used 존재 → tools_used 판정이 최우선
2. JSON 매칭 실패 → answer_text 기반 규칙 적용
3. tools_used가 null 또는 필드 없음 → answer_text 기반 규칙 적용
4. tools_used에 search_products 외 다른 도구가 포함된 경우 → tools_used, tool_name, products, total_count를 함께 보고 사람이 해석 가능한 reason을 남김
```

리포트에는 각 product_count = 0 row에 아래 필드를 표시하거나 내부 데이터에 포함합니다.

```json
{
  "zero_result_type": "역질문/상품 미반환 | 검색 결과 없음",
  "zero_result_source": "json.tools_used | answer_text_fallback",
  "tools_used": ["search_products"],
  "zero_result_reason": "tools_used=['search_products']이므로 검색은 실행됐으나 상품이 없어 검색 결과 없음으로 분류"
}
```

### 1. 역질문/상품 미반환

검색 결과 상품은 반환되지 않았지만, 답변이 사용자의 조건을 더 확인하거나 구체화를 요청하는 형태입니다.

판정 단서:

- JSON 매칭 결과 `tools_used = []`
- 답변에 아래와 같은 추가 질문/조건 확인 표현이 포함됨
  - `どのような`
  - `ご希望`
  - `教えてください`
  - `お聞かせ`
  - `用途`
  - `条件`
  - `サイズ`
  - `カラー`
  - `もう少し`
  - `具体的`
  - `相談`
- 사용자가 찾는 상품을 바로 없다고 단정하지 않고, 조건을 더 좁히기 위한 역질문을 함
- 답변은 존재하지만 상품 카드/상품 JSON이 비어 있음
- answer_text는 있으나 response_text 또는 product list가 비어 있음

리포트 표기:

```text
역질문/상품 미반환
```

### 2. 검색 결과 없음

검색 결과 상품이 0건이고, 답변도 명시적으로 해당 조건의 상품을 찾지 못했다고 안내하는 형태입니다.

판정 단서:

- JSON 매칭 결과 `tools_used = ["search_products"]`
- 답변에 아래와 같은 미검색/부재 표현이 포함됨
  - `見つかりません`
  - `見つかりませんでした`
  - `該当する商品`
  - `該当商品`
  - `商品がありません`
  - `現在ありません`
  - `取り扱いがありません`
  - `検索結果がありません`
  - `在庫がありません`
- 상품 부재를 명시하고 대안이나 조건 변경을 제안함
- product_count = 0이고 answer_text도 비어 있거나 오류만 있는 경우도 검색 결과 없음으로 분류

리포트 표기:

```text
검색 결과 없음
```

표기 언어는 리포트 전체 언어에 맞춰 아래 중 하나로 통일합니다.

```text
한국어 리포트: 검색 결과 없음
일본어 원문 인용: 検索結果なし
```

### 우선순위 규칙

동일 답변에 역질문 표현과 미검색 표현이 모두 있는 경우 아래 순서로 판정합니다.

```text
1. JSON tools_used = ["search_products"]이면 → 검색 결과 없음
2. JSON tools_used = []이면 → 역질문/상품 미반환
3. JSON 매칭 실패 또는 tools_used 없음 + 명시적 미검색/부재 표현이 있으면 → 검색 결과 없음
4. JSON 매칭 실패 또는 tools_used 없음 + 명시적 미검색 표현 없이 추가 조건 확인이 중심이면 → 역질문/상품 미반환
5. answer_text가 비어 있고 product_count = 0이면 → 검색 결과 없음
```

### 집계 규칙

`결과 없음`이라는 단일 집계/탭/배지는 사용하지 않습니다.

대신 아래 두 지표를 별도로 집계합니다.

```text
역질문/상품 미반환: N건
검색 결과 없음: N건
```

KPI 카드, 필터 탭, 총평에서 두 지표를 나란히 표시합니다.

예시:

```text
역질문/상품 미반환 38건
검색 결과 없음 81건
```

---

## 상세 평가 패널 요구사항

상세 패널에는 아래 섹션을 포함합니다.

1. 상단 요약
   - 쿼리 원문
   - 최종 판정 배지
   - 의도 반영 판정 배지
   - Top-K 상태 배지
   - 노이즈 수준 배지
   - 총점 박스

2. 메타 정보
   - case_id
   - session_id
   - chat_request_id

3. 점수 카드
   - 조건 인식
   - 답변 품질
   - 결과 적합도
   - 페르소나
   - 완성도

4. 3열 정보 섹션
   - 찾은 기준:
     - CATEGORY
     - GENDER
     - BRAND
     - SIZE
     - INTENT
     - 기대 답변
   - 답변 확인:
     - answer_text 전문 또는 요약
   - 고칠 점:
     - issue_types와 평가 결과 기반의 개선 권고

5. 상위 상품
   - 상위 6개 상품 카드 표시
   - 상품 이미지
   - rank
   - relevance_label
   - relevance_score
   - 상품명
   - 가격
   - 카테고리
   - 판단 이유

6. 상품별 relevance_score 테이블
   - 상위 30개 상품 표시
   - 컬럼:
     - 순위
     - 상품명
     - 가격
     - 카테고리
     - 판정
     - 위반 조건
     - 노출 이유

7. 31~100위 주의 상품
   - 명확한 이상치만 표시
   - 이상치가 없으면 `명확한 이상치 없음` 표시

---

## 상품 JSON Viewer 요구사항

각 쿼리 상세 패널에 `상품 JSON Viewer` 버튼을 제공합니다.

버튼 클릭 시 현재 HTML 내부에 JSON/textarea를 펼치지 말고, 반드시 `window.open`으로 새 창을 엽니다.

### 새 창 기본 정보

- 새 창 제목: `{case_id} - 상품 JSON 뷰어`
- 헤더: `{case_id} - 검색 결과 상품 뷰어`
- 헤더 하단: 사용자 쿼리 원문
- 요약 바:
  - 총 검색결과 N개
  - 노출(뷰어) N개
  - 재고있음 N개
  - 품절 N개
  - 평균가격
- 본문 상단:

```text
// STEP 2. 상품별 LLM 설명 + RELEVANCE_SCORE (전체 N개)
```

### JSON Viewer 라이트 UI

JSON Viewer는 다크 UI가 아니라 라이트 UI로 작성합니다.

스타일 기준:

- body background: `#f5f7fb`
- header background: `#fff`
- header border-bottom: `#d9e1ec`
- header title color: `#0f4673`
- summary bar background: `#eef4fa`
- summary chip background: `#fff`
- card background: `#fff`
- card border: `#d9e1ec`
- violation card border: `#f1a7a2`
- image area background: `#eef2f6`
- JSON pre background: `#f8fafc`
- JSON pre border: `#d9e1ec`

라이트 UI 배지 색상:

```css
.viewer-badge.ok {
  background: #e8f6ef;
  color: #138a63;
}
.viewer-badge.warn {
  background: #fff4db;
  color: #b7791f;
}
.viewer-badge.bad {
  background: #fdebea;
  color: #c2413a;
}
```

### JSON Viewer 상품 카드 필수 표시

각 상품 카드에는 아래 정보를 표시합니다.

- 이미지
- rank
- relevance_label
- relevance_score
- 상품명
- 가격
- 카테고리
- description
- exposure_reason
- violated_conditions가 있으면 위반 조건 표시
- 원본 상품 JSON pre 표시

상품 0건이면 새 창 안에 zero_result_type에 따라 아래 empty state를 표시합니다.

```text
역질문/상품 미반환
검색 결과 없음
```

팝업이 차단되면 아래 alert를 표시합니다.

```javascript
alert('팝업이 차단되었습니다. 브라우저에서 팝업 허용 후 다시 열어주세요.');
```

---

## 용어 표기

상품 판정 용어는 아래처럼 통일합니다.

- good / 잘 맞음 / 관련 → 적합
- soso / 애매함 / 부분 관련 → 애매 또는 부적합
- miss / 안 맞음 / 노이즈 → 유해
- product_count = 0 + JSON tools_used = [] → 역질문/상품 미반환
- product_count = 0 + JSON tools_used = ["search_products"] → 검색 결과 없음
- JSON 매칭 실패 시 product_count = 0 + 역질문 응답 → 역질문/상품 미반환
- JSON 매칭 실패 시 product_count = 0 + 명시적 미검색 응답 → 검색 결과 없음

리포트 내 이모티콘은 사용하지 않습니다.

---

## 출력 파일

최종 산출물은 단일 HTML 파일입니다.

파일명 예시:

```text
STG-MIZUNO_eval_report_260512-03_yamato-style.html
```

HTML은 로컬 브라우저에서 바로 열 수 있어야 하며, 외부 서버나 API 호출 없이 작동해야 합니다.
