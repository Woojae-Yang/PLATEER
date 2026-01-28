import yaml
import os 
from setup.logger import info, error 
from dotenv import load_dotenv

class ConfigLoader:
    
    def __init__(self, path: str | None = None, env_path: str | None = None):
        # 기본: 이 파일(config_loader.py)이 있는 디렉토리에서 config.yaml 찾음
        base_dir = os.path.dirname(os.path.abspath(__file__))
        default_path = os.path.join(base_dir, "config.yaml")

        self.path = path if path else default_path

        # .env 로드
        self._load_env(base_dir, env_path)

        # 디버깅용 정보
        info(f"[ConfigLoader] __file__ dir: {base_dir}")
        info(f"[ConfigLoader] trying to load config from: {self.path}")
        info(f"[ConfigLoader] current working dir: {os.getcwd()}")
        info(f"[ConfigLoader] exists? {os.path.exists(self.path)}")

        self.config = self.load_config()

        # env 파일 불러오기
    def _load_env(self, base_dir: str, env_path: str | None):
        """
        우선순위:
        1) 인자로 받은 env_path
        2) config_loader.py가 있는 디렉토리의 .env
        """
        if load_dotenv is None:
            info("[ConfigLoader] python-dotenv not installed. Skip loading .env")
            return  

        candidate = env_path if env_path else os.path.join(base_dir, ".env")
        if os.path.exists(candidate):
            load_dotenv(candidate, override=False)
            info(f"[ConfigLoader] loaded .env from: {candidate}")
        else:
            info(f"[ConfigLoader] .env not found: {candidate}")


    def load_config(self):
        with open(self.path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)


    @property
    def username(self):
        return self.config["credentials"]["username"]

    @property
    def password(self):
        return self.config["credentials"]["password"]
    
    @property
    def admin_url(self):
        return self.config["urls"]["admin_page"]

    @property
    def shop_url(self):
        return self.config["urls"]["shop_page"]
    
    @property
    def gelatto_url(self):
        return self.config["urls"]["gelatto_page"]
    
    @property
    def get_shop(self):
        return self.config["urls"]["shop_no"]
    
    @property
    def get_topic(self):
        return self.config["inputs"]["topic"]
    
    @property
    def get_input_word(self):
        return self.config["inputs"]["word"]
    
    @property
    def get_input_description(self):
        return self.config["inputs"]["description"]
    

    # -------------------------
    # TestRail settings
    # -------------------------
    @property
    def testrail_enabled(self) -> bool:
        return bool(self.config.get("testrail", {}).get("enabled", False))

    @property
    def testrail_base_url(self) -> str:
        return self.config["testrail"]["base_url"].rstrip("/")

    @property
    def testrail_user(self) -> str:
        return self.config["testrail"]["user"]

    @property
    def testrail_api_key_env(self) -> str:
        # yaml에 api_key_env: TESTRAIL_API_KEY 형태로 들어가므로 문자열로 반환
        return str(self.config["testrail"]["api_key_env"])

    @property
    def testrail_api_key(self) -> str:
        """
        실제 API Key 값은 환경변수에서 읽는다.
        예: api_key_env: TESTRAIL_API_KEY  ->  os.environ["TESTRAIL_API_KEY"]
        """
        env_name = self.testrail_api_key_env
        api_key = os.getenv(env_name, "").strip()

        if self.testrail_enabled and not api_key:
            error(f"[ConfigLoader] TestRail enabled but env var is empty: {env_name}")
            raise RuntimeError(f"TestRail API key env var is empty: {env_name}")

        return api_key

    @property
    def testrail_run_name_template(self) -> str:
        return self.config.get("testrail", {}).get("run", {}).get(
            "name_template",
            "pytest run {date}"
        )
    @property
    def testrail_run_id(self) -> int | None:
        run_id = self.config.get("testrail", {}).get("run", {}).get("id")
        if run_id in (None, "", 0):
            return None
        return int(run_id)