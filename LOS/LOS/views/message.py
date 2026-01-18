from flask import Blueprint, render_template, request, redirect, url_for, session
from ..utils import db
from ..utils.mes_type import mes_type


mes = Blueprint('message', __name__)

@mes.route('/message')
def show_message_list():
    user = session.get('user')
    if not user:
        return render_template("login.html", error="请先登录")
    
  
    role = user.get('role')
    if role == 'admin':
        sql = """
            SELECT m.id , m.user_id, u.user_name,m.time,m.type,m.message
            FROM message m 
            JOIN user u ON m.user_id = u.id
        """
        messages = db.fetchall(sql, [])
    else:
        sql = """
            SELECT m.id , m.user_id, u.user_name,m.time,m.type,m.message
            FROM message m 
            JOIN user u ON m.user_id = u.id
            WHERE m.user_id=%s
        """
        messages = db.fetchall(sql, [user['id']])
    
    return render_template("admin/message.html", messages=messages,message_type=mes_type)


@mes.route('/message/submit', methods=['GET', 'POST'])
def submit_message():
    user = session.get('user')
    if not user:
        return render_template("login.html", error="请先登录")
    
    if request.method == 'GET':
        return render_template("user/submit_message.html", user=user)
    
    data = request.form
    message = data.get('message', '').strip()

    if not message:
        return render_template("user/submit_message.html", user=user, error="消息内容不能为空！")
    if len(message) > 100:
        return render_template("user/submit_message.html", user=user, error="消息长度不能超过100个字符！")
    
 
    try:
        sql = "INSERT INTO message (user_id, message, time,type) VALUES (%s, %s, NOW(),1)"
        params = (user['id'], message)
        db.fetchone(sql, params)
        return redirect(url_for('message.show_message_list'))
    except Exception as e:
        return render_template("user/submit_message.html", user=user, error=f"提交失败：{str(e)}")
    
@mes.route('/message/receive', methods=['GET'])
def receive_message():
    user = session.get('user')
    if not user:
        return render_template("login.html", error="请先登录")

    role = user.get('role')
    if role == 'admin':
        sql = """
            SELECT m.id , m.user_id, m.message,  u.user_name,m.time,m.type
            FROM message m 
            JOIN user u ON m.user_id = u.id
        """
        messages = db.fetchall(sql, [])
        return render_template("admin/message.html", messages=messages,mes_type=mes_type)
    
    return render_template("login.html", error="您没有权限查看消息")
