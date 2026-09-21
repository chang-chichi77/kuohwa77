# -*- coding: UTF-8 -*-
import pymysql
from pymysql.cursors import DictCursor
import os

class MysqlAccess(object):
    connection_config = None

    @classmethod
    def initialise(cls):
        """初始化資料庫連線設定"""
        cls.connection_config = {
            'host': os.getenv('MYSQL_HOST', '127.0.0.1'),
            'port': int(os.getenv('MYSQL_PORT', 3306)),
            'user': os.getenv('MYSQL_USER', 'root'),
            'password': os.getenv('MYSQL_PASSWORD', 'root'),
            'database': os.getenv('MYSQL_DB', 'kuohwa_db'),
            'charset': 'utf8mb4',
            'autocommit': True,
            'cursorclass': DictCursor
        }

    @classmethod
    def get_connection(cls):
        """取得資料庫連線"""
        if not cls.connection_config:
            cls.initialise()
        return pymysql.connect(**cls.connection_config)

    @classmethod
    def query(cls, sql, params=None):
        """執行 SELECT 查詢"""
        conn = cls.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql, params or [])
                return cursor.fetchall()
        finally:
            conn.close()

    @classmethod
    def execute(cls, sql, params=None):
        """執行 INSERT / UPDATE / DELETE"""
        conn = cls.get_connection()
        try:
            with conn.cursor() as cursor:
                affected_rows = cursor.execute(sql, params or [])
                return affected_rows
        finally:
            conn.close()