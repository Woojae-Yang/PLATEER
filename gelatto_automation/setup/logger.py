
import sys
import os
import logging

# Docker 컨테이너 안의 로그 디렉토리
LOG_DIR = "./logs"
###"/app/logs"

# 디렉토리가 없으면 생성
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = f"{LOG_DIR}/run.log"
STDERR_FILE = f"{LOG_DIR}/stderr.log"

# 기존 핸들러 제거 (중복 초기화 방지)
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

# 표준 오류 로그 리다이렉트
sys.stderr = open(STDERR_FILE, "w", encoding="utf-8")

logger = logging.getLogger("app_logger")

def info(msg): logger.info(msg)
def warn(msg): logger.warning(msg)
def error(msg): logger.error(msg)
def debug(msg): logger.debug(msg)