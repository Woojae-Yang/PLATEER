from setup.config_loader import ConfigLoader
from setup.testrail_client import TestRailClient

def main():
    print("[temp] start")

    try:
        cfg = ConfigLoader()
        print("[temp] ConfigLoader OK")

        # TestRail 관련 값이 실제로 로딩됐는지 확인(키 값 자체는 출력하지 않음)
        print("[temp] testrail_enabled =", getattr(cfg, "testrail_enabled", None))
        print("[temp] base_url =", getattr(cfg, "testrail_base_url", None))
        print("[temp] user =", getattr(cfg, "testrail_user", None))
        print("[temp] api_key loaded =", bool(getattr(cfg, "testrail_api_key", "")))

        tr = TestRailClient(cfg)
        print("[temp] TestRailClient OK")

        cases = tr.get_cases(project_id=5, suite_id=16, limit=1)
        print("[temp] get_cases returned type:", type(cases))
        print("[temp] cases:", cases)

    except Exception as e:
        print("[temp] ERROR:", repr(e))
        raise

    finally:
        print("[temp] end")

if __name__ == "__main__":
    main()