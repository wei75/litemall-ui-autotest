"""
日志管理模块：同时输出到控制台和 logs/auto_test.log
"""
import logging
import os
from datetime import datetime

from base.config_reader import LOG_DIR, ensure_dir


def get_logger(name="litemall"):
    """获取 logger，重复调用不会重复添加 handler"""
    ensure_dir(LOG_DIR)
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    # 日志格式：时间 级别 模块名 信息
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-7s | %(module)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 控制台输出
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 文件输出，按天分文件
    log_file = os.path.join(LOG_DIR, "auto_test_{}.log".format(datetime.now().strftime("%Y%m%d")))
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


logger = get_logger()
