import json

from flask import Flask, request, jsonify
from threading import Lock

import Config

# 实例
app = Flask(__name__)
# 队列及集合
Visiting = set()
Visited = set()
# 限制
PageLimit = Config.PageLimit
# 锁
TLock = Lock()
ULock = Lock()


@app.route('/task', methods=['GET'])
def task():
    command, link = 'break', ''
    with TLock:
        while PageLimit > len(Visited):
            if len(Visiting):
                if (lnk := Visiting.pop()) not in Visited:
                    command, link = 'task', lnk
                    Visited.add(link)
                    break
            else:
                command, link = 'continue', ''
                break
    return jsonify({'command': command, 'link': link})


@app.route('/update', methods=['POST'])
def update():
    links = request.get_json()
    links = json.loads(links)['links']
    with ULock:
        for link in links:
            Visiting.add(link)
    return jsonify({'command': 'continue'})


if __name__ == '__main__':
    Visiting.add(Config.URL)
    app.run(host=Config.HOST, port=Config.PORT, threaded=True)
