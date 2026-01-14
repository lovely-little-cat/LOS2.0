from flask import Blueprint, render_template,  request, redirect, flash, session
from ..utils import db
from ..utils.STATUS_map import STATUS_MAP
from ..utils.products import products
import datetime


man = Blueprint('manage', __name__)

@man.route('/order/manage', methods=['GET', 'POST'])
def manage_order():
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
        return render_template(
            "admin/admin_manage.html", 
            status_map=STATUS_MAP, 
            orders=orders or [], 
            user=use, 
            products=products
        )

    else:
        sql = """
            SELECT u.user_name, u.address, u.phone, o.* 
            FROM `order` o 
            JOIN user u ON o.user_id = u.id
            WHERE o.user_id = %s
        """
        orders = db.fetchall(sql, [use['id']])
        return render_template(
            "user/user_manage.html", 
            status_map=STATUS_MAP, 
            orders=orders or [], 
            user=use, 
            products=products
        )

@man.route('/order/manage/update', methods=['POST'])
def admin_update():
    use = session.get('user')

    if not use:
        return render_template("login.html", error="请先登录")
    role = use.get('role')
    if role != 'admin':
        return render_template("login.html", error="您没有权限更新订单")

    data = request.form
    allowed_fields = ['status', 'products_id', 'count']
    update_fields = {k: v for k, v in data.items() if k in allowed_fields and v}


    if not update_fields:
        flash("未提供有效更新字段！", "error")
        return redirect("/order/manage")

    try:

        with db.manage_order() as (conn, cursor):
            set_clause = ', '.join([f"{k}=%s" for k in update_fields.keys()])
            sql = f"UPDATE `order` SET {set_clause} WHERE id=%s"
            cursor.execute(sql, list(update_fields.values()) + [data['id']])
            conn.commit()
        flash("订单更新成功！", "success")
    except Exception as e:
        flash(f"更新失败：{str(e)}", "error") 
    return redirect("/order/manage")

@man.route('/order/manage/create', methods=['GET', 'POST'])
def admin_create():

    use = session.get('user')
    if not use or use.get('role') != 'admin':
        return render_template("login.html", error="无权限创建订单")
    
    if request.method == 'GET':
        return render_template("admin/create_order.html", user=use)


    try:
        user_id = int(request.form.get('user_id'))
        products_id = int(request.form.get('products_name'))
        count = int(request.form.get('count'))
        status = int(request.form.get('status', 1))
        buy_time = request.form.get('buy_time') or datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        flash("用户ID/产品ID/数量必须为整数！", "error")
        return render_template("admin/create_order.html", user=use)


    if not all([user_id, products_id, count]) or count <= 0:
        flash("用户ID、产品ID为必填项，数量必须为正整数！", "error")
        return render_template("admin/create_order.html", user=use)


    try:

        sql_stock = "SELECT p.stock FROM price WHERE products_id = %s"
        stock_res = db.fetchone(sql_stock, [products_id])
        if not stock_res:
            flash("产品不存在！", "error")
            return render_template("admin/create_order.html", user=use)
        stock_now = int(stock_res[0])
        if count > stock_now:
            flash(f"库存不足！当前库存：{stock_now}", "error")
            return render_template("admin/create_order.html", user=use)

        with db.manage_order() as (conn, cursor):

            sql_insert = """
                INSERT INTO `order` (user_id, products_id, count, status, buy_time)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql_insert, [user_id, products_id, count, status, buy_time])

            sql_update_stock = "UPDATE price SET stock = stock - %s WHERE products_id = %s"
            cursor.execute(sql_update_stock, [count, products_id])
            conn.commit()
        flash("订单创建成功！", "success")
    except Exception as e:
        flash(f"创建失败：{str(e)}", "error")
    return redirect("/order/manage")

@man.route('/order/manage/delete', methods=['GET', 'POST'])
def admin_delete():
    use = session.get('user')

    if not use:
        return render_template("login.html", error="请先登录")
    role = use.get('role')
    if role != 'admin':
        return render_template("login.html", error="您没有权限删除订单")

    if request.method == 'GET':
        return render_template("admin/delete_order.html", user=use)



    data = request.form

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

    use = session.get('user')
    if not use:
        return render_template("login.html", error="请先登录")
    role = use.get('role')
    if role != 'user':
        return render_template("login.html", error="您没有权限提交订单")

    if request.method == 'GET':
        return render_template("user/submit_order.html", user=use)


    products_id = request.form.get('products_id')
    count = request.form.get('count')
    if not all([products_id, count]):
        flash("产品ID和数量为必填项！", "error")
        return render_template("user/submit_order.html", user=use)

    buy_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:

        with db.manage_order() as (conn, cursor):
            sql = """
                INSERT INTO `order`(user_id, products_id, count, buy_time, status)
                VALUES (%s, %s, %s, %s, 1)
            """
            cursor.execute(sql, [use['id'], products_id, count, buy_time])
            conn.commit()
        flash("订单提交成功！", "success")
    except Exception as e:
        flash(f"提交失败：{str(e)}", "error")
    return redirect("/order/manage")

@man.route('/order/manage/cancel', methods=['GET', 'POST'])
def user_cancel():

    use = session.get('user')
    if not use:
        return render_template("login.html", error="请先登录")
    role = use.get('role')
    if role != 'user':
        return render_template("login.html", error="您没有权限取消订单")

    if request.method == 'GET':
        return redirect("/order/manage")

    data = request.form

    if 'id' not in data or not data['id'].isdigit():
        flash("无效的订单ID！", "error")
        return redirect("/order/manage")

    try:
        with db.manage_order() as (conn, cursor):
            sql = "DELETE FROM `order` WHERE id=%s AND user_id=%s"
            cursor.execute(sql, [data['id'], use['id']])
            conn.commit()
        flash("订单取消成功！", "success")
    except Exception as e:
        flash(f"取消失败：{str(e)}", "error")
    return redirect("/order/manage")

