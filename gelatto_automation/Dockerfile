FROM selenium/standalone-chrome:latest

USER root

# Python 설치
RUN apt-get update && apt-get install -y python3 python3-pip

WORKDIR /app

# pip 패키지 설치
COPY requirements.txt .
RUN pip install -r requirements.txt

# 소스 코드 복사
COPY . .

# 실행할 파일 지정 (main.py 또는 test_flow.py)
CMD ["python", "test_flow.py"]