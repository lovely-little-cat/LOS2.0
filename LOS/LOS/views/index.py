from flask import Blueprint, render_template, session
from ..utils import db
from ..utils.STATUS_map import STATUS_MAP
from ..utils.products import products

ind = Blueprint('index', __name__)

@ind.route('/')
def index():
    user = session.get('user')
    if not user:
        return render_template("login.html", user=None, orders=[], 
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
        return render_template(
            "admin/index.html",
            user=user,
            orders=orders or [], 
            status_map=STATUS_MAP,
            products=products
        )
    else:
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
        return render_template(
            "user/user_index.html",
            user=user,
            orders=orders or [], 
            status_map=STATUS_MAP,
            products=products
        )

