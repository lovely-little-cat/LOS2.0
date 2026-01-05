from flask import Blueprint, render_template, session
from ..utils import db
from ..utils.STATUS_map import STATUS_MAP
from ..utils.products import products

ind = Blueprint('index', __name__)

@ind.route('/')
def index():
    # 获取当前登录用户信息，增加空值判断
    user = session.get('user')
    if not user:
        # 若未获取到用户信息，可根据实际需求处理（如重定向到登录页）
        return render_template("index.html", user=None, orders=[], 
                              status_map=STATUS_MAP, products=products)


    role = user.get('role')
    if role == 'admin':

        sql = """
            SELECT 
                u.user_name, 
                u.address, 
                u.phone,  
                o.* 
            FROM `order` o  
            JOIN user u ON o.user_id = u.id
        """
        orders = db.fetchall(sql, [])
    else:
        # 普通用户仅查询自己的订单
        sql = """
            SELECT 
                u.user_name, 
                u.address, 
                u.phone, 
                o.* 
            FROM `order` o 
            JOIN user u ON o.user_id = u.id
            WHERE o.user_id = %s
        """
        orders = db.fetchall(sql, [user['id']])

    # 统一渲染模板，减少代码冗余
    return render_template(
        "index.html",
        user=user,
        orders=orders or [],  # 确保orders始终为可迭代对象
        status_map=STATUS_MAP,
        products=products
    )