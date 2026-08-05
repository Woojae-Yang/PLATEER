#!/usr/bin/env python3
"""
reports/*.html (공유용 단일 HTML)에 임베드된 데이터의 비표준 JSON 값
(Infinity / -Infinity / NaN)을 null 로 치환한다. 이미 생성된 HTML을 재생성 없이 고침.

원리:
  공유 HTML은 데이터를
    <script id="__report_data__" type="application/json"> ... </script>
  안에 넣고 브라우저가 JSON.parse 로 읽는다. 따라서 .json 과 똑같이 Infinity 가
  있으면 깨진다. 이 스크립트는 **그 데이터 블록만** 정확히 파싱→정화→재직렬화하고,
  인라인된 app.js / style 은 손대지 않는다.

사용법:
  python3 deploy/sanitize_report_html.py reports/
  python3 deploy/sanitize_report_html.py reports/foo_report.html
"""
import json
import math
import os
import re
import sys
import glob

_BLOCK = re.compile(
    r'(<script id="__report_data__" type="application/json">)(.*?)(</script>)',
    re.DOTALL,
)


def _json_safe(o):
    if isinstance(o, float):
        return o if math.isfinite(o) else None
    if isinstance(o, dict):
        return {k: _json_safe(v) for k, v in o.items()}
    if isinstance(o, list):
        return [_json_safe(v) for v in o]
    return o


def fix_html(path: str) -> bool:
    html = open(path, encoding="utf-8").read()
    touched = {"v": False}

    def repl(m):
        body = m.group(2)
        if "Infinity" not in body and "NaN" not in body:
            return m.group(0)
        obj = json.loads(body)                       # 파이썬은 Infinity/NaN 읽음
        new = json.dumps(_json_safe(obj), ensure_ascii=False)
        new = new.replace("</script>", "<\\/script>")  # 생성 시와 동일 이스케이프
        touched["v"] = True
        return m.group(1) + new + m.group(3)

    new_html = _BLOCK.sub(repl, html)
    if touched["v"]:
        open(path, "w", encoding="utf-8").write(new_html)
    return touched["v"]


def _iter(args):
    for a in args:
        if os.path.isdir(a):
            yield from sorted(glob.glob(os.path.join(a, "*.html")))
        else:
            yield a


def main() -> int:
    args = sys.argv[1:] or ["reports"]
    n = 0
    for f in _iter(args):
        try:
            if fix_html(f):
                print("fixed:", f)
                n += 1
        except Exception as e:
            print(f"skip({os.path.basename(f)}): {e}")
    print(f"done: {n} file(s) fixed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
