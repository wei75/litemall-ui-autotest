"""
驱动工厂：负责创建和销毁浏览器实例
使用 Selenium Manager 自动匹配驱动版本，换机器不用手动放 chromedriver
"""
from selenium import webdriver

from base.config_reader import BROWSER_NAME, HEADLESS, WINDOW_SIZE
from base.logger import logger


def create_driver():
    """创建一个 Chrome 浏览器实例"""
    logger.info("开始创建浏览器实例，headless=%s", HEADLESS)

    options = webdriver.ChromeOptions()
    # 去掉“Chrome 正受到自动测试软件控制”的提示条
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--window-size={}".format(WINDOW_SIZE))
    options.add_argument("--disable-notifications")

    # CI / 无桌面环境必须开启无头模式
    if HEADLESS:
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(options=options)
    # 全局不使用隐式等待，统一由 BasePage 做显式等待，避免等待时间叠加
    driver.implicitly_wait(0)
    driver.maximize_window()

    logger.info("浏览器实例创建成功")
    return driver


def quit_driver(driver):
    """关闭浏览器"""
    if driver:
        try:
            driver.quit()
            logger.info("浏览器实例已关闭")
        except Exception as e:
            logger.warning("关闭浏览器时出现异常：%s", e)
