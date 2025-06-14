import datetime
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.common import TimeoutException

import Config
import Util

# 容器
visited_urls = Util.FIFOSet()  # 已访问的网页
visiting_urls = Util.FIFOSet()  # 待访问的网页


# 访问页面
def visit_page(driver: WebDriver) -> bool:
    # 跳过已访问的页面
    new_url = visiting_urls.pop()
    if new_url in visited_urls:
        return False  # 页面已下载，无效链接
    # 访问页面
    old_url = driver.current_url
    try:
        driver.get(new_url)
    except TimeoutException:
        pass
    finally:
        # 页面已访问
        visited_urls.add(new_url)
        if old_url == driver.current_url:
            # 页面未跳转即无效链接，下载或PDF被阻挡
            driver.get("about:blank")
            return False  # 无效链接
        else:
            # 过滤页面提取链接
            source = driver.page_source
            filter_pages(source, new_url)
            return True  # 页面未下载，有效链接


# 过滤获取到的页面
def filter_pages(source, cur_url):
    soup = BeautifulSoup(source, 'html.parser')
    elements = soup.find_all("a")
    # 提取链接
    links = []
    for element in elements:
        link = element.get("href")
        # 标签含有链接
        if not link:
            continue
        else:
            link = urljoin(cur_url, link)  # 获取url绝对路径
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
    for link in links:
        visiting_urls.add(link)  # 加入集合，避免某一个页面被多个页面指向


# 保存为MHTML
def save_page_as_mhtml(driver: WebDriver):
    # 执行chrome dev命令获得mhtml文件内容
    res = driver.execute_cdp_cmd('Page.captureSnapshot', {})
    # 用网址作为文件名需要替换字符，符合操作系统格式
    # 动态网页的链接太长了，改用时间
    save_path = str(datetime.datetime.now())
    save_path = save_path.replace(':', '.')
    # 保存网页文件到本地
    save_path += '.mhtml'
    with open('./download/' + save_path, 'w', newline='') as f:
        f.write(res['data'])
        f.close()


# 初始化爬虫
def driver_init(driver: WebDriver):
    # 设置超时
    driver.set_page_load_timeout(Config.WAIT_FOR_PAGE)
    # 初始化队列
    visiting_urls.add(Config.URL)


# 主函数
def main():
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
    # 初始化引擎
    driver_init(driver)
    # 开始，有页面待访问时访问，且获取到的页面数小于上限
    while len(visiting_urls) and (Config.PageLimit > len(visited_urls)):
        # 访问
        valid = visit_page(driver)
        # 下载
        if valid:
            save_page_as_mhtml(driver)
    # 退出
    driver.quit()


if __name__ == '__main__':
    main()
