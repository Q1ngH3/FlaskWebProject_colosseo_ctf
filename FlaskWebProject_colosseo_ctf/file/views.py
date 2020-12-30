import os
import time
from flask import Flask, render_template, send_from_directory, request, jsonify,flash
from . import file
from flask_wtf.file import FileField, FileRequired, FileAllowed
from FlaskWebProject_colosseo_ctf import app
from flask_wtf import FlaskForm
from wtforms import SubmitField,FileField
from wtforms.validators import DataRequired,EqualTo

'''
UPLOAD_FOLDER = 'upload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER  # 设置文件上传的目标文件夹
basedir = os.path.abspath(os.path.dirname(__file__))  # 获取当前项目的绝对路径
ALLOWED_EXTENSIONS = set(['txt', 'png', 'jpg', 'xls', 'JPG', 'PNG', 'xlsx', 'gif', 'GIF','py','md'])

class UploadForm(FlaskForm):
    photo = FileField('Upload Image', validators=[FileRequired(), FileAllowed(['jpg','jpeg','pdf','md','docx','txt','png'])])
    submit = SubmitField()

# 判断文件是否合法
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@file.route('/api/upload', methods=['POST'], strict_slashes=False)
def api_upload():
    file_dir = os.path.join(basedir, app.config['UPLOAD_FOLDER'])  # 拼接成合法文件夹地址
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)  # 文件夹不存在就创建
    f = request.files['file']  # 从表单的file字段获取文件，myfile为该表单的name值
    if f and allowed_file(f.filename):  # 判断是否是允许上传的文件类型
        fname = f.filename
        ext = fname.rsplit('.', 1)[1]  # 获取文件后缀
        unix_time = int(time.time())
        new_filename = str(unix_time)+'.'+ext   # 修改文件名
        f.save(os.path.join(file_dir, new_filename))  #保存文件到upload目录
        return jsonify({"errno": 0, "errmsg": "Upload Success !!! :)"})
    else:
        return jsonify({"errno": 1001, "errmsg": "Upload Fail...Try again ? ? :("})
'''


@file.route("/download/<filename>",methods=['GET', 'POST'])
def download(filename):
    dirpath = os.path.join(app.root_path, 'file/download')  # 这里是下在目录，从工程的根目录写起，比如你要下载static/js里面的js文件，这里就要写“static/js”
    return send_from_directory(dirpath, filename, as_attachment=True)  # as_attachment=True 一定要写，不然会变成打开，而不是下载

