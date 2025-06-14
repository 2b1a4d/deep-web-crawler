// 按钮控制服务器
document.addEventListener('DOMContentLoaded', function () {
    // 事件绑定
    document.getElementById('init-btn').addEventListener('click', initTask);
    document.getElementById('logs-btn').addEventListener('click', getLogs);
    document.getElementById('halt-btn').addEventListener('click', haltSlave);
});

// 添加初始任务
function initTask() {
    document.getElementById('init-btn').disabled = true;
    // 发送请求
    fetch('/control', {
        method: 'PUT', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({'command': 'init'})
    })
        .catch(console.error);
}

// 下载运行日志
function getLogs() {
    // 发送请求
    fetch('/Log.txt')
        .then(response => response.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'Log.txt';
            a.click();
        });
}

// 中止从机任务
function haltSlave() {
    document.getElementById('halt-btn').disabled = true;
    // 发送请求
    fetch('/control', {
        method: 'PUT', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({'command': 'halt'})
    })
        .catch(console.error);
}