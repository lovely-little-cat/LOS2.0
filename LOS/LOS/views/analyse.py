from flask import jsonify, render_template, session, Blueprint
from ..utils import db
from datetime import datetime, timedelta
import pytz
from dateutil.relativedelta import relativedelta  


ana = Blueprint('analyse', __name__)
local_tz = pytz.timezone('Asia/Shanghai')


# 1. 提取公共权限校验函数
def check_admin_permission():
    user = session.get('user')
    if not user or user.get('role') != 'admin':
        return jsonify({"error": "无权限访问"}), 403
    return None  # 权限通过


# 2. 提取时间范围计算函数（支持周/月/年）
def get_time_range(period):
    end_date = datetime.now(local_tz).replace(hour=23, minute=59, second=59)
    if period == 'week':
        start_date = end_date - timedelta(days=6)
        date_format = '%%m-%%d'  # 月-日
    elif period == 'month':
        start_date = end_date - timedelta(days=30)
        date_format = '%%Y-%%m-%%d'  # 年-月-日
    elif period == 'year':
        start_date = end_date - relativedelta(months=12)  # 精准计算12个月
        date_format = '%%Y-%%m'  # 年-月
    else:
        raise ValueError("不支持的时间周期")
    
    # 统一时区转换
    start_utc = start_date.astimezone(pytz.UTC)
    end_utc = end_date.astimezone(pytz.UTC)
    return start_utc, end_utc, date_format


# 3. 提取公共查询函数
def query_profit(period):
    # 权限校验
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
        # 区分"无数据"和"查询成功但无结果"
        return jsonify({"data": profits, "status": "success"})
    except Exception as e:
        # 捕获异常并返回错误信息
        return jsonify({"error": f"查询失败：{str(e)}", "status": "error"}), 500


# 4. 精简接口实现
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
def one_month_analyse():  # 修正函数名
    return query_profit('month')


@ana.route('/analyse/monthly')
def yearly_analyse():  # 修正函数名（实际是12个月）
    return query_profit('year')