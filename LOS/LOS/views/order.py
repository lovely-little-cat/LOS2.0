from flask import Blueprint, render_template, session, make_response, request

from io import BytesIO
from openpyxl import Workbook
from ..utils import db
from urllib.parse import quote
from ..utils.products import products
from ..utils.STATUS_map import STATUS_MAP


ord = Blueprint('order', __name__)

# 原订单列表路由（重命名函数名，避免冲突）
@ord.route('/order/list')
def show_order_list():  # 函数名从 order_list 改为 show_order_list
    if session.get('user'):
        user = session['user']
        role = user.get('role')
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
            orders = db.fetchall(sql, [user['id']])
        
        return render_template("order_list.html", orders=orders, status_map=STATUS_MAP,products=products)

    else:
        return render_template("login.html", error="请先登录")

# 新增Excel导出路由
@ord.route('/order/export')
def export_excel():
    user = session.get('user')
    if not user:
        return render_template("login.html", error="请先登录")
    
    # 查询数据库数据（复用权限逻辑）
    role = user.get('role')
    if role == 'admin':
        sql = """
            SELECT u.user_name, u.address, u.phone, o.id as order_id, 
                   o.user_id, o.products_id, o.count, o.status
            FROM `order` o 
            JOIN user u ON o.user_id = u.id
        """
        orders = db.fetchall(sql, [])
    else:
        sql = """
            SELECT u.user_name, u.address, u.phone, o.id as order_id, 
                   o.user_id, o.products_id, o.count, o.status
            FROM `order` o 
            JOIN user u ON o.user_id = u.id
            WHERE o.user_id=%s
        """
        orders = db.fetchall(sql, [user['id']])
    
    # 创建Excel文件
    wb = Workbook()
    ws = wb.active
    ws.title = "订单数据"
    
    # 写入表头
    headers = ["用户名", "地址", "电话", "订单ID", "用户ID", "商品ID", "数量", "订单状态"]
    ws.append(headers)
    
    # 写入数据行


    for order in orders:
        ws.append([
            order['user_name'],
            order['address'],
            order['phone'],
            order['order_id'],
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




