"""
首页页面对象
负责首页的元素定位和基础操作，不做业务断言
"""
from selenium.webdriver.common.by import By

from base.base_page import BasePage


class HomePage(BasePage):
    """首页"""

    # ---------------- 元素定位 ----------------
    SEARCH_BOX = (By.CSS_SELECTOR, ".tal_class_searchBox")
    SEARCH_MASK = (By.CSS_SELECTOR, ".tal_class_searchMask")
    CHANNEL_ITEMS = (By.CSS_SELECTOR, ".goods-channel .item")
    GOODS_CARDS = (By.CSS_SELECTOR, ".van-card")
    GOODS_TITLES = (By.CSS_SELECTOR, ".van-card__title")
    BANNER = (By.CSS_SELECTOR, ".van-swipe")
    TABBAR_ITEMS = (By.CSS_SELECTOR, ".van-tabbar-item")

    # ---------------- 页面操作 ----------------

    def open_home(self):
        """打开首页并等待首屏加载完成"""
        self.open("")
        self.wait_visible(self.SEARCH_BOX, desc="首页搜索框")
        self.logger.info("首页加载完成")

    def get_channels(self):
        """获取首页频道入口名称列表"""
        elements = self.find_all(self.CHANNEL_ITEMS, desc="首页频道入口")
        return [e.text.strip() for e in elements]

    def get_goods_titles(self):
        """获取首页商品卡片标题列表"""
        elements = self.find_all(self.GOODS_TITLES, desc="首页商品标题")
        return [e.text.strip() for e in elements]

    def get_tabbar_count(self):
        """底部导航栏数量"""
        return len(self.find_all(self.TABBAR_ITEMS, desc="底部导航"))

    def click_search_box(self):
        """点击首页搜索框，跳转到搜索页"""
        # 注意：遮罩层 .tal_class_searchMask 高度为 0 不可点击，要点容器本身
        self.click(self.SEARCH_BOX, desc="首页搜索框")
        self.wait_url_contains("/items/search", desc="搜索页跳转")

    def click_channel(self, index=0):
        """点击指定频道入口"""
        channels = self.find_all(self.CHANNEL_ITEMS, desc="首页频道入口")
        channels[index].click()

    def is_banner_displayed(self):
        """首页轮播图是否显示"""
        return self.is_displayed(self.BANNER, timeout=5)
