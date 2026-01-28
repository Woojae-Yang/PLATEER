FROM python:3.13-slim

USER root

# Python 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# pip 패키지 설치
COPY requirements.txt .
RUN python3 -m pip install --upgrade pip \
 && pip install -r requirements.txt

# 소스 코드 복사
COPY . .

# 실행할 파일 지정 (main.py 또는 test_flow.py)
CMD ["pytest", "-q"]