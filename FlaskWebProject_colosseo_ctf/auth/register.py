#------------------------------------------------------------------------------------
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://user:password@192.168.21.129/xiaoxiaorenwu'
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#db = SQLAlchemy(app)
from datetime import datetime
from flask import Flask,render_template,request,session, redirect, url_for, flash,session
#from FlaskWebProject_colosseo_ctfx import app
#import mysql.connector
#from  FlaskWebProject_colosseo_ctf.mydb import mydb
from flask import Blueprint
from flask_wtf import FlaskForm
from wtforms import SubmitField,StringField,PasswordField,BooleanField
from wtforms.validators import DataRequired,EqualTo
from FlaskWebProject_colosseo_ctf.alchemy_user import User
from sqlalchemy import create_engine, Table, MetaData,or_
from sqlalchemy.orm import Session
from sqlalchemy.orm import scoped_session,sessionmaker
from sqlalchemy.ext.automap import automap_base
from flask_login import login_user
from flask_login import logout_user
from . import auth
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
    font = ImageFont.truetype('verdana', 40)
    # 创建draw对象
    draw = ImageDraw.Draw(im)
    str = ''
    # 输出每一个文字
    for item in range(5):
        text = random.choice(total)
        str += text
        draw.text((5+random.randint(4,7)+20*item,5+random.randint(3,7)), text=text, fill='black',font=font )

    # 划几根干扰线
    for num in range(8):
        x1 = random.randint(0, width/2)
        y1 = random.randint(0, heighth/2)
        x2 = random.randint(0, width)
        y2 = random.randint(heighth/2, heighth)
        draw.line(((x1, y1),(x2,y2)), fill='black', width=1)

    # 模糊,加个滤镜
    im = im.filter(ImageFilter.FIND_EDGES)
    return im, str

class RegisterForm(FlaskForm):
    username = StringField('',validators=[DataRequired()])
    sequence = StringField('',validators=[DataRequired()])
    password = PasswordField('',validators=[DataRequired()])
    re_password = PasswordField('',validators=[DataRequired()])
    verify_code = StringField('验证码', validators=[DataRequired()])
    email_address = StringField('',validators=[DataRequired()])
    sign_up = SubmitField('sign up')
    

#regist = Blueprint('regist',__name__)
'''
mydb = mysql.connector.connect(
    host = "192.168.21.129",
    user = "user1",
    passwd = "password1",
    database = "xiaoxiaorenwu"
)

mycursor = mydb.cursor()
'''

#------------------------------------------------------------------------------------
'''
@app.route('/', methods=['GET', 'POST'])
def login():
    login_form = Loginform()
    return render_template('home_page.html',login_form = login_form)
'''

Base = automap_base()
engine_u = create_engine('mysql+mysqlconnector://remoteuser:password@192.168.80.144:3306/users',echo = True)
Base.prepare(engine_u, reflect=True)
#注册机制
session_factory = sessionmaker(bind=engine_u)
Session = scoped_session(session_factory)
session_uregister = Session()

@auth.route('/get_code')
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

@auth.route('/register',methods = ['GET','POST'])
def register():
    registerForm = RegisterForm()
    if registerForm.validate_on_submit():
        sequence = session_uregister.query(User).filter_by(sequence = registerForm.sequence.data).first()
        if session.get('image').lower() != registerForm.verify_code.data.lower():
            flash('验证码错误')
        if sequence:
            flash('用户名已被注册')
            return redirect(url_for('auth.register'))#已经注册过就重新刷新一遍

        elif len(registerForm.password.data) > 16 or len(registerForm.password.data) < 5 or '_' in registerForm.password.data or '-' in registerForm.password.data or '%'in registerForm.password.data or '@' in registerForm.password.data:
            flash('您的密码含有非法字符,请重新输入')
            return redirect(url_for('auth.register'))

        elif registerForm.password.data != registerForm.re_password.data:
            flash('两次密码输入不一致')
            return redirect(url_for('auth.register'))
        else:
            new_user = User(sequence=registerForm.sequence.data,name=registerForm.username.data,email_address=registerForm.email_address.data)
            new_user.password = registerForm.password.data
            session_uregister.add(new_user)
            session_uregister.commit()#到底要不要remove？
            Session.remove()
            redirect(url_for('log.login'))
    return render_template('register.html',registerForm=registerForm)


'''    
if request.method == 'POST':
        username = request.form.get('username')
        passwd = request.form.get('password')
        userid = request.form.get('userid')
        print (passwd)
        if (len(passwd) > 16 or len(passwd) < 5 or '_' in passwd or '-' in passwd):
            flash("Your passwd is too short or invaild ! ! !")
        else:
            sql = "SELECT IFNULL((select 1 from general_users where (sequence = %s OR name = %s) AND password = %s), 0);"  # "select 1 from general_users where (name =  %s OR sequence = %s) AND password = %s;"
            val = (userid, username, passwd)

            mycursor.execute(sql, val)
            print ('success1!!')
            re = mycursor.fetchone()
            print ('success2!!')
            print (re)
            if re == (1,):
                flash("您已经注册,请登录 ! ! !")
            else:
                sql = "INSERT INTO general_users (sequence, name, password, " \
                      "score, web_times, reverse_times, " \
                      "misc_times, crypto_times, stega_times, " \
                      "ppc_times, total_times, first_blood_times, " \
                      "second_blood_times, third_blood_times) " \
                      "VALUES (%s, %s, %s, " \
                      "%s, %s, %s, " \
                      "%s, %s, %s, " \
                      "%s, %s, %s, " \
                      "%s, %s);"
                val = (userid,username, passwd,0,0,0,0,0,0,0,0,0,0,0)
                try:
                    mycursor.execute(sql, val)
                except mysql.connector.Error as err:
                    print(err.msg)
                    flash("Register Fail ! ! !")

                mydb.commit()
                return "Register Success ! ! !"

    return render_template('register.html',register_form = register_form)
'''