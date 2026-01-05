// order_modle.js
function addProductOptions() {
    const select = document.querySelector('select[name="products_name"]');
    // 假设通过后端接口获取商品列表，或直接在前端定义（与products.py保持一致）
    const products = {1: "雨伞", 2: "雨帽", 3: "雨靴", 4: "雨衣", 5: "雨水"};
    select.innerHTML = ''; // 清空现有选项
    for (const [id, name] of Object.entries(products)) {
        const option = document.createElement('option');
        option.value = id;
        option.textContent = name;
        select.appendChild(option);
    }
}