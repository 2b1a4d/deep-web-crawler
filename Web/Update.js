// 获取系统状态
function getStatu() {
    fetch('/statu')
        .then(res => res.ok ? res.json() : Promise.reject(res.status))
        .then(updatePage)  // 更新页面
        .catch(err => console.error('Request Error:', err));
}

// 更新监视页面
function updatePage(data) {
    updateLeft(data)
    updateRight(data)
}

// 更新系统从机状态
function updateLeft(data) {
    // 更新左侧列表
    const leftContainer = document.getElementById('left-container');
    const leftList = leftContainer.querySelector('ul');
    leftList.innerHTML = ''; // 清空现有内容
    data.left.forEach(item => {
        const li = document.createElement('li');
        li.innerHTML = `<span>${item.name}</span><span>${item.num}</span>`;
        leftList.appendChild(li);
    });
}

// 更新系统任务切片
function updateRight(data) {
    // 更新右侧列表
    const rightContainer = document.getElementById('right-container');
    const rightList = rightContainer.querySelector('ul');
    rightList.innerHTML = ''; // 清空现有内容
    data.right.forEach(item => {
        const li = document.createElement('li');
        li.textContent = item;
        rightList.appendChild(li);
    });
}