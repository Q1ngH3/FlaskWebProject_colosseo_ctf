#from sqlalchemy.ext.automap import automap_base
#from sqlalchemy import create_engine, Table, MetaData
#from sqlalchemy.orm import Session
#from sqlalchemy.orm import scoped_session,sessionmaker
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from flask_login import UserMixin

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from sqlalchemy import create_engine, Table, MetaData,or_
from sqlalchemy.orm import Session
from sqlalchemy.orm import scoped_session,sessionmaker
from sqlalchemy.ext.automap import automap_base
from FlaskWebProject_colosseo_ctf import login_manager
from FlaskWebProject_colosseo_ctf import app
'''
    #判断flag正确与否？？？
    #def get_team():  没有必要，因为self.team记录了自己的team

    #def get_xxx
#property
#password只可写不可读，也就是使用在实体定义好之后
#使用 user.password会蹦出错误
#也就是说保证任何人都不能看：在端的层面
#但是还需要https保证传输安全
'''
'''
参数列表不能隔行
'''
'''
flask-login插件要求使用者必须实现一个回调方法，
是一个用@login_manager.user_loader装饰起来的方法。
这个方法同时接收一个用户标识符（通常情况下是用户id或类似的主键），
然后返回一个用户对象或者None。这个方法主要被用到的时候是，
用户请求进入@login_requrired的路由时，
程序将加载由这个方法返回的用户对象作为当前已经登录的用户对象。
如果返回的是None那么就说明当前没有用户已登录状态的用户，就禁止访问了。
'''

# 测试已经说明利用这种方式可以将所有表中的属性
# 以！！self.xxx！！的形式得到，即储存在这个类之后生成的实例中
Base = automap_base()
engine = create_engine('mysql+mysqlconnector://remoteuser:password@192.168.80.144:3306/users',echo = True)
Base.prepare(engine, reflect=True)
#注册机制
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

@login_manager.user_loader
def load_user(sequence):
    return Session.query(User).filter_by(sequence=sequence).first()# 不要忘了first()，否则返回的仅仅是Query对象，会报错。



class User(Base,UserMixin):
    __tablename__ = 'general_users'

    def __init__(self,sequence,name,email_address):
        self.sequence = sequence
        self.name = name
        self.email_address = email_address


    def submit_flag(self,question,flag):
        pass 


    @property 
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self,password):#注册时使用---密码的哈希生成；可以赋值但是不能取；这个hash即使密码相同，只要用户名不同最终得到的密码也不同
        self.hash_password = generate_password_hash(password)

    def verify_password(self,password):#登陆时使用--密码的验证
        return check_password_hash(self.hash_password,password)

    def get_id():
        return self.sequence






'''
    def generate_confirmation_token(self,expiration=3600):
        s = Serializer(app.config['SECRET_KEY'],expires_in=expiration)#创建这样一个Serializer需要一个秘钥参数，另外可以指定过期时间（秒数）。
        return s.dumps({'confirm':self.sequence})#创建完成后用dumps把一个可JSON序列化的python对象变成一串字符串，loads一串字符串可以解析出来这个python对象。

    def confirm(self, token):
        s = Serializer(app.config['SECRET_KEY'])  #解析用的不用设置过期时间
        try:
            data = s.loads(token)
        except Exception as e:
            return False
        if data.get('confirm') != self.sequence:    #这个判断是说，保证通过加密token验证的这个id必须是当前使用中用户的id，这样验证就有了密码和加密token的双重保障
            return False
        #若上面的条件都满足，则说明已验证完毕
        self.confirmed = True   #即==1
        session_u = Session()
        session_u.add(self)
        session_u.commit()
        Session.remove()
        return True

    def to_dict(self):
        d = {}
        d['sequence'] = self.sequence
        d['name'] = self.name

        return d
    """description of class"""
'''


'''
# reflect
engine_u = create_engine('mysql+mysqlconnector://remoteuser:password@192.168.80.144:3306/users',
echo = True)
Base.prepare(engine_u, reflect=True)
#注册机制
session_factory = sessionmaker(bind=engine_u)
Session = scoped_session(session_factory)
session_test = Session()
Session.remove()

new_user = User(sequence='2018213602',name='hans',email_address='a11111')
new_user.password='111111'
session_test.add(new_user)
session_test.commit()

#test
# User is the same as Base.classes.User now!!!!!!!
u1 = Session.query(User).filter_by(sequence='2018213602').first()#query是查询
#u0 = session_test.query(User).filter_by(sequence='2018213602').first()#query是查询
print (u1.to_dict())
#u2 = User.query.filter_by(sequence='2018213602').first() 不可行
print(u1.verify_password('111111'))#ok

scoped_session.remove(Session)
Session.remove(session_test)
'''