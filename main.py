# -*- coding: utf-8 -*-


"""
File   : 
Date   :2021/11/21
Author :vingurzhou
Project:demoProject
Product:PyCharm 
Details:

"""
from apps import App

app = App().app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
