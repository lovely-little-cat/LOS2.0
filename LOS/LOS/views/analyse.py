from flask import jsonify, render_template, session, Blueprint
from ..utils import db
from datetime import datetime, timedelta
import pytz
from dateutil.relativedelta import relativedelta  


ana = Blueprint('analyse', __name__)

local_tz = pytz.timezone('Asia/Shanghai')

def insertion_sort(arr, key, reverse=False):
    """
    插入排序实现
    :param arr: 待排序数组
    :param key: 排序依据的字段（如 'sell'/'stock'/'recommend_priority'）
    :param reverse: 是否降序（默认升序）
    :return: 排序后的数组
    """
    for i in range(1, len(arr)):
        current_item = arr[i]
        j = i - 1
        while j >= 0 and (
            (reverse and arr[j][key] < current_item[key]) or
            (not reverse and arr[j][key] > current_item[key])
        ):
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = current_item
    return arr

def check_admin_permission():
    user = session.get('user')
    if not user or user.get('role') != 'admin':
        return jsonify({"error": "无权限访问"}), 403
    return None  

def recommend_sort(price_data, min_stock=100):
    """
    插入排序：优先补货「缺货程度×销量」高的商品
    :param price_data: 商品库存/销量数据
    :param min_stock: 库存预警阈值
    :return: 排序后数据 + 补货列表
    """
    for item in price_data:
        stock = item.get('stock', 0)
        sell = item.get('sell', 0)
        shortage_degree = 1 - (stock / min_stock) if stock > 0 else 1
        item['recommend_priority'] = round(shortage_degree * sell, 2)
        item['need_restock'] = stock <= min_stock

    sorted_data = insertion_sort(price_data.copy(), 'recommend_priority', reverse=True)
    
    restock_list = insertion_sort(
        [item for item in sorted_data if item['need_restock']],
        'recommend_priority',
        reverse=True
    )
    restock_list = [
        {
            'products_id': item['products_id'],
            'current_stock': item['stock'],
            'sell_volume': item['sell'],
            'priority': item['recommend_priority']
        }
        for item in restock_list
    ]
    return sorted_data, restock_list

def sort_by_sell_desc(price_data):
    """按销量从高到低排序（插入排序）"""
    return insertion_sort(price_data.copy(), 'sell', reverse=True)

def sort_by_stock_desc(price_data):
    """按库存从高到低排序（插入排序）"""
    return insertion_sort(price_data.copy(), 'stock', reverse=True)

def dict_ss():
    sql = """
        SELECT products_id, stock, sell, products_price, cost
        FROM price
    """
    try:
        price_data = db.fetchall(sql, [])
        if not price_data:
            return jsonify({"error": "查询失败：无数据", "status": "error"}), 500
        
        sorted_price, restock_list = recommend_sort(price_data, min_stock=20)
        sorted_by_sell = sort_by_sell_desc(price_data)
        sorted_by_stock = sort_by_stock_desc(price_data)
        
        price_dict = {
            item['products_id']: {
                'stock': item['stock'],
                'sell': item['sell'],
                'products_price': item['products_price'],
                'cost': item['cost'],
                'recommend_priority': item.get('recommend_priority', 0),
                'need_restock': item.get('need_restock', False)
            }
            for item in price_data
        }
        
        sell_max = max(price_dict.items(), key=lambda x: x[1]['sell'])[0] if price_dict else None
        
        return {
            'price_dict': price_dict,
            'sell_max': sell_max,
            'restock_list': restock_list, 
            'sorted_price': sorted_price, 
            'sorted_by_sell': sorted_by_sell,  
            'sorted_by_stock': sorted_by_stock,
            'min_stock': 100  
        }
    except Exception as e:
        return jsonify({"error": f"查询失败：{str(e)}", "status": "error"}), 500

def get_time_range(period):
    end_date = datetime.now(local_tz).replace(hour=23, minute=59, second=59)
    if period == 'week':
        start_date = end_date - timedelta(days=6)
        date_format = '%%m-%%d'  
    elif period == 'month':
        start_date = end_date - timedelta(days=30)
        date_format = '%%Y-%%m-%%d' 
    elif period == 'year':
        start_date = end_date - relativedelta(months=12)  
        date_format = '%%Y-%%m'  
    else:
        raise ValueError("不支持的时间周期")
    
    start_utc = start_date.astimezone(pytz.UTC)
    end_utc = end_date.astimezone(pytz.UTC)
    return start_utc, end_utc, date_format

def query_profit(period):
    permission_error = check_admin_permission()
    if permission_error:
        return permission_error
    
    try:
        start_utc, end_utc, date_format = get_time_range(period)
        sql = f"""
            SELECT 
                DATE_FORMAT(o.buy_time, '{date_format}') as time_key,
                SUM((p.products_price - p.cost) * o.count) as profit
            FROM `order` o
            LEFT JOIN price p ON o.products_id = p.products_id
            WHERE o.buy_time BETWEEN %s AND %s
              AND o.status != 5  
            GROUP BY time_key
            ORDER BY time_key
        """
        profits = db.fetchall(
            sql, 
            [start_utc.strftime("%Y-%m-%d %H:%M:%S"), 
             end_utc.strftime("%Y-%m-%d %H:%M:%S")]
        )
        return jsonify({"data": profits, "status": "success"})  
    except Exception as e:
        return jsonify({"error": f"查询失败：{str(e)}", "status": "error"}), 500

@ana.route('/analyse/stock_sell')
def ss_analyse():
    permission_error = check_admin_permission()
    if permission_error:
        return permission_error
    
    result = dict_ss()
    if isinstance(result,tuple) and len(result)==2 and isinstance(result[1],int):
        return result
    
    return jsonify({
        'price_dict': result['price_dict'],
        'sell_max': result['sell_max'],
        'restock_list': result['restock_list'],  
        'sorted_price': result['sorted_price'], 
        'sorted_by_sell': result['sorted_by_sell'], 
        'sorted_by_stock': result['sorted_by_stock'], 
        'min_stock': result['min_stock'],  
        "status": "success"
    })

@ana.route('/analyse')
def show_analyse():
    user = session.get('user')
    if not user or user.get('role') != 'admin':
        return render_template("login.html", error="无权限访问，需管理员登录")
    return render_template("admin/profit.html")

@ana.route('/analyse/weekly')
def weekly_analyse():
    return query_profit('week')

@ana.route('/analyse/onemonth')
def one_month_analyse():  
    return query_profit('month')

@ana.route('/analyse/monthly')
def yearly_analyse(): 
    return query_profit('year')