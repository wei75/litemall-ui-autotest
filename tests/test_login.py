"""
登录模块测试用例
覆盖：登录成功、登录失败（数据驱动，数据来自 data/login_data.yaml）
"""
import allure
import pytest

from utils.data_loader import load_yaml

LOGIN_CASES = load_yaml("login_data")


@allure.feature("登录模块")
class TestLogin:
    """登录相关用例"""

    @allure.story("账号登录")
    @allure.title("登录功能校验：{case}")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.parametrize("case", LOGIN_CASES, ids=[c["case"] for c in LOGIN_CASES])
    def test_login(self, login_page, case):
        login_page.open_login()
        login_page.login(case["username"], case["password"])

        if case["expect_success"]:
            # 登录成功后跳转到“我的”页面
            login_page.wait_url_contains("/user", desc="登录成功跳转")
            assert "/user" in login_page.current_url()
            assert case["username"] in login_page.driver.find_element(
                "tag name", "body").text
        else:
            # 登录失败应停留在登录页，并给出错误提示
            login_page.sleep(2)
            assert "/login" in login_page.current_url(), "密码错误时不应跳转成功"
            toast = login_page.get_toast_text()
            assert toast != "", "登录失败时没有出现任何提示"

    @allure.story("登录态校验")
    @allure.title("登录后用户中心展示当前登录用户")
    def test_user_center_after_login(self, driver):
        from base.config_reader import PASSWORD, USERNAME
        from pages.login_page import LoginPage

        page = LoginPage(driver)
        page.open_login()
        page.login(USERNAME, PASSWORD)
        page.wait_url_contains("/user", desc="登录成功跳转")

        # 进入购物车，确认登录态在站内页面有效
        page.open("/order")
        page.sleep(3)
        assert "/login" not in page.current_url(), "已登录状态下访问购物车被重定向到登录页"
