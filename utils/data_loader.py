"""
数据层工具：统一加载 data 目录下的 yaml 测试数据
"""
import os

import yaml

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")


def load_yaml(file_name):
    """读取 data 目录下的 yaml 文件，文件名可以不带后缀"""
    if not file_name.endswith(".yaml"):
        file_name += ".yaml"
    file_path = os.path.join(DATA_DIR, file_name)
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
