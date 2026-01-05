import yaml
import os 
from setup.logger import info, error 

class ConfigLoader:
    
    def __init__(self, path: str | None = None):
        # 기본: 이 파일(config_loader.py)이 있는 디렉토리에서 config.yaml 찾음
        base_dir = os.path.dirname(os.path.abspath(__file__))
        default_path = os.path.join(base_dir, "config.yaml")

        self.path = path if path else default_path
        # 디버깅용 정보
        info(f"[ConfigLoader] __file__ dir: {base_dir}")
        info(f"[ConfigLoader] trying to load config from: {self.path}")
        info(f"[ConfigLoader] current working dir: {os.getcwd()}")
        info(f"[ConfigLoader] exists? {os.path.exists(self.path)}")

        self.config = self.load_config()


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