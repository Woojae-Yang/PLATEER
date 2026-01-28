import os
import requests
from datetime import datetime
from setup.config_loader import ConfigLoader
from setup.logger import info, error, debug

class TestRailClient:
    """
    ConfigLoader가 읽어온 TestRail 설정으로 동작하는 최소 클라이언트
    - base_url/user/api_key: config.yaml + .env
    """

    def __init__(self, cfg: ConfigLoader):
        if not cfg.testrail_enabled:
            raise RuntimeError("TestRail is disabled in config.yaml (testrail.enabled=false)")

        self.base_url = cfg.testrail_base_url.rstrip("/")
        self.user = cfg.testrail_user
        self.api_key = cfg.testrail_api_key  # env에서 읽힘
        self.run_name_template = cfg.testrail_run_name_template

        self.session = requests.Session()
        self.session.auth = (self.user, self.api_key)
        self.session.headers.update({"Content-Type": "application/json"})

    def _url(self, path: str) -> str:
        # path 예: "get_case/123", "add_run/5"
        return f"{self.base_url}/index.php?/api/v2/{path}"

    def get(self, path: str):
        url = self._url(path)
        r = self.session.get(url)
        self._raise_if_error(r, "GET", url)
        return r.json()

    def post(self, path: str, payload: dict):
        url = self._url(path)
        r = self.session.post(url, json=payload)
        self._raise_if_error(r, "POST", url)
        return r.json()

    def _raise_if_error(self, resp: requests.Response, method: str, url: str):
        if resp.ok:
            return
        # TestRail은 에러 바디에 메시지가 포함되는 경우가 많음
        msg = ""
        try:
            msg = resp.json()
        except Exception:
            msg = resp.text[:500]

        error(f"[TestRailClient] {method} {url} -> {resp.status_code} {msg}")
        resp.raise_for_status()

    # -------------------------
    # Minimal APIs for integration
    # -------------------------
    def get_case(self, case_id: int):
        return self.get(f"get_case/{case_id}")

    def get_cases(self, project_id: int, suite_id: int | None = None, limit: int = 5):
        # get_cases/{project_id}&suite_id=...&limit=...
        qs = f"limit={limit}"
        if suite_id is not None:
            qs = f"suite_id={suite_id}&{qs}"
        return self.get(f"get_cases/{project_id}&{qs}")

    def add_run(self, project_id: int, suite_id: int, case_ids: list[int], name: str):
        payload = {
            "suite_id": suite_id,
            "name": name,
            "include_all": False,
            "case_ids": case_ids,
        }
        return self.post(f"add_run/{project_id}", payload)

    def add_results_for_cases(self, run_id: int, results: list[dict]):
        """
        results item 예:
          {"case_id": 1234, "status_id": 1, "comment": "..." }
        """
        payload = {"results": results}
        return self.post(f"add_results_for_cases/{run_id}", payload)
    
    def get_tests(self, run_id: int):
        return self.get(f"get_tests/{run_id}")

