"""
结算页（确认订单）页面对象
"""
from selenium.webdriver.common.by import By

from base.base_page import BasePage


class CheckoutPage(BasePage):
    """订单结算页"""

    # ---------------- 元素定位 ----------------
    PAGE = (By.CSS_SELECTOR, ".order")
    # 收货地址所在单元格：结算页第一个 cell 即“收货地址”
    ADDRESS_CELL = (By.CSS_SELECTOR, ".order .van-cell-group:first-child .van-cell")
    ADDRESS_LABEL = (By.CSS_SELECTOR, ".order .van-cell-group:first-child .van-cell__label")
    ADDRESS_TEXT = (By.CSS_SELECTOR, ".order .van-cell__value")
    GOODS_CARDS = (By.CSS_SELECTOR, ".order .van-card")
    GOODS_TITLES = (By.CSS_SELECTOR, ".order .van-card__title")
    TOTAL_PRICE = (By.CSS_SELECTOR, ".van-submit-bar__price")
    REMARK_INPUT = (By.CSS_SELECTOR, "input[placeholder='请输入备注']")
    SUBMIT_BUTTON = (By.CSS_SELECTOR, ".van-submit-bar__button")
    TOAST = (By.CSS_SELECTOR, ".van-toast")
    # 地址选择列表页
    ADDRESS_ITEMS = (By.CSS_SELECTOR, ".van-address-item")

    # ---------------- 页面操作 ----------------

    def open_checkout(self):
        """打开结算页"""
        self.open("/order/checkout")
        self.wait_visible(self.PAGE, desc="结算页")

    def get_goods_count(self):
        return len(self.driver.find_elements(*self.GOODS_CARDS))

    def get_total_price(self):
        return self.get_text(self.TOTAL_PRICE, desc="订单总计")

    def input_remark(self, remark):
        """填写订单备注"""
        self.input(self.REMARK_INPUT, remark, desc="订单备注")

    def get_goods_titles(self):
        elements = self.driver.find_elements(*self.GOODS_TITLES)
        return [e.text.strip() for e in elements]

    def has_checked_address(self):
        """结算页是否已经带出收货地址（有姓名/电话）"""
        try:
            return self.get_text(self.ADDRESS_LABEL, desc="收货地址信息") != ""
        except Exception:
            return False

    def click_address_cell(self):
        """点击收货地址栏，跳转地址列表页"""
        self.click(self.ADDRESS_CELL, desc="收货地址")
        self.wait_url_contains("/user/address", desc="地址列表页跳转")

    def select_first_address(self):
        """在地址列表中选择第一条地址，选中后自动返回结算页"""
        items = self.find_all(self.ADDRESS_ITEMS, desc="地址列表")
        items[0].click()
        self.wait_url_contains("/order/checkout", desc="返回结算页")
        self.wait_visible(self.PAGE, desc="结算页")

    def ensure_address_selected(self):
        """确保结算页已选中收货地址，未选中则去地址列表选第一条"""
        if self.has_checked_address():
            return
        self.click_address_cell()
        self.select_first_address()
        # 选中地址后前端会重新请求结算信息
        self.wait_until(lambda: self.has_checked_address(), desc="收货地址回填")

    def submit_order(self):
        """点击提交订单"""
        self.click(self.SUBMIT_BUTTON, desc="提交订单按钮")

    def get_toast_text(self):
        if self.is_displayed(self.TOAST, timeout=3):
            return self.get_text(self.TOAST, desc="提示信息")
        return ""

    def is_loaded(self):
        return self.is_displayed(self.PAGE, timeout=5)
