#!/usr/bin/env python3
"""
data 디렉터리의 JSON에서 비표준 값(Infinity / -Infinity / NaN)을 null 로 치환.

배경:
  파이썬 json.dump 는 기본적으로 Infinity/NaN 을 그대로 쓰지만, 브라우저
  JSON.parse() 는 이를 거부한다. 그래서 그런 값이 들어간 회차 파일은
  대시보드에서 "리포트를 불러오지 못했습니다 ... is not valid JSON" 로 깨진다.
  이 스크립트는 기존에 이미 생성된 파일들을 일괄로 고친다.
  (앞으로 생성될 리포트는 report_generator.py 의 _json_safe 가 막아준다.)

사용법:
  python3 deploy/sanitize_data_json.py /var/www/qa-reports/data
  # 인자 생략 시 /var/www/qa-reports/data 를 대상으로 함
"""
import json
import math
import os
import sys
import glob


def _json_safe(o):
    if isinstance(o, float):
        return o if math.isfinite(o) else None
    if isinstance(o, dict):
        return {k: _json_safe(v) for k, v in o.items()}
    if isinstance(o, list):
        return [_json_safe(v) for v in o]
    return o


def main() -> int:
    target = sys.argv[1] if len(sys.argv) > 1 else "/var/www/qa-reports/dashboard/data"
    if not os.path.isdir(target):
        print(f"ERROR: 디렉터리 없음: {target}")
        return 1

    fixed = 0
    for path in sorted(glob.glob(os.path.join(target, "*.json"))):
        raw = open(path, encoding="utf-8").read()
        if "Infinity" not in raw and "NaN" not in raw:
            continue
        try:
            data = json.loads(raw)            # 파이썬은 Infinity/NaN 을 읽음
        except json.JSONDecodeError as e:
            print(f"skip(파싱 불가): {os.path.basename(path)} — {e}")
            continue
        json.dump(_json_safe(data), open(path, "w", encoding="utf-8"),
                  ensure_ascii=False, indent=2)
        print(f"fixed: {os.path.basename(path)}")
        fixed += 1

    print(f"done: {fixed} file(s) fixed in {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
