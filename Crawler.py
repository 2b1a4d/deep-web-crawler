from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.common import TimeoutException

import Config
import Util


class Crawler:
    # 初始化爬虫
    def __init__(self):
        # 创建驱动
        opt = Options()
        opt.binary_location = Config.BROWSER_PATH
        prefs = {
            "download_restrictions": 3,  # 禁用下载，过滤下载页面，该链接不会跳转
            # "plugins.always_open_pdf_externally": True,  # 禁用PDF预览，直接下载
        }
        opt.add_experimental_option("prefs", prefs)
        # opt.add_experimental_option('detach', True)  # 运行完成后不自动关闭
        # opt.add_argument('--headless')  # 无头模式，无用户界面
        ser = Service()
        ser.path = Config.DRIVER_PATH
        # 创建实例
        driver = webdriver.Chrome(opt, ser)
        # 设置超时
        # driver.set_script_timeout(10)  # 设置脚本超时
        driver.set_page_load_timeout(Config.WAIT_FOR_PAGE)  # 设置页面加载超时
        # 保存
        self.driver: WebDriver = driver
        # 初始化
        self.load_init()

    # 导入cookies或sessions
    def load_init(self):
        # 此处没有实现
        # 导出当前网页对应网站的cookies，并再次导入
        # cookies = self.driver.get_cookies()
        # self.driver.add_cookie(cookies)
        # # 获取浏览器的会话
        # session_id = self.driver.session_id
        # self.driver.session_id = session_id
        pass

    # 访问页面
    def visit_page(self, new_url: str) -> list[str]:
        # 访问页面
        old_url = self.driver.current_url
        # 超时中止页面加载
        try:
            self.driver.get(new_url)
        except TimeoutException:
            pass
        # 取当前的网页地址，也需要超时处理
        try:
            if old_url != self.driver.current_url:
                # 过滤页面提取链接
                source = self.driver.page_source
                links = Util.filter_pages(source, new_url)
                return links
        except TimeoutException:
            pass
        # 超时、页面未跳转，不使用finally块防止覆盖return
        self.driver.get("about:blank")
        return []

    # 获取页面
    def save_page_as_mhtml(self) -> str:
        # 执行chrome dev命令获得mhtml文件内容
        res = self.driver.execute_cdp_cmd('Page.captureSnapshot', {})
        # 保存网页文件为字符
        text = res['data']
        return text

    # 关闭爬虫
    def quit(self):
        self.driver.quit()
