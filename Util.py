import logging
import time
from collections import deque, defaultdict
from logging import FileHandler
from typing import Any
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

import Config


# 线程等待
def wait_task():
    time.sleep(Config.WAIT_FOR_TASK)


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


# 保存MHTML到本地
def save_mhtml(name: str, text: str) -> None:
    # 用网址作为文件名需要替换字符，符合操作系统格式
    # 动态网页的链接太长了，改用时间
    # 时间可能重复，改用索引
    with open(f'{Config.DOWNLOAD_PATH}{name}.mhtml', 'w', newline='') as f:
        f.write(text)


# 主机状态响应格式化
def statu_format(left: list[tuple[str, list[int]]], right: (list[str], list[str])) -> (list[dict[str, str]], list[str]):
    # 从机地址和实例池
    left_result = []
    for i, item in enumerate(left, start=1):
        name = f'从机{i} - {item[0]}'
        num = f'实例数 - {len(item[1])}'
        left_result.append({'name': name, 'num': num})
    # 任务列表节选
    right_result = []
    for item in right[0]:
        right_result.append(f'已访问 - {item}')
    for item in right[1]:
        right_result.append(f'待访问 - {item}')
    # 结果
    return left_result, right_result


# 先进先出集合
class FIFOSet:
    # 功能全为O(1)时间复杂度
    def __init__(self):
        self.queue = deque()
        self.table = set()

    # 元素加入队列
    def add(self, item):
        if item not in self.table:
            self.queue.append(item)
            self.table.add(item)

    # 队列取出元素
    def pop(self):
        item = self.queue.popleft()
        self.table.remove(item)
        return item

    # 队列长度
    def __len__(self):
        return len(self.queue)

    # 队列内是否包含某一元素
    def __contains__(self, item):
        return item in self.table

    # 队列列表化
    def __iter__(self):
        return iter(self.queue)


# 滑动集合
class SlideSet:
    # 功能全为O(1)时间复杂度
    def __init__(self):
        self.queue = list()  # 列表顺序存储元素
        self.table = set()  # 为列表中的元素建立集合
        self.pointer = 0  # 指向最先进入且还未的元素

    # 元素加入队列
    def add(self, item):
        if item not in self.table:
            self.queue.append(item)
            self.table.add(item)

    # 队列取出元素
    def pop(self):
        item = self.queue[self.pointer]
        self.pointer += 1
        return item

    # 已完成任务
    def done(self) -> int:
        return self.pointer

    # 待完成任务
    def doing(self) -> int:
        return len(self.queue) - self.pointer

    # 队列列表化
    def slice(self, num: int = 3) -> (list[str], list[str]):
        done = self.queue[max(0, self.pointer - num):self.pointer]
        doing = self.queue[self.pointer:self.pointer + num]
        return done, doing


# 计数字典
class CountDict:
    # 功能全为O(1)时间复杂度
    def __init__(self):
        self.pool: dict[str, list[int]] = defaultdict(list)  # 存储每个从机的实例编号
        self.total: int = 0  # 总共的实例数

    # 添加一个元素
    def add(self, address: str) -> int:
        self.total += 1
        self.pool[address].append(self.total)
        return self.total

    # 字典列表化
    def __iter__(self):
        return iter(self.pool.items())


# 集合树
class SetTree:
    # 功能全为O(1)时间复杂度
    def __init__(self):
        self.tree: dict[Any, int] = dict()  # 保存元素所在层数
        self.floor: int = 0  # 树的最深处

    # 添加一个元素
    def add(self, item, level: int = 1):
        if item not in self.tree:
            self.tree[item] = level
            if level > self.floor:
                self.floor = level

    # 取在树中的层数
    def level(self, start) -> int:
        return self.tree[start] + 1

    # 最深层为
    def depth(self) -> int:
        return self.floor


# 主机控制面板
class Panel:
    # 控制服务器
    def __init__(self):
        # 任务是否分配
        self.TaskFlag = True
        # 主机日志记录
        handler = FileHandler(Config.WEB_FILE_PATH + Config.LOG_FILE_NAME, mode='w')
        logger = logging.getLogger(Config.WHO_AM_I)
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)
        self.logger = logger  # 如果本实例创建后调用app.logger，那么self.logger is app.logger

    # 停止任务
    def halt(self):
        self.TaskFlag = False

    # 记录日志
    def info(self, request, response):
        sec = int(time.time())
        msg = f'{request.remote_addr} "{request.method} {request.path}" - {response.status_code}'
        self.logger.info(f'{sec} -- {msg}')
