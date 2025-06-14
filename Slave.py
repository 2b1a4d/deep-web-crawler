import requests

from Crawler import Crawler
import Config
import Util

BASE_URL: str


# 请求主机的页面
def master_task() -> dict:
    api = BASE_URL + '/task'
    data = requests.get(api).json()
    return data


# 将获取到的页面上传到主机
def master_upload(name: str, text: str) -> None:
    api = BASE_URL + '/upload'
    data = {'name': name, 'text': text}
    requests.post(api, json=data)


# 更新主机的页面
def master_update(links: list[str], start: str) -> None:
    api = BASE_URL + '/update'
    data = {'links': links, 'start': start}
    requests.post(api, json=data)


# 访问主机登记地址
def master_ping() -> None:
    api = BASE_URL + '/control'
    data = {'command': 'ping'}
    requests.put(api, json=data)


# 主函数
def main():
    # 初始化爬虫
    crawler = Crawler()
    master_ping()
    # 开始，有页面待访问时访问，且获取到的页面数小于上限
    while True:
        # 请求
        respond = master_task()
        match respond['command']:
            case 'task':  # 接受任务
                # 访问
                cur = respond['link']
                links = crawler.visit_page(cur)
                # 下载
                text = crawler.save_page_as_mhtml()
                master_upload(respond['counter'], text)
                # 更新
                master_update(links, cur)
            case 'continue':  # 等待任务
                Util.wait_task()
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
