"""
购物车页面对象
"""
from selenium.webdriver.common.by import By

from base.base_page import BasePage


class CartPage(BasePage):
    """购物车页"""

    # ---------------- 元素定位 ----------------
    PAGE = (By.CSS_SELECTOR, ".tab-cart")
    ITEMS = (By.CSS_SELECTOR, ".card-goods__item")
    ITEM_TITLES = (By.CSS_SELECTOR, ".card-goods__item .van-card__title")
    SUBMIT_BUTTON = (By.CSS_SELECTOR, ".van-submit-bar__button")
    TOTAL_PRICE = (By.CSS_SELECTOR, ".van-submit-bar__price")
    EDIT_BUTTON = (By.CSS_SELECTOR, ".editor_head span")
    DELETE_BUTTON = (By.CSS_SELECTOR, ".cart_delete")
    DIALOG_CONFIRM = (By.CSS_SELECTOR, ".van-dialog__confirm")
    CHECK_ALL = (By.CSS_SELECTOR, ".van-checkbox")
    STEPPER = (By.CSS_SELECTOR, ".van-stepper")
    STEPPER_PLUS = (By.CSS_SELECTOR, ".van-stepper__plus")
    STEPPER_MINUS = (By.CSS_SELECTOR, ".van-stepper__minus")
    EMPTY_TIP = (By.CSS_SELECTOR, ".is_empty")

    # ---------------- 页面操作 ----------------

    def open_cart(self):
        """打开购物车页"""
        self.open("/order")
        self.wait_visible(self.PAGE, desc="购物车页")
        self.logger.info("购物车页加载完成")

    def get_item_count(self, timeout=5):
        try:
            self.wait_all_present(self.ITEMS, timeout=timeout, desc="购物车商品列表")
        except Exception:
            return 0
        return len(self.driver.find_elements(*self.ITEMS))

    def get_item_titles(self, timeout=5):
        """购物车商品标题列表，列表异步加载，先等商品出现"""
        try:
            self.wait_all_present(self.ITEMS, timeout=timeout, desc="购物车商品列表")
        except Exception:
            return []
        elements = self.driver.find_elements(*self.ITEM_TITLES)
        return [e.text.strip() for e in elements]

    def wait_item_title(self, title, timeout=10):
        """等待购物车中出现指定商品"""
        self.wait_until(
            lambda: title in self.get_item_titles(timeout=1),
            timeout=timeout,
            desc="购物车出现商品【{}】".format(title),
        )

    def get_total_price(self):
        """购物车总计金额文本，形如 总计￥1539.00"""
        return self.get_text(self.TOTAL_PRICE, desc="购物车总计")

    def click_checkout(self):
        """点击底部结算按钮，进入结算页"""
        self.click(self.SUBMIT_BUTTON, desc="结算按钮")
        self.wait_url_contains("/order/checkout", desc="结算页跳转")

    def click_edit(self):
        """切换到编辑模式"""
        self.click(self.EDIT_BUTTON, desc="编辑按钮")

    def delete_item(self, index=0):
        """编辑模式下删除第 index 个商品，并在确认弹窗中点“确认”"""
        self.click_edit()
        delete_buttons = self.find_all(self.DELETE_BUTTON, desc="删除按钮")
        delete_buttons[index].click()
        self.click(self.DIALOG_CONFIRM, desc="确认删除")
        self.sleep(2)  # 等删除接口返回并刷新列表

    def increase_first_item_number(self):
        """第一个商品的购买数量加 1"""
        plus_buttons = self.find_all(self.STEPPER_PLUS, desc="数量加号")
        plus_buttons[0].click()
        self.sleep(2)  # 等数量更新接口返回

    def increase_until_plus_enabled(self, max_times=3):
        """数量加到上限后加号会禁用，这里最多点几次"""
        for _ in range(max_times):
            buttons = self.driver.find_elements(*self.STEPPER_PLUS)
            if not buttons:
                break
            if "disabled" in (buttons[0].get_attribute("class") or ""):
                break
            buttons[0].click()
            self.sleep(1.5)

    def is_empty(self):
        """购物车是否为空"""
        return self.is_displayed(self.EMPTY_TIP, timeout=5)
