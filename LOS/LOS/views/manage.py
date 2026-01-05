from flask import Blueprint, render_template, session, request, redirect, flash
from ..utils import db
from ..utils.STATUS_map import STATUS_MAP
from ..utils.products import products
import datetime

# 蓝图初始化
man = Blueprint('manage', __name__)

def check_login():
    """检查用户是否登录，未登录返回登录页"""
    user = session.get('user')
    if not user:
        return render_template("login.html", error="请先登录")
    return user  

def check_admin(user):
    """检查是否为管理员，非管理员返回错误页"""
    if user.get('role') != 'admin':
        return render_template("login.html", error="权限不足，仅管理员可操作")
    return True

def check_user(user):
    """检查是否为普通用户，非普通用户返回错误页"""
    if user.get('role') != 'user':
        return render_template("login.html", error="权限不足，仅用户可操作")
    return True

def get_db_connection():
    """获取数据库连接和游标（使用上下文管理器自动释放资源）"""
    conn = db.Pool.connection()
    cursor = conn.cursor()
    return conn, cursor


@man.route('/order/manage', methods=['GET', 'POST'])
def manage_order():
    # 检查登录状态
    user = check_login()
    if isinstance(user, tuple):  # 未登录时返回的是模板响应
        return user

    role = user.get('role')
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
            user=user, 
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
        orders = db.fetchall(sql, [user['id']])
        return render_template(
            "user_manage.html", 
            status_map=STATUS_MAP, 
            orders=orders or [], 
            user=user, 
            products=products
        )

@man.route('/order/manage/update', methods=['POST'])
def admin_update():
    # 权限校验
    user = check_login()
    if isinstance(user, tuple):
        return user
    if not check_admin(user):
        return check_admin(user)

    data = request.form
    allowed_fields = ['status', 'products_id', 'count']
    update_fields = {k: v for k, v in data.items() if k in allowed_fields and v}

    # 验证更新字段
    if not update_fields:
        flash("未提供有效更新字段！", "error")
        return redirect("/order/manage")

    try:
        # 使用上下文管理器自动释放连接
        with get_db_connection() as (conn, cursor):
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
    user = check_login()
    if isinstance(user, tuple):
        return user
    if not check_admin(user):
        return check_admin(user)

    if request.method == 'GET':
        return render_template("create_order.html", user=user)

    # 表单数据处理
    user_id = request.form.get('user_id')
    products_id = request.form.get('products_name')
    count = request.form.get('count')
    status = request.form.get('status', 1)  # 默认状态1
    buy_time = request.form.get('buy_time') or datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 基础验证
    if not all([user_id, products_id, count]):
        flash("用户ID、产品ID和数量为必填项！", "error")
        return render_template("create_order.html", user=user)

    try:
        with get_db_connection() as (conn, cursor):
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
    user = check_login()
    if isinstance(user, tuple):
        return user
    if not check_admin(user):
        return check_admin(user)

    if request.method == 'GET':
        return render_template("delete_order.html", user=user)

    data = request.form
    # 验证订单ID
    if 'id' not in data or not data['id'].isdigit():
        flash("无效的订单ID！", "error")
        return redirect("/order/manage")

    try:
        with get_db_connection() as (conn, cursor):
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
    user = check_login()
    if isinstance(user, tuple):
        return user
    if not check_user(user):
        return check_user(user)

    if request.method == 'GET':
        return render_template("submit_order.html", user=user)

    # 表单数据处理
    products_id = request.form.get('products_id')
    count = request.form.get('count')
    if not all([products_id, count]):
        flash("产品ID和数量为必填项！", "error")
        return render_template("submit_order.html", user=user)

    buy_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        # 统一数据库操作方式（与其他接口保持一致）
        with get_db_connection() as (conn, cursor):
            sql = """
                INSERT INTO `order`(user_id, products_id, count, buy_time, status)
                VALUES (%s, %s, %s, %s, 1)
            """
            cursor.execute(sql, [user['id'], products_id, count, buy_time])
            conn.commit()
        flash("订单提交成功！", "success")
    except Exception as e:
        flash(f"提交失败：{str(e)}", "error")
    return redirect("/order/manage")

@man.route('/order/manage/cancel', methods=['GET', 'POST'])
def user_cancel():
    # 权限校验
    user = check_login()
    if isinstance(user, tuple):
        return user
    if not check_user(user):
        return check_user(user)

    if request.method == 'GET':
        return redirect("/order/manage")

    data = request.form
    # 验证订单ID
    if 'id' not in data or not data['id'].isdigit():
        flash("无效的订单ID！", "error")
        return redirect("/order/manage")

    try:
        with get_db_connection() as (conn, cursor):
            sql = "DELETE FROM `order` WHERE id=%s AND user_id=%s"
            cursor.execute(sql, [data['id'], user['id']])
            conn.commit()
        flash("订单取消成功！", "success")
    except Exception as e:
        flash(f"取消失败：{str(e)}", "error")
    return redirect("/order/manage")

@man.route('/order/manage/contact_admin', methods=['GET', 'POST'])
def contact_admin():
    # 权限校验
    user = check_login()
    if isinstance(user, tuple):
        return user
    if not check_user(user):
        return check_user(user)

    if request.method == 'GET':
        return render_template("user_index.html", user=user)

    data = request.form
    message = data.get('message', '').strip()
    # 验证消息
    if not message:
        flash("消息内容不能为空！", "error")
        return render_template("user_index.html", user=user)
    if len(message) > 100:
        flash("消息长度不能超过100个字符！", "error")
        return render_template("user_index.html", user=user)

    # 频率限制
    min_interval = 60  # 60秒间隔
    current_time = datetime.datetime.now()
    last_time_str = user.get('last_contact_time')
    
    if last_time_str:
        try:
            last_time = datetime.datetime.strptime(last_time_str, "%Y-%m-%d %H:%M:%S")
            if (current_time - last_time).seconds < min_interval:
                flash(f"请勿频繁发送消息，请{min_interval}秒后再试！", "error")
                return render_template("user_index.html", user=user)
        except ValueError:
            # 时间格式错误时忽略限制（兼容旧数据）
            pass

    # 保存消息
    time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
    try:
        with get_db_connection() as (conn, cursor):
            sql = "INSERT INTO `message`(user_id, message, time) VALUES (%s, %s, %s)"
            cursor.execute(sql, [user['id'], message, time_str])
            conn.commit()
        # 更新最后发送时间
        user['last_contact_time'] = time_str
        flash("消息发送成功！", "success")
    except Exception as e:
        flash(f"发送失败：{str(e)}", "error")
    return redirect("/order/manage")