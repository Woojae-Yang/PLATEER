import gspread
import json
import threading
import time
from typing import Optional
from google.oauth2.service_account import Credentials
from core.config_loader import now_kst
from collections import defaultdict, OrderedDict
from core.chat_api_class import parse_turn_number


# ============================================================
# Google Sheets 연결
# ============================================================
def setup_google_sheets(credentials_file, spreadsheet_name, worksheet_name):
    print("=" * 60)
    print("Google Sheets 연결 중...")
    print("=" * 60)

    try:
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        creds = Credentials.from_service_account_file(credentials_file, scopes=scopes)
        client = gspread.authorize(creds)
        spreadsheet = client.open(spreadsheet_name)
        worksheet = spreadsheet.worksheet(worksheet_name)

        print(f"✅ 연결 성공")
        print(f"   스프레드시트: {spreadsheet_name}")
        print(f"   워크시트: {worksheet_name}\n")

        return worksheet
    except Exception as e:
        print(f"❌ Google Sheets 연결 실패: {e}")
        raise


# ============================================================
# 쿼리 로드 & 결과 컬럼 설정 (싱글턴 전용)
# ============================================================
def load_questions_and_setup_columns(worksheet, question_col_name,
                                     timestamp: Optional[str] = None):
    """
    질문 로드 및 결과 컬럼 생성 (배치 처리로 429 방지).

    Args:
        timestamp: 컬럼명에 붙일 타임스탬프. None이면 현재 KST 시각으로 자동 생성.

    Returns:
        (questions, question_col_index, result_cols, timestamp)
        ※ timestamp를 4번째 반환값으로 추가해 Phoenix 컬럼과 동일한 suffix 공유 가능.
    """
    print("=" * 60)
    print("데이터 로드 및 컬럼 설정")
    print("=" * 60)

    all_values = worksheet.get_all_values()
    if not all_values:
        raise ValueError("시트가 비어있습니다.")

    headers = all_values[0]
    print(f"현재 헤더: {headers}")

    try:
        question_col_index = headers.index(question_col_name) + 1
        print(f"✅ '{question_col_name}' 컬럼 찾음: {question_col_index}번째")
    except ValueError:
        raise ValueError(
            f"'{question_col_name}' 컬럼을 찾을 수 없습니다. 현재 헤더: {headers}"
        )

    # 결과 컬럼명 (timestamp 포함) — 외부에서 주입하거나 자동 생성
    if timestamp is None:
        timestamp = now_kst().strftime("%Y-%m-%d_%H:%M")
    result_col_names = {
        "session_id": f"session_id_{timestamp}",
        "answer_text": f"answer_text_{timestamp}",
        "progress_data": f"progress_data_{timestamp}",
        "keywords": f"keywords_{timestamp}",
        "latency": f"latency_{timestamp}",
        "chat_request_id": f"chat_request_id_{timestamp}",
        "product_count": f"product_count_{timestamp}",
        #"response_type": f"response_type_{timestamp}",

        # ※ faq_* 6개 컬럼은 여기서 만들지 않는다 — 실행 중 첫 FAQ 응답이 나올 때
        #   ensure_faq_columns()가 지연 생성한다 (상품만 있는 실행엔 컬럼 자체가 안 생김).

        # response_text 3개로 분리 (셀 50,000자 제한 대응)
        "response_text_1": f"response_text_1_{timestamp}",
        "response_text_2": f"response_text_2_{timestamp}",
        "response_text_3": f"response_text_3_{timestamp}",
        "response_text_4": f"response_text_4_{timestamp}",
        "response_text_5": f"response_text_5_{timestamp}",
        
        "product_ids": f"product_ids_{timestamp}",

        "error": f"error_{timestamp}",
    }

    print(f"\n생성할 컬럼명:")
    for key, name in result_col_names.items():
        print(f"  - {name}")

    # 컬럼 생성 — batch_update 1회로 묶어서 처리 (429 방지)
    result_cols = {}
    new_columns = []  # (key, col_name, target_index)

    for key, col_name in result_col_names.items():
        if col_name in headers:
            result_cols[key] = headers.index(col_name) + 1
            print(f"✅ '{col_name}' 컬럼 존재: {result_cols[key]}번째")
        else:
            new_col_index = len(headers) + 1
            new_columns.append((key, col_name, new_col_index))
            result_cols[key] = new_col_index
            headers.append(col_name)

    if new_columns:
        max_target = max(idx for _, _, idx in new_columns)
        current_cols = worksheet.col_count
        if max_target > current_cols:
            needed_cols = max_target - current_cols + 5
            print(f"    ℹ️  시트 확장 중: {current_cols}개 → {current_cols + needed_cols}개 컬럼")
            worksheet.add_cols(needed_cols)

        def _col_letter(col_num: int) -> str:
            result = ""
            while col_num > 0:
                col_num, remainder = divmod(col_num - 1, 26)
                result = chr(65 + remainder) + result
            return result

        updates = [
            {"range": f"{_col_letter(idx)}1", "values": [[col_name]]}
            for _, col_name, idx in new_columns
        ]
        worksheet.batch_update(updates, value_input_option='RAW')

        for _, col_name, idx in new_columns:
            print(f"✅ '{col_name}' 컬럼 생성: {idx}번째")

    # 질문 리스트 추출
    questions = []
    for i, row in enumerate(all_values[1:], start=2):
        if len(row) >= question_col_index:
            question = row[question_col_index - 1]
            if question.strip():
                questions.append((i, question))

    print(f"\n총 {len(questions)}개의 질문 발견\n")

    return questions, question_col_index, result_cols, timestamp


# ============================================================
# 시나리오 로드 & 결과 컬럼 설정 (멀티턴 전용)
# ============================================================
def load_scenarios_and_setup_columns(worksheet, scenario_col_name, turn_col_name,
                                     question_col_name, timestamp: Optional[str] = None):
    """
    멀티턴 시나리오 로드 및 결과 컬럼 생성 (배치 처리로 429 방지).

    Args:
        timestamp: 컬럼명에 붙일 타임스탬프. None이면 현재 KST 시각으로 자동 생성.

    Returns:
        (scenarios, col_indices, result_cols, timestamp)
        ※ timestamp를 4번째 반환값으로 추가.
    """
    print("=" * 60)
    print("데이터 로드 및 컬럼 설정")
    print("=" * 60)

    all_values = worksheet.get_all_values()
    if not all_values:
        raise ValueError("시트가 비어있습니다.")

    headers = all_values[0]
    print(f"현재 헤더: {headers}")

    # 필수 컬럼 인덱스
    col_indices = {}
    for key, col_name in [
        ("scenario_id", scenario_col_name),
        ("turn", turn_col_name),
        ("question", question_col_name),
    ]:
        try:
            col_indices[key] = headers.index(col_name) + 1
            print(f"✅ '{col_name}' 컬럼 찾음: {col_indices[key]}번째")
        except ValueError:
            raise ValueError(
                f"'{col_name}' 컬럼을 찾을 수 없습니다. 현재 헤더: {headers}"
            )

    # 결과 컬럼명 (timestamp 포함) — 외부에서 주입하거나 자동 생성
    if timestamp is None:
        timestamp = now_kst().strftime("%Y-%m-%d_%H:%M")
    result_col_names = OrderedDict([
        ("session_id", f"session_id_{timestamp}"),
        ("answer_text", f"answer_text_{timestamp}"),
        ("progress_data", f"progress_data_{timestamp}"),
        ("keywords", f"keywords_{timestamp}"),
        ("latency", f"latency_{timestamp}"),
        ("chat_request_id", f"chat_request_id_{timestamp}"),
        ("product_count", f"product_count_{timestamp}"),

        # ※ faq_* 6개 컬럼은 여기서 만들지 않는다 — 실행 중 첫 FAQ 응답이 나올 때
        #   ensure_faq_columns()가 지연 생성한다 (상품만 있는 실행엔 컬럼 자체가 안 생김).

        # response_text 5개로 분리 (셀 50,000자 제한 대응)
        ("response_text_1", f"response_text_1_{timestamp}"),
        ("response_text_2", f"response_text_2_{timestamp}"),
        ("response_text_3", f"response_text_3_{timestamp}"),
        ("response_text_4", f"response_text_4_{timestamp}"),
        ("response_text_5", f"response_text_5_{timestamp}"),

        ("product_ids", f"product_ids_{timestamp}"),

        ("error", f"error_{timestamp}"),
    ])

    print(f"\n생성할 컬럼명:")
    for key, name in result_col_names.items():
        print(f"  - {name}")

    # 컬럼 생성 — batch_update 1회로 묶어서 처리 (429 방지)
    result_cols = {}
    new_columns = []  # (key, col_name, target_index)

    for key, col_name in result_col_names.items():
        if col_name in headers:
            result_cols[key] = headers.index(col_name) + 1
            print(f"✅ '{col_name}' 컬럼 존재: {result_cols[key]}번째")
        else:
            new_col_index = len(headers) + 1
            new_columns.append((key, col_name, new_col_index))
            result_cols[key] = new_col_index
            headers.append(col_name)

    if new_columns:
        max_target = max(idx for _, _, idx in new_columns)
        current_cols = worksheet.col_count
        if max_target > current_cols:
            needed_cols = max_target - current_cols + 5
            print(f"    ℹ️  시트 확장 중: {current_cols}개 → {current_cols + needed_cols}개 컬럼")
            worksheet.add_cols(needed_cols)

        def _col_letter(col_num: int) -> str:
            result = ""
            while col_num > 0:
                col_num, remainder = divmod(col_num - 1, 26)
                result = chr(65 + remainder) + result
            return result

        updates = [
            {"range": f"{_col_letter(idx)}1", "values": [[col_name]]}
            for _, col_name, idx in new_columns
        ]
        worksheet.batch_update(updates, value_input_option='RAW')

        for _, col_name, idx in new_columns:
            print(f"✅ '{col_name}' 컬럼 생성: {idx}번째")

    # 시나리오별 그룹핑
    scenarios = OrderedDict()
    skipped_rows = 0
    turn_parse_failures = 0

    for i, row in enumerate(all_values[1:], start=2):
        max_idx = max(col_indices["scenario_id"], col_indices["turn"], col_indices["question"])
        if len(row) < max_idx:
            skipped_rows += 1
            continue

        scenario_id = row[col_indices["scenario_id"] - 1].strip()
        turn_raw = row[col_indices["turn"] - 1].strip()
        question = row[col_indices["question"] - 1].strip()

        if not scenario_id or not question:
            skipped_rows += 1
            continue

        turn_number = parse_turn_number(turn_raw)
        if turn_number is None:
            print(f"    ⚠️  행 {i}: 턴 번호 파싱 실패 ('{turn_raw}') - 스킵")
            turn_parse_failures += 1
            skipped_rows += 1
            continue

        if scenario_id not in scenarios:
            scenarios[scenario_id] = []
        scenarios[scenario_id].append((i, turn_number, question))

    # 시나리오 내 턴 번호 순 정렬
    for scenario_id in scenarios:
        scenarios[scenario_id].sort(key=lambda x: x[1])

    total_turns = sum(len(turns) for turns in scenarios.values())
    print(f"\n총 {len(scenarios)}개 시나리오, {total_turns}개 턴 발견")
    if skipped_rows > 0:
        print(f"(스킵된 행: {skipped_rows}개, 그 중 턴 파싱 실패: {turn_parse_failures}개)")

    # 턴 번호 중복/누락 경고
    for scenario_id, turns in scenarios.items():
        turn_nums = [t[1] for t in turns]
        if turn_nums != sorted(set(turn_nums)):
            print(f"    ⚠️  시나리오 '{scenario_id}': 턴 번호 중복/누락 가능 - {turn_nums}")

    print()
    return scenarios, col_indices, result_cols, timestamp


# ============================================================
# FAQ 컬럼 지연 생성 (실행 중 첫 FAQ 응답이 나온 시점에만 생성)
# ============================================================
def ensure_faq_columns(worksheet, result_cols: dict, timestamp: str,
                       sheet_lock: threading.Lock) -> None:
    """
    faq_* 6개 컬럼을 실행 시작 시점이 아니라, 실행 중 처음 FAQ 응답을 만났을 때
    지연 생성한다. 상품 응답만 있는 실행에서는 이 함수가 한 번도 시트에 쓰지 않아
    faq_* 컬럼 자체가 생기지 않는다.

    result_cols는 worker 스레드 간 공유되는 dict — 이미 키가 있으면(다른 스레드가
    먼저 생성했거나 재실행) API 호출 없이 즉시 반환한다. sheet_lock으로 컬럼 추가
    구간을 보호해 두 스레드가 동시에 같은 컬럼을 추가하는 걸 막는다(이미 시트 쓰기도
    같은 lock을 쓰고 있어 추가 락 없이 재사용).
    """
    if "faq_description" in result_cols:
        return

    with sheet_lock:
        # double-check: lock 대기 중 다른 스레드가 먼저 만들었을 수 있음
        if "faq_description" in result_cols:
            return

        faq_col_names = {
            "faq_description": f"faq_description_{timestamp}",
            "faq_summary": f"faq_summary_{timestamp}",
            "faq_detail_1": f"faq_detail_1_{timestamp}",
            "faq_detail_2": f"faq_detail_2_{timestamp}",
            "faq_resource": f"faq_resource_{timestamp}",
            "faq_length_type": f"faq_length_type_{timestamp}",
        }

        headers = worksheet.row_values(1)

        new_columns = []  # (key, col_name, target_index)
        for key, col_name in faq_col_names.items():
            if col_name in headers:
                # 재실행 등으로 이미 시트에 존재하면 재사용
                result_cols[key] = headers.index(col_name) + 1
            else:
                new_col_index = len(headers) + 1
                new_columns.append((key, col_name, new_col_index))
                result_cols[key] = new_col_index
                headers.append(col_name)

        if not new_columns:
            return

        def _col_letter(col_num: int) -> str:
            result = ""
            while col_num > 0:
                col_num, remainder = divmod(col_num - 1, 26)
                result = chr(65 + remainder) + result
            return result

        max_target = max(idx for _, _, idx in new_columns)
        current_cols = worksheet.col_count
        if max_target > current_cols:
            needed_cols = max_target - current_cols + 5
            print(f"    ℹ️  시트 확장 중(FAQ 컬럼): {current_cols}개 → {current_cols + needed_cols}개 컬럼")
            worksheet.add_cols(needed_cols)

        updates = [
            {"range": f"{_col_letter(idx)}1", "values": [[col_name]]}
            for _, col_name, idx in new_columns
        ]
        worksheet.batch_update(updates, value_input_option='RAW')

        print(f"    🆕 FAQ 컬럼 지연 생성: {[c for _, c, _ in new_columns]}")


# ============================================================
# Google Sheets 배치 업데이트 (KeyError 방어 + 429 재시도)
# ============================================================
def update_result_to_sheet_batch(worksheet, row_index, result_cols, result_data,
                                 sheet_lock: threading.Lock, write_delay: float = 0.1):
    """
    여러 셀을 batch_update로 한 번에 기록.
    - result_cols에 키가 없으면 해당 필드 스킵 (KeyError 방지)
    - 429 시 백오프 재시도
    """
    def col_letter(col_num: int) -> str:
        result = ""
        while col_num > 0:
            col_num, remainder = divmod(col_num - 1, 26)
            result = chr(65 + remainder) + result
        return result

    field_mapping = [
        ('session_id',      lambda d: d.get('session_id') or ""),
        ('latency',         lambda d: d.get('latency') or ""),
        ('chat_request_id', lambda d: d.get('chat_request_id') or ""),
        ('answer_text',     lambda d: d.get('answer_text') or ""),
        ('progress_data',   lambda d: d.get('progress_data') or "[]"),
        ('keywords',        lambda d: d.get('keywords') or "[]"),
        ('product_count',   lambda d: d.get('product_count') or 0),
        #('response_type',    lambda d: d.get('response_type') or ""),
        ('faq_description', lambda d: d.get('faq_description') or ""),
        ('faq_summary',     lambda d: d.get('faq_summary') or ""),
        ('faq_detail_1',    lambda d: (d.get('faq_detail') or "")[0:45000]),
        ('faq_detail_2',    lambda d: (d.get('faq_detail') or "")[45000:90000]),
        ('faq_resource',    lambda d: d.get('faq_resource') or ""),
        ('faq_length_type', lambda d: d.get('faq_length_type') or ""),
        ('response_text_1', lambda d: (d.get('response_text') or "")[0:45000]),
        ('response_text_2', lambda d: (d.get('response_text') or "")[45000:90000]),
        ('response_text_3', lambda d: (d.get('response_text') or "")[90000:135000]),
        ('response_text_4', lambda d: (d.get('response_text') or "")[135000:180000]),
        ('response_text_5', lambda d: (d.get('response_text') or "")[180000:200001]),
        ('product_ids',     lambda d: d.get('product_ids') or ""),
        ('error',           lambda d: d.get('error') or ""),
    ]

    updates = []
    for key, getter in field_mapping:
        if key not in result_cols:
            continue
        updates.append({
            "range": f"{col_letter(result_cols[key])}{row_index}",
            "values": [[getter(result_data)]],
        })

    if not updates:
        print(f"    ⚠️  쓸 컬럼이 없음 (row {row_index})")
        return

    with sheet_lock:
        for attempt in range(3):
            try:
                worksheet.batch_update(updates, value_input_option='RAW')
                time.sleep(write_delay)
                return
            except gspread.exceptions.APIError as e:
                if '429' in str(e) and attempt < 2:
                    backoff = 30 * (attempt + 1)
                    print(f"    ⏳ Sheets 429 (row {row_index}) — {backoff}s 대기 후 재시도")
                    time.sleep(backoff)
                    continue
                print(f"    ⚠️  Google Sheets 업데이트 실패 (row {row_index}): {e}")
                return
            except Exception as e:
                print(f"    ⚠️  Google Sheets 업데이트 실패 (row {row_index}): {e}")
                return


