from . import auth
from datetime import datetime
from flask import Flask,render_template,request,session, redirect, url_for, flash,session
from FlaskWebProject_colosseo_ctf import app
from flask_wtf import FlaskForm
from wtforms import SubmitField,StringField,PasswordField,BooleanField
from wtforms.validators import DataRequired,EqualTo
from FlaskWebProject_colosseo_ctf.models import User
from flask_login import login_user
from flask_login import logout_user
from flask_login import current_user
from flask_login import login_required
from flask_mail import Mail,Message
from FlaskWebProject_colosseo_ctf.email import send_mail
from datetime import datetime,timedelta
from FlaskWebProject_colosseo_ctf.database import db_session
from sqlalchemy import or_,and_
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
    # 设置字体:服务器改成上面的，本地用下面的
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf', 36)
    #font = ImageFont.truetype('verdana', 40)
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

@app.teardown_request
def shutdown_session(exception=None):
    db_session.remove()

class RegisterForm(FlaskForm):
    username = StringField('',validators=[DataRequired()])
    sequence = StringField('',validators=[DataRequired()])
    password = PasswordField('',validators=[DataRequired()])
    re_password = PasswordField('',validators=[DataRequired()])
    email_address = StringField('',validators=[DataRequired()])
    verify_code = StringField('验证码', validators=[DataRequired()])
    sign_up = SubmitField('sign up')

class ResetConfirmForm(FlaskForm):
    username = StringField('',validators=[DataRequired()])
    sequence = StringField('',validators=[DataRequired()])
    email_address = StringField('',validators=[DataRequired()])
    submit = SubmitField('sign up')

class ResetPasswordForm(FlaskForm):
    username = StringField('',validators=[DataRequired()])
    password = PasswordField('',validators=[DataRequired()])
    re_password = PasswordField('',validators=[DataRequired()])
    submit = SubmitField('sign up')

@auth.route('/get_code')
def get_code():
    image, str = validate_picture()
    # 将验证码图片以二进制形式写入在内存中，防止将图片都放在文件夹中，占用大量磁盘
    buf = BytesIO()
    image.save(buf, 'jpeg')
    buf_str = buf.getvalue()
    # 把二进制作为response发回前端，并设置首部
    response = make_response(buf_str)
    response.headers['Content-Type'] = 'image/gif'
    # 将验证码字符串储存在session中
    session['image'] = str
    return response

@auth.route('/register',methods = ['GET','POST'])
def register():
    registerForm = RegisterForm()
    if registerForm.validate_on_submit():
        user = db_session.query(User).filter(User.sequence == registerForm.sequence.data).first()
        user_name =db_session.query(User).filter(User.name == registerForm.username.data).first()
        user_email=db_session.query(User).filter(User.email_address == registerForm.email_address.data).first()
        if session.get('image').lower() != registerForm.verify_code.data.lower():
            flash('验证码错误')
            return redirect(url_for('auth.register'))
        if user or user_name:
            flash('用户名已被注册 :(')
            return redirect(url_for('auth.register'))#已经注册过就重新刷新一遍
        elif user_email:
            flash('邮箱已被注册 :(')
            return redirect(url_for('auth.register'))
        elif len(registerForm.username.data) > 20:
            flash('您的用户名太长了 :(')
            return redirect(url_for('auth.register'))
        elif registerForm.sequence.data.startswith('2018')==False:
            flash('您的用户id有误 :(')
            return redirect(url_for('auth.register'))
        elif len(registerForm.password.data) > 16 or len(registerForm.password.data) < 5:
            flash('您的密码长度必须在5~16范围内 :(')
        elif '_' in registerForm.password.data or '-' in registerForm.password.data or '%'in registerForm.password.data or '@' in registerForm.password.data:
            flash('您的密码含有一个或多个非法字符(-,_,@,%),请重新输入 :(')
            return redirect(url_for('auth.register'))
        elif registerForm.password.data != registerForm.re_password.data:
            flash('您的两次密码输入不一致 :(')
            return redirect(url_for('auth.register'))
        else:
            new_user = User(sequence=registerForm.sequence.data,name=registerForm.username.data,email_address=registerForm.email_address.data,date=datetime.now())
            new_user.password = registerForm.password.data
            db_session.add(new_user)
            db_session.commit()

            token = new_user.generate_confirmation_token()
            send_mail(new_user.email_address,"请确认您的账号",'confirm',id = new_user.sequence, name = new_user.name,token=token)
            flash("有一份邮件已经发往您的邮箱")
            return redirect(url_for('log.login'))
    return render_template('register.html',registerForm=registerForm)


@auth.route('/confirm/<token>')
def confirm(token):
    if User.check_activate_token(token):
        flash('激活成功')
        return redirect(url_for('log.login'))
    else:
        flash('激活失败')
        return redirect(url_for('auth.register'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('log.login'))

@auth.route('/reset_password_confirm',methods = ['GET','POST'])
def reset_password_confirm():
    reset_confirm_form = ResetConfirmForm()
    if reset_confirm_form.validate_on_submit():
        user = db_session.query(User).filter(User.sequence == reset_confirm_form.sequence.data).first()
        if not user:
            flash("没有找到相关用户，请先注册")
            return redirect(url_for('auth.register'))
        elif user.name != reset_confirm_form.username.data:
            flash("用户名与学号不匹配")
            return redirect(url_for('auth.reset_password_confirm'))
        elif user.email_address != reset_confirm_form.email_address.data:
            flash("您的邮箱输入有误")
            return redirect(url_for('auth.reset_password_confirm'))
        else:
            send_mail(user.email_address,"重置密码",'confirm_resetable',id = user.sequence, name = user.name)
            flash("有一份邮件已经发往您的邮箱")
            return redirect(url_for('auth.reset_password'))
    return render_template('reset_password_confirm.html',reset_confirm_form=reset_confirm_form)

@auth.route('/reset_password',methods = ['GET','POST'])
def reset_password():
    reset_password_form = ResetPasswordForm()
    if reset_password_form.validate_on_submit():
        user = db_session.query(User).filter(User.name == reset_password_form.username.data).first()
        if not user.resetable:
            flash("请先在邮箱完成认证")
            return redirect(url_for('auth.reset_password_confirm'))
        elif not user:
            flash("没有找到相关用户，请先注册")
            return redirect(url_for('auth.register'))
        elif len(reset_password_form.password.data) > 16 or len(reset_password_form.password.data) < 5:
            flash('您的密码长度必须在5~16范围内 :(')
            return redirect(url_for('auth.reset_password'))
        elif '_' in reset_password_form.password.data or '-' in reset_password_form.password.data or '%'in reset_password_form.password.data or '@' in reset_password_form.password.data:
            flash('您的密码含有一个或多个非法字符(-,_,@,%),请重新输入 :(')
            return redirect(url_for('auth.reset_password'))
        elif reset_password_form.password.data != reset_password_form.re_password.data:
            flash('您的两次密码输入不一致 :(')
            return redirect(url_for('auth.reset_password'))
        else:
            user.password = reset_password_form.password.data
            user.resetable = False
            db_session.commit()
            flash("密码修改成功")
            return redirect(url_for('log.login'))
    return render_template('reset_password.html',reset_password_form=reset_password_form)
    

@auth.route('/confirm_resetable/<name>')
def confirm_resetable(name):
    user = db_session.query(User).filter(User.name == name).first()
    user.resetable = True
    db_session.commit()
    return redirect(url_for('auth.reset_password'))