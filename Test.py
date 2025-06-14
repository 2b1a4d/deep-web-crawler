import requests

import Config

BASE_URL: str


# 主函数
def main():
    requests.put(BASE_URL + '/control', json={'command': 'ping'})
    requests.put(BASE_URL + '/control', json={'command': 'init'})


if __name__ == '__main__':
    # 设置网址
    BASE_URL = f'{Config.SCHEME}://{Config.HOST}:{Config.PORT}'
    # 启动爬虫
    main()
