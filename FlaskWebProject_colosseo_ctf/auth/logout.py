from . import auth
from flask import render_template,url_for,redirect
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

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('log.login'))
