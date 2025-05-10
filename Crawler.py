import datetime
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.common import TimeoutException

import Config


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
        opt.add_argument('--headless')  # 无头模式，无用户界面
        ser = Service()
        ser.path = Config.DRIVER_PATH
        # 创建实例
        driver = webdriver.Chrome(opt, ser)
        # 设置超时
        # driver.set_script_timeout(10)  # 设置脚本超时
        driver.set_page_load_timeout(Config.TIME_TO_WAIT)  # 设置页面加载超时
        # 保存
        self.driver: WebDriver = driver

    # 访问页面
    def visit_page(self, new_url: str) -> list[str]:
        # 访问页面
        source = ''
        old_url = self.driver.current_url
        try:
            self.driver.get(new_url)
            source = self.driver.page_source
        except TimeoutException:
            source = self.driver.page_source
        finally:
            if old_url == self.driver.current_url:
                # 页面未跳转即无效链接
                return []
            else:
                # 过滤页面提取链接
                return filter_pages(source, new_url)

    # 保存为MHTML
    def save_page_as_mhtml(self):
        # 执行chrome dev命令获得mhtml文件内容
        res = self.driver.execute_cdp_cmd('Page.captureSnapshot', {})
        # 用网址作为文件名需要替换字符，符合操作系统格式
        # 动态网页的链接太长了，改用时间
        save_path = str(datetime.datetime.now())
        save_path = save_path.replace(':', '.')
        save_path += '.mhtml'
        # 保存网页文件到本地
        with open('./download/' + save_path, 'w', newline='') as f:
            f.write(res['data'])

    # 关闭爬虫
    def quit(self):
        self.driver.quit()


# 过滤获取到的页面
def filter_pages(source: str, base_url: str) -> list[str]:
    soup = BeautifulSoup(source, 'html.parser')
    elements = soup.find_all("a")
    # 提取链接
    links = []
    for element in elements:
        link = element.get("href")
        # 标签含有链接
        if link:
            link = urljoin(base_url, link)  # 获取url绝对路径
            # 过滤链接
            result = urlparse(link)
            if result.fragment:
                continue  # 锚点
            elif 'http' not in result.scheme:  # js或mailto
                continue  # 无效
            elif Config.DOMAIN not in result.netloc:  # 解析url，避免查询参数的干扰
                continue  # 外站
            else:
                links.append(link)
    # 加入队列
    return links
