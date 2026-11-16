"""
搜索页页面对象
"""
from selenium.webdriver.common.by import By

from base.base_page import BasePage


class SearchPage(BasePage):
    """商品搜索页"""

    # ---------------- 元素定位 ----------------
    PAGE = (By.CSS_SELECTOR, ".item_search")
    SEARCH_INPUT = (By.CSS_SELECTOR, ".item_search input")
    RESULT_CARDS = (By.CSS_SELECTOR, ".van-card")
    RESULT_TITLES = (By.CSS_SELECTOR, ".van-card__title")
    EMPTY_TIP = (By.CSS_SELECTOR, ".is_empty")
    HISTORY_TAGS = (By.CSS_SELECTOR, ".item_search_history .van-tag")
    CLEAR_HISTORY = (By.CSS_SELECTOR, ".item_search_text .float-r")

    # ---------------- 页面操作 ----------------

    def open_search(self):
        """直接打开搜索页"""
        self.open("/items/search")
        self.wait_visible(self.SEARCH_INPUT, desc="搜索输入框")

    def search(self, keyword):
        """
        输入关键词并回车搜索
        搜索结果由前端异步渲染，用显式等待替代固定 sleep
        """
        self.input(self.SEARCH_INPUT, keyword, desc="搜索输入框")
        self.press_key(self.SEARCH_INPUT, "ENTER", desc="搜索输入框")
        self.logger.info("搜索关键词：%s", keyword)

    def wait_result_loaded(self, timeout=10):
        """
        等待结果列表渲染
        注意：当前版本无结果时页面不会渲染任何提示（前端缺陷），
        这里超时后不抛异常，由用例自己断言结果数量
        """
        try:
            self.wait_all_present(self.RESULT_CARDS, timeout=timeout, desc="搜索结果列表")
        except Exception:
            self.logger.warning("未加载到搜索结果，可能是无结果场景")

    def get_result_count(self):
        return len(self.driver.find_elements(*self.RESULT_CARDS))

    def get_result_titles(self):
        elements = self.driver.find_elements(*self.RESULT_TITLES)
        return [e.text.strip() for e in elements]

    def is_empty_result(self):
        """是否展示“没有找到商品”的提示"""
        return self.is_displayed(self.EMPTY_TIP, timeout=5)

    def get_empty_tip_text(self):
        return self.get_text(self.EMPTY_TIP, desc="无结果提示")

    def click_result(self, index=0):
        """点击第 index 个搜索结果，进入商品详情"""
        cards = self.find_all(self.RESULT_CARDS, desc="搜索结果")
        cards[index].click()
        self.wait_url_contains("/items/detail", desc="商品详情页跳转")

    def get_history_keywords(self):
        elements = self.driver.find_elements(*self.HISTORY_TAGS)
        return [e.text.strip() for e in elements]
