"""
登录页页面对象
"""
from selenium.webdriver.common.by import By

from base.base_page import BasePage


class LoginPage(BasePage):
    """登录页"""

    # ---------------- 元素定位 ----------------
    ACCOUNT_INPUT = (By.CSS_SELECTOR, "input[placeholder*='测试账号']")
    PASSWORD_INPUT = (By.CSS_SELECTOR, "input[placeholder*='测试密码']")
    LOGIN_BUTTON = (By.CSS_SELECTOR, "button.van-button--danger")
    REGISTER_LINK = (By.CSS_SELECTOR, "a[href='#/login/registerGetCode']")
    TOAST = (By.CSS_SELECTOR, ".van-toast")

    # ---------------- 页面操作 ----------------

    def open_login(self):
        """打开登录页"""
        self.open("/login")
        self.wait_visible(self.ACCOUNT_INPUT, desc="账号输入框")

    def input_account(self, username):
        self.input(self.ACCOUNT_INPUT, username, desc="账号输入框")

    def input_password(self, password):
        self.input(self.PASSWORD_INPUT, password, desc="密码输入框")

    def click_login(self):
        """点击登录按钮"""
        self.click(self.LOGIN_BUTTON, desc="登录按钮")

    def login(self, username, password):
        """完整登录动作：输入账号密码并提交"""
        self.input_account(username)
        self.input_password(password)
        self.click_login()

    def get_toast_text(self):
        """获取登录失败时的提示文案，没有提示返回空字符串"""
        if self.is_displayed(self.TOAST, timeout=3):
            return self.get_text(self.TOAST, desc="登录提示")
        return ""
