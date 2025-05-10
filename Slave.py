import requests
import json

from Crawler import Crawler

import Config

BASE_URL: str


# 请求主机的页面
def master_task() -> dict:
    api = BASE_URL + '/task'
    data = requests.get(api).json()
    return data


# 更新主机的页面
def master_update(links: list[str]):
    api = BASE_URL + '/update'
    data = json.dumps({'links': links})
    data = requests.post(api, json=data).json()
    return data


# 主函数
def main():
    # 初始化爬虫
    crawler = Crawler()
    # 开始，有页面待访问时访问，且获取到的页面数小于上限
    while True:
        # 请求
        respond = master_task()
        match respond['command']:
            case 'task':  # 接受任务
                # 访问
                links = crawler.visit_page(respond['link'])
                # 更新
                master_update(links)
                # 下载
                crawler.save_page_as_mhtml()
            case 'continue':  # 等待任务
                continue
            case 'break':  # 任务结束
                break
    # 退出
    crawler.quit()


if __name__ == '__main__':
    # 设置网址
    BASE_URL = f'{Config.SCHEME}://{Config.HOST}:{Config.PORT}'
    # 启动爬虫
    main()
