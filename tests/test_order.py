"""
订单模块测试用例
覆盖：确认订单页信息、填写备注、提交订单
"""
import allure

from utils.data_loader import load_yaml

ORDER = load_yaml("goods_data")["order"]


@allure.feature("订单模块")
class TestOrder:
    """下单流程用例"""

    @allure.story("确认订单")
    @allure.title("确认订单页展示商品、金额和收货地址")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_checkout_page_info(self, checkout_ready):
        assert checkout_ready.get_goods_count() > 0, "确认订单页没有商品"
        assert "¥" in checkout_ready.get_total_price(), "确认订单页没有展示总计金额"

        body = checkout_ready.driver.find_element("tag name", "body").text
        assert "收货地址" in body
        assert "提交订单" in body

    @allure.story("确认订单")
    @allure.title("可以填写订单备注")
    def test_checkout_remark(self, checkout_ready):
        checkout_ready.input_remark(ORDER["remark"])
        assert checkout_ready.get_attribute(checkout_ready.REMARK_INPUT, "value") == ORDER["remark"]

    @allure.story("提交订单")
    @allure.title("确认订单页提交订单成功")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_submit_order(self, checkout_ready):
        checkout_ready.input_remark(ORDER["remark"])
        checkout_ready.submit_order()
        checkout_ready.sleep(3)

        # 提交成功后跳转到支付页，地址中带订单号
        current_url = checkout_ready.current_url()
        assert "/order/payment" in current_url, \
            "提交订单后没有跳转到支付页，当前地址：{}".format(current_url)
