"""
一键执行入口：执行 pytest 用例并生成 Allure HTML 报告

用法：
    python run.py                        # 全量执行并生成报告
    python run.py tests/test_login.py    # 只执行指定模块
    python run.py -k login               # 按关键字筛选用例
    python run.py --no-report            # 只执行用例，不生成报告
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
ALLURE_JS = os.path.join(ROOT, "tools", "node_modules", "allure-commandline", "bin", "allure")
RESULT_DIR = os.path.join(ROOT, "reports", "allure-results")
REPORT_DIR = os.path.join(ROOT, "reports", "allure-report")
REPORT_INDEX = os.path.join(REPORT_DIR, "index.html")


def generate_report():
    """调用 allure 命令行把 allure-results 渲染成 HTML 报告"""
    if not os.path.exists(ALLURE_JS):
        print("[WARN] 未找到 allure 命令行，跳过报告生成")
        print("       安装命令：npm install allure-commandline --prefix tools")
        return
    subprocess.call(
        ["node", ALLURE_JS, "generate", RESULT_DIR, "-o", REPORT_DIR, "--clean"],
        cwd=ROOT,
    )
    print("[INFO] 测试报告：{}".format(REPORT_INDEX))


def main():
    args = [a for a in sys.argv[1:] if a != "--no-report"]
    need_report = "--no-report" not in sys.argv[1:]

    # pytest 参数统一在 pytest.ini 里配置，这里只追加用户传入的参数
    exit_code = subprocess.call([sys.executable, "-m", "pytest"] + args, cwd=ROOT)

    if need_report:
        generate_report()

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
