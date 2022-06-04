# -*- coding: utf-8 -*-


"""
File   :setting
Author :wezhou
Date   :2021/11/9
Product:PyCharm
Project:demoProject
Details:

"""


# 封装配置的基类
class BaseConfig(object):
    DEBUG = None


# 开发配置
class DevelopmentConfig(BaseConfig):
    DEBUG = True
    ENV = 'development'


# 生产配置
class ProductionConfig(BaseConfig):
    DEBUG = False
    ENV = 'production'


