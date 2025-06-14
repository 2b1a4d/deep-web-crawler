// 按钮控制监视器
let monitorInterval = null;
document.addEventListener('DOMContentLoaded', function () {
    // 事件绑定
    document.getElementById('start-btn').addEventListener('click', startRequest);
    document.getElementById('pause-btn').addEventListener('click', pauseRequest);
    document.getElementById('pause-btn').disabled = true;
});

// 开始监视
function startRequest() {
    document.getElementById('monitor').textContent = '监视已开启';
    document.getElementById('start-btn').disabled = true;
    document.getElementById('pause-btn').disabled = false;
    // 计时器请求
    monitorInterval = setInterval(getStatu, 1000); // 单位毫秒
}

// 停止监视
function pauseRequest() {
    document.getElementById('monitor').textContent = '监视未开启';
    document.getElementById('start-btn').disabled = false;
    document.getElementById('pause-btn').disabled = true;
    // 清除计时器
    clearInterval(monitorInterval);
    monitorInterval = null;
}