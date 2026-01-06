from flask import Blueprint, render_template,  request, redirect, flash
from ..utils import db
from ..utils.STATUS_map import STATUS_MAP
from ..utils.products import products
import datetime
from ..utils.info import U

# 蓝图初始化
man = Blueprint('manage', __name__)

@man.route('/order/manage', methods=['GET', 'POST'])
def manage_order():
    # 检查登录状态
    if not U:
        return render_template("login.html", error="请先登录")
    role = U.get('role')
    # 管理员查询所有订单
    if role == 'admin':
        sql = """
            SELECT u.user_name, u.address, u.phone, o.* 
            FROM `order` o 
            JOIN user u ON o.user_id = u.id
        """
        orders = db.fetchall(sql, [])
        return render_template(
            "admin_manage.html", 
            status_map=STATUS_MAP, 
            orders=orders or [], 
            user=U, 
            products=products
        )
    # 普通用户查询自己的订单
    else:
        sql = """
            SELECT u.user_name, u.address, u.phone, o.* 
            FROM `order` o 
            JOIN user u ON o.user_id = u.id
            WHERE o.user_id = %s
        """
        orders = db.fetchall(sql, [U['id']])
        return render_template(
            "user_manage.html", 
            status_map=STATUS_MAP, 
            orders=orders or [], 
            user=U, 
            products=products
        )

@man.route('/order/manage/update', methods=['POST'])
def admin_update():
    # 权限校验
    if not U:
        return render_template("login.html", error="请先登录")
    role = U.get('role')
    if role != 'admin':
        return render_template("login.html", error="您没有权限更新订单")

    data = request.form
    allowed_fields = ['status', 'products_id', 'count']
    update_fields = {k: v for k, v in data.items() if k in allowed_fields and v}

    # 验证更新字段
    if not update_fields:
        flash("未提供有效更新字段！", "error")
        return redirect("/order/manage")

    try:
        # 使用上下文管理器自动释放连接
        with db.manage_order() as (conn, cursor):
            set_clause = ', '.join([f"{k}=%s" for k in update_fields.keys()])
            sql = f"UPDATE `order` SET {set_clause} WHERE id=%s"
            cursor.execute(sql, list(update_fields.values()) + [data['id']])
            conn.commit()
        flash("订单更新成功！", "success")
    except Exception as e:
        flash(f"更新失败：{str(e)}", "error")  # 捕获具体错误信息
    return redirect("/order/manage")

@man.route('/order/manage/create', methods=['GET', 'POST'])
def admin_create():
    # 权限校验
    if not U:
        return render_template("login.html", error="请先登录")
    role = U.get('role')
    if role != 'admin':
        return render_template("login.html", error="您没有权限创建订单")
    
    if request.method == 'GET':
        return render_template("create_order.html", user=U)

    # 表单数据处理
    user_id = request.form.get('user_id')
    products_id = request.form.get('products_name')
    count = request.form.get('count')
    status = request.form.get('status', 1)  # 默认状态1
    buy_time = request.form.get('buy_time') or datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 基础验证
    if not all([user_id, products_id, count]):
        flash("用户ID、产品ID和数量为必填项！", "error")
        return render_template("create_order.html", user=U)

    try:
        with db.manage_order() as (conn, cursor):
            sql = """
                INSERT INTO `order` (user_id, products_id, count, status, buy_time)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, [user_id, products_id, count, status, buy_time])
            conn.commit()
        flash("订单创建成功！", "success")
    except Exception as e:
        flash(f"创建失败：{str(e)}", "error")
    return redirect("/order/manage")

@man.route('/order/manage/delete', methods=['GET', 'POST'])
def admin_delete():
    # 权限校验
    if not U:
        return render_template("login.html", error="请先登录")
    role = U.get('role')
    if role != 'admin':
        return render_template("login.html", error="您没有权限删除订单")

    if request.method == 'GET':
        return render_template("delete_order.html", user=U)

    data = request.form
    # 验证订单ID
    if 'id' not in data or not data['id'].isdigit():
        flash("无效的订单ID！", "error")
        return redirect("/order/manage")

    try:
        with db.manage_order() as (conn, cursor):
            sql = "DELETE FROM `order` WHERE id=%s"
            cursor.execute(sql, [data['id']])
            conn.commit()
        flash("订单删除成功！", "success")
    except Exception as e:
        flash(f"删除失败：{str(e)}", "error")
    return redirect("/order/manage")

@man.route('/order/manage/submit', methods=['GET', 'POST'])
def user_submit():
    # 权限校验
    if not U:
        return render_template("login.html", error="请先登录")
    role = U.get('role')
    if role != 'user':
        return render_template("login.html", error="您没有权限提交订单")

    if request.method == 'GET':
        return render_template("submit_order.html", user=U)

    # 表单数据处理
    products_id = request.form.get('products_id')
    count = request.form.get('count')
    if not all([products_id, count]):
        flash("产品ID和数量为必填项！", "error")
        return render_template("submit_order.html", user=U)

    buy_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        # 统一数据库操作方式（与其他接口保持一致）
        with db.manage_order() as (conn, cursor):
            sql = """
                INSERT INTO `order`(user_id, products_id, count, buy_time, status)
                VALUES (%s, %s, %s, %s, 1)
            """
            cursor.execute(sql, [U['id'], products_id, count, buy_time])
            conn.commit()
        flash("订单提交成功！", "success")
    except Exception as e:
        flash(f"提交失败：{str(e)}", "error")
    return redirect("/order/manage")

@man.route('/order/manage/cancel', methods=['GET', 'POST'])
def user_cancel():
    # 权限校验
    if not U:
        return render_template("login.html", error="请先登录")
    role = U.get('role')
    if role != 'user':
        return render_template("login.html", error="您没有权限取消订单")

    if request.method == 'GET':
        return redirect("/order/manage")

    data = request.form
    # 验证订单ID
    if 'id' not in data or not data['id'].isdigit():
        flash("无效的订单ID！", "error")
        return redirect("/order/manage")

    try:
        with db.manage_order() as (conn, cursor):
            sql = "DELETE FROM `order` WHERE id=%s AND user_id=%s"
            cursor.execute(sql, [data['id'], U['id']])
            conn.commit()
        flash("订单取消成功！", "success")
    except Exception as e:
        flash(f"取消失败：{str(e)}", "error")
    return redirect("/order/manage")

