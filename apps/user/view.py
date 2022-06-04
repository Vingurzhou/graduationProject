# -*- coding: utf-8 -*-


"""
File   :view
Author :wezhou
Date   :2021/11/12
Product:PyCharm
Project:demoProject
Details:

"""
from functools import wraps
import smtplib
from email.mime.text import MIMEText
import pandas
from flask import *
from apps.extend import MysqlUtil

user_blueprint = Blueprint('user', __name__, template_folder='../../templates')
app = Flask(__name__)


# 首页
@user_blueprint.route('/')
def index():
    return render_template('/user/home.html')  # 渲染模板


# 关于本站
@user_blueprint.route('/about')
def about():
    return render_template('/user/about.html')  # 渲染模板


# 用户登录
@user_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if "logged_in" in session:  # 如果已经登录，则直接跳转到控制台
        return redirect(url_for("user.dashboard"))

    if request.method == 'POST':  # 如果提交表单，并字段验证通过
        # 从表单中获取字段
        username = request.form['username']
        password_candidate = request.form['password']
        try:
            sql = "SELECT * FROM users  WHERE username = '%s'" % username  # 根据用户名查找user表中记录
            m = MysqlUtil(sql)  # 实例化数据库操作类
            m.fetchone()  # 获取一条记录
            result = m.result
            assert password_candidate == result['password']  # 用户填写的密码
            # 写入session
            session['logged_in'] = True
            session['username'] = username
            flash('登录成功！', 'success')  # 闪存信息
            return redirect(url_for('user.dashboard'))  # 跳转到控制台
        except:  # 如果密码错误
            flash('用户名或密码不正确！', 'danger')  # 闪存信息

    return render_template('/user/login.html')


# 用户注册
@user_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    if "logged_in" in session:  # 如果已经登录，则直接跳转到控制台
        return redirect(url_for("user.dashboard"))

    if request.method == 'POST':  # 如果提交表单，并字段验证通过
        # 从表单中获取字段
        username = request.form['username']
        password_candidate = request.form['password']
        re_password_candidate = request.form['re_password']
        area = request.form['area']
        # 对比用户填写的密码和数据库中记录密码是否一致
        if password_candidate == re_password_candidate:
            sql = f"""INSERT INTO users(username,password,area) VALUES ('{username}', '{password_candidate}','{area}')"""
            m = MysqlUtil(sql)  # 实例化数据库操作类
            m.insert()

            _user = "786000694@qq.com"
            _pwd = "dslnnxvzuoarbcbi"
            _to = request.form['email']

            msg = MIMEText(f"账号:{username}，密码:{password_candidate},http://127.0.0.1:5000")
            msg["Subject"] = "恭喜你注册成功"
            msg["From"] = _user
            msg["To"] = _to

            with smtplib.SMTP_SSL("smtp.qq.com", 465) as s:
                s.login(_user, _pwd)
                s.sendmail(_user, _to, msg.as_string())
            flash('注册成功！', 'success')  # 闪存信息
            return redirect(url_for('user.login'))  # 跳转到控制台
        else:  # 如果密码错误
            flash('请确认输入是否正确！', 'danger')  # 闪存信息

    return render_template('/user/register.html')


# 如果用户已经登录
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:  # 判断用户是否登录
            return f(*args, **kwargs)  # 如果登录，继续执行被装饰的函数
        else:  # 如果没有登录，提示无权访问
            flash('无权访问，请先登录', 'danger')
            return redirect(url_for('login'))

    return wrap


# 退出
@user_blueprint.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('您已成功退出', 'success')  # 闪存信息
    return redirect(url_for('user.login'))  # 跳转到登录页面


# 控制台
@user_blueprint.route('/dashboard')
@is_logged_in
def dashboard():
    if session['username'] == 'zhouwenzhe':
        return redirect(url_for('user.admin'))
    else:
        sql = "SELECT * FROM fund_relationship"  # 查找基金信息
        m = MysqlUtil(sql)  # 实例化数据库操作类
        m.fetchall()  # 查找所有基金
        result = m.results
        return render_template('/user/dashboard.html', articles=result)


@user_blueprint.route('/admin')
def admin():
    assert session['username'] == 'zhouwenzhe'
    sql = "SELECT * FROM users"
    m = MysqlUtil(sql)  # 实例化数据库操作类
    m.fetchall()
    result = m.results
    df = pandas.DataFrame(result)
    data = []
    for area, group in df.groupby('area'):
        data.append({'value': len(group), 'name': area})
    return render_template('/user/admin.html', users=result, data=data)


# 删除
@user_blueprint.route('/delete_user', methods=['POST'])
@is_logged_in
def delete_user():
    sql = "DELETE FROM users WHERE username = '%s' " % (request.form['username'])  # 执行删除笔记的SQL语句
    db = MysqlUtil(sql)  # 实例化数据库操作类
    db.delete()  # 删除数据库
    flash('删除成功', 'success')  # 闪存信息
    return redirect(url_for('user.dashboard'))  # 跳转到控制台


@user_blueprint.route('/edit_user', methods=['POST'])
@is_logged_in
def edit_user():
    sql = "UPDATE users SET username='%s', password='%s',area='%s' WHERE username='%s' and password = '%s' and area='%s'" % (
        request.form['username'], request.form['password'], request.form['area'], request.form['username2'],
        request.form['password2'], request.form['area2'])
    db = MysqlUtil(sql)  # 实例化数据库操作类
    db.update()
    flash('保存成功', 'success')  # 闪存信息
    return redirect(url_for('user.dashboard'))  # 跳转到控制台


# 404页面
@user_blueprint.errorhandler(404)
def page_not_found(error):
    """
    404
    """
    return render_template("/404.html"), 404
