from datetime import datetime
from flask import Flask,render_template,request,session, redirect, url_for, flash,session
from flask import Blueprint
from flask_wtf import FlaskForm
from wtforms import SubmitField,StringField,PasswordField,BooleanField
from wtforms.validators import DataRequired,EqualTo
from FlaskWebProject_colosseo_ctf.models import User
from flask_login import login_user
from flask_login import logout_user
from FlaskWebProject_colosseo_ctf.database import db_session
from FlaskWebProject_colosseo_ctf import app
from sqlalchemy import or_,and_
import json
from PIL import Image, ImageFont, ImageDraw, ImageFilter
import random
from io import BytesIO
from flask import make_response

def validate_picture():
    total = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ012345789'
    # 图片大小130 x 50
    width = 130
    heighth = 50
    # 先生成一个新图片对象
    im = Image.new('RGB',(width, heighth), 'white')
    # 设置字体
    #font = ImageFont.truetype('verdana', 35)
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf', 36)
    # 创建draw对象
    draw = ImageDraw.Draw(im)
    str = ''
    # 输出每一个文字
    for item in range(5):
        text = random.choice(total)
        str += text
        draw.text((5+25*item,4), text=text, fill='black',font=font )

    # 划几根干扰线
 #   for num in range(8):
  #      x1 = random.randint(0, width/2)
   #     y1 = random.randint(0, heighth/2)
    #    x2 = random.randint(0, width)
     #   y2 = random.randint(heighth/2, heighth)
      #  draw.line(((x1, y1),(x2,y2)), fill='black', width=1)

    # 模糊,加个滤镜
    im = im.filter(ImageFilter.FIND_EDGES)
    return im, str



log = Blueprint('log',__name__)

'''
# 关于到底提交到哪里，可能根本就没有必要担心，因为这里路由定义了/，所以htmlaction即便定义位空也并不是大事
'''
@app.teardown_request
def shutdown_session(exception=None):
    db_session.remove()

class Create_Xss_Form(FlaskForm):
    search = StringField('',validators=[DataRequired()])
    create = SubmitField('create')

class LoginForm(FlaskForm):
    username = StringField('',validators=[DataRequired()])
    password = PasswordField('',validators=[DataRequired()])
    verify_code = StringField('验证码', validators=[DataRequired()])
    sign_in = SubmitField('sign in')
    remember_me = BooleanField('记住我')

@log.route('/get_code')
def get_code():
    image, str = validate_picture()
    # 将验证码图片以二进制形式写入在内存中，防止将图片都放在文件夹中，占用大量磁盘
    buf = BytesIO()
    image.save(buf, 'jpeg')
    buf_str = buf.getvalue()
    # 把二进制作为response发回前端，并设置首部字段
    response = make_response(buf_str)
    response.headers['Content-Type'] = 'image/gif'
    # 将验证码字符串储存在session中
    session['image'] = str
    return response

@log.route('/',methods=['GET','POST'])
def login():
    loginForm = LoginForm()
    if loginForm.validate_on_submit(): #这个东西只有当表单提交了之后才会验证
        user = User.query.filter(or_(User.sequence == loginForm.username.data,User.name== loginForm.username.data)).first()
        #if session.get('image').lower() != loginForm.verify_code.data.lower():
        #    flash('验证码错误')
        if not user:
            flash("没有找到相关用户，请先注册")
            return redirect(url_for('auth.register'))
        elif not user.verify_password(loginForm.password.data):
            flash("密码错误")
        elif not user.confirmed:
            flash("未认证!!!")
        else:
            login_user(user,loginForm.remember_me.data) #如果remember_me是True，那么走cookie保存信息，如果是False走session保存信息
            return redirect(request.args.get('next') or url_for('home_page.home',id=user.sequence))#蓝图名称.函数名称URL后面会家一串GET请求的参数，其中有next参数，next其实就是记录了在跳转到login_view之前我是从什么页面过来的，这样在login_view成功登录之后我可以借此信息返回原页面。在这里，redirect先尝试能不能返回原页面，不能再返回默认的index页面去。
    return render_template( 'log_page.html',loginForm=loginForm)

@log.route('/site_itself',methods=['GET','POST'])
def site_itself():
    form = Create_Xss_Form()
    contents="<script>alert(1);</script>"
    if form.validate_on_submit():
        contents = form.search.data

        redirect(url_for('log.site_itself',contents=contents))
        
    return render_template('site_itself.html',form=form,contents=contents)

@log.route('/notice')
def notice():
    return render_template('notice.html')

@log.route('/help')
def help():
    return render_template('help.html')