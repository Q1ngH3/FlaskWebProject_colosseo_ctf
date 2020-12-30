from flask import render_template,request,session, redirect, url_for, flash
from flask import Blueprint

test=Blueprint('test',__name__)
@test.route('/')
def hello():
    """Renders a sample page."""
    my_list=[1,2,3,4,5]
    url_string="www.abc.com"
    my_dict={
      'name':'xxxx',
       'url':"www.xxxx.com"
        }
    return render_template(
        'test.html',
        url_string=url_string,
        my_list=my_list,
        my_dict=my_dict
        )
