from . import home_page
from datetime import datetime,timedelta
from flask import Flask,render_template,request,session, redirect, url_for, flash,session,jsonify,make_response,request
from flask import Blueprint,Response,abort
from flask_login import login_required
from FlaskWebProject_colosseo_ctf.database import db_session
from sqlalchemy import or_,and_
from FlaskWebProject_colosseo_ctf import app
from flask_wtf import FlaskForm
from wtforms import SubmitField,StringField,FileField,IntegerField,TextAreaField,SelectMultipleField
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.validators import DataRequired,EqualTo
from FlaskWebProject_colosseo_ctf.models import User,Team,Question,t_relation_q,u_relation_q,u_request,u_response,Notice,Message,PostForm,Article
import json
from PIL import Image, ImageFont, ImageDraw, ImageFilter
import random
from io import BytesIO
import time,os
from flask import Markup
import markdown
from markdown import Markdown
from qiniu import Auth, put_file, etag, put_data


def uploadImg(fileData):
    # 需要填写你的 Access Key 和 Secret Key
    QINIU_ACCESS_KEY = "OhxcDS3eN_FnjAIihnybjjCiSjvhMgA7TeT8QMJU"
    QINIU_SECRET_KEY = "xl7cQissXgPM-tmADW_rhvlDtOeTdV12O4Z9ZrLh"
    QQINIU_BUCKET_NAME = "ws-blogs"
    QINIU_BUCKET_DOMAIN = "q2ahmypys.bkt.clouddn.com"

    access_key = QINIU_ACCESS_KEY
    secret_key = QINIU_SECRET_KEY
    # 构建鉴权对象
    q = Auth(access_key, secret_key)

    # 要上传的空间
    bucket_name = QQINIU_BUCKET_NAME

    # 上传后保存的文件名
    key = 'background.png'
    # 生成上传 Token，可以指定过期时间等 None is key默认
    token = q.upload_token(bucket_name, None, 3600)

    # 要上传文件的本地路径
    localfile = r'D:\blogs\app\static\profile\images\background.jpg'
    # put_file上传指定路径文件
    # put_data上传二进制文件
    # ret, info = put_file(token, None, fileData)
    ret, info = put_data(token, None, fileData)
    # assert ret['key'] == key
    # assert ret['hash'] == etag(localfile)
    # 判断状态码是否200
    if info.status_code == 200:
    	# 获取七牛云保存的图片名称
        fileName = ret.get("hash")
        # 拼接完整图片url路径返回
        imgUrl = "http://{}/{}".format(QINIU_BUCKET_DOMAIN, fileName)
        return imgUrl

def validate_picture():
    total = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ012345789'
    # 图片大小130 x 50
    width = 130
    heighth = 50
    # 生成一个新图片对象
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
    # 干扰线
    for num in range(8):
        x1 = random.randint(0, width/2)
        y1 = random.randint(0, heighth/2)
        x2 = random.randint(0, width)
        y2 = random.randint(heighth/2, heighth)
        draw.line(((x1, y1),(x2,y2)), fill='black', width=1)

    # 模糊滤镜
    im = im.filter(ImageFilter.FIND_EDGES)
    return im, str

@app.teardown_request
def shutdown_session(exception=None):
    db_session.remove()

def Response_headers(content):
    resp = Response(content)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

class Web_One_Form(FlaskForm):
    flag = StringField('',validators=[DataRequired()])
    create = SubmitField('create')

class Create_Challenge_Form(FlaskForm):
    name = StringField('',validators=[DataRequired()])
    type = StringField('',validators=[DataRequired()])
    points_now = IntegerField('',validators=[DataRequired()])
    level = StringField('',validators=[DataRequired()])
    hyper_link = StringField('',validators=[DataRequired()])
    describe = StringField('',validators=[DataRequired()])
    flag = StringField('',validators=[DataRequired()])
    create = SubmitField('create')
    

class Create_Message_Form(FlaskForm):
    title = StringField('',validators=[DataRequired()])
    contents = StringField('',validators=[DataRequired()])
    receiver = StringField('',validators=[DataRequired()])
    create = SubmitField('create')

class Create_Notice_Form(FlaskForm):
    title = StringField('',validators=[DataRequired()])
    contents = StringField('',validators=[DataRequired()])
    create = SubmitField('create')

class Create_Team_Form(FlaskForm):
    team_name = StringField('',validators=[DataRequired()])
    verify_code = StringField('验证码', validators=[DataRequired()])
    create = SubmitField('create')

class Team_Form(FlaskForm):
    dismiss = SubmitField('解散战队')
    exit = SubmitField('退出战队')
    remove = SubmitField('移除此用户')

class Finish_Question_Form(FlaskForm):
    flag = StringField('',validators=[DataRequired()])
    submit = SubmitField('submit')

class General_Form(FlaskForm):
    submit = SubmitField('submit')

class Sort_Ranking_Form(FlaskForm):
    WEB = SubmitField('WEB')
    REV = SubmitField('REV')
    PWN = SubmitField('PWN')
    MISC = SubmitField('MISC')
    CRYPTO = SubmitField('CRYPTO')

class Flag_String(FlaskForm):
    flag = StringField('',validators=[DataRequired()])

class Submit_Flag(FlaskForm):
    verify_code = StringField('验证码', validators=[DataRequired()])
    flag = StringField('',validators=[DataRequired()])
    submit = SubmitField('Submit')

class UploadForm(FlaskForm):
    verify_code = StringField('验证码', validators=[DataRequired()])
    file = FileField('choice file',validators=[FileRequired('choice a file!!!!'), FileAllowed(['jpg','jpeg','pdf','md','docx','txt','png','py'])])
    submit = SubmitField('submit')

@home_page.route('/get_code')
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

@home_page.route('/<id>')
@login_required
def home(id):
    user = db_session.query(User).filter(User.sequence == id).first()
    Notices = db_session.query(Notice).filter().all()
    Messages = db_session.query(Message).filter(Message.receiver == user.name).all()
    Questions = db_session.query(u_relation_q).filter(u_relation_q.user_sequence == id).order_by(u_relation_q.date).all()
    has_team=user.has_team
    name = user.name
    if not Messages:
        new_message = Message(title="Welcome",
                            contents="尊敬的用户，恭喜你注册成功！在这里开始你的CTF之旅吧！",
                            time=user.date,
                            receiver=user.name,
                            sender="系统",
                            type="system")
        db_session.add(new_message)
        db_session.commit()
    return render_template('/homepage_files/home_page.html',
                            id=id,
                            has_team=has_team,
                            name=name,
                            Notices=Notices,
                            Messages=Messages,
                            Questions=Questions)#has_team似乎是用来出现战队列表或不出现


@home_page.route('/my_information/<id>')
@login_required
def user_information(id):
    user = db_session.query(User).filter(User.sequence == id).first()
    user_relation_question = db_session.query(u_relation_q).filter(u_relation_q.user_sequence == id).order_by(u_relation_q.date).all()
    has_team=user.has_team
    return render_template('/homepage_files/user_information.html',
                           id=id,
                           user_relation_question=user_relation_question,
                           user = user)

@home_page.route('/other_user_information/<id>/<other_user_name>')
@login_required
def other_user_information(id,other_user_name):
    user = db_session.query(User).filter(User.sequence == id).first()
    other_user = db_session.query(User).filter(User.name == other_user_name).first()
    user_relation_question = db_session.query(u_relation_q).filter(u_relation_q.user_name == other_user_name).order_by(u_relation_q.date).all()
    has_team=user.has_team
    return render_template('/homepage_files/other_user_information.html',
                           id=id,
                           user_relation_question=user_relation_question,
                           user = user,
                           other_user=other_user)

@home_page.route('/team/<id>',methods=['GET','POST'])
@login_required
def team_general(id):#在这个页面生成所有战队，当战队和本人的一样跳转到my_team进行之前的操作；若战队和本人的不一样就跳转到other_team
    form = Create_Team_Form()
    Teams = db_session.query(Team).order_by(Team.date).all() #对象列表，元组列表
    user = db_session.query(User).filter(User.sequence == id).first()
    is_member = user.is_member
    is_leader = user.is_leader
    user = db_session.query(User).filter(User.sequence == id).first()
    has_team=user.has_team
    name = user.name

    if form.validate_on_submit():#新建战队;注意不能重名
        if session.get('image').lower() != form.verify_code.data.lower():
            flash('验证码错误')
            return render_template('/homepage_files/team.html',
                           id=id,
                           Teams=Teams,
                           is_member=is_member,
                           is_leader=is_leader,
                           form=form,
                           user=user,
                           has_team=has_team,
                           name=name)
        new_team_name = form.team_name.data
        #判断重名
        old_team = db_session.query(Team).filter(Team.name == new_team_name).first()
        if old_team:#如果有重名战队直接退回
            flash('已有同名战队，请重新命名')
            return render_template('/homepage_files/team.html',
                           id=id,
                           Teams=Teams,
                           is_member=is_member,
                           is_leader=is_leader,
                           form=form,
                           user=user,
                           has_team=has_team,
                           name=name)
            

        #下面开始创建战队,逻辑是新建战队；并且将自己的所有做题记录放入战队的做题记录中;还要将个人的信息导入到战队中,还要更改个人信息


        new_team = Team(name=new_team_name,date=datetime.now(),leader_name = user.name)#新建战队
        db_session.add(new_team)
        db_session.commit()

        user.has_team = True
        user.is_leader = True
        user.is_member = True
        user.team_number = new_team.number
        user.team_name = new_team.name

        db_session.commit()

        #创建战队消息
        new_message = Message(title="创建战队",
                            contents="尊敬的"+user.name+"：\n"
                                    "    恭喜你成功创建了战队！您的战队名为："+
                                    user.team_name+" \n赶快通知你的队友加入吧！",
                            time=datetime.now(),
                            receiver=user.name,
                            sender="系统",
                            type="system")
        db_session.add(new_message)
        db_session.commit()

        User_Relation_Question=db_session.query(u_relation_q).filter(u_relation_q.user_sequence == id).all()
        
        # 个人做题信息移入战队做题信息
        for user_relation_question in User_Relation_Question:
            new_team_relation_question = t_relation_q(team_number = new_team.number,
                                                  team_name = new_team_name,
                                                  question_sequence = user_relation_question.question_sequence,
                                                  question_name = user_relation_question.question_name,
                                                  question_type= user_relation_question.question_type,
                                                  this_times = user_relation_question.this_times,
                                                  this_points=user_relation_question.this_points,
                                                  is_first_blood = user_relation_question.is_first_blood,
                                                  is_second_blood = user_relation_question.is_second_blood,
                                                  is_third_blood = user_relation_question.is_third_blood,
                                                  contributor = user.name,
                                                  date = user_relation_question.date)
            db_session.add(new_team_relation_question)

        db_session.commit()

        #个人信息导入战队
        new_team.web_score=new_team.web_score + user.web_score
        new_team.pwn_score=new_team.pwn_score + user.pwn_score
        new_team.reverse_score=new_team.reverse_score + user.reverse_score
        new_team.misc_score=new_team.misc_score + user.misc_score
        new_team.crypto_score=new_team.crypto_score + user.crypto_score
        new_team.score=new_team.score + user.score

        new_team.web_times=new_team.web_times + user.web_times
        new_team.pwn_times=new_team.pwn_times + user.pwn_times
        new_team.reverse_times=new_team.reverse_times + user.reverse_times
        new_team.misc_times=new_team.misc_times + user.misc_times
        new_team.crypto_times=new_team.crypto_times + user.crypto_times
        new_team.total_times=new_team.total_times + user.total_times

        new_team.first_blood_times=new_team.first_blood_times + user.first_blood_times
        new_team.second_blood_times=new_team.second_blood_times + user.second_blood_times
        new_team.third_blood_times=new_team.third_blood_times + user.third_blood_times

        #这里不会对member_count++，因为本身设置其默认值为1
        db_session.commit()

        return redirect(url_for('home_page.team_general',id=id))

    return render_template('/homepage_files/team.html',
                           id=id,
                           Teams=Teams,
                           is_member=is_member,
                           is_leader=is_leader,
                           form=form,
                           user=user,
                           has_team=has_team,
                           name=name)


@home_page.route('/other_team_information/<id>/<team_name>')#别人的战队必须双参数
@login_required
def other_team_information(id,team_name):
    # 这里还必须计算战队已有人数，如果team.count_member<3才显示加入按钮
    #申请加入还必须让当前用户不能属于任何战队
    user = db_session.query(User).filter(User.sequence == id).first()
    team = db_session.query(Team).filter(Team.name == team_name).first()
    messages = db_session.query(Message).filter(Message.type == "team_apply" and Message.receiver == team.leader_name and Message.sender == user.name).order_by(Message.time).all()
    if messages:
        message = messages[-1]
    else:
        message = None

    members=team.member_of_team  #返回元组列表,列出的时候用 for member in members 来做就行
    register_date=team.date
    if team.total_times !=0:
        web_percentage=(100*(round(team.web_times/team.total_times,2)))
        pwn_percentage=(100*(round(team.pwn_times/team.total_times,2)))
        reverse_percentage=(100*(round(team.reverse_times/team.total_times,2)))
        misc_percentage=(100*(round(team.misc_times/team.total_times,2)))
        crypto_percentage=(100*(round(team.crypto_times/team.total_times,2)))

    team_relation_question = db_session.query(t_relation_q).filter(t_relation_q.team_number == team.number).order_by(t_relation_q.date).all()

    if team.total_times !=0:
        return render_template('/homepage_files/other_team_information.html',
                           id=id,
                           team_name=team_name,
                           members=members,#返回元组列表,列出的时候用 for member in members 来做就行
                           register_date=register_date,
                           web_percentage=web_percentage,
                           pwn_percentage=pwn_percentage,
                           reverse_percentage=reverse_percentage,
                           misc_percentage=misc_percentage,
                           crypto_percentage=crypto_percentage,
                           team_relation_question = team_relation_question,#也会生成对象列表，对象用元组表示,但是应该可以通过"."调用
                           user=user,
                           team=team,
                           message=message)
    else:
        return render_template('/homepage_files/other_team_information.html',
                           id=id,
                           team_name=team_name,
                           members=members,#返回元组列表,列出的时候用 for member in members 来做就行
                           register_date=register_date,
                           team_relation_question = team_relation_question,#也会生成对象列表，对象用元组表示,但是应该可以通过"."调用
                           user=user,
                           team=team,
                           message=message)

@home_page.route('/my_team_information/<id>')
@login_required
def my_team_information(id):
    user = db_session.query(User).filter(User.sequence == id).first()
    team_name=user.team_name
    team = db_session.query(Team).filter(Team.name == team_name).first()
    
    if team:
        members=team.member_of_team
        register_date=team.date

        if team.total_times != 0:
            web_percentage=(100*(round(team.web_times/team.total_times,2)))
            pwn_percentage=(100*(round(team.pwn_times/team.total_times,2)))
            reverse_percentage=(100*(round(team.reverse_times/team.total_times,2)))
            misc_percentage=(100*(round(team.misc_times/team.total_times,2)))
            crypto_percentage=(100*(round(team.crypto_times/team.total_times,2)))

        team_relation_question = db_session.query(t_relation_q).filter(t_relation_q.team_number == team.number).order_by(t_relation_q.date).all()

        if team.total_times != 0:
            return render_template('/homepage_files/my_team_information.html',
                           id=id,
                           team_name=team_name,
                           members=members,#返回元组列表,列出的时候用 for member in members 来做就行
                           register_date=register_date,
                           web_percentage=web_percentage,
                           pwn_percentage=pwn_percentage,
                           reverse_percentage=reverse_percentage,
                           misc_percentage=misc_percentage,
                           crypto_percentage=crypto_percentage,
                           team_relation_question = team_relation_question,#也会生成对象列表，对象用元组表示,但是应该可以通过"."调用
                           user=user,
                           team = team
                                   )
        else:
            return render_template('/homepage_files/my_team_information.html',
                           id=id,
                           team_name=team_name,
                           members=members,#返回元组列表,列出的时候用 for member in members 来做就行
                           register_date=register_date,
                           team_relation_question = team_relation_question,#也会生成对象列表，对象用元组表示,但是应该可以通过"."调用
                           user=user,
                           team = team
                           )
    flash('您还没有战队')
    return redirect(url_for('home_page.home',id=id))


@home_page.route('/my_team_information/remove_member/<id>/<myid>')#队长的移除队员操作，以及队员或队长的退出操作全用这个就好了
@login_required
def remove_member(id,myid):#处理
    myuser = db_session.query(User).filter(User.sequence == myid).first()
    user = db_session.query(User).filter(User.sequence == id).first()#当前要被删除的人
    team = db_session.query(Team).filter(Team.number == user.team_number).first()
    db_session.query(t_relation_q).filter(t_relation_q.contributor == user.name).delete()#删除所有有这个人贡献的队伍做题，应该不会报错吧
    if team.member_count == 1:#如果只剩一个人还要退出战队，那么战队删除
        return redirect(url_for('home_page.dismiss_team',id=id,myid=myuser.sequence))

    #若退出人员为队长
    max_member = None
    if user.is_leader:#
        max_contributes=0
        
        for member in team.member_of_team:
            if member.is_leader == False and member.score >= max_contributes: #若只有两个人，队长和成员都是一样的分数。那么队长推出之后便会出现空用户
                max_contributes=member.score
                max_member = member
        #队长退出战队消息
        new_message = Message(title="退出战队",
                        contents="尊敬的"+user.name+"：\n"
                                    "    您退出了您的战队："+team.name+" 战队队长的身份已经交给："+
                                    max_member.name+
                                    " 您可以点击team导航栏，创建新的战队或者加入其他战队！",
                        time=datetime.now(),
                        receiver=user.name,
                        sender="系统",
                        type="system")

        team.leader_name = max_member.name
        db_session.commit()

        db_session.add(new_message)
        db_session.commit()
        #把消息发给他人：
        new_message = Message(title="退出战队",
                        contents="尊敬的"+max_member.name+"：\n"
                                    "    您的队长："+user.name+" 退出了战队："+team.name+
                                    " 由于您的战队贡献度最大，战队队长的身份已经自动交给了您。"+
                                    "快去管理您的战队吧。",
                        time=datetime.now(),
                        receiver=max_member.name,
                        sender="系统",
                        type="system")
        db_session.add(new_message)
        db_session.commit()
        for member in team.member_of_team:
            if not member.is_leader:
                if member != max_member:
                    new_message = Message(title="退出战队",
                                contents="尊敬的"+member.name+"：\n"
                                            "    您的队长："+user.name+" 退出了战队："+team.name+
                                            " 由于战队成员贡献度最大的是："+max_member.name+
                                            " 战队队长的身份已经自动交给："+max_member.name+
                                            " 您可以点击您的战队，查看您的战队信息。",
                                time=datetime.now(),
                                receiver=member.name,
                                sender="系统",type="system")
                    db_session.add(new_message)
                    db_session.commit()
    else:
        #退出战队消息
        for member in team.member_of_team:
            if member == user:
                new_message = Message(title="战队退出",
                                    contents="尊敬的"+member.name+"：\n"
                                                "    您退出了您的战队："+team.name+
                                                "您可以点击team导航栏，创建新的战队或者加入其他战队！",
                                    time=datetime.now(),
                                    receiver=member.name,
                                    sender="系统",type="system")
                db_session.add(new_message)
                db_session.commit()
            else:
                new_message = Message(title="战队成员退出",
                                    contents="尊敬的"+member.name+"：\n"
                                                "    您的战队："+team.name+" 有一位成员退出，他的用户名是："+user.name+
                                                "您可以查看您的战队信息，查看您的战队变化。",
                                    time=datetime.now(),
                                    receiver=member.name,
                                    sender="系统",type="system")
                db_session.add(new_message)
                db_session.commit()

    if max_member:
        max_member.is_leader = True
    # 把权限授权给除了自己以外贡献最多的，即分数最高的；自己分数最高就意味着给战队带来的分数最高

    user.team_number = None
    user.team_name = None
    user.has_team = False
    user.is_member=False
    user.is_leader=False
    #relationship字段应该就没了
    #常规操作，相当于让team所有的数据都进行一个移除
    team.web_score=team.web_score-user.web_score
    team.pwn_score=team.pwn_score-user.pwn_score
    team.reverse_score=team.reverse_score-user.reverse_score
    team.misc_score=team.misc_score-user.misc_score
    team.crypto_score=team.crypto_score-user.crypto_score
    team.score=team.score-user.score

    team.web_times=team.web_times-user.web_times
    team.pwn_times=team.pwn_times-user.pwn_times
    team.reverse_times=team.reverse_times-user.reverse_times
    team.misc_times=team.misc_times-user.misc_times
    team.crypto_times=team.crypto_times-user.crypto_times
    team.total_times=team.total_times-user.total_times

    team.first_blood_times=team.first_blood_times-user.first_blood_times
    team.second_blood_times=team.second_blood_times-user.second_blood_times
    team.third_blood_times=team.third_blood_times-user.third_blood_times

    team.member_count = team.member_count-1
    #######################################################################################
    db_session.commit()

    return redirect(url_for('home_page.my_team_information',id=myuser.sequence,myid=user.sequence))


@home_page.route('/my_team_information/dismiss_team/<id>/<myid>')
@login_required
def dismiss_team(id,myid):#解散战队页；解散战队显然只能解散自己的战队
    myuser = db_session.query(User).filter(User.sequence == myid).first()
    user = db_session.query(User).filter(User.sequence == id).first()#申请人
    team = db_session.query(Team).filter(Team.name == user.team_name).first()
    # 申请人要么是点击解散战队“按钮”的队长要么是退出的S最后一个人；但是如果是退出的最后一个人，那么他一定是队长；所以能进入到这个页面的一定是队长
    
    if team.member_count == 1:# 如果最后只剩下一个人了，也就是最后那个人进行的战队退出或解散
        user.team_name = None
        user.team_name = None
        user.has_team = False
        user.is_member = False
        user.is_leader = False
        #战队退出消息
        new_message = Message(title="战队解散",
                        contents="尊敬的"+user.name+"：\n"
                                    "    您退出了您的战队："+team.name+"  由于战队中没有其他成员，战队已经解散。"+
                                    "您可以点击team导航栏，创建新的战队或者加入其他战队！",
                        time=datetime.now(),
                        receiver=user.name,
                        sender="系统",
                        type="system")
        db_session.add(new_message)
        db_session.commit()

    elif team.member_count > 1:# 成员还大于一个的战队解散
        USER = db_session.query(User).filter(User.team_name == team.name).all()
        for u in USER:
            u.team_name = None
            u.team_name = None
            u.has_team = False
            u.is_member = False
            u.is_leader = False
        #解散战队
        for member in team.member_of_team:
            if member.is_leader:
                new_message = Message(title="战队解散",
                                contents="尊敬的"+user.name+"：\n"
                                            "    您解散了您的战队："+team.name+
                                            "您可以点击team导航栏，创建新的战队或者加入其他战队！",
                                time=datetime.now(),
                                receiver=member.name,
                                sender="系统",type="system")
                db_session.add(new_message)
                db_session.commit()
            else:
                new_message = Message(title="战队解散",
                                contents="尊敬的"+user.name+"：\n"
                                            "    您的队长"+team.leader_name+"解散了您的战队："+team.name+
                                            "您可以点击team导航栏，创建新的战队或者加入其他战队！",
                                time=datetime.now(),
                                receiver=member.name,
                                sender="系统",type="system")
                db_session.add(new_message)
                db_session.commit()

 #首先需要把是所有人对战队的外键干掉，再去干掉战队对象，不然的话会有完整性问题

    #这个应该可以删除所有number是team_number的记录项
    # chai diao ti mu de yin yong

    Team_relation_Question = db_session.query(t_relation_q).filter(t_relation_q.team_number == team.number).all()
    for relation in Team_relation_Question:
        if relation.is_first_blood:
            relation.question.first_blood_team = None
        elif relation.is_second_blood:
            relation.question.second_blood_team = None
        elif relation.is_third_blood:
            relation.question.third_blood_team = None


    db_session.query(t_relation_q).filter(t_relation_q.team_number == team.number).delete()

    db_session.delete(team)
    db_session.commit()

    return redirect(url_for('home_page.my_team_information',id=myuser.sequence,user=myuser,myid=user.sequence))


#=============================================================================================================
@home_page.route('/ranking/<id>')
@login_required
def ranking(id):
    user = db_session.query(User).filter(User.sequence == id).first()

    has_team = user.has_team
    name = user.name
    return redirect(url_for('home_page.user_ranking',id = id))
    #return render_template('/homepage_files/ranking_list.html',id=id,has_team=has_team,name=name)


@home_page.route('/ranking/user_ranking/<id>')
@login_required
def user_ranking(id):
    user1 = db_session.query(User).filter(User.sequence == id).first()
    USER = db_session.query(User).order_by(User.score.desc()).all()
    i=1
    for user in USER:
        user.rank = i
        i=i+1

    db_session.commit()

    USER = db_session.query(User).order_by(User.score.desc()).all()
    #更新一下
    return render_template('/homepage_files/ranking_child/user_ranking_list.html',
                    id = id,
                    USER = USER,
                    user = user1)



@home_page.route('/ranking/group_ranking/<id>')
@login_required
def group_ranking(id):
    TEAM = db_session.query(Team).order_by(Team.score.desc()).all()
    user = db_session.query(User).filter(User.sequence == id).first()
    i=1
    for team in TEAM:
        team.rank = i
        i=i+1

    db_session.commit()
    TEAM = db_session.query(Team).order_by(Team.score.desc()).all()
    return render_template('/homepage_files/ranking_child/group_ranking_list.html',
                    id=id,
                    TEAM=TEAM,
                    user=user)


@home_page.route('/ranking/sort_ranking/<id>', methods=['GET', 'POST'])
@login_required
def sort_ranking(id):
    USER = None
    user = db_session.query(User).filter(User.sequence == id).first()
    return render_template('/homepage_files/ranking_child/sort_ranking_list.html',
                           id=id,
                           USER=USER,
                           user=user)

# ===================================================================================================================
@home_page.route('/ranking/sort_ranking/<id>/<question_type>', methods=['GET', 'POST'])
@login_required
def sort_ranking_handler(id, question_type):
    USER = None
    user = db_session.query(User).filter(User.sequence == id).first()
    if question_type == 'web':
        USER = db_session.query(User.team_name, User.name, User.web_times.label('TIMES'),
                                User.web_score.label('SCORE')).order_by(User.web_score.desc()).all()

    elif question_type == 'pwn':
        USER = db_session.query(User.team_name, User.name, User.pwn_times.label('TIMES'),
                                User.pwn_score.label('SCORE')).order_by(User.pwn_score.desc()).all()

    elif question_type == 'misc':

        USER = db_session.query(User.team_name, User.name, User.misc_times.label('TIMES'),
                                User.misc_score.label('SCORE')).order_by(User.misc_score.desc()).all()
    elif question_type == 'reverse':
        USER = db_session.query(User.team_name, User.name, User.reverse_times.label('TIMES'),
                                User.reverse_score.label('SCORE')).order_by(User.reverse_score.desc()).all()

    elif question_type == 'crypto':
        USER = db_session.query(User.team_name, User.name, User.crypto_times.label('TIMES'),
                                User.crypto_score.label('SCORE')).order_by(User.crypto_score.desc()).all()

    return render_template('/homepage_files/ranking_child/sort_ranking_list.html',
                           id=id,
                           USER=USER,
                           user=user)

#===================================================================================================================

@home_page.route('/challenge/<id>',methods=['GET','POST'])
@login_required
def challenge(id):
    challenge_form = Create_Challenge_Form()
    user = db_session.query(User).filter(User.sequence == id).first()
    User_Relation_Question=db_session.query(u_relation_q).filter(u_relation_q.user_sequence == id).all()
    has_team=user.has_team
    name = user.name

    if challenge_form.validate_on_submit():

        new_challenge = Question(name=challenge_form.name.data,
                                  type=challenge_form.type.data,
                                  describe=challenge_form.describe.data,
                                  points_now=challenge_form.points_now.data,
                                  level=challenge_form.level.data,
                                  hyper_link=challenge_form.hyper_link.data,
                                  flag=challenge_form.flag.data)#新建题目
        db_session.add(new_challenge)
        db_session.commit()

    Question_Web=db_session.query(Question).filter(Question.type == 'web').all()
    Question_Pwn=db_session.query(Question).filter(Question.type == 'pwn').all()
    Question_Misc=db_session.query(Question).filter(Question.type == 'misc').all()
    Question_Rev=db_session.query(Question).filter(Question.type == 'reverse').all()
    Question_Crypto=db_session.query(Question).filter(Question.type == 'crypto').all()

    return render_template('/homepage_files/exercise.html',
                           id=id,
                           user=user,
                           has_team=has_team,
                           name = name,
                           User_Relation_Question = User_Relation_Question,
                           Question_Web=Question_Web,
                           Question_Pwn=Question_Pwn,
                           Question_Misc=Question_Misc,
                           Question_Rev=Question_Rev,
                           Question_Crypto=Question_Crypto)

@home_page.route('/challenge/web/<id>',methods=['GET','POST'])
@login_required
def web(id):
    user = db_session.query(User).filter(User.sequence == id).first()
    has_team=user.has_team
    name = user.name
    User_Relation_Question=db_session.query(u_relation_q).filter(u_relation_q.user_sequence == id).all()
    Question_Web=db_session.query(Question).filter(Question.type == 'web').all()
    return render_template('/homepage_files/exercise_child/web.html',
                           id=id,
                           user=user,
                           has_team=has_team,
                           name = name,
                           User_Relation_Question = User_Relation_Question,
                           Question_Web=Question_Web)

@home_page.route('/challenge/pwn/<id>',methods=['GET','POST'])
@login_required
def pwn(id):
    user = db_session.query(User).filter(User.sequence == id).first()
    has_team=user.has_team
    name = user.name
    User_Relation_Question=db_session.query(u_relation_q).filter(u_relation_q.user_sequence == id).all()
    Question_Pwn=db_session.query(Question).filter(Question.type == 'pwn').all()
    return render_template('/homepage_files/exercise_child/pwn.html',
                           id=id,
                           user=user,
                           has_team=has_team,
                           name = name,
                           Question_Pwn=Question_Pwn)

@home_page.route('/challenge/misc/<id>',methods=['GET','POST'])
@login_required
def misc(id):
    user = db_session.query(User).filter(User.sequence == id).first()
    has_team=user.has_team
    name = user.name
    User_Relation_Question=db_session.query(u_relation_q).filter(u_relation_q.user_sequence == id).all()
    Question_Misc=db_session.query(Question).filter(Question.type == 'misc').all()
    return render_template('/homepage_files/exercise_child/misc.html',
                           id=id,
                           user=user,
                           has_team=has_team,
                           name = name,
                           User_Relation_Question = User_Relation_Question,
                           Question_Misc=Question_Misc)

@home_page.route('/challenge/rev/<id>',methods=['GET','POST'])
@login_required
def rev(id):
    user = db_session.query(User).filter(User.sequence == id).first()
    has_team=user.has_team
    name = user.name
    User_Relation_Question=db_session.query(u_relation_q).filter(u_relation_q.user_sequence == id).all()
    Question_Rev=db_session.query(Question).filter(Question.type == 'reverse').all()
    return render_template('/homepage_files/exercise_child/rev.html',
                           id=id,
                           user=user,
                           has_team=has_team,
                           name = name,
                           User_Relation_Question = User_Relation_Question,
                           Question_Rev=Question_Rev)

@home_page.route('/challenge/crypto/<id>',methods=['GET','POST'])
@login_required
def crypto(id):
    user = db_session.query(User).filter(User.sequence == id).first()
    has_team=user.has_team
    name = user.name
    User_Relation_Question=db_session.query(u_relation_q).filter(u_relation_q.user_sequence == id).all()
    Question_Crypto=db_session.query(Question).filter(Question.type == 'crypto').all()
    return render_template('/homepage_files/exercise_child/crypto.html',
                           id=id,
                           user=user,
                           has_team=has_team,
                           name = name,
                           User_Relation_Question = User_Relation_Question,
                           Question_Crypto=Question_Crypto)


@home_page.route('/challenge/flag_handler/<id>/<question_name>',methods=['GET','POST'])
@login_required
def submit(id,question_name):
    fileform = UploadForm()
    form = Submit_Flag()
    question = db_session.query(Question).filter(Question.name == question_name).first()
    user = db_session.query(User).filter(User.sequence == id).first()
    old_u_relation_q = db_session.query(u_relation_q).filter(and_(u_relation_q.question_name == question_name, u_relation_q.user_name == user.name)).first()

    if old_u_relation_q == None:
        if form.validate_on_submit():
            if session.get('image').lower() != form.verify_code.data.lower():
                flash('验证码错误')
                return redirect(url_for('home_page.submit',id=id,question_name = question_name))
            if question.flag != form.flag.data:
                flash('您的flag输入错误 :(')
                return redirect(url_for('home_page.submit',id=id,question_name = question_name))
            else:
                if user.has_team:
                    team = db_session.query(Team).filter(Team.name == user.team_name).first()
                    team.score += question.points_now
                    if question.type == 'web':
                        team.web_score += question.points_now
                        team.web_times += 1
                    elif question.type == 'pwn':
                        team.pwn_score += question.points_now
                        team.pwn_times += 1
                    elif question.type == 'misc':
                        team.misc_score += question.points_now
                        team.misc_times += 1
                    elif question.type == 'reverse':
                        team.reverse_score += question.points_now
                        team.reverse_times += 1
                    elif question.type == 'crypto':
                        team.crypto_score += question.points_now
                        team.crypto_times += 1

                    if question.total_finish_times == 0:
                        question.first_blood_team = team.number
                        team.first_blood_times += 1
                    elif question.total_finish_times == 1:
                        question.second_blood_team = team.number
                        team.second_blood_times += 1
                    elif question.total_finish_times == 2:
                        question.third_blood_team = team.number
                        team.third_blood_times += 1


                user.score += question.points_now
                user.total_times += 1
                if question.type == 'web':
                    user.web_score += question.points_now
                    user.web_times += 1
                elif question.type == 'pwn':
                    user.pwn_score += question.points_now
                    user.pwn_times += 1
                elif question.type == 'misc':
                    user.misc_score += question.points_now
                    user.misc_times += 1
                elif question.type == 'reverse':
                    user.reverse_score += question.points_now
                    user.reverse_times += 1
                elif question.type == 'crypto':
                    user.crypto_score += question.points_now
                    user.crypto_times += 1


                first=False
                second=False
                third=False

                if question.total_finish_times == 0:
                    question.first_blood_user = user.name
                    user.first_blood_times += 1
                    first=True
                elif question.total_finish_times == 1:
                    question.second_blood_user = user.name
                    user.second_blood_times += 1
                    second=True
                elif question.total_finish_times == 2:
                    question.third_blood_user = user.name
                    user.third_blood_times += 1
                    third=True
                db_session.commit()

                new_user_relation_question = u_relation_q(user_sequence = id,
                                                      user_name = user.name,
                                                      question_sequence = question.sequence,
                                                      question_name = question.name,
                                                      question_type= question.type,
                                                      this_times = question.total_finish_times+1,
                                                      this_points=question.points_now,
                                                      is_first_blood = first,
                                                      is_second_blood = second,
                                                      is_third_blood = third,
                                                      date = datetime.now())
                db_session.add(new_user_relation_question)
                db_session.commit()

                if user.has_team:
                    old_team_relation_question = db_session.query(t_relation_q).filter(and_(t_relation_q.team_number== team.number,t_relation_q.question_sequence == new_user_relation_question.question_sequence)).first()
                    if not old_team_relation_question:
                        new_team_relation_question = t_relation_q(team_number = team.number,
                                                      team_name = user.team_name,
                                                      question_sequence = new_user_relation_question.question_sequence,
                                                      question_name = new_user_relation_question.question_name,
                                                      question_type= new_user_relation_question.question_type,
                                                      this_times = new_user_relation_question.this_times,
                                                      this_points=new_user_relation_question.this_points,
                                                      is_first_blood = new_user_relation_question.is_first_blood,
                                                      is_second_blood = new_user_relation_question.is_second_blood,
                                                      is_third_blood = new_user_relation_question.is_third_blood,
                                                      contributor = user.name,
                                                      date = new_user_relation_question.date)

                        db_session.add(new_team_relation_question)

                    else:
                        if question.total_finish_times == 0:
                            old_team_relation_question.is_first_blood = True

                        elif question.total_finish_times == 1:
                            old_team_relation_question.is_second_blood = True

                        elif question.total_finish_times == 2:
                            old_team_relation_question.is_third_blood = True

                    db_session.commit()

                question.total_finish_times += 1
                question.points_now *= 0.9

                db_session.commit()

                flash('解答正确,您真nb,分给您加上了 : )')

                return redirect(url_for('home_page.submit',id=id,question_name = question_name))

    else:
        if fileform.validate_on_submit():
            basedir = os.path.abspath(os.path.dirname(__file__))
            file_dir = os.path.join(basedir, '../file/upload')
            print('file_dir')
            f = fileform.file.data
            fname = f.filename
            print(fname)
            ext = fname.rsplit('.', 1)[1]
            unix_time = int(time.time())
            new_filename = str(unix_time) + '.' + ext
            f.save(os.path.join(file_dir,new_filename))
            flash('Upload success :)')
            return redirect(url_for('home_page.submit',id=id,question_name = question_name))

    return render_template('/homepage_files/problem.html',
                           id=id,
                           question_name=question_name,
                           form = form,
                           fileform = fileform,
                           question = question,
                           user = user,
                           key = old_u_relation_q
                           )


@home_page.route('/trend/<id>',methods=['GET','POST'])
@login_required
def trend(id):
    user = db_session.query(User).filter(User.sequence == id).first() 
    return render_template('/homepage_files/trend.html',
                           user = user,
                           id = id)

@home_page.route('/get_data/<id>',methods=['GET','POST'])
@login_required
def get_data(id):
    user = db_session.query(User).filter(User.sequence == id).first()
    startDay = datetime.strptime('2019-11-10','%Y-%m-%d')
    today = datetime.now()
    diff_days = (today-startDay).days + 1
    list_time = [None]*diff_days
    for i in range(0,diff_days):
        list_time[i] = (startDay + timedelta(days = i)).strftime("%Y-%m-%d")

    #下面求最近一周每个战队的分数

    TEAM = db_session.query(Team).order_by(Team.date).all() #对象列表，元组列表
    list = []
    score = [0]*diff_days
    name = []
    tmp = []
    for team in TEAM:
        members=team.member_of_team
        name.append(team.name)
        for member in members:
            User_Relation_Question=db_session.query(u_relation_q).filter(u_relation_q.user_sequence == member.sequence).all()
            for row in User_Relation_Question:
                t = row.date.strftime("%Y-%m-%d")
                tt = datetime.strptime(t, "%Y-%m-%d")
                tmp_diff_days = (tt-startDay).days
                score[tmp_diff_days] += row.this_points
                    
        for i in range(1,diff_days):
            score[i] = score[i] + score[i-1]
        tmp.append(score)
        score = [0]*diff_days

    list_data=[]
    i = 0
    for team in TEAM:
        list_data.append({
            "name": team.name, "value": tmp[i]
                })
        i = i + 1

    datas = {
        "startDay":(today - timedelta(days = 6)).strftime("%Y-%m-%d"),
        "name":name,
        "time":list_time,
        "data": list_data
    }
    content = json.dumps(datas)
    resp = Response_headers(content)
    return resp

@home_page.route('/user_achievement_data/<id>',methods=['GET','POST'])
@login_required
def user_achievement_data(id):
    user = db_session.query(User).filter(User.sequence == id).first()
    web = user.web_times
    pwn = user.pwn_times
    rev = user.reverse_times
    misc = user.misc_times
    crypto = user.crypto_times
    datas = {
        "data": [
            {"name": "web", "value": web},
            {"name": "pwn", "value": pwn},
            {"name": "misc", "value": misc},
            {"name": "rev", "value": rev},
            {"name": "crypto", "value": crypto},
        ]
    }
    content = json.dumps(datas)
    resp = Response_headers(content)
    return resp

@home_page.route('/team_achievement_data/<team_name>',methods=['GET','POST'])
@login_required
def team_achievement_data(team_name):
    team = db_session.query(Team).filter(Team.name == team_name).first()
    web = team.web_times
    pwn = team.pwn_times
    rev = team.reverse_times
    misc = team.misc_times
    crypto = team.crypto_times
    datas = {
        "data": [
            {"name": "web", "value": web},
            {"name": "pwn", "value": pwn},
            {"name": "misc", "value": misc},
            {"name": "rev", "value": rev},
            {"name": "crypto", "value": crypto},
        ]
    }
    content = json.dumps(datas)
    resp = Response_headers(content)
    return resp

#other_user_name
@home_page.route('/other_user_achievement_data/<id>/<other_user_name>',methods=['GET','POST'])
@login_required
def other_user_achievement_data(id,other_user_name):
    user = db_session.query(User).filter(User.name == other_user_name).first()
    web = user.web_times
    pwn = user.pwn_times
    rev = user.reverse_times
    misc = user.misc_times
    crypto = user.crypto_times
    datas = {
        "data": [
            {"name": "web", "value": web},
            {"name": "pwn", "value": pwn},
            {"name": "misc", "value": misc},
            {"name": "rev", "value": rev},
            {"name": "crypto", "value": crypto},
        ]
    }
    content = json.dumps(datas)
    resp = Response_headers(content)
    return resp

@home_page.route('/notice_detail/<id>/<notice_sequence>',methods=['GET','POST'])
@login_required
def notice_detail(id,notice_sequence):
    user = db_session.query(User).filter(User.sequence == id).first()
    notice = db_session.query(Notice).filter(Notice.sequence == notice_sequence).first()
    return render_template('/homepage_files/notice_detail.html',
                           user=user,
                           id = id,
                           notice=notice)


@home_page.route('/notice/<id>',methods=['GET','POST'])
@login_required
def notice(id):
    form = Create_Notice_Form()
    user = db_session.query(User).filter(User.sequence == id).first()
    Notices = db_session.query(Notice).filter().all()
    if form.validate_on_submit():

        new_title = form.title.data
        new_contents = form.contents.data

        new_notice = Notice(title=new_title,
                            contents=new_contents,
                            time=datetime.now(),
                            publisher=user.name)#新建公告
        db_session.add(new_notice)
        db_session.commit()

    return render_template('/homepage_files/notice.html',
                           id=id,
                           form=form,
                           user=user,
                           Notices=Notices)

@home_page.route('/message/<id>',methods=['GET','POST'])
@login_required
def message(id):
    form = Create_Message_Form()
    Users = db_session.query(User).filter().all()
    user = db_session.query(User).filter(User.sequence == id).first()
    Messages = db_session.query(Message).filter(Message.receiver == user.name).all()
    if not Messages:
        new_message = Message(title="Welcome",
                            contents="尊敬的用户，恭喜你注册成功！在这里开始你的CTF之旅吧！",
                            time=user.date,
                            receiver=user.name,
                            sender="系统",
                            type="system")
        db_session.add(new_message)
        db_session.commit()

    message_form = Create_Message_Form()

    if message_form.validate_on_submit():
        new_receiver = message_form.receiver.data
        new_title = message_form.title.data
        new_contents = message_form.contents.data

        new_message = Message(title=new_title,
                              contents=new_contents,
                              time=datetime.now(),
                              receiver=new_receiver,
                              sender=user.name,
                              type="manager")#新建消息
        db_session.add(new_message)
        db_session.commit()

    return render_template('/homepage_files/message.html',
                           id=id,
                           form=form,
                           message_form=message_form,
                           user=user,
                           Users=Users,
                           Messages=Messages)

@home_page.route('/message_detail/<id>/<message_sequence>',methods=['GET','POST'])
@login_required
def message_detail(id,message_sequence):
    user = db_session.query(User).filter(User.sequence == id).first()
    message = db_session.query(Message).filter(Message.sequence == message_sequence).first()
    sender = db_session.query(User).filter(User.name == message.sender).first()
    return render_template('/homepage_files/message_detail.html',
                           user=user,
                           id = id,
                           message=message,
                           sender = sender)

@home_page.route('/manager/<id>',methods=['GET','POST'])
@login_required
def manager(id):
    user = db_session.query(User).filter(User.sequence == id).first()

    #管理员可以新建消息
    message_form = Create_Message_Form()

    #管理员可以新建公告
    notice_form = Create_Notice_Form()

    #管理员可以发布题目
    challenge_form = Create_Challenge_Form()
    if challenge_form.validate_on_submit():

        new_challenge = Question(title=challenge_form.title.data,
                                  type=challenge_form.type.data,
                                  describe=challenge_form.describe.data,
                                  points_now=challenge_form.points_now.data,
                                  level=challenge_form.level.data,
                                  hyper_link=challenge_form.hyper_link.data)#新建题目
        db_session.add(new_challenge)
        db_session.commit()

    return render_template('/homepage_files/manager.html',
                           user=user,
                           id = id,
                           notice_form = notice_form,
                           message_form = message_form,
                           challenge_form = challenge_form)

@home_page.route('/manager_notice/<id>',methods=['GET','POST'])
@login_required
def manager_notice(id):
    notice_form = Create_Notice_Form()
    update_notice_form = Create_Notice_Form()
    user = db_session.query(User).filter(User.sequence == id).first()
    Notices = db_session.query(Notice).filter().all()
    if notice_form.validate_on_submit():

        new_title = notice_form.title.data
        new_contents = notice_form.contents.data

        new_notice = Notice(title=new_title,
                            contents=new_contents,
                            time=datetime.now(),
                            publisher=user.name)#新建公告
        db_session.add(new_notice)
        db_session.commit()

    return render_template('/homepage_files/manager_child/manager_notice.html',
                           id=id,
                           notice_form=notice_form,
                           user=user,
                           Notices=Notices,
                           update_notice_form=update_notice_form)

@home_page.route('/drop_notice/<id>/<notice_sequence>',methods=['GET','POST'])
@login_required
def drop_notice(id,notice_sequence):
    notice_form = Create_Notice_Form()
    update_notice_form = Create_Notice_Form()
    user = db_session.query(User).filter(User.sequence == id).first()
    Notices = db_session.query(Notice).filter().all()
    notice = db_session.query(Notice).filter(Notice.sequence == notice_sequence).first()
    db_session.delete(notice)
    db_session.commit()
    return render_template('/homepage_files/manager_child/manager_notice.html',
                           id=id,
                           notice_form=notice_form,
                           user=user,
                           Notices=Notices,
                           update_notice_form=update_notice_form)

@home_page.route('/update_notice/<id>/<notice_sequence>',methods=['GET','POST'])
@login_required
def update_notice(id,notice_sequence):
    form = Create_Notice_Form()
    update_notice_form = Create_Notice_Form()
    notice_form = Create_Notice_Form()
    user = db_session.query(User).filter(User.sequence == id).first()
    Notices = db_session.query(Notice).filter().all()
    notice = db_session.query(Notice).filter(Notice.sequence == notice_sequence).first()

    if update_notice_form.validate_on_submit():
        notice.time = datetime.now()
        notice.title = form.title.data
        notice.contents = form.contents.data
        notice.publisher = user.name

        db_session.commit()

    return render_template('/homepage_files/manager_child/manager_notice.html',
                           id=id,
                           form=form,
                           notice_form=notice_form,
                           update_notice_form=update_notice_form,
                           user=user,
                           Notices=Notices)

@home_page.route('/manager_challenge/<id>',methods=['GET','POST'])
@login_required
def manager_challenge(id):
    challenge_form = Create_Challenge_Form()
    update_challenge_form = Create_Challenge_Form()
    user = db_session.query(User).filter(User.sequence == id).first()
    Challenges = db_session.query(Question).filter().all()
    if challenge_form.validate_on_submit():

        new_challenge = Question(name=challenge_form.name.data,
                                  type=challenge_form.type.data,
                                  describe=challenge_form.describe.data,
                                  points_now=challenge_form.points_now.data,
                                  level=challenge_form.level.data,
                                  hyper_link=challenge_form.hyper_link.data,
                                  flag=challenge_form.flag.data)#新建题目
        db_session.add(new_challenge)
        db_session.commit()

    return render_template('/homepage_files/manager_child/manager_challenge.html',
                           id=id,
                           challenge_form=challenge_form,
                           user=user,
                           Challenges=Challenges,
                           update_challenge_form=update_challenge_form)

@home_page.route('/drop_challenge/<id>/<challenge_sequence>',methods=['GET','POST'])
@login_required
def drop_challenge(id,challenge_sequence):
    challenge_form = Create_Challenge_Form()
    update_challenge_form = Create_Challenge_Form()
    user = db_session.query(User).filter(User.sequence == id).first()
    Challenges = db_session.query(Question).filter().all()
    challenge = db_session.query(Question).filter(Question.sequence == challenge_sequence).first()
    db_session.delete(challenge)
    db_session.commit()
    return render_template('/homepage_files/manager_child/manager_challenge.html',
                           id=id,
                           challenge_form=challenge_form,
                           user=user,
                           Challenges=Challenges,
                           update_challenge_form=update_challenge_form)

@home_page.route('/update_challenge/<id>/<challenge_sequence>',methods=['GET','POST'])
@login_required
def update_challenge(id,challenge_sequence):
    form = Create_Challenge_Form()
    update_challenge_form = Create_Challenge_Form()
    challenge_form = Create_Challenge_Form()
    user = db_session.query(User).filter(User.sequence == id).first()
    Challenges = db_session.query(Question).filter().all()
    challenge = db_session.query(Question).filter(Question.sequence == challenge_sequence).first()

    if update_challenge_form.validate_on_submit():
        challenge.name = update_challenge_form.name.data
        challenge.describe = update_challenge_form.describe.data
        challenge.type=challenge_form.type.data
        challenge.points_now=challenge_form.points_now.data
        challenge.level=challenge_form.level.data
        challenge.hyper_link=challenge_form.hyper_link.data
        challenge.flag=challenge_form.flag.data

        db_session.commit()

    return render_template('/homepage_files/manager_child/manager_challenge.html',
                           id=id,
                           form=form,
                           challenge_form=challenge_form,
                           update_challenge_form=update_challenge_form,
                           user=user,
                           Challenges=Challenges)

#
@home_page.route('/manager_message/<id>',methods=['GET','POST'])
@login_required
def manager_message(id):
    Users = db_session.query(User).filter().all()
    message_form = Create_Message_Form()
    update_message_form = Create_Message_Form()
    user = db_session.query(User).filter(User.sequence == id).first()
    Messages = db_session.query(Message).filter().all()
    if message_form.validate_on_submit():

        new_message = Message(title=message_form.title.data,
                            contents=message_form.contents.data,
                            time=datetime.now(),
                            sender=user.name,
                            receiver=message_form.receiver.data,
                            type="manager")#新建消息
        db_session.add(new_message)
        db_session.commit()

    return render_template('/homepage_files/manager_child/manager_message.html',
                           id=id,
                           message_form=message_form,
                           user=user,
                           Messages=Messages,
                           update_message_form=update_message_form,
                           Users=Users)

@home_page.route('/drop_message/<id>/<message_sequence>',methods=['GET','POST'])
@login_required
def drop_message(id,message_sequence):
    message_form = Create_Message_Form()
    update_message_form = Create_Message_Form()
    user = db_session.query(User).filter(User.sequence == id).first()
    Users = db_session.query(User).filter().all()
    Messages = db_session.query(Message).filter().all()
    message = db_session.query(Message).filter(Message.sequence == message_sequence).first()
    db_session.delete(message)
    db_session.commit()
    return render_template('/homepage_files/manager_child/manager_message.html',
                           id=id,
                           message_form=message_form,
                           user=user,
                           Messages=Messages,
                           update_message_form=update_message_form,
                           Users=Users)

@home_page.route('/update_message/<id>/<message_sequence>',methods=['GET','POST'])
@login_required
def update_message(id,message_sequence):
    form = Create_Notice_Form()
    message_form = Create_Message_Form()
    update_message_form = Create_Message_Form()
    Users = db_session.query(User).filter().all()
    user = db_session.query(User).filter(User.sequence == id).first()
    Messages = db_session.query(Message).filter().all()
    message = db_session.query(Message).filter(Message.sequence == message_sequence).first()

    if update_message_form.validate_on_submit():
        message.title=message_form.title.data
        message.contents=message_form.contents.data
        message.time=message_form.time.data
        message.sender=message_form.sender.data
        message.receiver=message_form.receiver.data
        message.type=message_form.type.data

        db_session.commit()

    return render_template('/homepage_files/manager_child/manager_message.html',
                           id=id,
                           form=form,
                           message_form=message_form,
                           update_message_form=update_message_form,
                           user=user,
                           Messages=Messages,
                           Users=Users)

@home_page.route('/other_team_information/send_message_join_in/<id>/<team_name>')#申请加入战队消息
@login_required
def send_message_join_in(id,team_name):
    user = db_session.query(User).filter(User.sequence == id).first()
    team = db_session.query(Team).filter(Team.name == team_name).first()
    new_message = Message(title="战队申请",
                            contents="用户："+user.name+" 申请加入您的战队，请确认是否同意。",
                            time=datetime.now(),
                            receiver=team.leader_name,
                            sender=user.name,
                            type="team_apply")
    db_session.add(new_message)
    db_session.commit()
    flash("申请消息已发送，请等待队长审核")
    return redirect(url_for('home_page.other_team_information',id=id,team_name=team_name))

@home_page.route('/message/agree_join_in/<id>/<applicant_name>/<message_sequence>')
@login_required
def agree_join_in(id,applicant_name,message_sequence):
    user = db_session.query(User).filter(User.name == applicant_name).first()
    team_leader = db_session.query(User).filter(User.sequence == id).first()
    team = db_session.query(Team).filter(Team.leader_name == team_leader.name).first()
    team_name = team.name
    message = db_session.query(Message).filter(Message.sequence == message_sequence).first()
    applicant = db_session.query(User).filter(User.name == applicant_name).first()

    #消息已经被处理
    message.is_dealt = True
    db_session.commit()

    user.is_member = True
    user.has_team = True
    user.team_name = team_name
    user.team_number = team.number

    User_Relation_Question=db_session.query(u_relation_q).filter(u_relation_q.user_sequence == applicant.sequence).all()

    for user_relation_question in User_Relation_Question:
        old_team_relation_question = db_session.query(t_relation_q).filter(
                and_(t_relation_q.team_number == team.number,
                     t_relation_q.question_sequence == user_relation_question.question_sequence)).first()
        if not old_team_relation_question:
            new_team_relation_question = t_relation_q(team_number = team.number,
                                                  team_name = team_name,
                                                  question_sequence = user_relation_question.question_sequence,
                                                  question_name = user_relation_question.question_name,
                                                  question_type= user_relation_question.question_type,
                                                  this_times = user_relation_question.this_times,
                                                  this_points=user_relation_question.this_points,
                                                  is_first_blood = user_relation_question.is_first_blood,
                                                  is_second_blood = user_relation_question.is_second_blood,
                                                  is_third_blood = user_relation_question.is_third_blood,
                                                  contributor = user.name,
                                                  date = user_relation_question.date)
            db_session.add(new_team_relation_question)

        else:

            if user_relation_question. is_first_blood== 0:
                old_team_relation_question.is_first_blood = True

            elif user_relation_question.is_second_blood == 1:
                old_team_relation_question.is_second_blood = True

            elif user_relation_question.is_third_blood == 2:
                old_team_relation_question.is_third_blood = True

    db_session.commit()

        #个人信息导入战队
    team.web_score=team.web_score + user.web_score
    team.pwn_score=team.pwn_score + user.pwn_score
    team.reverse_score=team.reverse_score + user.reverse_score
    team.misc_score=team.misc_score + user.misc_score
    team.crypto_score=team.crypto_score + user.crypto_score
    team.score=team.score + user.score

    team.web_times=team.web_times + user.web_times
    team.pwn_times=team.pwn_times + user.pwn_times
    team.reverse_times=team.reverse_times + user.reverse_times
    team.misc_times=team.misc_times + user.misc_times
    team.crypto_times=team.crypto_times + user.crypto_times
    team.total_times=team.total_times + user.total_times

    team.first_blood_times=team.first_blood_times + user.first_blood_times
    team.second_blood_times=team.second_blood_times + user.second_blood_times
    team.third_blood_times=team.third_blood_times + user.third_blood_times
    ###########################################################################################################
    team.member_count = team.member_count + 1
        #这里不会对member_count++，因为本身设置其默认值为1
    db_session.commit()

    #加入战队消息
    for member in team.member_of_team:
        if member == user:

            new_message = Message(title="成功加入战队",
                                    contents="战队："+team_leader.team_name+" 的队长："+team_leader.name+" 同意了你的战队申请！您可以点击右上方查看自己的战队信息",
                                    time=datetime.now(),
                                    receiver=user.name,
                                    sender=team_leader.name,
                                    type="team_agree")
            db_session.add(new_message)
            db_session.commit()

        else:
            new_message = Message(title="战队加入新成员",
                        contents="尊敬的"+member.name+"：\n"
                                    "    您的战队："+
                                    member.team_name+" 新增了一位新成员："+
                                    user.name+" 您可在战队信息界面查看他的个人信息。",
                        time=datetime.now(),
                        receiver=member.name,
                        sender="系统",
                        type="system")
            db_session.add(new_message)
            db_session.commit()

    #1232323233232 team没有给人

    return redirect(url_for('home_page.message_detail',id=id,message_sequence=message_sequence))

@home_page.route('/message/refuse_join_in/<id>/<applicant_name>/<message_sequence>')
@login_required
def refuse_join_in(id,applicant_name,message_sequence):
    user = db_session.query(User).filter(User.sequence == id).first()
    message = db_session.query(Message).filter(Message.sequence == message_sequence).first()
    applicant = db_session.query(User).filter(User.name == applicant_name).first()
    
    message.is_dealt = True
    db_session.commit()
    
    new_message = Message(title="战队拒绝加入",
                            contents="战队："+user.team_name+" 的队长："+user.name+" 拒绝了你的战队申请。",
                            time=datetime.now(),
                            receiver=applicant.name,
                            sender=user.name,
                            type="team_refuse")
    db_session.add(new_message)
    db_session.commit()

    return redirect(url_for('home_page.message_detail',id=id,message_sequence=message_sequence))

# 发布writeup
@home_page.route("/publish/<id>/<question_id>", methods=["GET", "POST"])
@login_required
def publish(id,question_id):
    user = db_session.query(User).filter(User.sequence == id).first()
    question = db_session.query(Question).filter(Question.sequence == question_id).first()
    if request.method == "POST":
        #一人一题只能发一个writeup吧，如果还要发那就直接是修改
        old_writeup = db_session.query(Article).filter(Article.user_name == user.name and Article.question_id == question_id).first()
        if not old_writeup:
            # 获取博客内容
            title = request.form.get("title")
            TextContent = request.form.get("TextContent")
            data = Article(title=title, body=TextContent,user_name=user.name,question_id=question_id)
            db_session.add(data)
            db_session.commit()
            flash("发布成功！")
        else:
            old_writeup.title = request.form.get("title")
            old_writeup.TextContent = request.form.get("TextContent")
            old_writeup.body_html = markdown.markdown(old_writeup.TextContent)
            db_session.commit()
            flash("修改成功！")

    return render_template('/homepage_files/writeup_publish.html',id=id,user=user,question=question)

#writeup列表
@home_page.route("/writeup_list/<id>")
@login_required
def writeup_list(id):
    user = db_session.query(User).filter(User.sequence == id).first()
    Writeups = db_session.query(Article).filter().all()

    return render_template('/homepage_files/writeup_list.html',id=id,user=user,Writeups=Writeups)


#writeup详情
@home_page.route("/writeup_detail/<id>/<question_id>")
@login_required
def writeup_detail(id,question_id):
    user = db_session.query(User).filter(User.sequence == id).first()
    writeup = db_session.query(Article).filter(Article.question_id == question_id).first()

    return render_template('/homepage_files/writeup_detail.html',id=id,user=user,writeup=writeup)


# 查看博客
@home_page.route("/searchHtml", methods=["GET", "POST"])
@login_required
def searchHtml():
    if request.method == "GET":
        dataInfo = db_session.query(Article).filter().all()
        info = dataInfo[0].body_html
        return render_template("/homepage_files/writeup_detail.html", info=info)

    if request.method == "POST":
        # 获取博客内容，返回前端
        title = request.form.get("title")
        # 模糊查询
        dataInfo = db_session.query(Article).filter(Article.title.like("%" + title + "%")).all()
        if not dataInfo:
            info = "没有找到你搜索的博客标题，请输入正确的标题"
            return render_template("/homepage_files/writeup_detail.html", info=info)
        info = dataInfo[0].body_html
        return render_template("/homepage_files/writeup_detail.html", info=info)


# 同域上传图片
@home_page.route('/upload/', methods=['POST'])
@login_required
def upload():
    file = request.files.get('editormd-image-file')
    if not file:
        res = {
            'success': 0,
            'message': '上传失败'
        }
    else:
        ex = os.path.splitext(file.filename)[1]
        filename = datetime.now().strftime('%Y%m%d%H%M%S') + ex
        file.save(".\\app\\static\\upload\\{}".format(filename))
        res = {
            'success': 1,
            'message': '上传成功',
            'url': url_for('home_page.image', name=filename)
        }
    return jsonify(res)


# 跨域上传图片
@home_page.route('/uploads/', methods=['POST'])
@login_required
def uploads():
    file = request.files.get('editormd-image-file')
    if not file:
        res = {
            'success': 0,
            'message': '上传失败'
        }
    else:
        # ex = os.path.splitext(file.filename)[1]
        # filename = datetime.now().strftime('%Y%m%d%H%M%S') + ex
        # file.save(".\\app\\static\\upload\\{}".format(filename))
        # filePath = os.path.join('.\\app\\static\\upload', filename)
        # 图片上传七牛云
        imgData = file.read()
        imgUrl = uploadImg(imgData)
        print("七牛云返回图片URL", imgUrl)
        if imgUrl:
            res = {
                'success': 1,
                'message': '上传成功',
                # 跨域上传只需要返回图像imgUrl即可
                'url': imgUrl
            }
        else:
            res = {
                'success': 0,
                'message': '上传失败'
            }
    return jsonify(res)


# 同域给前端Markdown编辑器返回图片二进制对象
@home_page.route('/image/<name>')
@login_required
def image(name):
    with open(os.path.join('.\\app\\static\\upload', name), 'rb') as f:
        resp = Response(f.read(), mimetype="image/jpeg")
    return resp

@home_page.route('/web_one', methods=["GET", "POST"])
@login_required
def web_one():
    form = Web_One_Form()
    if form.validate_on_submit():
        flag = form.flag.data
        if flag == "We1c0m3t0Col0sseoCTFi3Ld":
            flash("flag{We1c0m3t0Col0sseoCTFi3Ld}")

    return render_template('/homepage_files/problems/web-1.html',form = form)