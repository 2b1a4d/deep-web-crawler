import threading
from threading import Lock

from flask import Flask, request, jsonify, send_from_directory, redirect

import Config
import Util

# 实例
app = Flask(Config.WHO_AM_I)
# 链接集合
LinkSet = Util.SlideSet()
# LinkTree = Util.SetTree()
# 爬虫实例池
CrawlerPool = Util.CountDict()
# 线程锁
SLock = Lock()
# 服务器控制
Panel = Util.Panel()


@app.route('/task', methods=['GET'])
def task():  # 网页爬取任务调度
    with SLock:
        if (Config.PageLimit > LinkSet.done()) and Panel.TaskFlag:
            if LinkSet.doing():
                command, link, counter = 'task', LinkSet.pop(), LinkSet.done()
            else:
                command, link, counter = 'continue', '', ''
        else:
            command, link, counter = 'break', '', ''
    return jsonify({'command': command, 'link': link, 'counter': counter})


@app.route('/upload', methods=['POST'])
def upload():  # 网页保存到本地
    data = request.get_json()
    name, text = data['name'], data['text']
    threading.Thread(target=Util.save_mhtml, args=(name, text)).start()
    return jsonify({'': ''})


@app.route('/update', methods=['POST'])
def update():  # 更新任务集合
    data = request.get_json()
    links, start = data['links'], data['start']
    with SLock:
        for link in links:
            LinkSet.add(link)
            # LinkTree.add(link, LinkTree.level(start))
    return jsonify({'': ''})


@app.route('/', methods=['GET'])
def root():  # 重定向到前端
    return redirect('/Index.html')


@app.route('/control', methods=['PUT'])
def control():  # 控制主机
    command = request.get_json()['command']
    match command:
        case 'init':
            LinkSet.add(Config.URL)
            # LinkTree.add(Config.URL)
        case 'ping':
            CrawlerPool.add(request.remote_addr)
        case 'halt':
            Panel.halt()
    return jsonify({'': ''})


@app.route('/<path:filename>', methods=['GET'])
def file(filename):
    return send_from_directory(Config.WEB_FILE_PATH, filename)


@app.route('/statu', methods=['GET'])
def statu():  # 前端监视所需状态
    left, right = Util.statu_format(list(CrawlerPool), LinkSet.slice())
    return jsonify({'left': left, 'right': right})


@app.after_request
def logs(response):  # 记录请求与响应
    Panel.info(request, response)
    return response


if __name__ == '__main__':
    # 运行服务器
    app.run(host=Config.HOST, port=Config.PORT, threaded=True)
