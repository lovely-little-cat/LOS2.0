// 填充更新表单的订单ID和当前状态
function fillUpdateForm(orderId) {
    // 获取订单当前状态
    const statusSelect = document.getElementById(orderId);
    const currentStatus = statusSelect.value;
    // 填充更新表单
    const updateForm = document.querySelector('.order-form');
    updateForm.querySelector('input[name="id"]').value = orderId;
    updateForm.querySelector('select[name="status"]').value = currentStatus;
}

// 刷新订单列表（重新加载页面）
function refreshBtn() {
    window.location.reload();
}

// 可选：异步更新订单（优化用户体验）
async function updateOrderAsync(orderId) {
    const status = document.getElementById(orderId).value;
    try {
        const res = await fetch('/order/manage/update', {
            method: 'POST',
            headers: {'Content-Type': 'application/x-www-form-urlencoded'},
            body: `id=${orderId}&status=${status}`
        });
        if (res.ok) {
            alert('更新成功！');
            refreshBtn();
        } else {
            alert('更新失败！');
        }
    } catch (e) {
        alert('更新异常：' + e.message);
    }
}