from sqlalchemy import Column, Integer, String,Boolean,ForeignKey,DATE,INTEGER,Text
from sqlalchemy.orm import relationship
from FlaskWebProject_colosseo_ctf.database import Base
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from FlaskWebProject_colosseo_ctf import login_manager
from FlaskWebProject_colosseo_ctf import app
from FlaskWebProject_colosseo_ctf.database import db_session
from datetime import datetime
import bleach
from markdown import markdown
from sqlalchemy import event

@login_manager.user_loader#???
def load_user(sequence):
    return db_session.query(User).filter(sequence ==sequence).first()# 不要忘了first()，否则返回的仅仅是Query对象，会报错。

class Question(Base):
    __tablename__ = 'questions'
    sequence = Column(INTEGER(),primary_key=True,autoincrement=True)
    name = Column(String(50),nullable=False,unique=True)
    type = Column(String(50),nullable=False)
    level = Column(String(20),nullable=False)
    total_finish_times = Column(INTEGER(),nullable=False,default=0)
    points_now = Column(INTEGER(),nullable = False)
    hyper_link = Column(String(200))
    is_hinted = Column(Boolean(),default=False)
    describe = Column(String(500))
    flag = Column(String(150),nullable=False)#可以设置unique
    first_blood_user = Column(String(200),ForeignKey("users.name"))
    second_blood_user = Column(String(200),ForeignKey("users.name"))
    third_blood_user = Column(String(200),ForeignKey("users.name"))
    first_blood_team = Column(INTEGER(),ForeignKey("teams.number"))
    second_blood_team = Column(INTEGER(),ForeignKey("teams.number"))
    third_blood_team = Column(INTEGER(),ForeignKey("teams.number"))        

    def serialize(self):
        return {
        'sequence': self.sequence,
        'name': self.name,
        'type': self.type,
        'level': self.level,
        'total_finish_times': self.total_finish_times,
        'points_now': self.points_now,
        'hyper_link': self.hyper_link,
        'is_hinted': self.is_hinted,
        'describe': self.describe,
        'flag': self.flag,

        'first_blood_user': self.first_blood_user,
        'second_blood_user': self.second_blood_user,
        'third_blood_user': self.third_blood_user,

        'first_blood_team': self.first_blood_team,
        'second_blood_team': self.second_blood_team,
        'third_blood_team': self.third_blood_team,

        }

class Team(Base):
    __tablename__ = 'teams'
    number = Column(INTEGER(),primary_key=True,autoincrement=True)
    name = Column(String(200),nullable=False,unique=True)
    score = Column(INTEGER(),nullable=False,default=0)#假设score可以为负
    web_score = Column(INTEGER(),nullable=False,default=0)
    pwn_score = Column(INTEGER(),nullable=False,default=0)
    reverse_score = Column(INTEGER(),nullable=False,default=0)
    misc_score = Column(INTEGER(),nullable=False,default=0)
    crypto_score = Column(INTEGER(),nullable=False,default=0)

    rank = Column(INTEGER())

    web_times = Column(INTEGER(),nullable=False,default=0)
    pwn_times = Column(INTEGER(),nullable=False,default=0)
    reverse_times = Column(INTEGER(),nullable=False,default=0)
    misc_times = Column(INTEGER(),nullable=False,default=0)
    crypto_times = Column(INTEGER(),nullable=False,default=0)
    total_times = Column(INTEGER(),nullable=False,default=0)
    first_blood_times = Column(INTEGER(),nullable=False,default=0)
    second_blood_times = Column(INTEGER(),nullable=False,default=0)
    third_blood_times = Column(INTEGER(),nullable=False,default=0)

    date = Column(DATE())
    leader_name=Column(String(200),nullable=False)
    member_count=Column(INTEGER(),nullable=False,default=1)#成员个数，最大为三

    def __init__(self,name,date,leader_name):
        self.name = name
        self.date = date
        self.leader_name = leader_name

class t_relation_q(Base):
    __tablename__='team_relation_question'
    team_number=Column(Integer(),ForeignKey("teams.number"),primary_key=True)
    question_sequence=Column(Integer(),ForeignKey("questions.sequence"),primary_key=True)
    team_name=Column(String(200),nullable=False)
    question_name=Column(String(50),nullable=False)
    question_type=Column(String(50),nullable=False)
    this_times=Column(Integer(),nullable=False)
    this_points=Column(Integer(),nullable=False)#可能有作弊所以可能并不是正数
    is_first_blood=Column(Boolean(),nullable=False,default=False)
    is_second_blood=Column(Boolean(),nullable=False,default=False)
    is_third_blood=Column(Boolean(),nullable=False,default=False)
    is_published=Column(Boolean(),nullable=False,default=False)#做出题目之后是否发布了
    contributor=Column(String(200),ForeignKey("users.name"))#有用
    date=Column(DATE())
    team = relationship("Team",backref="relation_to_question")#查询relation表，得到object，可以用object.Team.xxx查询到Team中的数据；反过来通过team的object也可以通过relation_to_question查询到relation表中的内容
    question = relationship("Question",backref="relation_to_team")#查询relation表，得到object，可以用object.Question.xxx查询到Question中的数据；反过来通过question的object也可以通过relation_to_team查询到relation表中的内容
    
    def __init__(self,team_number,team_name,question_sequence,question_name,question_type,this_times,this_points,is_first_blood,is_second_blood,is_third_blood,contributor,date):
        
        self.team_number=team_number
        self.team_name=team_name
        self.question_sequence=question_sequence
        self.question_name=question_name
        self.question_type=question_type
        self.this_times=this_times
        self.this_points=this_points
        self.is_first_blood=is_first_blood
        self.is_second_blood=is_second_blood
        self.is_third_blood=is_third_blood
        self.contributor=contributor
        self.date=date

class User(Base,UserMixin):
    __tablename__ = 'users'
    sequence = Column(String(10),primary_key=True)
    hash_password = Column(String(300))
    name = Column(String(200),nullable=False,unique=True)
    score = Column(INTEGER(),nullable=False,default=0)#假设score可以为负
    web_score = Column(INTEGER(),nullable=False,default=0)
    pwn_score = Column(INTEGER(),nullable=False,default=0)
    reverse_score = Column(INTEGER(),nullable=False,default=0)
    misc_score = Column(INTEGER(),nullable=False,default=0)
    crypto_score = Column(INTEGER(),nullable=False,default=0)

    rank = Column(INTEGER())
    team_number = Column(INTEGER(),ForeignKey("teams.number"))
    team_name = Column(String(200))
    web_times = Column(INTEGER(),nullable=False,default=0)
    pwn_times = Column(INTEGER(),nullable=False,default=0)
    reverse_times = Column(INTEGER(),nullable=False,default=0)
    misc_times = Column(INTEGER(),nullable=False,default=0)
    crypto_times = Column(INTEGER(),nullable=False,default=0)
    total_times = Column(INTEGER(),nullable=False,default=0)
    first_blood_times = Column(INTEGER(),nullable=False,default=0)
    second_blood_times = Column(INTEGER(),nullable=False,default=0)
    third_blood_times = Column(INTEGER(),nullable=False,default=0)
    email_address= Column(String(45),nullable=False,unique=True)
    has_team = Column(Boolean(),nullable=False,default=False)
    confirmed = Column(Boolean(),nullable=False,default=False)#邮箱验证的一个识别符：用户是否认证
    resetable = Column(Boolean(),nullable=False,default=False)#邮箱验证的一个识别符：用户是否可以重置密码
    is_leader = Column(Boolean(),nullable=False,default=False)
    is_member = Column(Boolean(),nullable=False,default=False)
    is_manager = Column(Boolean(),nullable=False,default=False)
    #如果是队长则两周都要置为True
    date = Column(DATE())
    has_inform=Column(Boolean(),nullable=False,default=False)#是否有未读或未确认消息
    team=relationship("Team",backref="member_of_team")  

    def __init__(self,sequence,name,email_address,date):
        self.sequence = sequence
        self.name = name
        self.email_address = email_address
        self.date = date

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

    def get_id(self):
        return self.sequence

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(app.config['SECRET_KEY'], expiration)
        # 这个函数需要两个参数，一个密匙，从配置文件获取，一个时间，这里1小时
        return s.dumps({'confirm': self.sequence})

    @staticmethod
    def check_activate_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            print ("error1!!!")
            return False
        u = User.query.get(data['confirm'])
        if not u:
            print ("error2!!!")
            return False
        print (u.confirmed)
        if not u.confirmed:
            u.confirmed = True
            print(u.confirmed)
            db_session.add(u)
            db_session.commit()
        return True

    def to_dict(self):
        d = {}
        d['sequence'] = self.sequence
        d['name'] = self.name

        return d
    """description of class"""

class u_relation_q(Base):
    __tablename__='user_relation_question'
    user_sequence=Column(String(10),ForeignKey("users.sequence"),primary_key=True)
    question_sequence=Column(INTEGER(),ForeignKey("questions.sequence"),primary_key=True)
    user_name=Column(String(200),nullable=False)
    question_name=Column(String(50),nullable=False)
    question_type=Column(String(50),nullable=False)
    this_times=Column(INTEGER(),nullable=False)
    this_points=Column(INTEGER(),nullable=False)#可能有作弊所以可能并不是正数
    is_first_blood=Column(Boolean(),nullable=False,default=False)
    is_second_blood=Column(Boolean(),nullable=False,default=False)
    is_third_blood=Column(Boolean(),nullable=False,default=False)
    is_published=Column(Boolean(),nullable=False,default=False)
    date=Column(DATE())
    question=relationship("Question",backref="relation_to_question")#对于人来说要relation_to_question
    user=relationship("User",backref="relation_to_user")#对于题目来说要有relation_to_user

    def __init__(self,user_sequence,user_name,question_sequence,question_name,question_type,this_times,this_points,is_first_blood,is_second_blood,is_third_blood,date):
        
        self.user_sequence=user_sequence
        self.user_name=user_name
        self.question_sequence=question_sequence
        self.question_name=question_name
        self.question_type=question_type
        self.this_times=this_times
        self.this_points=this_points
        self.is_first_blood=is_first_blood
        self.is_second_blood=is_second_blood
        self.is_third_blood=is_third_blood

        self.date=date

class u_request(Base):
    __tablename__='user_request'
    ord=Column(INTEGER(),primary_key=True,autoincrement=True)
    to_user=Column(String(200),ForeignKey("users.name"),nullable=False)#用名字来搜
    from_user=Column(String(200),ForeignKey("users.name"),nullable=False)
    is_confirmed=Column(Boolean(),nullable=False,default=False)


class u_response(Base):
    __tablename__='user_response'
    ord=Column(INTEGER(),primary_key=True,autoincrement=True)
    to_user=Column(String(200),ForeignKey("users.name"),nullable=False)
    from_user=Column(String(200),ForeignKey("users.name"),nullable=False)
    is_confirmed=Column(Boolean(),nullable=False,default=False)
    is_agreed=Column(Boolean(),nullable=False,default=False)

class Notice(Base):
    __tablename__='notice'
    sequence = Column(INTEGER(),primary_key=True,autoincrement=True)
    publisher=Column(String(200),nullable=False)
    time=Column(DATE())# 要精确到秒
    title = Column(String(200),nullable=False)
    contents = Column(String(500),nullable=True)

class Message(Base):
    __tablename__='message'
    sequence = Column(INTEGER(),primary_key=True,autoincrement=True)
    type = Column(String(200),nullable=False) #战队消息：team,系统消息：system,...
    sender = Column(String(200),nullable=False)
    receiver = Column(String(200),nullable=False)
    time=Column(DATE())# 要精确到秒
    title = Column(String(200),nullable=False)
    contents = Column(String(500),nullable=True)
    is_dealt=Column(Boolean(),nullable=False,default=False)
   
class PostForm(Base):
    __tablename__ = 'postMarkdown'
    id = Column(INTEGER(),primary_key=True,autoincrement=True)
    title = Column(String(225),nullable=False)
    text = Column(String(1000),nullable=True)
    modified_date=Column(DATE())# 要精确到秒
    categories = Column(String(100),nullable=True)

class Article(Base):
    __tablename__ = 'article'
    id = Column(Integer(), primary_key=True,autoincrement=True)
    title = Column(String(128))
    body = Column(Text)
    body_html = Column(Text)
    create_time = Column(DATE(), index=True, default=datetime.utcnow)
    user_name = Column(String(50),nullable=False)
    question_id = Column(INTEGER(),nullable=False)
    seo_link = Column(String(128))

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p', 'img', 'video', 'div', 'iframe', 'p', 'br', 'span', 'hr', 'src', 'class']
        allowed_attrs = {'*': ['class'],
                         'a': ['href', 'rel'],
                         'img': ['src', 'alt']}
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True, attributes=allowed_attrs))


event.listen(Article.body, 'set', Article.on_changed_body)