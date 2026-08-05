"""
latency_stats.py
================
쿼리셋(JSON) 안에 저장된 e2e 라운드트립 latency 를 집계하여 통계 지표를 낸다.

지표 정의
---------
메인(그리고 유일하게 추적하는) 지표는 **e2e 라운드트립 latency** 다.
    queries[i]["latency_ms"]   ← chat_api 가 측정한 요청~finish 벽시계 시간(ms)
    (= 시트의 latency_{timestamp} 초값 * 1000. scoring.round_trip_ms 가 주입)

이 값은 네트워크 + 서버의 모든 처리(라우팅·전처리·모든 툴/LLM 호출·스트리밍)를
포함한 "사용자 체감 지연" 이다.
phoenix_tool_latency_ms / phoenix_final_llm_latency_ms 는 구간 분해 참고용일 뿐
여기서는 집계/추적하지 않는다.

통계 지표 (비대칭 분포 대응 — IQR 을 메인으로)
    count, mean, std, min,
    p25, p50, p75, p90, p95, p99, max,
    iqr (= p75 - p25)

사용
----
모듈 함수:
    compute_stats(values)    -> dict | None
    stats_for_queryset(data) -> {"n_total", "n_with_latency", "stats": {...}|None}

스크립트:
    python -m core.latency_stats          # dashboard/data/latency.json 생성
    python core/latency_stats.py --out X  # 출력 경로 지정

⚠️ 주의: e2e latency 는 2026-06-23 이후 생성된 data.json 부터 들어간다.
   과거 회차는 generate_report 로 재생성해야 latency_ms 가 채워진다.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# ── 경로 기본값 ────────────────────────────────────────────
_THIS = Path(__file__).resolve()
PROJECT_ROOT = _THIS.parent.parent
DATA_DIR = PROJECT_ROOT / "dashboard" / "data"
INDEX_FILE = DATA_DIR / "index.json"
OUT_FILE = DATA_DIR / "latency.json"

# 계산할 백분위수 (퍼센트). p50=중앙값
PERCENTILES = [25, 50, 75, 90, 95, 99]


# ── 통계 계산 ──────────────────────────────────────────────
def _percentile(sorted_vals: List[float], pct: float) -> float:
    """선형보간 백분위수 (numpy 기본=type7 과 동일). sorted_vals 는 오름차순 정렬 가정."""
    n = len(sorted_vals)
    if n == 1:
        return sorted_vals[0]
    rank = (pct / 100.0) * (n - 1)
    lo = int(rank)
    frac = rank - lo
    if lo + 1 >= n:
        return sorted_vals[-1]
    return sorted_vals[lo] + frac * (sorted_vals[lo + 1] - sorted_vals[lo])


def compute_stats(values: List[float]) -> Optional[Dict[str, float]]:
    """
    숫자 리스트 → 통계 dict. None/빈 리스트면 None 반환.
    반환 키: count, mean, std, min, p25, p50, p75, p90, p95, p99, max, iqr
    std 는 표본표준편차(ddof=1); n<2 면 0.0.
    """
    vals = [float(v) for v in values if v is not None]
    if not vals:
        return None
    vals.sort()
    n = len(vals)
    mean = sum(vals) / n
    if n >= 2:
        var = sum((v - mean) ** 2 for v in vals) / (n - 1)
        std = var ** 0.5
    else:
        std = 0.0

    out: Dict[str, float] = {
        "count": n,
        "mean": round(mean, 1),
        "std": round(std, 1),
        "min": round(vals[0], 1),
        "max": round(vals[-1], 1),
    }
    pmap: Dict[int, float] = {}
    for p in PERCENTILES:
        val = _percentile(vals, p)
        pmap[p] = val
        out[f"p{p}"] = round(val, 1)
    out["iqr"] = round(pmap[75] - pmap[25], 1)
    return out


def stats_for_queryset(data: dict) -> Dict[str, object]:
    """
    쿼리셋 dict({meta,kpi,queries}) → e2e latency 통계.
    반환: {"n_total": int, "n_with_latency": int, "stats": {...}|None}
    """
    queries = data.get("queries", []) or []
    vals: List[float] = []
    for q in queries:
        v = q.get("latency_ms")
        if v is not None and v != "":
            try:
                vals.append(float(v))
            except (TypeError, ValueError):
                pass
    return {
        "n_total": len(queries),
        "n_with_latency": len(vals),
        "stats": compute_stats(vals),
    }


# ── 전체 집계(대시보드용 JSON) ─────────────────────────────
def _now_kst_str() -> str:
    return datetime.now(timezone(timedelta(hours=9))).strftime("%Y.%m.%d %H:%M")


def build_latency_index(data_dir: Path = DATA_DIR,
                        index_file: Path = INDEX_FILE) -> dict:
    """
    index.json 의 모든 회차를 읽어 환경별 시계열 + 전체 스냅샷 집계 생성.

    출력 스키마 (e2e 단일 지표):
    {
      "generated_at": "...",
      "metric": "e2e_ms",
      "unit": "ms",
      "stat_keys": ["count","mean","std","min","p25",...,"iqr"],
      "environments": {
        "<env>": {
          "runs": [
            { "file","date","label","generated_at",
              "n_total","n_with_latency",
              "stats": { count, mean, std, min, p25..p99, max, iqr } | null },
            ...                      # generated_at 오름차순(시계열)
          ]
        }, ...
      },
      "overview": [                  # 환경별 '최신 회차' 스냅샷 (전체 한눈에 비교용)
        { "env","date","label","generated_at","n_with_latency","stats": {...}|null }, ...
      ]
    }
    """
    index = json.loads(Path(index_file).read_text(encoding="utf-8"))

    environments: Dict[str, Dict[str, list]] = {}
    for entry in index:
        env = entry.get("env", "unknown")
        fpath = data_dir / entry["file"]
        if not fpath.exists():
            continue
        try:
            data = json.loads(fpath.read_text(encoding="utf-8"))
        except Exception:
            continue
        s = stats_for_queryset(data)
        run = {
            "file": entry["file"],
            "date": entry.get("date"),
            "label": entry.get("label") or None,
            "generated_at": entry.get("generated_at"),
            "n_total": s["n_total"],
            "n_with_latency": s["n_with_latency"],
            "stats": s["stats"],
        }
        environments.setdefault(env, {"runs": []})["runs"].append(run)

    # 시계열: generated_at 오름차순 정렬
    overview = []
    for env, payload in environments.items():
        payload["runs"].sort(key=lambda r: str(r.get("generated_at") or ""))
        latest = payload["runs"][-1] if payload["runs"] else None
        if latest:
            overview.append({
                "env": env,
                "date": latest["date"],
                "label": latest["label"],
                "generated_at": latest["generated_at"],
                "n_with_latency": latest["n_with_latency"],
                "stats": latest["stats"],
            })
    overview.sort(key=lambda o: str(o.get("generated_at") or ""), reverse=True)

    stat_keys = ["count", "mean", "std", "min"] + \
                [f"p{p}" for p in PERCENTILES] + ["max", "iqr"]
    return {
        "generated_at": _now_kst_str(),
        "metric": "e2e_ms",
        "unit": "ms",
        "stat_keys": stat_keys,
        "environments": environments,
        "overview": overview,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="쿼리셋 e2e latency 통계 집계 JSON 생성")
    ap.add_argument("--data-dir", default=str(DATA_DIR), help="쿼리셋 JSON 디렉터리")
    ap.add_argument("--index", default=str(INDEX_FILE), help="index.json 경로")
    ap.add_argument("--out", default=str(OUT_FILE), help="출력 JSON 경로")
    args = ap.parse_args()

    result = build_latency_index(Path(args.data_dir), Path(args.index))
    out_path = Path(args.out)
    out_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    n_env = len(result["environments"])
    n_runs = sum(len(p["runs"]) for p in result["environments"].values())
    n_with = sum(1 for p in result["environments"].values()
                 for r in p["runs"] if r["stats"])
    print(f"✓ {out_path}")
    print(f"  환경 {n_env}개 / 회차 {n_runs}개 (e2e 측정 있는 회차 {n_with}개) "
          f"| generated_at {result['generated_at']}")
    if n_with == 0:
        print("  ⚠️ e2e latency_ms 가 있는 회차가 없습니다. "
              "generate_report 로 data.json 을 재생성하세요(2026-06-23 이후 파이프라인 필요).")


if __name__ == "__main__":
    main()
