
function fillUpdateForm(orderId) {

    const statusSelect = document.getElementById(orderId);
    const currentStatus = statusSelect.value;

    const updateForm = document.querySelector('.order-form');
    updateForm.querySelector('input[name="id"]').value = orderId;
    updateForm.querySelector('select[name="status"]').value = currentStatus;
}


function refreshBtn() {
    window.location.reload();
}


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