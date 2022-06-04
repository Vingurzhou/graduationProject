# -*- coding: utf-8 -*-


"""
File   :__init__.py
Author :wezhou
Date   :2021/11/12
Product:PyCharm
Project:demoProject
Details:

"""
import sys
import traceback
import pymysql


class MysqlUtil(object):
    def __init__(self, sql):
        """
            初始化方法，连接数据库
        """
        host = '139.196.137.117'  # 主机名
        user = 'root'  # 数据库用户名
        password = 'Z00a0319'  # 数据库密码
        database = 'zwz'  # 数据库名称
        port = 4306
        self.db = pymysql.connect(host=host, user=user, password=password, db=database, port=port)  # 建立连接
        self.cursor = self.db.cursor(cursor=pymysql.cursors.DictCursor)  # 设置游标，并将游标设置为字典类型
        self.result = None
        self.results = None
        self.sql = sql

    def insert(self):
        """
            插入数据库
            sql:插入数据库的sql语句
        """
        # noinspection PyBroadException
        try:
            # 执行sql语句
            self.cursor.execute(self.sql)
            # 提交到数据库执行
            self.db.commit()
        except Exception:  # 方法一：捕获所有异常
            # 如果发生异常，则回滚
            print("发生异常", Exception)
            self.db.rollback()
        finally:
            # 最终关闭数据库连接
            self.db.close()

    def fetchone(self):
        """
            查询数据库：单个结果集
            fetchone(): 该方法获取下一个查询结果集。结果集是一个对象
        """
        result = None
        # noinspection PyBroadException
        try:
            # 执行sql语句
            self.cursor.execute(self.sql)
            self.result = self.cursor.fetchone()
        except Exception:  # 方法二：采用traceback模块查看异常
            # 输出异常信息
            traceback.print_exc()
            # 如果发生异常，则回滚
            self.db.rollback()
        finally:
            # 最终关闭数据库连接
            self.db.close()

    def fetchall(self):
        """
            查询数据库：多个结果集
            fetchall(): 接收全部的返回结果行.
        """
        # noinspection PyBroadException
        try:
            # 执行sql语句
            self.cursor.execute(self.sql)
            self.results = self.cursor.fetchall()
        except Exception:  # 方法三：采用sys模块回溯最后的异常
            # 输出异常信息
            info = sys.exc_info()
            print(info[0], ":", info[1])
            # 如果发生异常，则回滚
            self.db.rollback()
        finally:
            # 最终关闭数据库连接
            self.db.close()

    def delete(self):
        """
            删除结果集
        """
        # noinspection PyBroadException
        try:
            # 执行sql语句
            self.cursor.execute(self.sql)
            self.db.commit()
        except Exception:  # 把这些异常保存到一个日志文件中，来分析这些异常
            # 将错误日志输入到目录文件中
            f = open("/log.txt", 'a')
            traceback.print_exc(file=f)
            f.flush()
            f.close()
            # 如果发生异常，则回滚
            self.db.rollback()
        finally:
            # 最终关闭数据库连接
            self.db.close()

    def update(self):
        """
            更新结果集
        """
        # noinspection PyBroadException
        try:
            # 执行sql语句
            self.cursor.execute(self.sql)
            self.db.commit()
        except Exception:
            # 如果发生异常，则回滚
            self.db.rollback()
        finally:
            # 最终关闭数据库连接
            self.db.close()
