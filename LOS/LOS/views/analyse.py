from flask import jsonify, render_template, session, Blueprint
from ..utils import db
from datetime import datetime, timedelta
import pytz
from dateutil.relativedelta import relativedelta  


ana = Blueprint('analyse', __name__)




local_tz = pytz.timezone('Asia/Shanghai')



def check_admin_permission():
    user = session.get('user')
    if not user or user.get('role') != 'admin':
        return jsonify({"error": "无权限访问"}), 403
    return None  

def insert_sort(price,key='sell',order='desc'):
    for i in range(1, len(price)):
        key = price[i]
        j = i - 1
        while j >= 0 and (key['sell'] > price[j]['sell'] if order == 'desc' else key['sell'] < price[j]['sell']):
            price[j + 1] = price[j]
            j -= 1
        price[j + 1] = key
    return price



def dict_ss():
    sql = """
        SELECT products_id, stock, sell
        FROM price
    """
    try:
        price_data = db.fetchall(sql, [])
        if not price_data:
            return jsonify({"error": "查询失败：无数据", "status": "error"}), 500
        price_dict = {
            item['products_id']: {
                'stock': item['stock'],
                'sell': item['sell']
            }

            for item in price_data
            
                
        }
        if price_dict:
            sell_max = max(price_dict.items(), 
                       key=lambda x: x[1]['sell'])[0]
        else:
            sell_max = None
        stock_shortage = [
            pdt_id for pdt_id, values in price_dict.items()
            if values['stock'] <= 10
            
        ]
        sorted_price = insert_sort(price_data.copy(), key='sell', order='desc')
        return {
            'price_dict': price_dict,
            'sell_max': sell_max,
            'stock_shortage': stock_shortage,
            'sorted_price': sorted_price
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
        date_format = '%%m-%%d' 
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

        return jsonify({"data": profits, "status": "4"})
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
        'stock_shortage': result['stock_shortage'],
        'sorted_price': result['sorted_price'],
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

@ana.route('/analyse/stock_sell')
def stock_sell_analyse():
    permission_error = check_admin_permission()
    if permission_error:
        return permission_error
    #插入排序，倒序sell
    try:
        sql ="""
            SELECT products_id, stock, sell
            FROM price
        """
        price_data = db.fetchall(sql, [])
        price_dict = insert_sort(price_data, key='sell', order='desc')
        
    except Exception as e:
        return jsonify({"error": f"查询失败：{str(e)}", "status": "error"}), 500


    return dict_ss(),price_dict 
