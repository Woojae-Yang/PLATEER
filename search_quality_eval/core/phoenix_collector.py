"""
Phoenix LLM Observability 로그 수집 모듈.

두 가지 사용 방식:
  1. 인라인 (runners.py에서 API 테스트 직후 호출)
       client = PhoenixClient.from_phoenix_config(config["phoenix"])
       collect_phoenix_for_row(client, project_id, session_id, ...)

  2. 독립 실행 (기존 시트에 사후 보정)
       python -m core.phoenix_collector --spreadsheet ... --worksheet ...
"""

import argparse
import json
import os
import threading
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import gspread
import requests
import yaml
from google.oauth2.service_account import Credentials


# ============================================================
# 상수
# ============================================================
# 검색 툴 판별 — search_로 시작하면 검색 툴로 간주
NON_SEARCH_TOOLS: set = set()

# 시트에 저장할 상품 최대 개수
MAX_PRODUCTS_IN_OUTPUT = 30

# PHOENIX_COLUMNS: key → 컬럼 기본명 (timestamp suffix는 phoenix_col_names()에서 처리)
_PHOENIX_COLUMN_KEYS = [
    "trace_id",
    "tool_name",
    "tools_used",
    "total_count",
    "tool_input",
    "tool_output",
    "llm_response",
    "tool_latency_ms",
    "final_llm_latency_ms",
    "error",
]


# ============================================================
# 컬럼명 헬퍼
# ============================================================
def phoenix_col_names(timestamp: str = "") -> Dict[str, str]:
    """
    timestamp가 있으면 phoenix_trace_id_2026-05-22_16:04 형태,
    없으면 phoenix_trace_id 형태의 고정 이름을 반환.
    """
    suffix = f"_{timestamp}" if timestamp else ""
    return {k: f"phoenix_{k}{suffix}" for k in _PHOENIX_COLUMN_KEYS}


# ============================================================
# 공통 유틸
# ============================================================
def col_letter(col_num: int) -> str:
    result = ""
    while col_num > 0:
        col_num, rem = divmod(col_num - 1, 26)
        result = chr(65 + rem) + result
    return result


def truncate_for_sheet(value: Any, limit: int = 49000) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        value = json.dumps(value, ensure_ascii=False)
    else:
        value = str(value)
    return value[:limit] + "...(truncated)" if len(value) > limit else value


def find_col(headers: List[str], name: str) -> Optional[int]:
    for idx, h in enumerate(headers, start=1):
        if h.strip() == name:
            return idx
    return None


def find_col_fuzzy(headers: List[str], base_name: str) -> Optional[int]:
    """
    정확히 일치하면 우선 사용,
    없으면 base_name이 포함된 마지막 컬럼 반환.
    """
    exact = find_col(headers, base_name)
    if exact:
        return exact
    base = base_name.lower()
    matched = [idx for idx, h in enumerate(headers, start=1) if base in h.strip().lower()]
    return matched[-1] if matched else None


def esc_gql(value: str) -> str:
    return str(value).replace("\\", "\\\\").replace('"', '\\"')


def parse_attrs(raw: Any) -> Dict[str, Any]:
    if not raw:
        return {}
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str):
        try:
            data = json.loads(raw)
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}
    return {}


def span_ms(start_time: str, end_time: str) -> Optional[int]:
    if not start_time or not end_time:
        return None
    try:
        start = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
        end   = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
        return int((end - start).total_seconds() * 1000)
    except Exception:
        return None


def is_search_tool(tool_name: str) -> bool:
    if not tool_name:
        return False
    if tool_name in NON_SEARCH_TOOLS:
        return False
    return tool_name.startswith("search_")


def parse_products(tool_output: str):
    """execute_tool span output에서 products / total_count 추출."""
    try:

        data    = json.loads(tool_output)
        content = (data.get("response") or {}).get("content", []) or []
        if content:
            inner      = json.loads(content[0].get("text", "{}"))
            products   = inner.get("products", [])
            total_count = inner.get("total_count", len(products))
            return products, total_count
        products    = data.get("products", [])
        total_count = data.get("total_count", len(products))
        return products, total_count
    except Exception:
        return [], 0


def compact_products(products: List[Any], max_count: int = MAX_PRODUCTS_IN_OUTPUT) -> List[Dict]:
    """상품 리스트 상위 N개를 핵심 필드로 압축."""
    if not products:
        return []
    compact = []
    for idx, p in enumerate(products[:max_count], start=1):
        if not isinstance(p, dict):
            compact.append({"rank": idx, "raw": str(p)[:200]})
            continue
        item = {"rank": idx}
        pid   = p.get("product_id") or p.get("id") or p.get("productId")
        if pid is not None:
            item["product_id"] = pid
        title = p.get("title") or p.get("name") or p.get("product_name")
        if title:
            item["title"] = str(title)[:200]

        price = p.get("price") or p.get("price_amount")
        if price is not None:
            item["price"] = price
        seller = p.get("seller_name") or p.get("seller") or p.get("vendor_name")
        if seller:
            item["seller"] = str(seller)[:100]
        score = p.get("score") or p.get("relevance_score") or p.get("_score")
        if score is not None:
            item["score"] = score
        compact.append(item)
    return compact


def extract_gemini_text(raw: str) -> str:
    if not raw:
        return ""
    try:

        data  = json.loads(raw)
    except Exception:
        return raw
    parts = (data.get("content") or {}).get("parts", []) or []
    texts = [p["text"] for p in parts if isinstance(p, dict) and p.get("text")]
    return "\n".join(texts) if texts else raw


def first_non_empty(*values):
    for v in values:
        if v not in (None, ""):
            return v
    return None


def find_nested_value(obj: Any, candidate_keys):
    if obj is None:
        return None
    if isinstance(candidate_keys, str):
        candidate_keys = [candidate_keys]
    norm = {str(k).lower().replace("_", "-") for k in candidate_keys}
    if isinstance(obj, dict):
        for k, v in obj.items():
            if str(k).lower().replace("_", "-") in norm and v not in (None, ""):
                return v
        for v in obj.values():
            found = find_nested_value(v, candidate_keys)
            if found not in (None, ""):
                return found
    elif isinstance(obj, list):
        for v in obj:
            found = find_nested_value(v, candidate_keys)
            if found not in (None, ""):
                return found
    elif isinstance(obj, str):
        s = obj.strip()
        if s and s[0] in "[{":
            try:
                return find_nested_value(json.loads(s), candidate_keys)
            except Exception:
                return None
    return None


def extract_qa_meta(attrs: Dict[str, Any]) -> Dict[str, Any]:
    candidates = {
        "run_id":         ["qa_run_id", "run_id", "x-qa-run-id", "x_qa_run_id",
                           "http.request.header.x-qa-run-id"],
        "query_id":       ["qa_query_id", "query_id", "x-qa-query-id",
                           "http.request.header.x-qa-query-id"],
        "row_no":         ["qa_row_no", "row_no", "x-qa-row-no",
                           "http.request.header.x-qa-row-no"],
        "worker_id":      ["qa_worker_id", "worker_id", "x-qa-worker-id",
                           "http.request.header.x-qa-worker-id"],
        "chat_request_id":["chat_request_id", "chatRequestId", "request_id", "requestId"],
    }
    return {k: find_nested_value(attrs, keys) for k, keys in candidates.items()}


# ============================================================
# PhoenixClient — 연결·인증·조회를 캡슐화
# ============================================================
class PhoenixClient:
    """
    Phoenix GraphQL API 클라이언트.
    - 토큰을 인스턴스 레벨에서 캐싱 (thread-safe)
    - 여러 워커가 같은 인스턴스를 공유해도 안전
    """

    def __init__(self, url: str, email: str, password: str):
        self.url      = url.rstrip("/")
        self.email    = email
        self.password = password
        self._token:          Optional[str] = None
        self._token_expires:  float = 0.0
        self._lock = threading.Lock()

    @classmethod
    def from_phoenix_config(cls, phoenix_config: dict) -> "PhoenixClient":
        """config["phoenix"] dict로부터 클라이언트 생성."""
        return cls(
            url      = phoenix_config.get("url",      ""),
            email    = phoenix_config.get("email",    ""),
            password = phoenix_config.get("password", ""),
        )

    # ── 인증 ──────────────────────────────────────────────────
    def login(self, force: bool = False) -> str:
        with self._lock:
            now = time.time()
            if not force and self._token and self._token_expires > now:
                return self._token

            if not self.email or not self.password:
                raise RuntimeError(
                    "Phoenix 인증 정보 없음. phoenix.yaml 또는 "
                    "환경변수 PHOENIX_EMAIL / PHOENIX_PASS를 확인하세요."
                )

            resp = requests.post(
                f"{self.url}/auth/login",
                json={"email": self.email, "password": self.password},
                timeout=10,
            )
            cookies = resp.headers.get("set-cookie", "")
            for part in cookies.split(","):
                if "phoenix-access-token=" in part:
                    token = part.split("phoenix-access-token=")[1].split(";")[0]
                    self._token         = token
                    self._token_expires = now + 25 * 60
                    return token

            raise RuntimeError(
                f"Phoenix login 실패. status={resp.status_code}, body={resp.text[:200]}"
            )

    # ── GraphQL 호출 ──────────────────────────────────────────
    def query(self, gql: str) -> Dict[str, Any]:
        token = self.login()
        headers = {
            "Content-Type": "application/json",
            "Cookie": f"phoenix-access-token={token}",
        }
        resp = requests.post(
            f"{self.url}/graphql",
            headers=headers,
            json={"query": gql},
            timeout=30,
        )
        if resp.status_code == 401:
            token = self.login(force=True)
            headers["Cookie"] = f"phoenix-access-token={token}"
            resp = requests.post(
                f"{self.url}/graphql",
                headers=headers,
                json={"query": gql},
                timeout=30,
            )
        try:
            return resp.json()
        except Exception:
            raise RuntimeError(
                f"Phoenix GraphQL JSON 파싱 실패. "
                f"status={resp.status_code}, body={resp.text[:500]}"
            )

    # ── session_id → trace_id 목록 ────────────────────────────
    def fetch_trace_ids_by_session(self, project_id: str, session_id: str) -> List[str]:
        gql = f"""
        {{
          node(id: "{project_id}") {{
            ... on Project {{
              sessions(first: 50, sessionId: "{esc_gql(session_id)}") {{
                edges {{
                  node {{
                    sessionId
                    traces(first: 200) {{
                      edges {{
                        node {{ traceId }}
                      }}
                    }}
                  }}
                }}
              }}
            }}
          }}
        }}
        """
        data  = self.query(gql)
        if "errors" in data:
            raise RuntimeError(f"Phoenix sessions query 오류: {data['errors']}")

        node   = ((data.get("data") or {}).get("node") or {})
        edges  = ((node.get("sessions") or {}).get("edges") or [])
        result = []
        for edge in edges:
            snode = edge.get("node") or {}
            for te in ((snode.get("traces") or {}).get("edges") or []):
                tid = (te.get("node") or {}).get("traceId")
                if tid:
                    result.append(tid)
        return result

    # ── trace_id → 상세 정보 ──────────────────────────────────
    def fetch_trace_detail(self, project_id: str, trace_id: str) -> Dict[str, Any]:
        gql = f"""
        {{
          node(id: "{project_id}") {{
            ... on Project {{
              spans(
                first: 200,
                sort: {{col: startTime, dir: asc}},
                filterCondition: "context.trace_id == \\"{esc_gql(trace_id)}\\""
              ) {{
                edges {{
                  node {{
                    name
                    startTime
                    endTime
                    input  {{ value }}
                    output {{ value }}
                    attributes
                    context {{ traceId spanId }}
                  }}
                }}
              }}
            }}
          }}
        }}
        """
        data       = self.query(gql)
        if "errors" in data:
            raise RuntimeError(f"Phoenix trace query 오류: {data['errors']}")

        span_edges = (((data.get("data") or {}).get("node") or {}).get("spans") or {}).get("edges") or []
        spans      = [e.get("node") or {} for e in span_edges]

        if not spans:
            return {**_empty_trace(trace_id), "error": "NO_SPANS_FOUND"}

        tools_used:          List[str]  = []
        tool_name:           str        = ""
        tool_input:          str        = ""
        tool_output:         Any        = ""
        total_count:         Any        = None
        tool_latency_ms:     Any        = None
        final_llm_latency_ms: Any       = None
        llm_response:        str        = ""
        session_id           = ""
        user_id              = ""
        run_id               = ""
        query_id             = ""
        row_no               = ""
        worker_id            = ""
        chat_request_id      = ""

        for span in spans:
            name         = span.get("name", "")
            input_value  = (span.get("input")  or {}).get("value", "")
            output_value = (span.get("output") or {}).get("value", "")
            attrs        = parse_attrs(span.get("attributes"))

            if not session_id:
                session_id = (
                    find_nested_value(attrs, ["session_id", "session.id"])
                    or ((attrs.get("session") or {}).get("id")
                        if isinstance(attrs.get("session"), dict) else None)
                    or attrs.get("session.id") or ""
                )
            if not user_id:
                user_id = (
                    find_nested_value(attrs, ["user_id", "user.id"])
                    or ((attrs.get("user") or {}).get("id")
                        if isinstance(attrs.get("user"), dict) else None)
                    or attrs.get("user.id") or ""
                )

            qa = extract_qa_meta(attrs)
            run_id          = first_non_empty(run_id,          qa.get("run_id"))          or ""
            query_id        = first_non_empty(query_id,        qa.get("query_id"))        or ""
            row_no          = first_non_empty(row_no,          qa.get("row_no"))          or ""
            worker_id       = first_non_empty(worker_id,       qa.get("worker_id"))       or ""
            chat_request_id = first_non_empty(chat_request_id, qa.get("chat_request_id")) or ""

            if name.startswith("execute_tool "):
                current_tool = name.split(" ", 1)[1].strip()
                if current_tool not in tools_used:
                    tools_used.append(current_tool)
                if is_search_tool(current_tool) and not tool_name:
                    tool_name       = current_tool
                    tool_input      = input_value
                    tool_latency_ms = span_ms(span.get("startTime"), span.get("endTime"))
                    products, total_count = parse_products(output_value)
                    compact = compact_products(products, MAX_PRODUCTS_IN_OUTPUT)
                    tool_output = {
                        "total_count":    total_count,
                        "returned_count": len(products),
                        "shown_count":    len(compact),
                        "products":       compact,
                    }

            if name == "call_llm":
                ms = span_ms(span.get("startTime"), span.get("endTime"))
                if ms is not None:
                    final_llm_latency_ms = ms


            if "generate_content" in name and output_value:
                llm_response = extract_gemini_text(output_value)

        return {
            "trace_id":             trace_id,
            "tool_name":            tool_name,
            "tools_used":           tools_used,
            "total_count":          total_count if total_count is not None else "",
            "tool_input":           tool_input,
            "tool_output":          tool_output,
            "llm_response":         llm_response,
            "tool_latency_ms":      tool_latency_ms      if tool_latency_ms      is not None else "",
            "final_llm_latency_ms": final_llm_latency_ms if final_llm_latency_ms is not None else "",
            "error":                "",
            # 디버깅용 (시트에는 쓰지 않음)
            "session_id":     session_id,
            "user_id":        user_id,
            "run_id":         run_id,
            "query_id":       query_id,
            "row_no":         row_no,
            "worker_id":      worker_id,
            "chat_request_id": chat_request_id,
        }

    # ── session_id → 가장 최근 trace 1건 ─────────────────────
    def fetch_phoenix_by_session(self, project_id: str, session_id: str) -> Dict[str, Any]:
        trace_ids = self.fetch_trace_ids_by_session(project_id, session_id)
        if not trace_ids:
            return _empty_trace("", error="NO_TRACE_FOUND")

        seen:    set       = set()
        results: List[dict] = []
        # 최신 trace를 먼저 보기 위해 역순 처리
        for tid in reversed(trace_ids):
            if tid in seen:
                continue
            seen.add(tid)
            results.append(self.fetch_trace_detail(project_id, tid))
            break          # n=1

        if not results:
            return _empty_trace("", error="NO_TRACE_FOUND")

        return results[0]

    # ── 재시도 포함 조회 (runners.py에서 호출) ────────────────
    def fetch_with_retry(
        self,
        project_id:    str,
        session_id:    str,
        delay_sec:     float = 5.0,
        max_retries:   int   = 3,
        retry_backoff: float = 2.0,
    ) -> Dict[str, Any]:
        """
        초기 delay_sec 대기 후 fetch.
        NO_TRACE_FOUND 이면 max_retries 횟수까지 지수 백오프로 재시도.
        """
        if delay_sec > 0:
            print(f"    ⏳ Phoenix 대기 {delay_sec:.1f}s (session={session_id})")
            time.sleep(delay_sec)

        result    = None
        last_wait = 0.0
        for attempt in range(max_retries):
            result = self.fetch_phoenix_by_session(project_id, session_id)
            if result.get("error") != "NO_TRACE_FOUND":
                return result              # 성공 또는 다른 오류
            if attempt < max_retries - 1:
                last_wait = retry_backoff * (2 ** attempt)
                print(
                    f"    🔄 Phoenix NO_TRACE_FOUND — "
                    f"{last_wait:.0f}s 후 재시도 ({attempt + 1}/{max_retries - 1})"
                )
                time.sleep(last_wait)

        # 최종 시도 결과 그대로 반환 (여전히 NO_TRACE_FOUND일 수 있음)
        return result


# ============================================================
# Google Sheets 컬럼 관리
# ============================================================
def ensure_phoenix_columns(ws, timestamp: str = "") -> Dict[str, int]:
    """
    Phoenix 컬럼을 시트에 확보하고 {key: col_index} 반환.
    timestamp가 있으면 phoenix_trace_id_<timestamp> 형태로 생성.
    """
    col_names = phoenix_col_names(timestamp)
    values    = ws.get_all_values()
    if not values:
        raise RuntimeError("시트가 비어 있습니다.")

    headers = list(values[0])

    def _col_letter(n: int) -> str:
        r = ""
        while n > 0:
            n, rem = divmod(n - 1, 26)
            r = chr(65 + rem) + r
        return r

    result_cols: Dict[str, int] = {}
    new_cols: list = []   # (key, col_name, target_idx)

    for key, col_name in col_names.items():
        if col_name in headers:
            result_cols[key] = headers.index(col_name) + 1
        else:
            new_idx = len(headers) + 1
            new_cols.append((key, col_name, new_idx))
            result_cols[key] = new_idx
            headers.append(col_name)

    if new_cols:
        max_target  = max(idx for _, _, idx in new_cols)
        current_cnt = ws.col_count
        if max_target > current_cnt:
            ws.add_cols(max_target - current_cnt + 5)

        updates = [
            {"range": f"{_col_letter(idx)}1", "values": [[col_name]]}
            for _, col_name, idx in new_cols
        ]
        ws.batch_update(updates, value_input_option="RAW")
        for _, col_name, idx in new_cols:
            print(f"✅ Phoenix 컬럼 생성: '{col_name}' ({idx}번째)")

    return result_cols


def open_worksheet(credentials_file: str, spreadsheet_name: str, worksheet_name: str):
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds  = Credentials.from_service_account_file(credentials_file, scopes=scopes)
    client = gspread.authorize(creds)
    return client.open(spreadsheet_name).worksheet(worksheet_name)


def build_row_phoenix_updates(
    row_idx:     int,
    result_cols: Dict[str, int],
    phoenix:     Dict[str, Any],
) -> List[Dict]:
    updates = []
    for key, col_idx in result_cols.items():
        value = phoenix.get(key, "")
        if key == "tools_used":
            value = json.dumps(value or [], ensure_ascii=False)
        if key == "tool_output" and isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False, indent=2)
        value = truncate_for_sheet(value)
        updates.append({
            "range":  f"{col_letter(col_idx)}{row_idx}",
            "values": [[value]],
        })
    return updates


# ============================================================
# 인라인 수집 (runners.py → 각 워커에서 호출)
# ============================================================
def collect_phoenix_for_row(
    client:             "PhoenixClient",
    project_id:         str,
    session_id:         str,
    worksheet,
    row_idx:            int,
    phoenix_result_cols: Dict[str, int],
    sheet_lock:         threading.Lock,
    delay_sec:          float = 5.0,
    max_retries:        int   = 3,
    retry_backoff:      float = 2.0,
    sheet_write_delay:  float = 0.3,
) -> None:
    """
    API 테스트 완료 후 Phoenix 로그를 수집하고 시트에 기록.

    Args:
        client              : PhoenixClient 인스턴스 (run_api_test에서 생성, 워커 공유)
        project_id          : Phoenix 프로젝트 base64 ID
        session_id          : Gelatto API 호출 시 사용한 session_id
        worksheet           : gspread Worksheet 객체
        row_idx             : 업데이트 대상 시트 행 번호
        phoenix_result_cols : {key: col_index} (ensure_phoenix_columns 반환값)
        sheet_lock          : 워커 간 Sheets 동시 쓰기 방지 Lock
        delay_sec           : Phoenix 로그 생성 대기 시간 (초)
        max_retries         : NO_TRACE_FOUND 재시도 횟수
        retry_backoff       : 재시도 대기 배수 (지수 백오프)
        sheet_write_delay   : 시트 업데이트 후 추가 대기 (초)
    """
    phoenix = client.fetch_with_retry(
        project_id    = project_id,
        session_id    = session_id,
        delay_sec     = delay_sec,
        max_retries   = max_retries,
        retry_backoff = retry_backoff,
    )

    updates = build_row_phoenix_updates(row_idx, phoenix_result_cols, phoenix)
    if not updates:
        return

    with sheet_lock:
        for attempt in range(3):
            try:
                worksheet.batch_update(updates, value_input_option="RAW")
                time.sleep(sheet_write_delay)
                break
            except gspread.exceptions.APIError as e:
                if "429" in str(e) and attempt < 2:
                    wait = 30 * (attempt + 1)
                    print(f"    ⏳ Phoenix Sheets 429 (row {row_idx}) — {wait}s 대기 후 재시도")
                    time.sleep(wait)
                    continue
                print(f"    ⚠️ Phoenix 시트 업데이트 실패 (row {row_idx}): {e}")
                break
            except Exception as e:
                print(f"    ⚠️ Phoenix 시트 업데이트 실패 (row {row_idx}): {e}")
                break

    if phoenix.get("error"):
        print(f"    ⚠️ Phoenix 수집 결과 확인 필요 | row={row_idx} error={phoenix['error']}")
    else:
        print(
            f"    🔍 Phoenix 수집 완료 | row={row_idx} "
            f"trace_id={phoenix.get('trace_id')} "
            f"tool={phoenix.get('tool_name') or '-'}"
        )


# ============================================================
# 사후 시트 보정 (standalone 배치 실행용)
# ============================================================
def collect_to_sheet(
    credentials_file: str,
    spreadsheet_name: str,
    worksheet_name:   str,
    project_key:      str,
    session_col_name: str,
    phoenix_config:   Optional[dict] = None,
    start_row:        int   = 2,
    sleep_sec:        float = 0.3,
    skip_no_trace:    bool  = True,
):
    """
    기존 시트의 session_id를 읽어 Phoenix 로그를 사후 수집.
    standalone main() 또는 외부 스크립트에서 사용.
    """
    # phoenix_config 미전달 시 config_loader에서 로드
    if phoenix_config is None:
        from core.config_loader import YAML_CONFIG
        phoenix_raw = YAML_CONFIG.get("phoenix") or {}
        projects    = phoenix_raw.get("projects") or {}
        phoenix_config = {
            "url":      phoenix_raw.get("url", ""),
            "email":    os.getenv("PHOENIX_EMAIL", phoenix_raw.get("email", "")),
            "password": os.getenv("PHOENIX_PASS",  phoenix_raw.get("password", "")),
        }
        projects_map = projects
    else:
        from core.config_loader import YAML_CONFIG
        projects_map = (YAML_CONFIG.get("phoenix") or {}).get("projects") or {}

    project_id = projects_map.get(project_key)
    if not project_id:
        raise ValueError(
            f"지원하지 않는 project_key: '{project_key}'. "
            f"사용 가능: {list(projects_map.keys())}"
        )

    client = PhoenixClient.from_phoenix_config(phoenix_config)
    ws     = open_worksheet(credentials_file, spreadsheet_name, worksheet_name)
    values = ws.get_all_values()
    if not values:
        raise RuntimeError("시트가 비어 있습니다.")

    headers = values[0]

    session_col = find_col(headers, session_col_name)
    if not session_col and session_col_name == "session_id":
        session_col = find_col_fuzzy(headers, "session_id")
    if not session_col:
        raise RuntimeError(f"session_id 컬럼을 찾을 수 없습니다: {session_col_name}")
    print(f"session_id 컬럼 사용: {headers[session_col - 1]}")

    # 타임스탬프 없이 고정 컬럼명으로 확보 (standalone 모드)
    result_cols   = ensure_phoenix_columns(ws, timestamp="")
    sheet_lock    = threading.Lock()

    total = success = failed = skipped = 0
    pending_updates: List[dict] = []
    batch_size      = 3

    for row_idx, row in enumerate(values[start_row - 1:], start=start_row):
        sid = (row[session_col - 1].strip() if len(row) >= session_col else "")
        if not sid:
            continue
        total += 1

        try:
            print(f"🔎 [행 {row_idx}] session_id={sid} Phoenix 조회 중...")
            phoenix = client.fetch_with_retry(
                project_id    = project_id,
                session_id    = sid,
                delay_sec     = 0,          # 사후 배치이므로 delay 없음
                max_retries   = 3,
                retry_backoff = 2.0,
            )

            if phoenix.get("error") == "NO_TRACE_FOUND" and skip_no_trace:
                failed  += 1
                skipped += 1
                print("   ⚠️ NO_TRACE_FOUND | 시트 업데이트 생략")
                continue

            pending_updates.extend(build_row_phoenix_updates(row_idx, result_cols, phoenix))
            if len(pending_updates) >= batch_size * len(result_cols):
                _flush(ws, pending_updates)

            if phoenix.get("error"):
                failed += 1
                print(f"   ⚠️ error={phoenix['error']}")
            else:
                success += 1
                print(f"   ✅ trace_id={phoenix.get('trace_id')}")

        except Exception as e:
            failed += 1
            err_data = _empty_trace("", error=str(e))
            pending_updates.extend(build_row_phoenix_updates(row_idx, result_cols, err_data))
            if len(pending_updates) >= batch_size * len(result_cols):
                _flush(ws, pending_updates)
            print(f"   ❌ 예외: {e}")

        time.sleep(sleep_sec)

    _flush(ws, pending_updates)
    print("=" * 60)
    print(f"Phoenix 로그 수집 완료 | 대상={total} 성공={success} 실패={failed} 생략={skipped}")
    print("=" * 60)


# ============================================================
# 내부 헬퍼
# ============================================================
def _empty_trace(trace_id: str, error: str = "") -> Dict[str, Any]:
    return {
        "trace_id":             trace_id,
        "tool_name":            "",
        "tools_used":           [],
        "total_count":          "",
        "tool_input":           "",
        "tool_output":          "",
        "llm_response":         "",
        "tool_latency_ms":      "",
        "final_llm_latency_ms": "",
        "error":                error,
    }


def _flush(ws, pending: List[dict]) -> None:
    if not pending:
        return
    ws.batch_update(pending)
    print(f"   📝 Google Sheet 반영 완료 | 업데이트 셀 수={len(pending)}")
    pending.clear()


# ============================================================
# Standalone 진입점
# ============================================================
def _load_standalone_config() -> dict:
    """
    독립 실행 시 config_loader를 통해 phoenix 설정 로드.
    환경변수 > phoenix.yaml 순으로 우선 적용.
    """
    try:
        from core.config_loader import YAML_CONFIG
        phoenix = YAML_CONFIG.get("phoenix") or {}
    except Exception:
        phoenix = {}

    return {
        "url":      phoenix.get("url", os.getenv("PHOENIX_URL", "http://34.47.106.52:6006")),
        "email":    os.getenv("PHOENIX_EMAIL",  phoenix.get("email",    "")),
        "password": os.getenv("PHOENIX_PASS",   phoenix.get("password", "")),
        "projects": phoenix.get("projects", {}),
        "default_project": phoenix.get("default_project", "GELATTO-STG"),
    }


def main():
    standalone_cfg = _load_standalone_config()
    projects_map   = standalone_cfg.get("projects", {})

    parser = argparse.ArgumentParser(description="Phoenix 로그 사후 수집")
    parser.add_argument("--credentials",  default="config/credentials.json")
    parser.add_argument("--spreadsheet",  default=None)
    parser.add_argument("--worksheet",    default=None)
    parser.add_argument(
        "--project",
        default=standalone_cfg.get("default_project", "GELATTO-STG"),
        choices=list(projects_map.keys()) if projects_map else None,
    )
    parser.add_argument("--session-col",   default="session_id")
    parser.add_argument("--start-row",     type=int,   default=2)
    parser.add_argument("--sleep",         type=float, default=0.3)
    parser.add_argument("--list-projects", action="store_true")
    parser.add_argument(
        "--write-no-trace",
        action="store_true",
        help="NO_TRACE_FOUND도 시트에 기록 (기본: 생략)",
    )
    args = parser.parse_args()

    if args.list_projects:
        client = PhoenixClient.from_phoenix_config(standalone_cfg)
        gql    = "{ projects(first: 50) { edges { node { id name } } } }"
        print(json.dumps(client.query(gql), ensure_ascii=False, indent=2))
        return

    if not args.spreadsheet:
        args.spreadsheet = input(" ✅ 구글 스프레드시트 이름을 입력하세요: ").strip()
    if not args.worksheet:
        args.worksheet = input(" ✅ 시트 탭 이름을 입력하세요: ").strip()

    collect_to_sheet(
        credentials_file = args.credentials,
        spreadsheet_name = args.spreadsheet,
        worksheet_name   = args.worksheet,
        project_key      = args.project,
        session_col_name = args.session_col,
        phoenix_config   = standalone_cfg,
        start_row        = args.start_row,
        sleep_sec        = args.sleep,
        skip_no_trace    = not args.write_no_trace,
    )


if __name__ == "__main__":
    main()
