from flask import Blueprint
auth = Blueprint('auth',__name__)    #;这里的main只是为蓝本取得一个名字，并不一定要和main这个主程序包一致
#from . import test
from . import views

