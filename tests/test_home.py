"""
首页模块测试用例
覆盖：页面加载、频道入口、商品展示、搜索入口、底部导航
"""
import allure

from utils.data_loader import load_yaml


@allure.feature("首页模块")
class TestHome:
    """首页相关用例"""

    @allure.story("首页展示")
    @allure.title("首页加载成功，页面标题正确")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_home_page_load(self, home_page):
        home_page.open_home()
        assert "litemall" in home_page.driver.title.lower()

    @allure.story("首页展示")
    @allure.title("首页展示 9 个商品频道入口")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_home_channels(self, home_page):
        home_page.open_home()
        channels = home_page.get_channels()
        assert len(channels) == 9, "首页频道数量不对，实际：{}".format(channels)
        assert "居家" in channels
        assert "服装" in channels

    @allure.story("首页展示")
    @allure.title("首页展示轮播图和推荐商品")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_home_banner_and_goods(self, home_page):
        home_page.open_home()
        assert home_page.is_banner_displayed(), "首页轮播图未展示"
        titles = home_page.get_goods_titles()
        assert len(titles) > 0, "首页没有展示任何商品"

    @allure.story("首页展示")
    @allure.title("底部导航栏包含 4 个入口")
    def test_home_tabbar(self, home_page):
        home_page.open_home()
        assert home_page.get_tabbar_count() == 4

    @allure.story("搜索入口")
    @allure.title("点击首页搜索框能跳转到搜索页")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_click_search_box(self, home_page):
        home_page.open_home()
        home_page.click_search_box()
        assert "/items/search" in home_page.current_url()
