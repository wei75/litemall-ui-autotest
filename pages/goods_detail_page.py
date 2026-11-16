"""
商品详情页页面对象
"""
from selenium.webdriver.common.by import By

from base.base_page import BasePage


class GoodsDetailPage(BasePage):
    """商品详情页"""

    # ---------------- 元素定位 ----------------
    PAGE = (By.CSS_SELECTOR, ".item_detail")
    TITLE = (By.CSS_SELECTOR, ".item-title")
    PRICE = (By.CSS_SELECTOR, ".item_price")
    MARKET_PRICE = (By.CSS_SELECTOR, ".item_market_price")
    INTRO = (By.CSS_SELECTOR, ".item_intro")
    ADD_CART_BUTTON = (By.CSS_SELECTOR, ".van-goods-action-button--warning")
    BUY_NOW_BUTTON = (By.CSS_SELECTOR, ".van-goods-action-button--danger")
    # 注意：该弹窗元素本身同时带有 van-popup--bottom 与 van-sku-container 两个类
    SKU_POPUP = (By.CSS_SELECTOR, ".van-popup--bottom.van-sku-container")
    # 规格选项：未选中规格前 SKU 库存按 0 处理，加购会失败，必须先选规格
    SKU_SPEC_ITEM = (By.CSS_SELECTOR, ".van-sku-row__item")
    SKU_ADD_CART = (By.CSS_SELECTOR, ".van-sku-actions .van-button--warning")
    TOAST = (By.CSS_SELECTOR, ".van-toast")

    # ---------------- 页面操作 ----------------

    def open_detail(self, goods_id):
        """按商品 id 打开详情页"""
        self.open("/items/detail/{}".format(goods_id))
        self.wait_visible(self.PAGE, desc="商品详情页")
        self.wait_visible(self.TITLE, desc="商品标题")

    def get_title(self):
        return self.get_text(self.TITLE, desc="商品标题")

    def get_price(self):
        return self.get_text(self.PRICE, desc="商品价格")

    def get_market_price(self):
        return self.get_text(self.MARKET_PRICE, desc="商品市场价")

    def get_intro(self):
        return self.get_text(self.INTRO, desc="商品简介")

    def select_first_spec(self):
        """选择规格弹窗中的第一个规格（不选规格时库存为 0，加购会失败）"""
        items = self.find_all(self.SKU_SPEC_ITEM, desc="规格选项")
        items[0].click()
        self.logger.info("已选择第一个规格")

    def select_specs(self, specs):
        """
        按文本依次选择规格，例如 ['1.5m床垫*1+枕头*2', '玛瑙红']
        用 JS 点击避免弹窗滚动导致元素被遮挡
        """
        for spec in specs:
            locator = (
                By.XPATH,
                "//span[contains(@class,'van-sku-row__item')][normalize-space(.)='{}']".format(spec),
            )
            element = self.wait_visible(locator, desc="规格【{}】".format(spec))
            self.driver.execute_script("arguments[0].click();", element)
            self.sleep(0.3)
            self.logger.info("已选择规格：%s", spec)

    def click_add_cart(self, specs=None):
        """
        点击详情页底部“加入购物车”，弹出规格选择框并选择规格
        specs 为空时只选每组第一个规格，适合单规格商品
        """
        self.click(self.ADD_CART_BUTTON, desc="加入购物车按钮")
        self.wait_visible(self.SKU_POPUP, desc="规格选择弹窗")
        if specs:
            self.select_specs(specs)
        else:
            self.select_first_spec()

    def confirm_add_cart(self):
        """在规格弹窗中点确认，完成加入购物车"""
        self.click(self.SKU_ADD_CART, desc="弹窗内加入购物车按钮")

    def add_to_cart(self, specs=None):
        """加入购物车完整动作，并等待弹窗关闭（加购成功后前端会关闭规格弹窗）"""
        self.click_add_cart(specs)
        self.confirm_add_cart()
        self.wait_until(
            lambda: not self.is_displayed(self.SKU_POPUP, timeout=1),
            desc="加购完成、规格弹窗关闭",
        )

    def get_toast_text(self):
        if self.is_displayed(self.TOAST, timeout=3):
            return self.get_text(self.TOAST, desc="操作提示")
        return ""

    def is_sku_popup_displayed(self):
        return self.is_displayed(self.SKU_POPUP, timeout=5)
