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
              AND o.status != 5  # 排除未付款订单
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



@ana.route('/analyse')
def show_analyse():
    user = session.get('user')
    if not user or user.get('role') != 'admin':
        return render_template("login.html", error="无权限访问，需管理员登录")
    return render_template("profit.html")


@ana.route('/analyse/weekly')
def weekly_analyse():
    return query_profit('week')


@ana.route('/analyse/onemonth')
def one_month_analyse():  
    return query_profit('month')


@ana.route('/analyse/monthly')
def yearly_analyse(): 
    return query_profit('year')