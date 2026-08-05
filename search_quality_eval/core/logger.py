
from pathlib import Path
from datetime import datetime
import logging
from core.config_loader import now_kst
from core.config_loader import now_kst, PROJECT_ROOT  # 기존 PROJECT_ROOT 재사용


"""실행별 로그 디렉토리 관리 및 response_text 저장."""
# logs/YYYYMMDD_HHMMSS/ 구조로 실행마다 폴더 분리
RUN_ID = now_kst().strftime("%Y%m%d_%H%M%S")
RUN_LOG_DIR = PROJECT_ROOT / "logs" / RUN_ID
RUN_LOG_DIR.mkdir(parents=True, exist_ok=True)

# 진행 로그 (stdout + 파일)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(threadName)s] %(message)s",
    handlers=[
        #logging.FileHandler(RUN_LOG_DIR / "_run.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


def save_response_log(
    identifier: str,
    query: str,
    response_text: str,
    session_id: str = "",
    turn: int = None,
) -> None:
    """
    identifier: singleturn이면 'row_0001', multiturn이면 'scn_001'
    turn: multiturn일 때만 (0-indexed)
    """
    suffix = f"_turn{turn}" if turn is not None else ""
    filepath = RUN_LOG_DIR / f"{identifier}{suffix}.txt"

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"=== session_id: {session_id} ===\n")
        f.write(f"=== query: {query} ===\n")
        f.write(f"=== timestamp: {datetime.now().isoformat()} ===\n\n")
        f.write(response_text)