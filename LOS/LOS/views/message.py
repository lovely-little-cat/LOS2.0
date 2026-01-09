from flask import Blueprint, render_template, request, redirect, url_for, session
from ..utils import db


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
            SELECT m.id , m.user_id, m.message,  u.user_name,m.time
            FROM message m 
            JOIN user u ON m.user_id = u.id
        """
        messages = db.fetchall(sql, [])
    else:
        sql = """
            SELECT m.id , m.user_id, m.message,  u.user_name,m.time
            FROM message m 
            JOIN user u ON m.user_id = u.id
            WHERE m.user_id=%s
        """
        messages = db.fetchall(sql, [user['id']])
    
    return render_template("admin/message_list.html", messages=messages or [])

@mes.route('/message/submit', methods=['GET', 'POST'])
def submit_message():
    user = session.get('user')
    if not user:
        return render_template("login.html", error="请先登录")
    
    if request.method == 'GET':
        return render_template("user/submit_message.html", user=user)
    
    data = request.form
    message = data.get('message', '').strip()
    # 验证消息
    if not message:
        return render_template("user_message.html", user=user, error="消息内容不能为空！")
    if len(message) > 100:
        return render_template("user_message.html", user=user, error="消息长度不能超过100个字符！")
    
@mes.route('/message/receive', methods=['GET'])
def receive_message():
    user = session.get('user')
    if not user:
        return render_template("login.html", error="请先登录")
    
    # 查询数据库数据（复用权限逻辑）
    role = user.get('role')
    if role == 'admin':
        sql = """
            SELECT m.id , m.user_id, m.message,  u.user_name,m.time
            FROM message m 
            JOIN user u ON m.user_id = u.id
        """
        messages = db.fetchall(sql, [])
        return render_template("admin/message.html", messages=messages or [])
    
    return render_template("login.html", error="您没有权限查看消息")
