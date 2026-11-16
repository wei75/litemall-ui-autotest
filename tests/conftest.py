"""
pytest 全局配置
- 提供浏览器实例和页面对象
- 用例失败自动截图并附加到 allure 报告
- 生成 allure 的环境信息
"""
import os
import time

import allure
import pytest

from base.config_reader import (
    BASE_URL,
    BROWSER_NAME,
    HEADLESS,
    PASSWORD,
    REPORT_DIR,
    SCREENSHOT_DIR,
    USERNAME,
    ensure_dir,
)
from base.driver_factory import create_driver, quit_driver
from base.logger import logger
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.goods_detail_page import GoodsDetailPage
from pages.home_page import HomePage
from pages.login_page import LoginPage
from pages.search_page import SearchPage
from utils.data_loader import load_yaml

GOODS = load_yaml("goods_data")["goods"]


@pytest.fixture(scope="function")
def driver():
    """每个用例一个干净的浏览器实例，用例之间互不影响"""
    browser = create_driver()
    yield browser
    quit_driver(browser)


@pytest.fixture(scope="function")
def home_page(driver):
    return HomePage(driver)


@pytest.fixture(scope="function")
def login_page(driver):
    return LoginPage(driver)


@pytest.fixture(scope="function")
def search_page(driver):
    return SearchPage(driver)


@pytest.fixture(scope="function")
def goods_detail_page(driver):
    return GoodsDetailPage(driver)


@pytest.fixture(scope="function")
def cart_page(driver):
    return CartPage(driver)


@pytest.fixture(scope="function")
def checkout_page(driver):
    return CheckoutPage(driver)


@pytest.fixture(scope="function")
def logged_in_driver(driver):
    """已登录状态的浏览器，供需要登录的用例直接使用"""
    page = LoginPage(driver)
    page.open_login()
    page.login(USERNAME, PASSWORD)
    page.wait_url_contains("/user", desc="登录成功跳转")
    logger.info("用例前置：使用账号 %s 登录成功", USERNAME)
    return driver


@pytest.fixture(scope="function")
def cart_with_goods(logged_in_driver):
    """已登录且购物车中至少有一件商品，返回购物车页面对象"""
    detail = GoodsDetailPage(logged_in_driver)
    detail.open_detail(GOODS["id"])
    detail.add_to_cart(GOODS["specs"])
    detail.sleep(2)  # 等加购接口返回

    cart = CartPage(logged_in_driver)
    cart.open_cart()
    return cart


@pytest.fixture(scope="function")
def checkout_ready(cart_with_goods):
    """已从购物车进入确认订单页，并且已选中收货地址"""
    cart_with_goods.click_checkout()

    checkout = CheckoutPage(cart_with_goods.driver)
    checkout.wait_visible(checkout.PAGE, desc="确认订单页")
    # 未选中地址时，去地址列表选第一条
    checkout.ensure_address_selected()
    return checkout


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """用例失败时自动截图，并附加到 allure 报告"""
    outcome = yield
    report = outcome.get_result()

    if report.when in ("setup", "call") and report.failed:
        driver = item.funcargs.get("driver") or item.funcargs.get("logged_in_driver")
        if driver is None:
            # 用例使用页面对象或复合 fixture 时，从里面取浏览器实例
            for value in item.funcargs.values():
                candidate = getattr(value, "driver", value)
                if hasattr(candidate, "get_screenshot_as_png"):
                    driver = candidate
                    break
        if driver is None:
            return
        # 附加页面截图
        try:
            png = driver.get_screenshot_as_png()
            allure.attach(png, name="失败截图", attachment_type=allure.attachment_type.PNG)

            ensure_dir(SCREENSHOT_DIR)
            file_name = "{}_{}.png".format(item.name, time.strftime("%H%M%S"))
            file_path = os.path.join(SCREENSHOT_DIR, file_name)
            with open(file_path, "wb") as f:
                f.write(png)
            logger.error("用例失败，截图已保存：%s", file_path)
        except Exception as e:
            logger.warning("失败截图保存异常：%s", e)

        # 附加当前地址，方便定位
        try:
            allure.attach(driver.current_url, name="失败页面地址", attachment_type=allure.attachment_type.TEXT)
        except Exception:
            pass


def pytest_sessionfinish(session, exitstatus):
    """测试执行结束后写入 allure 环境信息"""
    ensure_dir(REPORT_DIR)
    env_file = os.path.join(REPORT_DIR, "environment.properties")
    with open(env_file, "w", encoding="utf-8") as f:
        f.write("被测环境={}\n".format(BASE_URL))
        f.write("浏览器={}\n".format(BROWSER_NAME))
        f.write("无头模式={}\n".format(HEADLESS))
        f.write("测试账号={}\n".format(USERNAME))
        f.write("技术栈=Python + Selenium + Pytest + Allure\n")
    logger.info("allure 环境信息已写入：%s", env_file)
