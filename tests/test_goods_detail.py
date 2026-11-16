"""
商品详情模块测试用例
覆盖：详情信息展示、加入购物车
"""
import allure

from pages.cart_page import CartPage
from pages.goods_detail_page import GoodsDetailPage
from utils.data_loader import load_yaml

GOODS = load_yaml("goods_data")["goods"]


@allure.feature("商品详情模块")
class TestGoodsDetail:
    """商品详情相关用例"""

    @allure.story("详情展示")
    @allure.title("商品详情页展示标题、价格和简介")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_goods_detail_info(self, goods_detail_page):
        goods_detail_page.open_detail(GOODS["id"])

        assert goods_detail_page.get_title() == GOODS["title"]
        assert goods_detail_page.get_price() == GOODS["price"]
        # 市场价应高于售价，并且是金额格式
        assert "¥" in goods_detail_page.get_market_price()
        assert goods_detail_page.get_intro() != ""

    @allure.story("加入购物车")
    @allure.title("详情页加入购物车，购物车能看到该商品")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_add_to_cart(self, logged_in_driver):
        detail = GoodsDetailPage(logged_in_driver)
        detail.open_detail(GOODS["id"])
        detail.click_add_cart(GOODS["specs"])

        # 点击加入购物车应弹出规格选择
        assert detail.is_sku_popup_displayed(), "点击加入购物车后没有弹出规格选择框"
        detail.confirm_add_cart()
        detail.sleep(2)

        # 到购物车页面确认商品已加入
        cart = CartPage(logged_in_driver)
        cart.open_cart()
        cart.wait_item_title(GOODS["title"])
        assert GOODS["title"] in cart.get_item_titles(), "购物车中找不到刚加入的商品"

    @allure.story("加入购物车")
    @allure.title("未登录点击加入购物车会跳转登录页")
    def test_add_cart_without_login(self, goods_detail_page):
        goods_detail_page.open_detail(GOODS["id"])
        goods_detail_page.click_add_cart(GOODS["specs"])
        goods_detail_page.confirm_add_cart()
        goods_detail_page.sleep(2)

        # 未登录时前端会拦截并跳转登录页
        assert "/login" in goods_detail_page.current_url()
