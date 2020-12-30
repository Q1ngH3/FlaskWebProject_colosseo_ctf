from . import auth
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
####app/auth/views.py####

#...

@auth.route('/confirm/<token>')
@login_required    #保证访问这个端点时要有登录用户，结合User.confirm方法中对self.id的判断又要求这个用户不能是其他人只能是要验证的用户本人
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('home_page.home'))
    if current_user.confirm(token):
        flash('已完成账号认证')
    else:
        flash('账号认证失败，凭证不正确或已过期')
    return redirect(url_for('home_page.home'))

