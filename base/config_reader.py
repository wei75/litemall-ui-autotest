"""
配置读取模块：统一读取 config/config.yaml
所有环境地址、账号、超时时间都从这里取，不在代码里硬编码
"""
import os
import yaml

# 项目根目录（base 目录的上一级）
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_FILE = os.path.join(BASE_DIR, "config", "config.yaml")


class ConfigReader:
    """读取 yaml 配置，支持 a.b.c 形式的键"""

    def __init__(self, file_path=CONFIG_FILE):
        with open(file_path, "r", encoding="utf-8") as f:
            self.data = yaml.safe_load(f)

    def get(self, key, default=None):
        """按 env.base_url 这种路径取值，取不到返回默认值"""
        value = self.data
        for part in key.split("."):
            if not isinstance(value, dict) or part not in value:
                return default
            value = value[part]
        return value


CONFIG = ConfigReader()

# 常用配置项，其他地方直接 import 使用
BASE_URL = os.getenv("BASE_URL", CONFIG.get("env.base_url"))
BROWSER_NAME = CONFIG.get("browser.name", "chrome")
HEADLESS = os.getenv("HEADLESS", str(CONFIG.get("browser.headless", "false"))).lower() == "true"
WINDOW_SIZE = CONFIG.get("browser.window_size", "1440,900")
TIMEOUT = CONFIG.get("timeout.default", 20)
POLL_FREQUENCY = CONFIG.get("timeout.poll", 0.5)

USERNAME = CONFIG.get("account.username")
PASSWORD = CONFIG.get("account.password")
WRONG_PASSWORD = CONFIG.get("account.wrong_password")

LOG_DIR = os.path.join(BASE_DIR, CONFIG.get("paths.logs", "logs"))
SCREENSHOT_DIR = os.path.join(BASE_DIR, CONFIG.get("paths.screenshots", "screenshots"))
REPORT_DIR = os.path.join(BASE_DIR, CONFIG.get("paths.reports", "reports"))


def ensure_dir(path):
    """目录不存在就创建"""
    if not os.path.exists(path):
        os.makedirs(path)
    return path
