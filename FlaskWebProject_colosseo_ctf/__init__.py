from datetime import timedelta
from flask_login import LoginManager #是全局的
from flask_mail import Mail

from flask import Flask,session
import os

login_manager = LoginManager()
login_manager.session_protection = 'strong'#程序会对客户端IP及浏览器的代理信息做记录，一旦发生异动，就会立刻登出用户
login_manager.login_view = 'log.login'#与login_required装饰器有关，会在默认不登陆的时候强制跳转到login_view
login_manager.login_message = "您还没有登录，请登录"
mail = Mail()

app = Flask(__name__)

app.config['SECRET_KEY'] = 'xiaoxiaorenwu_wangshuo_lingxiaohan'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1) # 配置1天有效 
app.config['MAIL_SERVER'] = 'smtp.qq.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = '2379448326@qq.com'
app.config['MAIL_PASSWORD'] = 'rcqfrwuvexkseaaf'
app.config['MAIL_DEFAULT_SENDER'] = '2379448326@qq.com'
#app.config['DEBUG']= False
app.config['DEBUG']= True

login_manager.init_app(app)
mail.init_app(app)

from FlaskWebProject_colosseo_ctf.log import log
from FlaskWebProject_colosseo_ctf.test import test
from FlaskWebProject_colosseo_ctf.auth import auth
from FlaskWebProject_colosseo_ctf.home_page import home_page
from FlaskWebProject_colosseo_ctf.file import file

app.register_blueprint(test, url_prefix='/test')
app.register_blueprint(log,url_prefix='/')
app.register_blueprint(auth,url_prefix='/auth')
app.register_blueprint(home_page,url_prefix='/home_page')
app.register_blueprint(file,url_prefix='/file')
