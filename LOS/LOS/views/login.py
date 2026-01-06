from flask import Blueprint,render_template,request,session,redirect,url_for

from LOS.utils.db import fetchone




log = Blueprint('login', __name__)


@log.route('/login',methods=['GET','POST'])

def login():
    if request.method == 'GET':
        return render_template('login.html')
    role = request.form.get('role')
    phone = request.form.get('phone')
    pwd = request.form.get('pwd')
    if not phone or not pwd:
        return render_template("login.html",error="请输入完整信息")
    


    print(role,phone,pwd)

    sql = "SELECT * FROM user WHERE phone=%s AND pwd=%s AND role=%s"
    params = (phone,pwd,role)
    data = fetchone(sql,params)


    if data:
        session['user'] = {
            "role": role,
            "phone": phone,
            "user_name": data['user_name'],
            "id": data['id'],
        }
        return redirect(url_for('index.index'))

        
    return render_template("login.html", error="账号或密码错误")


@log.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    role = request.form.get('role')
    phone = request.form.get('phone')
    pwd = request.form.get('pwd')
    if pwd != request.form.get('confirm_pwd'):
        return render_template("register.html",error="两次密码不一致")
    if len(phone) != 11:
        return render_template("register.html",error="手机号格式错误")
    if len(pwd) < 6 or len(pwd) > 12:
        return render_template("register.html",error="密码长度必须在6-12位之间")
    


    print(role,phone,pwd)

    sql = "INSERT INTO user (role, phone, pwd) VALUES (%s, %s, %s)"
    params = (role, phone, pwd)
    fetchone(sql,params)
    return redirect(url_for('login.login'))



@log.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login.login'))

