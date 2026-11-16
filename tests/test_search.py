"""
搜索模块测试用例
覆盖：有结果搜索、无结果搜索、结果跳转详情、关键词回填
说明：被测版本前端存在两个缺陷，已在用例中显式标记
1. 无结果时页面不渲染任何提示文案（test_empty_result_tip 标记 xfail）
2. 搜索关键词不会写入历史搜索（pushHistoryTolocal 未被调用）
"""
import allure
import pytest

from utils.data_loader import load_yaml

SEARCH_CASES = load_yaml("search_data")


@allure.feature("搜索模块")
class TestSearch:
    """搜索相关用例"""

    @allure.story("关键词搜索")
    @allure.title("搜索校验：{case}")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.parametrize("case", SEARCH_CASES, ids=[c["case"] for c in SEARCH_CASES])
    def test_search(self, search_page, case):
        search_page.open_search()
        search_page.search(case["keyword"])
        search_page.wait_result_loaded()

        if case["expect_empty"]:
            assert search_page.get_result_count() == 0, "不存在的关键词不应返回商品"
        else:
            titles = search_page.get_result_titles()
            assert len(titles) > 0, "搜索结果为空"
            # 结果标题里至少有一条包含关键词
            assert any(case["keyword"] in t for t in titles), \
                "搜索结果与关键词无关：{}".format(titles)

    @allure.story("关键词搜索")
    @allure.title("搜索关键词会保留在搜索框中")
    def test_search_keyword_kept(self, search_page):
        search_page.open_search()
        search_page.search("衣")
        search_page.wait_result_loaded()

        assert search_page.get_attribute(search_page.SEARCH_INPUT, "value") == "衣"

    @allure.story("搜索结果跳转")
    @allure.title("点击搜索结果可以进入商品详情页")
    def test_click_search_result(self, search_page):
        search_page.open_search()
        search_page.search("衣")
        search_page.wait_result_loaded()
        first_title = search_page.get_result_titles()[0]

        search_page.click_result(0)
        assert "/items/detail" in search_page.current_url()
        # 详情页标题应与搜索结果标题一致
        detail_title = search_page.get_text(
            ("css selector", ".item-title"), desc="详情页商品标题")
        assert detail_title == first_title

    @allure.story("无结果提示")
    @allure.title("无匹配商品时展示空结果提示")
    @pytest.mark.xfail(reason="已知缺陷：前端 isEmpty 从未被置为 true，无结果时页面空白")
    def test_empty_result_tip(self, search_page):
        search_page.open_search()
        search_page.search("手机")
        search_page.wait_result_loaded()

        assert search_page.is_empty_result(), "无结果时应展示“抱歉,没有找到符合条件商品”"
        assert "没有找到" in search_page.get_empty_tip_text()
