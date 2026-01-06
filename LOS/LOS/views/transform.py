from flask import  render_template, session, Blueprint, make_response
from ..utils import db
from io import BytesIO
from openpyxl import Workbook
from urllib.parse import quote
from ..utils.STATUS_map import STATUS_MAP



tra = Blueprint('transform', __name__)

@tra.route('/transform/user',method=['GET','POST'])
def transform_user():
    use = session.get('user')
    if not use:
        return render_template("login.html", error="请先登录")
    role = use.get('role')
    if role != 'user':
        return render_template("login.html", error="您没有权限访问")
    sql = """
        SELECT u.user_name, u.address, u.phone, o.* 
        FROM `order` o 
        JOIN user u ON o.user_id = u.id
        WHERE o.user_id=%s
    """
    orders = db.fetchall(sql, [use['id']])
    wb = Workbook()
    ws = wb.active
    ws.title = "用户订单数据"
    headers = ["用户名", "地址", "电话", "订单ID", "用户ID", "商品ID", "数量", "订单状态"]
    ws.append(headers)
    for order in orders:
        ws.append([
            order['user_name'],
            order['address'],
            order['phone'],
            order['id'],
            order['user_id'],
            order['products_id'],
            order['count'],
            STATUS_MAP.get(order['status'], "未知状态")
        ])
    # 生成下载响应
    output = BytesIO()
    wb.save(output)
    output.seek(0)  # 重置文件指针到开头
     
    filename = "用户订单数据.xlsx"
    encoded_filename = quote(filename, encoding='utf-8')
    response = make_response(output.getvalue())
    # 使用UTF-8编码声明文件名
    response.headers["Content-Disposition"] = f"attachment; filename*=UTF-8''{encoded_filename}"
    response.headers["Content-Type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    return response



@tra.route('/transform/order')
def export_transform_excel():
    use = session.get('user')
    if not use:
        return render_template("login.html", error="请先登录")
    role = use.get('role')
    if role == 'admin':
        sql = """
            SELECT u.user_name, u.address, u.phone, o.* 
            FROM `order` o 
            JOIN user u ON o.user_id = u.id
        """
        orders = db.fetchall(sql, [])
    else:
        sql = """
            SELECT u.user_name, u.address, u.phone, o.* 
            FROM `order` o 
            JOIN user u ON o.user_id = u.id
            WHERE o.user_id=%s
        """
        orders = db.fetchall(sql, [use['id']])
    wb = Workbook()
    ws = wb.active
    ws.title = "订单数据"
    headers = ["用户名", "地址", "电话", "订单ID", "用户ID", "商品ID", "数量", "订单状态"]
    ws.append(headers)
    for order in orders:
        ws.append([
            order['user_name'],
            order['address'],
            order['phone'],
            order['id'],
            order['user_id'],
            order['products_id'],
            order['count'],
            STATUS_MAP.get(order['status'], "未知状态")
        ])
    # 生成下载响应
    output = BytesIO()
    wb.save(output)
    output.seek(0)  # 重置文件指针到开头
     
    filename = "订单数据.xlsx"
    encoded_filename = quote(filename, encoding='utf-8')
    response = make_response(output.getvalue())
    # 使用UTF-8编码声明文件名
    response.headers["Content-Disposition"] = f"attachment; filename*=UTF-8''{encoded_filename}"
    response.headers["Content-Type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    return response

@tra.route('/transform/order/price')
def transform_order_price():
    use = session.get('user')
    if not use:
        return render_template("login.html", error="请先登录")
    
    role = use.get('role')
    if role == 'admin':
        sql = """
            SELECT u.user_name, u.address, u.phone, o.* 
            FROM `order` o 
            JOIN user u ON o.user_id = u.id
        """
        orders = db.fetchall(sql, [])
    else:
        sql = """
            SELECT u.user_name, u.address, u.phone, o.* 
            FROM `order` o 
            JOIN user u ON o.user_id = u.id
            WHERE o.user_id=%s
        """
        orders = db.fetchall(sql, [use['id']])
    wb = Workbook()
    ws = wb.active
    ws.title = "订单数据"
    headers = ["用户名", "地址", "电话", "订单ID", "用户ID", "商品ID", "数量", "订单状态"]
    ws.append(headers)
    for order in orders:
        ws.append([
            order['user_name'],
            order['address'],
            order['phone'],
            order['id'],
            order['user_id'],
            order['products_id'],
            order['count'],
            STATUS_MAP.get(order['status'], "未知状态")
        ])
    # 生成下载响应
    output = BytesIO()
    wb.save(output)
    output.seek(0)  # 重置文件指针到开头
     
    filename = "用户订单数据.xlsx"
    encoded_filename = quote(filename, encoding='utf-8')
    response = make_response(output.getvalue())
    # 使用UTF-8编码声明文件名
    response.headers["Content-Disposition"] = f"attachment; filename*=UTF-8''{encoded_filename}"
    response.headers["Content-Type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    return response


