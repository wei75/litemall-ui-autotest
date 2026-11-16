"""
页面基类 BasePage
封装所有页面通用的操作：打开页面、元素等待、点击、输入、取文本、截图等
具体的业务页面类都继承它，只写自己的元素定位和业务动作
"""
import os
import time
from datetime import datetime

import allure
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from base.config_reader import BASE_URL, POLL_FREQUENCY, SCREENSHOT_DIR, TIMEOUT, ensure_dir
from base.exceptions import ElementNotClickableError, ElementNotFoundError
from base.logger import logger


class BasePage:
    """页面对象基类"""

    def __init__(self, driver):
        self.driver = driver
        self.timeout = TIMEOUT
        self.poll = POLL_FREQUENCY
        self.logger = logger

    # ---------------- 页面跳转 ----------------

    def open(self, hash_path=""):
        """
        打开站内页面
        本项目前端是 Vue hash 路由，页面地址形如 http://ip:6255/#/login
        """
        url = "{}/#{}".format(BASE_URL, hash_path)
        with allure.step("打开页面：{}".format(url)):
            self.logger.info("打开页面：%s", url)
            self.driver.get(url)

    def open_url(self, url):
        with allure.step("打开地址：{}".format(url)):
            self.logger.info("打开地址：%s", url)
            self.driver.get(url)

    def current_url(self):
        return self.driver.current_url

    def wait_url_contains(self, text, timeout=None, desc="地址"):
        """等待地址栏包含指定内容，用于判断跳转是否成功"""
        timeout = timeout or self.timeout
        try:
            WebDriverWait(self.driver, timeout, self.poll).until(
                EC.url_contains(text)
            )
            self.logger.info("%s校验通过，当前地址：%s", desc, self.current_url())
            return True
        except TimeoutException:
            raise AssertionError(
                "等待{}跳转超时，期望包含【{}】，实际地址：{}".format(desc, text, self.current_url())
            )

    # ---------------- 元素查找 ----------------

    def wait_present(self, locator, timeout=None, desc="元素"):
        """等待元素出现在 DOM 中"""
        timeout = timeout or self.timeout
        try:
            return WebDriverWait(self.driver, timeout, self.poll).until(
                EC.presence_of_element_located(locator)
            )
        except TimeoutException:
            raise ElementNotFoundError(
                "{}定位超时，定位方式：{}，当前地址：{}".format(desc, locator, self.current_url())
            )

    def wait_visible(self, locator, timeout=None, desc="元素"):
        """等待元素可见"""
        timeout = timeout or self.timeout
        try:
            return WebDriverWait(self.driver, timeout, self.poll).until(
                EC.visibility_of_element_located(locator)
            )
        except TimeoutException:
            raise ElementNotFoundError(
                "{}不可见，定位方式：{}，当前地址：{}".format(desc, locator, self.current_url())
            )

    def wait_clickable(self, locator, timeout=None, desc="元素"):
        """等待元素可点击"""
        timeout = timeout or self.timeout
        try:
            return WebDriverWait(self.driver, timeout, self.poll).until(
                EC.element_to_be_clickable(locator)
            )
        except TimeoutException:
            raise ElementNotFoundError(
                "{}不可点击，定位方式：{}，当前地址：{}".format(desc, locator, self.current_url())
            )

    def wait_all_present(self, locator, timeout=None, desc="元素列表"):
        """等待一组元素出现，返回列表"""
        timeout = timeout or self.timeout
        try:
            WebDriverWait(self.driver, timeout, self.poll).until(
                EC.presence_of_all_elements_located(locator)
            )
        except TimeoutException:
            raise ElementNotFoundError(
                "{}为空，定位方式：{}，当前地址：{}".format(desc, locator, self.current_url())
            )
        return self.driver.find_elements(*locator)

    def find(self, locator, desc="元素"):
        """查找单个元素，找不到直接抛业务异常"""
        return self.wait_present(locator, desc=desc)

    def find_all(self, locator, desc="元素列表"):
        return self.wait_all_present(locator, desc=desc)

    def wait_until(self, condition, timeout=None, desc="页面状态"):
        """
        等待自定义条件成立
        condition 是一个无参函数，返回 True 表示条件满足
        """
        timeout = timeout or self.timeout
        try:
            WebDriverWait(self.driver, timeout, self.poll).until(
                lambda _: condition()
            )
            return True
        except TimeoutException:
            raise AssertionError(
                "等待{}超时（{}s），当前地址：{}".format(desc, timeout, self.current_url())
            )

    # ---------------- 常用操作 ----------------

    def click(self, locator, desc="元素"):
        """点击元素，被遮挡时用 JS 兜底再点一次"""
        with allure.step("点击 {}".format(desc)):
            element = self.wait_clickable(locator, desc=desc)
            try:
                element.click()
            except ElementClickInterceptedException:
                self.logger.warning("{}被遮挡，改用 JS 点击", desc)
                self.driver.execute_script("arguments[0].click();", element)
            except StaleElementReferenceException:
                self.logger.warning("{}元素已刷新，重新定位后再点一次", desc)
                self.wait_clickable(locator, desc=desc).click()
            self.logger.info("点击成功：%s", desc)

    def input(self, locator, text, desc="输入框"):
        """清空并输入文本"""
        with allure.step("{}输入：{}".format(desc, text)):
            element = self.wait_visible(locator, desc=desc)
            element.clear()
            element.send_keys(text)
            self.logger.info("%s输入内容：%s", desc, text)

    def get_text(self, locator, desc="元素"):
        """获取元素显示文本"""
        element = self.wait_visible(locator, desc=desc)
        text = element.text.strip()
        self.logger.info("获取%s文本：%s", desc, text)
        return text

    def get_attribute(self, locator, attr, desc="元素"):
        element = self.wait_present(locator, desc=desc)
        return element.get_attribute(attr)

    def is_displayed(self, locator, timeout=3):
        """元素是否可见，等待超时返回 False，用于断言“不存在/不显示”场景"""
        try:
            WebDriverWait(self.driver, timeout, self.poll).until(
                EC.visibility_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False

    def click_text(self, text, desc="文本元素"):
        """按可见文本点击，适合按钮文字固定的场景"""
        locator = (By.XPATH, "//*[normalize-space(text())='{}']".format(text))
        self.click(locator, desc=desc or text)

    def press_key(self, locator, key, desc="元素"):
        """向元素发送按键，比如回车、TAB"""
        from selenium.webdriver.common.keys import Keys  # 局部导入避免循环依赖
        element = self.wait_visible(locator, desc=desc)
        element.send_keys(getattr(Keys, key))
        self.logger.info("%s发送按键：%s", desc, key)

    def scroll_to_bottom(self):
        """滚动到页面底部，配合懒加载列表使用"""
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)

    def sleep(self, seconds):
        """少量必须的硬等待，仅在页面动画场景使用"""
        time.sleep(seconds)

    # ---------------- 截图与调试 ----------------

    def screenshot(self, name="screenshot"):
        """截图并保存到 screenshots 目录，返回文件路径"""
        ensure_dir(SCREENSHOT_DIR)
        file_name = "{}_{}.png".format(name, datetime.now().strftime("%H%M%S"))
        file_path = os.path.join(SCREENSHOT_DIR, file_name)
        try:
            self.driver.save_screenshot(file_path)
            self.logger.info("截图已保存：%s", file_path)
        except Exception as e:
            self.logger.error("截图失败：%s", e)
            return None
        return file_path
