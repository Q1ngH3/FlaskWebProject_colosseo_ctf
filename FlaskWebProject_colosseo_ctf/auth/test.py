from flask import render_template,url_for,redirect
from . import auth

@auth.route('/test')
def auth_test():
    return render_template('exercise.html')
