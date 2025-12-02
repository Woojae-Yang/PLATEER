# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import zipfile
import json
import tiktoken
from datetime import datetime
from collections import defaultdict

# 최신 OpenAI 모델 공통 인코딩
enc = tiktoken.get_encoding("o200k_base")


def load_conversations_from_zip(zip_path):
    with zipfile.ZipFile(zip_path, "r") as z:
        target = [f for f in z.namelist() if "conversations.json" in f][0]
        with z.open(target) as jf:
            data = json.load(jf)

    return data  # 최신 구조는 list 형태


def count_tokens(text):
    return len(enc.encode(text or ""))


def extract_messages(conv):
    ## mapping 트리 구조에서 실제 메시지들을 순서 없이 모두 추출
    messages = []
    mapping = conv.get("mapping", {})

    for node_id, node in mapping.items():
        msg = node.get("message")
        if msg is None:
            continue

        # content text
        content_obj = msg.get("content", {})
        parts = content_obj.get("parts", [])
        text_list = []
        
        for p in parts:
            # 문자열이면 그대로
            if isinstance(p, str):
                text_list.append(p)
            # dict이면 text 또는 content 또는 message 등의 key에서 문자열을 추출
            elif isinstance(p, dict):
                # 가능한 모든 키 후보에서 text를 추출
                if "text" in p and isinstance(p["text"], str):
                    text_list.append(p["text"])
                elif "content" in p and isinstance(p["content"], str):
                    text_list.append(p["content"])
                    # dict 구조이지만 텍스트가 없다면 그냥 str로 변환
                else:
                    text_list.append(str(p))
            else:
                # 완전 예외적인 타입이면 일단 문자열 변환
                text_list.append(str(p))
            
        # 최종 메시지 텍스트 생성
        text = "\n".join(text_list)

        messages.append({
            "id": msg.get("id"),
            "role": msg.get("author", {}).get("role"),
            "text": text,
            "tokens": count_tokens(text),
            "create_time": msg.get("create_time")
        })

    return messages


# ===============================
# 전월 계산 함수
# ===============================
def get_previous_month(year, month):
    if month == 1:
        return year - 1, 12
    return year, month - 1


# ===============================
# 월별 사용량 계산
# ===============================
def analyze_month(conversations, year, month):
    """
    지정된 연/월에 해당하는 메시지 필터 후 사용량 계산
    """
    total_tokens = 0
    total_messages = 0
    total_user_messages = 0
    total_assistant_messages = 0

    # 전월 대화 수 계산용
    relevant_conversation_count = 0

    for conv in conversations:
        msgs = extract_messages(conv)

        # 이 대화에 '전월 메시지'가 하나라도 있으면 카운트
        conv_has_message_in_month = False

        for msg in msgs:
            ts = msg["create_time"]

            # create_time이 null인 메시지는 건너뜀
            if ts is None:
                continue

            dt = datetime.fromtimestamp(ts)
            if dt.year == year and dt.month == month:
                # 이 메시지는 원하는 월에 포함됨
                total_tokens += msg["tokens"]
                total_messages += 1
                if msg["role"] == "user":
                    total_user_messages += 1
                elif msg["role"] == "assistant":
                    total_assistant_messages += 1

                conv_has_message_in_month = True

        if conv_has_message_in_month:
            relevant_conversation_count += 1

    return {
        "year": year,
        "month": month,
        "conversations": relevant_conversation_count,
        "messages": total_messages,
        "user_messages": total_user_messages,
        "assistant_messages": total_assistant_messages,
        "tokens": total_tokens
    }



#%%
# 데모 실행
if __name__ == "__main__":
    """
    [zip_path]
     ZIP 파일 경로 : 각자의 로컬환경에 맞게 알아서 수정 (절대경로 가능)
     py 코드와 같은 디렉토리에 존재하는 경우에는 절대경로 설정 없이 파일 명만 입력해도 됨
    """
    zip_path = "ywj.zip"   

    # ZIP에서 전체 대화 불러오기
    conversations = load_conversations_from_zip(zip_path)

    # 오늘 기준으로 전월 계산
    today = datetime.today()
    prev_year, prev_month = get_previous_month(today.year, today.month)

    print(f"📌 분석 대상: {prev_year}년 {prev_month}월")

    stats = analyze_month(conversations, prev_year, prev_month)

    print("\n===== 월간 사용량 =====")
    #print(f"대화 수: {stats['conversations']}")
    #print(f"메시지 수: {stats['messages']}")
    print(f" - User 메시지: {stats['user_messages']}")
    print(f" - Assistant 메시지: {stats['assistant_messages']}")
    print(f"총 토큰: {stats['tokens']}")
    
    
    
