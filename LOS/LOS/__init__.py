from flask import Flask,request,session,render_template,redirect,url_for



def auth():
    if request.path.startswith('/static'):
        return 
    if request.path == '/login' or request.path == '/users':
        return 
    user = session.get('user')
    if not user:
        return redirect(url_for('login.login', error="请先登录"))
    return


def create_app():
    app = Flask(__name__)
    app.secret_key = 'fzhgfdjfykghe'

    from .views import login, order,index,analyse,manage,message

    app.register_blueprint(login.log)
    app.register_blueprint(order.ord)
    app.register_blueprint(index.ind)
    app.register_blueprint(analyse.ana)
    app.register_blueprint(manage.man)
    app.register_blueprint(message.mes)
    
    app.before_request(auth)

    return app
    
