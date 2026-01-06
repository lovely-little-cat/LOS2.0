from flask import Blueprint, render_template, session
from ..utils import db
from ..utils.products import products
from ..utils.STATUS_map import STATUS_MAP


ord = Blueprint('order', __name__)

@ord.route('order/list/user')
def show_user_list():
    if session.get('user'):
        user = session['user']
        role = user.get['role']
        if role != 'admin':
            return render_template("login.html",error="无权限！")
        return render_template("user_list.html",success="请查看用户列表")
    


@ord.route('/order/list')
def show_order_list(): 
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
            return render_template("admin/order_list.html", orders=orders, status_map=STATUS_MAP,products=products)
        else:
            sql = """
                SELECT u.user_name, u.address, u.phone, o.* 
                FROM `order` o 
                JOIN user u ON o.user_id = u.id
                WHERE o.user_id=%s
            """
            orders = db.fetchall(sql, [user['id']])
        
        return render_template("user/user_order_list.html", orders=orders, status_map=STATUS_MAP,products=products)

    else:
        return render_template("login.html", error="请先登录")




