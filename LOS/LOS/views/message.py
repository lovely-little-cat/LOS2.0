from flask import Blueprint, render_template, request, redirect, url_for, session
from LOS import db


mes = Blueprint('message', __name__)

@mes.route('/message')
def show_message_list():
    user = session.get('user')
    if not user:
        return render_template("login.html", error="请先登录")
    
    # 查询数据库数据（复用权限逻辑）
    role = user.get('role')
    if role == 'admin':
        sql = """
            SELECT m.id as message_id, m.user_id, m.content, m.status, u.user_name
            FROM message m 
            JOIN user u ON m.user_id = u.id
        """
        messages = db.fetchall(sql, [])
    else:
        sql = """
            SELECT m.id as message_id, m.user_id, m.content, m.status, u.user_name
            FROM message m 
            JOIN user u ON m.user_id = u.id
            WHERE m.user_id=%s
        """
        messages = db.fetchall(sql, [user['id']])
    
    return render_template("message_list.html", messages=messages)