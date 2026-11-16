# litemall 商城 Web UI 自动化测试项目

基于 **Python + Selenium + Pytest + Allure** 的 Web UI 自动化测试框架，被测对象为 litemall 商城前台
（`http://192.168.2.146:6255`，Vue + Vant 的移动端 H5 商城）。

## 一、目录结构

```
litemall_ui_autotest/
├── base/                       # 基础层：与业务无关的公共能力
│   ├── config_reader.py        # 读取 config/config.yaml，输出全局配置常量
│   ├── logger.py               # 日志封装，按天写入 logs/
│   ├── exceptions.py           # 自定义异常（元素找不到、页面加载失败、业务异常等）
│   ├── driver_factory.py       # 浏览器创建/销毁，Selenium Manager 自动匹配驱动
│   └── base_page.py            # 页面基类：显式等待、点击、输入、取文本、截图等通用操作
├── config/
│   └── config.yaml             # 环境地址、浏览器、超时、账号、目录配置
├── data/                       # 数据层：测试数据与配置分离
│   ├── login_data.yaml         # 登录用例数据（正确账号 / 错误密码）
│   ├── search_data.yaml        # 搜索用例数据（有结果 / 无结果）
│   └── goods_data.yaml         # 商品、规格、订单备注、收货地址数据
├── pages/                      # 业务层 POM：元素定位 + 业务动作
│   ├── home_page.py            # 首页
│   ├── login_page.py           # 登录页
│   ├── search_page.py          # 搜索页
│   ├── goods_detail_page.py    # 商品详情页（含规格选择弹窗）
│   ├── cart_page.py            # 购物车页
│   └── checkout_page.py        # 确认订单页（含地址选择）
├── tests/                      # 测试层：用例 + 断言 + Allure 注解
│   ├── conftest.py             # driver / 页面对象 / 登录态 fixture，失败自动截图
│   ├── test_home.py            # 首页
│   ├── test_login.py           # 登录
│   ├── test_search.py          # 搜索
│   ├── test_goods_detail.py    # 商品详情 / 加入购物车
│   ├── test_cart.py            # 购物车
│   └── test_order.py           # 下单流程
├── utils/
│   └── data_loader.py          # YAML 数据读取
├── tools/                      # 第三方工具（allure 命令行，npm 安装）
├── logs/                       # 运行日志（按天滚动）
├── screenshots/                # 失败截图（自动附加到 Allure 报告）
├── reports/
│   ├── allure-results/         # allure 原始结果（pytest 生成）
│   └── allure-report/          # allure HTML 报告（allure generate 生成）
├── pytest.ini                  # pytest 配置
├── requirements.txt            # Python 依赖
└── run.py                      # 一键执行入口
```

分层调用关系：`tests` → `pages` → `base`，测试数据统一放在 `data`，配置放在 `config`。
用例层不写元素定位，页面层不写断言，基础层不含业务。

## 二、环境准备

```bash
# 1. 创建虚拟环境并安装依赖
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt

# 2. 安装 allure 命令行（用于生成 HTML 报告，需要 Node.js）
npm install allure-commandline --prefix tools
```

浏览器使用本机 Chrome，驱动由 Selenium 4 的 Selenium Manager 自动下载匹配版本，无需手动配置。

## 三、执行方式

```bash
# 全量执行并生成 Allure 报告
python run.py

# 只跑某个模块
python run.py tests/test_login.py

# 按关键字筛选
python run.py -k cart

# 只执行用例，不生成报告
python run.py --no-report

# 直接使用 pytest（报告数据仍会写入 reports/allure-results）
.venv\Scripts\python -m pytest
```

报告生成后打开 `reports/allure-report/index.html` 查看，或执行：

```bash
node tools/node_modules/allure-commandline/bin/allure open reports/allure-results
```

## 四、用例覆盖

| 模块 | 用例数 | 覆盖内容 |
| ---- | ---- | ---- |
| 首页 test_home | 5 | 页面标题、频道入口、轮播图与商品列表、底部导航、搜索框跳转 |
| 登录 test_login | 3 | 正确账号登录成功、错误密码提示、登录后进入个人中心 |
| 搜索 test_search | 5 | 有结果搜索、无结果搜索、关键词回填、点击结果进详情、空结果提示（已知缺陷 xfail） |
| 商品详情 test_goods_detail | 3 | 标题/价格/简介展示、登录后加入购物车、未登录加购跳登录页 |
| 购物车 test_cart | 3 | 商品列表与合计金额、进入确认订单页、编辑模式删除商品 |
| 订单 test_order | 3 | 确认订单页信息、填写订单备注、提交订单跳转支付页 |

合计 **21 条通过 + 1 条 xfail（已知缺陷）**。

## 五、框架能力说明

- **显式等待**：所有元素操作基于 `WebDriverWait`，不使用固定 sleep（仅动画场景少量使用）。
- **失败自动截图**：`conftest.py` 中 `pytest_runtest_makereport` 钩子监听用例失败，自动截图并附加到 Allure 报告。
- **Allure 报告**：用例标注 `feature / story / title / severity`，步骤使用 `allure.step`，报告可按模块、严重级别查看。
- **配置与数据分离**：环境地址、超时、账号在 `config/config.yaml`；用例数据在 `data/*.yaml`，改数据不改代码。
- **日志**：每次运行写入 `logs/auto_test_YYYYMMDD.log`，同时输出到控制台。
- **无头模式**：`config.yaml` 中 `browser.headless: true` 可切换为无头运行，适合 Jenkins 等 CI 环境。

## 六、被测系统已知缺陷（用例已按实际行为处理）

1. **搜索无结果时页面空白**：前端 `isEmpty` 变量从未被置为 `true`，`.is_empty` 空状态组件不会渲染，
   预期提示“抱歉,没有找到符合条件商品”不出现。用例 `test_empty_result_tip` 标记为 `xfail`。
2. **搜索历史不记录**：前端 `pushHistoryTolocal` 方法已定义但从未被调用，搜索历史不会写入本地存储，
   因此未编写搜索历史相关用例。
3. **支付流程不可用**：支付页“去支付”依赖第三方支付回调，当前环境无法完成真实支付。
   订单用例只校验提交后跳转到 `/order/payment`，不继续执行支付操作。

## 七、新增用例规范

1. 元素定位写在 `pages/xxx_page.py` 的类属性中，统一使用 `(By.CSS_SELECTOR, "...")` 元组。
2. 业务动作封装为页面方法，内部只调用 `BasePage` 的通用方法，日志与等待由基础层负责。
3. 用例文件命名 `test_*.py`，用例类命名 `Test*`，使用 `allure.feature/story/title` 标注。
4. 测试数据放 `data/*.yaml`，通过 `utils.data_loader.load_yaml` 读取。
5. 用例之间保持独立：每个用例独立创建浏览器（function 级 fixture），不依赖执行顺序。
