
function addProductOptions() {
    const select = document.querySelector('select[name="products_name"]');
    const products = {1: "雨伞", 2: "雨帽", 3: "雨靴", 4: "雨衣", 5: "雨水"};
    select.innerHTML = ''; 
    for (const [id, name] of Object.entries(products)) {
        const option = document.createElement('option');
        option.value = id;
        option.textContent = name;
        select.appendChild(option);
    }
}