
import argparse
from typing import Optional
from core.config_loader import YAML_CONFIG


def _format_profile_help(profile_keys: list[str]) -> str:
    from collections import defaultdict
    groups = defaultdict(list)

    for key in profile_keys:
        if "_" in key:
            group = key.split("_")[0] + "_" + key.split("_")[1].split("-")[0]
        else:
            group = key.split("-")[0]
        groups[group].append(key)

    lines = ["사용 가능한 프로파일:"]
    for group, keys in groups.items():
        lines.append(f"\n  [{group}]")
        for key in keys:
            lines.append(f"    {key}")

    return "\n".join(lines)


def build_parser(description: str = "검색 품질 테스트") -> argparse.ArgumentParser:
    profile_keys    = list(YAML_CONFIG["clients"].get("profiles", {}).keys())
    default_workers = YAML_CONFIG["defaults"]["max_workers"]

    parser = argparse.ArgumentParser(
        description=description,
        epilog=_format_profile_help(profile_keys),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # ── 공통 인자 ─────────────────────────────────────────────
    parser.add_argument( "--lang", choices=profile_keys,
                metavar="PROFILE", help="테스트 환경 (자세한 목록은 아래 참조)")
    parser.add_argument("--spreadsheet", help="Google Sheets 스프레드시트 이름")
    
    # ── 테스트 전용 (싱글턴/멀티턴 각각 사용) ─────────────────
    parser.add_argument("--worksheet",   help="워크시트(탭) 이름")
    parser.add_argument("--workers", type=int,
        default=None,  help=f"병렬 처리 워커 수 (기본: {default_workers})")

    # ── 리포트 전용 인자 ──────────────────────────────────────
    parser.add_argument(
        "--worksheet-single",
        dest="worksheet_single",
        help="싱글턴 워크시트(탭) 이름 (리포트 생성 시 사용)",
    )
    parser.add_argument(
        "--worksheet-multi",
        dest="worksheet_multi",
        help="멀티턴 워크시트(탭) 이름 (리포트 생성 시 사용)",
    )
#    parser.add_argument(
#        "--prompt",
#        default=None,
#        help="prompt/ 디렉토리 내 md 파일명 (예: eval_singleturn.md). 미지정 시 리포트 생성 스킵",
#    )
    parser.add_argument(
        "--env",
        default=None,
        help="리포트에 적용할 환경 이름. 미지정 시 --lang 값으로부터 추출 (예: MIZUNO_STG)",
    )
    parser.add_argument(
        "--label",
        default=None,
        help="리포트 라벨 (선택). 작성자/버전 구분·메모용. 예: OHA-v1.0.5. "
             "미지정 시 '라벨링 없음'으로 저장",
    )

    return parser


def prompt_if_missing(value: Optional[str], prompt_text: str,
                      choices: Optional[list] = None) -> str:
    if value:
        return value
    while True:
        if choices:
            print(_format_profile_help(choices))
            answer = input(f"\n{prompt_text}: ").strip()
        else:
            answer = input(f"{prompt_text}: ").strip()

        if not answer:
            print("   ⚠️  값을 입력하세요.")
            continue
        if choices and answer not in choices:
            print(f"   ⚠️  유효한 값: 위 목록에서 선택해주세요.")
            continue
        return answer