"""
购物车模块测试用例
覆盖：购物车列表、商品结算跳转、删除商品
"""
import allure

from pages.checkout_page import CheckoutPage
from utils.data_loader import load_yaml

GOODS = load_yaml("goods_data")["goods"]


@allure.feature("购物车模块")
class TestCart:
    """购物车相关用例"""

    @allure.story("购物车展示")
    @allure.title("购物车展示已加入的商品和合计金额")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_cart_show_goods(self, cart_with_goods):
        assert cart_with_goods.get_item_count() > 0, "购物车商品数量为 0"
        assert "¥" in cart_with_goods.get_total_price(), "购物车没有展示合计金额"

    @allure.story("结算")
    @allure.title("购物车点击结算能进入确认订单页")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_cart_to_checkout(self, cart_with_goods):
        cart_with_goods.click_checkout()

        checkout = CheckoutPage(cart_with_goods.driver)
        assert checkout.is_loaded(), "没有进入确认订单页"
        assert "/order/checkout" in cart_with_goods.current_url()

    @allure.story("删除商品")
    @allure.title("编辑模式下可以删除购物车商品")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_delete_cart_goods(self, cart_with_goods):
        titles_before = cart_with_goods.get_item_titles()
        index = titles_before.index(GOODS["title"])

        # 进入编辑模式，删除对应位置的商品并确认
        cart_with_goods.delete_item(index)

        titles_after = cart_with_goods.get_item_titles()
        assert titles_after.count(GOODS["title"]) < titles_before.count(GOODS["title"]), \
            "删除商品后购物车中仍然存在该商品"
