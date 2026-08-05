
import threading
import uuid
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from core.chat_api_class import (
    GelattoClient,
    AdkFrontClient,
    GcloudRunClient,
    generate_session_id,
    process_query,
)
from core.sheets_io import (
    update_result_to_sheet_batch,
    setup_google_sheets,
    load_questions_and_setup_columns,
    load_scenarios_and_setup_columns,
    ensure_faq_columns,
)
from core.logger import save_response_log, logger
from core.config_loader import now_kst
from core.phoenix_collector import (
    PhoenixClient,
    ensure_phoenix_columns,
    collect_phoenix_for_row,
)


# ============================================================
# 클라이언트 팩토리 — profile의 api_type에 따라 분기
# ============================================================
def build_client(config: dict):
    """
    config['api_type'] 값에 따라 알맞은 API 클라이언트를 생성한다.
      - 'adk_front'  : ADK2-front API (표준 SSE + IAP 인증)
      - 'gcloud_run' : ADK2 body/SSE 동일, 인증만 Cloud Run IAM
                       (gcloud auth print-identity-token) — qa-gelatto-genserd-chat 등
      - 그 외/미지정 : 기존 GelattoClient (기본값)
    세 클라이언트 모두 send_chat / get_product_histories 인터페이스를 공유하므로
    process_query() 는 동일하게 동작한다.
    """
    api_type = (config.get("api_type") or "gelatto").lower()
    if api_type in ("gcloud_run", "gcloud", "cloud_run", "cloudrun", "genserd", "qa_gcloud"):
        print(f"    🔌 클라이언트: GcloudRunClient (api_type={api_type})")
        return GcloudRunClient.from_config(config)
    if api_type in ("adk_front", "adk2_front", "adk2-front", "adk"):
        print(f"    🔌 클라이언트: AdkFrontClient (api_type={api_type})")
        return AdkFrontClient.from_config(config)
    return GelattoClient.from_config(config)


# ============================================================
# 쿼리 워커 (병렬 - 싱글턴 전용)
# ============================================================
def worker_task(
    idx:                 int,
    total:               int,
    row_index:           int,
    query:               str,
    client,
    worksheet,
    result_cols:         dict,
    config:              dict,
    sheet_lock:          threading.Lock,
    timestamp:           str,
    phoenix_client:      "PhoenixClient | None" = None,
    phoenix_result_cols: "dict | None"          = None,
) -> dict:
    """단일 쿼리 처리 + 시트 기록 + Phoenix 수집 (스레드 안전)"""
    session_id = generate_session_id(row_index, config["session_id_readable"])

    print(f"\n{'='*60}")
    print(f"[{idx}/{total}] 행 {row_index} 시작: {query}")
    print(f"{'='*60}")

    try:
        result_data = process_query(client, query, session_id, config)

        save_response_log(
            identifier    = f"row_{idx:04d}",
            query         = query,
            response_text = result_data["response_text"],
            session_id    = session_id,
        )
        logger.info(f"row {idx} done | len={len(result_data)}")

        # FAQ 응답이면(faq_description 키 존재) 시트에 컬럼이 없을 수 있으니
        # 쓰기 전에 지연 생성 — 상품 응답 행은 API 호출 없이 즉시 통과.
        if "faq_description" in result_data:
            ensure_faq_columns(worksheet, result_cols, timestamp, sheet_lock)

        update_result_to_sheet_batch(
            worksheet, row_index, result_cols, result_data,
            sheet_lock, config["sheet_write_delay"],
        )

        print(
            f"    💾 [{idx}/{total}] 행 {row_index} 시트 업데이트 완료 "
            f"(products={result_data['product_count']}개)"
        )

        # ── Phoenix 로그 수집 ──────────────────────────────────
        _collect_phoenix(
            phoenix_client, phoenix_result_cols,
            config, session_id, worksheet, row_index, sheet_lock,
            label=f"[{idx}/{total}] 행 {row_index}",
        )

        return {
            "idx":        idx,
            "row_index":  row_index,
            "session_id": session_id,
            "success":    bool(result_data["chat_request_id"]),
            "result":     result_data,
        }

    except Exception as e:
        import traceback
        print(f"    ❌ [{idx}/{total}] 행 {row_index} 처리 실패: {e}")
        traceback.print_exc()
        return {
            "idx":        idx,
            "row_index":  row_index,
            "session_id": session_id,
            "success":    False,
            "result":     None,
            "error":      str(e),
        }


# ============================================================
# 시나리오 워커 (한 시나리오의 모든 턴을 순차 처리 — 멀티턴 전용)
# ============================================================
def scenario_worker(
    scenario_idx:        int,
    total_scenarios:     int,
    scenario_id:         str,
    turns:               list,
    client,
    worksheet,
    result_cols:         dict,
    config:              dict,
    sheet_lock:          threading.Lock,
    timestamp:           str,
    phoenix_client:      "PhoenixClient | None" = None,
    phoenix_result_cols: "dict | None"          = None,
) -> dict:
    """
    한 시나리오의 모든 턴을 순차 처리 (session_id + user_id 공유).
    각 턴 완료 후 Phoenix 로그를 수집한다.
    """
    session_id = generate_session_id(scenario_id, config["session_id_readable"])

    safe_scenario = "".join(c for c in str(scenario_id) if c.isalnum() or c in "-_")
    user_id       = f"{config['user_id_prefix']}-{safe_scenario}-{uuid.uuid4().hex[:6]}"

    scenario_config            = dict(config)
    scenario_config["user_id"] = user_id

    print(f"\n{'#' * 60}")
    print(
        f"[시나리오 {scenario_idx}/{total_scenarios}] ID: {scenario_id} | "
        f"session_id: {session_id} | user_id: {user_id} | 턴: {len(turns)}개"
    )
    print(f"{'#' * 60}")

    scenario_success = 0
    scenario_fail    = 0

    for turn_idx, (row_index, turn_number, query) in enumerate(turns, start=1):
        print(f"\n{'=' * 60}")
        print(f"[시나리오 {scenario_id} / 턴 {turn_number}] 행 {row_index}: {query}")
        print(f"{'=' * 60}")

        try:
            result_data = process_query(client, query, session_id, scenario_config)

            print(
                f"    📊 [{scenario_id}/T{turn_number}] "
                f"req_id={result_data['chat_request_id']} "
                f"latency={result_data['latency']}s "
                f"products={result_data['product_count']}개"
            )

            save_response_log(
                identifier    = f"row_{safe_scenario}",
                query         = query,
                response_text = result_data["response_text"],
                session_id    = session_id,
                turn          = turn_number,
            )
            logger.info(
                f"row {scenario_idx} turn {turn_number} done | "
                f"len={len(result_data['response_text'])}"
            )

            if result_data["error"]:
                print(f"    ⚠️  [{scenario_id}/T{turn_number}] error: {result_data['error']}")

            # FAQ 응답이면 시트에 컬럼이 없을 수 있으니 쓰기 전에 지연 생성
            if "faq_description" in result_data:
                ensure_faq_columns(worksheet, result_cols, timestamp, sheet_lock)

            update_result_to_sheet_batch(
                worksheet, row_index, result_cols, result_data,
                sheet_lock, scenario_config["sheet_write_delay"],
            )
            print(f"    💾 [{scenario_id}/T{turn_number}] 시트 업데이트 완료")

            # ── Phoenix 로그 수집 (턴 단위) ─────────────────────
            _collect_phoenix(
                phoenix_client, phoenix_result_cols,
                scenario_config, session_id, worksheet, row_index, sheet_lock,
                label=f"[{scenario_id}/T{turn_number}] 행 {row_index}",
            )

            turn_success = bool(result_data["chat_request_id"])
            if turn_success:
                scenario_success += 1
            else:
                scenario_fail += 1

            if not turn_success and not scenario_config["continue_on_turn_failure"]:
                remaining = len(turns) - turn_idx
                if remaining > 0:
                    print(f"    ⛔ 턴 실패 — 시나리오 '{scenario_id}'의 남은 {remaining}개 턴 스킵")
                    scenario_fail += remaining
                break

            if turn_idx < len(turns):
                time.sleep(scenario_config["delay_between_turns"])

        except Exception as e:
            import traceback
            print(f"    ❌ [{scenario_id}/T{turn_number}] 예외: {e}")
            traceback.print_exc()
            scenario_fail += 1

    return {
        "scenario_id": scenario_id,
        "success":     scenario_success,
        "fail":        scenario_fail,
        "total_turns": len(turns),
    }


# ============================================================
# Phoenix 수집 공통 헬퍼 (내부용)
# ============================================================
def _collect_phoenix(
    phoenix_client:      "PhoenixClient | None",
    phoenix_result_cols: "dict | None",
    config:              dict,
    session_id:          str,
    worksheet,
    row_index:           int,
    sheet_lock:          threading.Lock,
    label:               str = "",
) -> None:
    """
    phoenix_client와 phoenix_result_cols가 모두 있을 때만 수집을 시도한다.
    예외는 잡아서 경고만 출력 — Phoenix 실패가 전체 테스트를 막지 않도록.
    """
    if not phoenix_client or not phoenix_result_cols:
        return

    phoenix_cfg = config.get("phoenix", {})
    try:
        collect_phoenix_for_row(
            client              = phoenix_client,
            project_id          = phoenix_cfg["project_id"],
            session_id          = session_id,
            worksheet           = worksheet,
            row_idx             = row_index,
            phoenix_result_cols = phoenix_result_cols,
            sheet_lock          = sheet_lock,
            delay_sec           = phoenix_cfg.get("delay_sec",     5.0),
            max_retries         = phoenix_cfg.get("max_retries",   3),
            retry_backoff       = phoenix_cfg.get("retry_backoff", 2.0),
            sheet_write_delay   = config.get("sheet_write_delay",  0.3),
        )
    except Exception as e:
        print(f"    ⚠️ Phoenix 수집 실패 {label}: {e}")


# ============================================================
# 메인 실행 (싱글턴)
# ============================================================
def run_api_test(config: dict):
    print("\n" + "=" * 60)
    print(
        f"API 기반 LLM 테스트 시작 "
        f"(profile={config['profile_key']}, 병렬 {config['max_workers']}개)"
    )
    print("=" * 60)

    # 타임스탬프를 먼저 생성 — API 컬럼과 Phoenix 컬럼이 동일한 suffix를 공유
    timestamp = now_kst().strftime("%Y-%m-%d_%H:%M")

    worksheet = setup_google_sheets(
        config["credentials_file"],
        config["spreadsheet_name"],
        config["worksheet_name"],
    )

    questions, _question_col, result_cols, _ = load_questions_and_setup_columns(
        worksheet, config["question_column"], timestamp=timestamp,
    )

    # ── Phoenix 클라이언트 & 컬럼 초기화 ──────────────────────
    phoenix_client      = None
    phoenix_result_cols = None
    phoenix_cfg         = config.get("phoenix", {})
    if phoenix_cfg.get("enabled"):
        phoenix_client      = PhoenixClient.from_phoenix_config(phoenix_cfg)
        phoenix_result_cols = ensure_phoenix_columns(worksheet, timestamp=timestamp)
        print(
            f"\n🔍 Phoenix 수집 활성화 | "
            f"project={phoenix_cfg['project_key']} | "
            f"delay={phoenix_cfg['delay_sec']}s | "
            f"max_retries={phoenix_cfg['max_retries']}"
        )
    else:
        print("\n⏭️  Phoenix 수집 비활성화 (phoenix.yaml 미설정 또는 project_id 없음)")

    client = build_client(config)

    if not questions:
        print("테스트할 질문이 없습니다.")
        return

    print("=" * 60)
    print(f"API 엔드포인트: {config['api_base_url']}")
    print(f"총 {len(questions)}개 질문 처리 예정")
    print("=" * 60)

    # 이미 처리된 행 확인
    all_values     = worksheet.get_all_values()
    processed_rows = set()

    if "chat_request_id" in result_cols:
        crid_col = result_cols["chat_request_id"]
        for i, row in enumerate(all_values[1:], start=2):
            if len(row) >= crid_col and str(row[crid_col - 1]).strip():
                processed_rows.add(i)

    pending    = [(ri, q) for ri, q in questions if ri not in processed_rows]
    skip_count = len(questions) - len(pending)

    if skip_count > 0:
        print(f"⏭️  이미 처리된 {skip_count}개 건너뜀")
    if not pending:
        print("🎉 모든 질문이 이미 처리되었습니다.")
        return

    success_count = 0
    fail_count    = 0
    sheet_lock    = threading.Lock()

    with ThreadPoolExecutor(max_workers=config["max_workers"]) as executor:
        futures = {
            executor.submit(
                worker_task,
                idx, len(pending), row_index, query,
                client,
                worksheet, result_cols, config, sheet_lock, timestamp,
                phoenix_client, phoenix_result_cols,
            ): (idx, row_index, query)
            for idx, (row_index, query) in enumerate(pending, start=1)
        }

        for future in as_completed(futures):
            idx, row_index, query = futures[future]
            try:
                outcome = future.result()
                if outcome["success"]:
                    success_count += 1
                else:
                    fail_count += 1
            except Exception as e:
                fail_count += 1
                print(f"    ❌ 행 {row_index} 예외: {e}")

    print("\n" + "=" * 60)
    print("🎉 모든 테스트 완료!")
    print("=" * 60)
    print(f"총 처리: {len(pending)}개 (건너뜀: {skip_count}개)")
    print(f"성공: {success_count}개")
    print(f"실패: {fail_count}개")
    print("=" * 60)


# ============================================================
# 메인 실행 (멀티턴 — 시나리오 단위 병렬)
# ============================================================
def run_multiturn_test(config: dict):
    """멀티턴 시나리오 기반 LLM 테스트 (시나리오 단위 병렬)"""
    print("\n" + "=" * 60)
    print(
        f"멀티턴 LLM 테스트 시작 "
        f"(profile={config['profile_key']}, 병렬 {config['max_workers']}개)"
    )
    print("=" * 60)

    # 타임스탬프를 먼저 생성 — API 컬럼과 Phoenix 컬럼이 동일한 suffix를 공유
    timestamp = now_kst().strftime("%Y-%m-%d_%H:%M")

    worksheet = setup_google_sheets(
        config["credentials_file"],
        config["spreadsheet_name"],
        config["worksheet_name"],
    )

    scenarios, _col_indices, result_cols, _ = load_scenarios_and_setup_columns(
        worksheet,
        config["scenario_id_column"],
        config["turn_column"],
        config["question_column"],
        timestamp=timestamp,
    )

    if not scenarios:
        print("테스트할 시나리오가 없습니다.")
        return

    # ── Phoenix 클라이언트 & 컬럼 초기화 ──────────────────────
    phoenix_client      = None
    phoenix_result_cols = None
    phoenix_cfg         = config.get("phoenix", {})
    if phoenix_cfg.get("enabled"):
        phoenix_client      = PhoenixClient.from_phoenix_config(phoenix_cfg)
        phoenix_result_cols = ensure_phoenix_columns(worksheet, timestamp=timestamp)
        print(
            f"\n🔍 Phoenix 수집 활성화 | "
            f"project={phoenix_cfg['project_key']} | "
            f"delay={phoenix_cfg['delay_sec']}s | "
            f"max_retries={phoenix_cfg['max_retries']}"
        )
    else:
        print("\n⏭️  Phoenix 수집 비활성화 (phoenix.yaml 미설정 또는 project_id 없음)")

    total_turns = sum(len(turns) for turns in scenarios.values())
    client      = build_client(config)

    print("=" * 60)
    print(f"API 엔드포인트: {config['api_base_url']}")
    print(f"총 {len(scenarios)}개 시나리오, {total_turns}개 턴 처리 예정")
    print("=" * 60)

    total_success  = 0
    total_fail     = 0
    sheet_lock     = threading.Lock()
    scenario_items = list(scenarios.items())

    with ThreadPoolExecutor(max_workers=config["max_workers"]) as executor:
        futures = {
            executor.submit(
                scenario_worker,
                idx, len(scenario_items), scenario_id, turns,
                client,
                worksheet, result_cols, config, sheet_lock, timestamp,
                phoenix_client, phoenix_result_cols,
            ): scenario_id
            for idx, (scenario_id, turns) in enumerate(scenario_items, start=1)
        }

        for future in as_completed(futures):
            scenario_id = futures[future]
            try:
                outcome        = future.result()
                total_success += outcome["success"]
                total_fail    += outcome["fail"]
                print(
                    f"\n✓ 시나리오 '{scenario_id}' 완료: "
                    f"성공 {outcome['success']}/{outcome['total_turns']}"
                )
            except Exception as e:
                print(f"\n❌ 시나리오 '{scenario_id}' 예외: {e}")
                total_fail += len(scenarios[scenario_id])

    print("\n" + "=" * 60)
    print("🎉 모든 테스트 완료!")
    print("=" * 60)
    print(f"총 시나리오: {len(scenarios)}개")
    print(f"총 턴:       {total_turns}개")
    print(f"성공:        {total_success}개")
    print(f"실패:        {total_fail}개")
    print("=" * 60)
