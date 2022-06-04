# -*- coding: utf-8 -*-


"""
File   :view
Author :wezhou
Date   :2021/11/13
Product:PyCharm
Project:demoProject
Details:

"""
import flask
from flask import send_from_directory, request, redirect, url_for, flash, render_template

from apps.fund import Fund

fund_blueprint = flask.Blueprint('fund', __name__, template_folder='../../templates', static_folder='../../static')


@fund_blueprint.route('/<fund>')
def show(fund):
    try:
        lst = fund.split(',')
        # try:
        if len(lst) == 1:
            f = Fund(fund)
            f.spider_single_fund()
            # html_str = flask.render_template('/fund/index.html', src=f"../../../static/js/{fund}.js",text=f.text,data=f.data,fund=fund)
            html_str = flask.render_template('/fund/index.html', text=f.text, data=f.data, fund=fund)
            response = flask.Response(html_str)
            return response
        else:
            f = Fund(fund.split(','))
            f.funds = f.funds[0]
            f.compare_funds()
            html_str = flask.render_template('/fund/index2.html', datas=f.datas)
            response = flask.Response(html_str)
            return response
    except:
        return render_template("/404.html"), 404
    # except:
    #     flash('请确认输入是否正确！', 'danger')
    #     return redirect(url_for('user.login'))


# @fund_blueprint.route('/<funds>')
# def compare(funds):
#     funds = funds.replace('_', ',')
#     # f = Fund(funds)
#     exec(f'f = Fund({funds})')
#     f.compare_funds()
#     html_str = flask.render_template('/fund/index2.html', datas=f.datas)
#     response = flask.Response(html_str)
#     return response


@fund_blueprint.route('/download<fund>')
def download(fund):
    return send_from_directory(r"../static/data", f"{fund}.csv", as_attachment=True)


@fund_blueprint.route('/dashboard', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':  # 如果提交表单，并字段验证通过
        # 从表单中获取字段
        name = request.form['name']
        lst = name.split(',')
        if len(lst) != 0:
            return redirect(f'/{name}')
        else:
            flash('请确认输入是否正确！', 'danger')
    return render_template('/user/dashboard.html')


@fund_blueprint.route('/<fund>k2')
def predict(fund):
    f = Fund(fund)
    f.spider_single_fund()
    f.predict_fund()
    # html_str = flask.render_template('/fund/index.html', src=f"../../../static/js/{fund}.js",text=f.text,data=f.data,fund=fund)
    html_str = flask.render_template('/fund/index3.html', text=f.text, data=f.data, fund=fund, k2=f.k2, result=f.result)
    response = flask.Response(html_str)
    return response
