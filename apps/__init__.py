# -*- coding: utf-8 -*-


"""
File   :__init__.py
Author :wezhou
Date   :2021/11/12
Product:PyCharm
Project:demoProject
Details:

"""
import flask
from apps.fund.view import fund_blueprint
from apps.user.view import user_blueprint
from apps.config import DevelopmentConfig


class App(object):
    def __init__(self):
        app = flask.Flask(__name__, template_folder='../templates', static_folder='../static')
        app.config.from_object(DevelopmentConfig)
        app.register_blueprint(user_blueprint)
        app.register_blueprint(fund_blueprint)
        app.add_template_filter(f=self.replace_word, name='replace')
        app.config["SECRET_KEY"] = '79537d00f4834892986f09a100aa1edf'  # CSRF保护

        self.app = app

        @app.route('/favicon.ico')
        def favicon():
            return app.send_static_file('images/favicon.ico')

        @app.template_filter('add')
        def add_word(value):
            value = value + 'have_been_added'
            return value

    @staticmethod
    def replace_word(value):
        value = value.replace(value, 'have_been_replaced')
        return value
