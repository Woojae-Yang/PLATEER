"""
1단계: 쿼리/시나리오 단위 평가 (v2.1).

흐름
  · LLM(Vertex AI Gemini)은 **정성 판단만** 출력 (schemas.LLMQueryEval / LLMScenarioEval).
  · 그 출력을 scoring.compute_query 로 넘겨 모든 수치·판정·Phoenix 검증을 코드가 계산.
  · 최종 반환값은 data.json 의 queries[] 객체(들).

멀티턴 시나리오는 LLM이 turns[] 를 한 번에 평가하고, 코드가 턴별로 compute_query 한다.
Vertex AI 병렬 호출 + 프롬프트 캐싱은 기존과 동일.
"""
import json
import re
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from threading import Lock

from google import genai
from google.genai import types
from google.oauth2 import service_account

from .config_loader import now_kst
from .schemas import (
    LLMQueryEval, LLMScenarioEval, LLMProductScoreList,
    LLMQueryEvalYamato, LLMScenarioEvalYamato,
)
from .scoring import compute_query
from .yamato_scoring import compute_query_yamato
from .sheet_parser import scenario_turn_inputs


DEFAULT_MODEL = "gemini-3.1-flash-lite"
_VERTEX_SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]


def _build_vertex_client(vertex_config: dict) -> genai.Client:
    """Vertex AI 백엔드 genai.Client 생성 (서비스 계정 또는 ADC)."""
    creds_file = vertex_config.get("credentials_file", "")
    credentials = None
    if creds_file and Path(creds_file).exists():
        credentials = service_account.Credentials.from_service_account_file(
            creds_file, scopes=_VERTEX_SCOPES,
        )
        print(f"   🔑 Vertex AI 인증: 서비스 계정 ({Path(creds_file).name})")
    else:
        print("   🔑 Vertex AI 인증: ADC (gcloud 계정)")

    client_kwargs = dict(
        vertexai=True,
        project=vertex_config["project_id"],
        location=vertex_config["location"],
    )
    if credentials:
        client_kwargs["credentials"] = credentials
    # 호출당 타임아웃(ms): 한 콜이 늘어져 워커가 무한 대기하는 것을 방지
    try:
        timeout_ms = int(float(vertex_config.get("request_timeout", 180)) * 1000)
        client_kwargs["http_options"] = types.HttpOptions(timeout=timeout_ms)
    except Exception:
        pass
    return genai.Client(**client_kwargs)


# ─────────────────────────────────────────────
# LLM 입력 구성 (정성 판단에 필요한 최소 정보만)
# ─────────────────────────────────────────────
def _compact_product(p: dict) -> dict:
    return {
        "rank": p.get("rank"),
        "title": p.get("title") or p.get("product_name"),
        "brand": p.get("brand_name") or p.get("brand"),
        "selling_price": p.get("selling_price"),
        "currency": p.get("currency"),
        "category_path": p.get("category_path") or p.get("category"),
    }


def _build_llm_input(eval_input: dict) -> dict:
    """단일 쿼리/턴 입력 → LLM 전달용 정성 판단 입력."""
    ph = eval_input.get("phoenix") or {}
    return {
        "query": eval_input.get("query"),
        "answer_text": eval_input.get("answer_text") or "",
        "keywords": eval_input.get("keywords") or [],
        "product_count": eval_input.get("product_count", 0),
        "previous_turn_queries": eval_input.get("previous_turn_queries") or [],
        "turn_number": eval_input.get("turn_number"),
        "phoenix_tool_input": ph.get("tool_input"),
        "phoenix_tools_used": ph.get("tools_used"),
        "products": [_compact_product(p) for p in (eval_input.get("products") or [])],
    }


class PerQueryEvaluator:
    def __init__(self, vertex_config: dict, prompt_path: Path, output_dir: Path):
        self.client = _build_vertex_client(vertex_config)
        self.model = vertex_config.get("model") or DEFAULT_MODEL
        # 출력 잘림(MAX_TOKENS) 방지를 위해 하한을 16384로 보장.
        # v2.1 은 상품 메타를 LLM이 출력하지 않아 출력이 작지만, Warning/Fail 케이스의
        # 코멘트까지 안전하게 담도록 여유를 둔다.
        self.max_output_tokens = max(int(vertex_config.get("max_output_tokens") or 8192), 16384)
        self.max_workers = int(vertex_config.get("max_workers") or 5)
        self.max_retries = int(vertex_config.get("max_retries") or 3)
        self.retry_backoff = float(vertex_config.get("retry_backoff") or 2.0)
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        print(
            f"   Vertex AI 모델: {self.model}, "
            f"max_output_tokens={self.max_output_tokens}, "
            f"workers={self.max_workers}, retries={self.max_retries}"
        )

        if not prompt_path.exists():
            raise FileNotFoundError(f"프롬프트 파일 없음: {prompt_path}")
        self.prompt_text = prompt_path.read_text(encoding="utf-8")

        # thinking 비활성화 설정 (SDK가 지원할 때만)
        self._thinking_off = None
        try:
            self._thinking_off = types.ThinkingConfig(thinking_budget=0)
        except Exception:
            self._thinking_off = None

        self.cache = self._create_cache()
        self.write_lock = Lock()

    def _create_cache(self):
        try:
            cache = self.client.caches.create(
                model=self.model,
                config=types.CreateCachedContentConfig(
                    system_instruction=self.prompt_text,
                    ttl="3600s",
                    display_name="per_query_eval_v21",
                ),
            )
            print("   캐싱 등록 완료 → 토큰 절약 모드")
            return cache
        except Exception as e:
            print(f"   캐싱 미지원 → system_instruction 직접 전달 모드 ({e})")
            return None

    # ─────────────────────────────────────────────
    # 배치 평가
    # ─────────────────────────────────────────────
    def evaluate_all(self, inputs: list[dict]) -> list[dict]:
        """
        inputs: build_single_input(싱글턴) + group_multi_scenarios(멀티턴) 합집합.
        반환: data.json queries[] 객체들의 평탄화된 리스트.
        """
        # 파일명: KST 시각(YYYYMMDD_HHMMSS) + 식별자.
        #  · 이 평가가 단일 세션이면 그 session_id 꼬리(sess-adhoc-XXXX → XXXX)를 붙여 추적 용이
        #  · 세션이 여러 개(시트 배치 등)면 랜덤 6자리로 폴백
        stamp = now_kst().strftime("%Y%m%d_%H%M%S")
        jsonl_path = self.output_dir / f"queries_{stamp}_{self._jsonl_suffix(inputs)}.jsonl"
        results: list[dict] = []
        total = len(inputs)
        t0 = time.time()
        ok = err_cnt = 0

        print(f"  호출 시작: {total}건 (workers={self.max_workers}) → {jsonl_path.name}", flush=True)

        with ThreadPoolExecutor(max_workers=self.max_workers) as pool:
            futures = {
                pool.submit(self._evaluate_one_with_retry, inp): inp
                for inp in inputs
            }
            done = 0
            for fut in as_completed(futures):
                inp = futures[fut]
                case_id = inp.get("case_id", "?")
                try:
                    query_objs = fut.result()  # list[dict]
                    for q in query_objs:
                        results.append(q)
                        self._append_jsonl(jsonl_path, q)
                    ok += 1
                except Exception as e:
                    err = {"case_id": case_id, "error": str(e)}
                    results.append(err)
                    self._append_jsonl(jsonl_path, err)
                    err_cnt += 1
                    print(f"  ✗ {case_id}: {e}", flush=True)
                done += 1
                # 처음 3건 + 이후 5건마다 진행 출력 (초기 무응답 구간 가시화)
                if done <= 3 or done % 5 == 0 or done == total:
                    rate = done / max(time.time() - t0, 0.001)
                    print(f"  진행: {done}/{total} (성공 {ok} / 실패 {err_cnt}, "
                          f"{rate:.1f}건/s)", flush=True)

        elapsed = time.time() - t0
        print(f"  완료: {len(results)}건 ({elapsed:.0f}s) → {jsonl_path.name}", flush=True)
        return results

    # 상품 점수 누락 보완 시 한 번에 재질의할 상품 수 (작게 → lite도 끝까지 채움)
    GAP_BATCH = 12
    GAP_ROUNDS = 3

    def _evaluate_one_with_retry(self, eval_input: dict) -> list[dict]:
        is_multi = eval_input.get("track_hint") == "multi"
        is_yamato = eval_input.get("report_type") == "yamato"
        if is_yamato:
            schema = LLMScenarioEvalYamato if is_multi else LLMQueryEvalYamato
        else:
            schema = LLMScenarioEval if is_multi else LLMQueryEval
        compute = compute_query_yamato if is_yamato else compute_query

        # 1) 메인 호출 — temperature=0 고정 (환각 방지 / 판정 재현성)
        last_err = None
        llm_out = None
        for attempt in range(self.max_retries):
            try:
                llm_out = self._call_llm(eval_input, schema, is_multi)
                break
            except Exception as e:
                last_err = e
                self._dump_debug(eval_input, e, attempt)
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_backoff * (2 ** attempt))
        if llm_out is None:
            raise last_err or RuntimeError("평가 실패")

        # 2) 상품 점수 누락분 보완 — temperature=0, 누락 rank만 작은 묶음으로 재질의
        if is_multi:
            self._fill_gaps_multi(eval_input, llm_out)
            return self._assemble_multi(eval_input, llm_out, compute)
        self._fill_gaps_single(eval_input, eval_input.get("products") or [], llm_out)
        return [compute(eval_input, llm_out)]

    # ─────────────────────────────────────────────
    # 상품 점수 누락 보완 (gap-fill, 전부 temperature=0)
    # ─────────────────────────────────────────────
    def _fill_gaps_single(self, ctx_input: dict, products: list, target: dict) -> None:
        """target(메인 출력 또는 한 턴)의 product_scores 중 빠진 rank를 재질의해 채운다."""
        expected_ranks = [p.get("rank") for p in products[:30] if p.get("rank") is not None]
        have = {s.get("rank") for s in (target.get("product_scores") or [])}
        missing = [r for r in expected_ranks if r not in have]
        if not missing:
            return

        by_rank = {p["rank"]: p for p in products if p.get("rank") is not None}
        remaining = [by_rank[r] for r in missing]
        collected = []
        for _ in range(self.GAP_ROUNDS):
            if not remaining:
                break
            still = []
            for i in range(0, len(remaining), self.GAP_BATCH):
                batch = remaining[i:i + self.GAP_BATCH]
                got = self._score_only(ctx_input, batch)
                got_ranks = {g.get("rank") for g in got}
                collected.extend(got)
                still.extend(p for p in batch if p.get("rank") not in got_ranks)
            remaining = still

        if collected:
            target.setdefault("product_scores", [])
            existing = {s.get("rank") for s in target["product_scores"]}
            for s in collected:
                if s.get("rank") not in existing:
                    target["product_scores"].append(s)
                    existing.add(s.get("rank"))
            target["product_scores"].sort(key=lambda s: s.get("rank") or 0)
            print(f"    ＋ {ctx_input.get('case_id','?')}: 상품 점수 누락 {len(missing)}건 중 "
                  f"{len(collected)}건 보완", flush=True)

    def _fill_gaps_multi(self, scenario_input: dict, llm_out: dict) -> None:
        turn_inputs = scenario_turn_inputs(scenario_input)
        by_turn = {ti.get("turn_number"): ti for ti in turn_inputs}
        for idx, lt in enumerate(llm_out.get("turns") or []):
            ti = by_turn.get(lt.get("turn_number")) or (
                turn_inputs[idx] if idx < len(turn_inputs) else None)
            if ti is None:
                continue
            self._fill_gaps_single(ti, ti.get("products") or [], lt)

    def _score_only(self, ctx_input: dict, batch: list) -> list:
        """누락 상품 묶음에 대해 relevance_score만 재질의 (temperature=0)."""
        payload = {
            "query": ctx_input.get("query"),
            "answer_text": (ctx_input.get("answer_text") or "")[:1500],
            "products": [_compact_product(p) for p in batch],
        }
        user_content = (
            "아래 검색 결과 상품들의 적합성만 평가하라.\n"
            "products의 모든 rank에 빠짐없이 relevance_score(0~4)를 부여하라.\n"
            "score ≤ 2 인 경우에만 reason/violated_conditions/description/exposure_reason 작성.\n"
            "INPUT:\n" + json.dumps(payload, ensure_ascii=False)
        )
        cfg_kwargs = dict(
            response_mime_type="application/json",
            response_schema=LLMProductScoreList,
            temperature=0,
            max_output_tokens=self.max_output_tokens,
        )
        if self._thinking_off is not None:
            cfg_kwargs["thinking_config"] = self._thinking_off
        if self.cache is not None:
            cfg_kwargs["cached_content"] = self.cache.name
        else:
            cfg_kwargs["system_instruction"] = self.prompt_text
        try:
            resp = self.client.models.generate_content(
                model=self.model, contents=user_content,
                config=types.GenerateContentConfig(**cfg_kwargs),
            )
            parsed = getattr(resp, "parsed", None)
            if parsed is not None:
                d = parsed.model_dump() if hasattr(parsed, "model_dump") else parsed
            else:
                d = _loads_lenient(resp.text, resp)
            return d.get("product_scores") or []
        except Exception as e:
            print(f"    ⚠ gap-fill 실패 ({ctx_input.get('case_id','?')}): {e}", flush=True)
            return []

    def _assemble_multi(self, scenario_input: dict, llm_out: dict, compute=compute_query) -> list[dict]:
        """멀티턴: LLM turns[] 를 턴별 입력과 매칭해 compute(GELATTO 또는 야마토)."""
        turn_inputs = scenario_turn_inputs(scenario_input)
        by_turn = {ti.get("turn_number"): ti for ti in turn_inputs}
        out = []
        llm_turns = llm_out.get("turns") or []
        for idx, lt in enumerate(llm_turns):
            tn = lt.get("turn_number")
            ti = by_turn.get(tn) or (turn_inputs[idx] if idx < len(turn_inputs) else None)
            if ti is None:
                continue
            out.append(compute(ti, lt))
        return out

    # ─────────────────────────────────────────────
    # 단일 LLM 호출
    # ─────────────────────────────────────────────
    def _call_llm(self, eval_input: dict, schema, is_multi: bool) -> dict:
        if is_multi:
            turn_inputs = scenario_turn_inputs(eval_input)
            payload = {
                "case_id": eval_input.get("case_id"),
                "turns": [_build_llm_input(ti) for ti in turn_inputs],
            }
            rule = (
                "멀티턴 시나리오다. turns[] 의 각 턴을 평가해 LLMScenarioEval 형식으로 반환하라.\n"
                "각 턴 객체에 turn_number 를 반드시 포함하라. previous_turn_queries 로 이전 맥락을 판단하라.\n"
                "각 턴의 product_scores 개수는 그 턴 INPUT products 개수와 정확히 같아야 한다(모든 rank 평가).\n"
            )
        else:
            payload = _build_llm_input(eval_input)
            n_prod = len(payload.get("products") or [])
            rule = (
                f"INPUT products[]에 상품이 {n_prod}개 있다. product_scores도 정확히 {n_prod}개여야 하며,\n"
                f"products[]의 모든 rank(1~{n_prod})에 빠짐없이 relevance_score를 부여하라. 일부만 채우지 마라.\n"
            )

        user_content = (
            "아래 INPUT_JSON을 평가하라. response_schema를 따르는 JSON 객체 하나만 반환하라.\n"
            "수치·판정·KPI·phoenix_checks(기계 항목)는 출력하지 마라(코드가 계산).\n"
            "당신은 라벨/이유/상품 relevance_score(0~4)/params_ok/grounding_ok만 출력한다.\n"
            "상품 relevance_score는 INPUT의 products[].rank 기준으로 부여하라.\n"
            "같은 문장을 반복하지 마라. 모든 이유는 1~2문장.\n"
            + rule +
            "INPUT_JSON:\n" + json.dumps(payload, ensure_ascii=False)
        )

        cfg_kwargs = dict(
            response_mime_type="application/json",
            response_schema=schema,
            temperature=0,
            max_output_tokens=self.max_output_tokens,
        )
        # gemini-2.5 계열: thinking 비활성화 → 지연/토큰 소모 감소 (지원 시에만)
        if self._thinking_off is not None:
            cfg_kwargs["thinking_config"] = self._thinking_off

        if self.cache is not None:
            cfg_kwargs["cached_content"] = self.cache.name
        else:
            cfg_kwargs["system_instruction"] = self.prompt_text

        gen_config = types.GenerateContentConfig(**cfg_kwargs)

        response = self.client.models.generate_content(
            model=self.model, contents=user_content, config=gen_config,
        )

        parsed = getattr(response, "parsed", None)
        if parsed is not None:
            if hasattr(parsed, "model_dump"):
                return parsed.model_dump()
            if isinstance(parsed, dict):
                return parsed
            return json.loads(json.dumps(parsed, ensure_ascii=False, default=str))

        if response.text is None:
            finish = "UNKNOWN"
            if response.candidates:
                finish = str(response.candidates[0].finish_reason)
            raise RuntimeError(
                f"response.text=None (finish_reason={finish}). MAX_TOKENS/SAFETY 가능성."
            )
        return _loads_lenient(response.text, response)

    def _dump_debug(self, eval_input: dict, err: Exception, attempt: int):
        case_id = eval_input.get("case_id", "?")
        path = self.output_dir / f"debug_{case_id}_attempt{attempt + 1}.txt"
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write("INPUT:\n")
                f.write(json.dumps(eval_input, ensure_ascii=False, indent=2, default=str))
                f.write("\n\nERROR:\n")
                f.write(str(err))
        except Exception:
            pass

    @staticmethod
    def _jsonl_suffix(inputs: list[dict]) -> str:
        """평가 입력들의 session_id 를 모아, 단일 세션이면 그 꼬리를, 아니면 랜덤 6자리."""
        session_ids = set()
        for inp in inputs:
            if inp.get("session_id"):
                session_ids.add(inp["session_id"])
            for t in (inp.get("turns") or []):       # 멀티턴 시나리오
                if t.get("session_id"):
                    session_ids.add(t["session_id"])
        if len(session_ids) == 1:
            sid = next(iter(session_ids))
            tail = str(sid).rsplit("-", 1)[-1]       # sess-adhoc-abcd1234 → abcd1234
            tail = re.sub(r"[^A-Za-z0-9]", "", tail)  # 파일명 안전화
            if tail:
                return tail
        return uuid.uuid4().hex[:6]

    def _append_jsonl(self, path: Path, obj: dict):
        with self.write_lock:
            with open(path, "a", encoding="utf-8") as f:
                f.write(json.dumps(obj, ensure_ascii=False, default=str) + "\n")


# ─────────────────────────────────────────────
# JSON 파싱 (잘림 대비 salvage) — 모듈 레벨 헬퍼
# ─────────────────────────────────────────────
def _loads_lenient(text: str, response=None) -> dict:
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        repaired = _repair_truncated_json(text)
        try:
            return json.loads(repaired)
        except json.JSONDecodeError:
            finish = ""
            if response is not None and getattr(response, "candidates", None):
                finish = f" finish_reason={response.candidates[0].finish_reason}"
            raise json.JSONDecodeError(
                f"{e.msg} (잘린 출력 복구 실패 — MAX_TOKENS 가능성{finish})",
                e.doc, e.pos,
            )


def _repair_truncated_json(text: str) -> str:
    """MAX_TOKENS로 잘린 JSON을 best-effort로 닫아 복구한다."""
    stack = []
    in_str = False
    esc = False
    for ch in text:
        if esc:
            esc = False
            continue
        if in_str:
            if ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch in "{[":
            stack.append("}" if ch == "{" else "]")
        elif ch in "}]":
            if stack:
                stack.pop()

    repaired = text
    if in_str:                       # 문자열 중간에서 끊김 → 닫기
        repaired += '"'
    repaired = repaired.rstrip()
    # 매달린 콜론/콤마/불완전 키 제거
    while repaired and repaired[-1] in ",:":
        repaired = repaired[:-1].rstrip()
    # 불완전 키("foo 뒤에 값 없음)만 남았으면 그 키 제거
    repaired = re.sub(r',\s*"[^"]*"$', "", repaired)
    repaired += "".join(reversed(stack))
    return repaired
