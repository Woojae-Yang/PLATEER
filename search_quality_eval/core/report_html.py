"""
core/report_html.py — 외부 공유용 단일 HTML 리포트 빌더.

gelatto_report/ 의 정적 자산(index.html + style.css + App.js)과 data.json 을
**self-contained HTML 한 파일**로 묶는다. 서버/네트워크 없이 더블클릭으로 열린다.

설계 포인트
  · App.js 는 한 글자도 수정하지 않는다.
    대신 App.js 보다 먼저 실행되는 작은 shim 을 넣어 `fetch('data.json')` 호출을
    가로채 인라인 데이터를 돌려준다 (file:// 에서 fetch 가 막히는 문제 회피).
  · style.css 와 App.js 는 <style> / <script> 로 인라인.
  · data.json 은 <script id="__report_data__" type="application/json"> 로 임베드.

평가 로직과 무관한 '패키징'이므로, data.json 이 만들어진 직후 호출하면 된다.
"""
from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Union


def _json_safe(o):
    """비표준 JSON float(Infinity/-Infinity/NaN)을 None(null)으로 치환."""
    if isinstance(o, float):
        return o if math.isfinite(o) else None
    if isinstance(o, dict):
        return {k: _json_safe(v) for k, v in o.items()}
    if isinstance(o, list):
        return [_json_safe(v) for v in o]
    return o


def _inline_data_shim(data_json_text: str) -> str:
    """App.js 의 fetch('data.json') 을 가로채는 shim + 임베드 데이터."""
    return (
        '<script id="__report_data__" type="application/json">'
        + data_json_text
        + "</script>\n"
        "<script>\n"
        "(function () {\n"
        "  var el = document.getElementById('__report_data__');\n"
        "  var DATA = JSON.parse(el.textContent);\n"
        "  window.__REPORT_DATA__ = DATA;\n"
        "  var orig = window.fetch ? window.fetch.bind(window) : null;\n"
        "  window.fetch = function (url, opts) {\n"
        "    var u = (typeof url === 'string') ? url : (url && url.url) || '';\n"
        "    if (u.indexOf('data.json') !== -1) {\n"
        "      return Promise.resolve({\n"
        "        ok: true, status: 200,\n"
        "        json: function () { return Promise.resolve(DATA); },\n"
        "        text: function () { return Promise.resolve(JSON.stringify(DATA)); }\n"
        "      });\n"
        "    }\n"
        "    return orig ? orig(url, opts) : Promise.reject(new Error('fetch unavailable'));\n"
        "  };\n"
        "})();\n"
        "</script>\n"
    )


def build_shareable_html(
    data: Union[dict, str, Path],
    assets_dir: Union[str, Path],
) -> str:
    """
    data       : data.json dict, JSON 문자열, 또는 data.json 파일 경로
    assets_dir : index.html / style.css / App.js 가 있는 폴더 (예: gelatto_report)
    Returns    : 단일 HTML 문자열
    """
    assets = Path(assets_dir)
    index_html = (assets / "index.html").read_text(encoding="utf-8")
    css = (assets / "style.css").read_text(encoding="utf-8")

    # 앱 스크립트 파일명은 app.js / App.js 둘 다 허용
    app_path = next(
        (assets / n for n in ("app.js", "App.js") if (assets / n).exists()),
        None,
    )
    if app_path is None:
        raise FileNotFoundError(f"app.js(또는 App.js)를 찾을 수 없습니다: {assets}")
    app_js = app_path.read_text(encoding="utf-8")

    # data → JSON 텍스트
    if isinstance(data, (str, Path)) and Path(str(data)).exists():
        data_text = Path(str(data)).read_text(encoding="utf-8")
        json.loads(data_text)  # 유효성 확인
    elif isinstance(data, str):
        json.loads(data)
        data_text = data
    else:
        data_text = json.dumps(data, ensure_ascii=False)

    # 비표준 JSON 값(Infinity/-Infinity/NaN) 제거 — 브라우저 JSON.parse 호환
    # (파이썬 json.loads 는 Infinity 를 읽으므로, 다시 파싱→정화→직렬화한다.)
    data_text = json.dumps(_json_safe(json.loads(data_text)), ensure_ascii=False)

    # </script> 가 데이터 안에 있으면 조기 종료되므로 이스케이프
    data_text = data_text.replace("</script>", "<\\/script>")

    html = index_html

    # NOTE: re.sub 는 '치환 문자열'의 백슬래시(\n, \t 등)를 이스케이프로 해석한다.
    # 임베드 JSON/App.js/CSS 안의 \n 이 실제 개행으로 망가지므로, 반드시
    # '함수형 치환'(lambda)을 써서 반환값을 그대로 삽입한다.
    style_block = f"<style>\n{css}\n</style>"
    inline_app = _inline_data_shim(data_text) + f"<script>\n{app_js}\n</script>"

    # 1) stylesheet 링크 → 인라인 <style>
    html, n_css = re.subn(
        r'<link[^>]*rel=["\']stylesheet["\'][^>]*>',
        lambda _m: style_block,
        html, count=1,
    )
    if n_css == 0:  # 링크가 없으면 </head> 앞에 삽입
        html = html.replace("</head>", style_block + "\n</head>", 1)

    # 2) <script src="app.js"/"App.js"> → 데이터 shim + 인라인 앱 스크립트
    html, n_js = re.subn(
        r'<script[^>]*src=["\'][^"\']*[Aa]pp\.js[^"\']*["\'][^>]*>\s*</script>',
        lambda _m: inline_app,
        html, count=1,
    )
    if n_js == 0:  # src 스크립트가 없으면 </body> 앞에 삽입
        html = html.replace("</body>", inline_app + "\n</body>", 1)

    return html


def write_shareable_html(
    data: Union[dict, str, Path],
    out_path: Union[str, Path],
    assets_dir: Union[str, Path],
) -> Path:
    """단일 HTML 을 out_path 에 저장하고 경로를 반환."""
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build_shareable_html(data, assets_dir), encoding="utf-8")
    return out


# ── CLI: python -m core.report_html <data.json> <out.html> [assets_dir] ──
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("usage: python -m core.report_html <data.json> <out.html> [assets_dir]")
        raise SystemExit(1)

    data_path = sys.argv[1]
    out_path = sys.argv[2]
    assets = sys.argv[3] if len(sys.argv) > 3 else str(Path(__file__).resolve().parent.parent / "dashboard")
    p = write_shareable_html(data_path, out_path, assets)
    size_kb = p.stat().st_size / 1024
    print(f"✅ 단일 HTML 저장: {p}  ({size_kb:.0f} KB)")
