# -*- coding:utf-8 -*-
import logging
import pymysql
from configs import (MYSQL_HOST, MYSQL_PORT, MYSQL_DATABASE,
                    MYSQL_USER, MYSQL_PASSWD, MYSQL_CHARSET)

logger = logging.getLogger(__name__)


class OracleAccess(object):

    @staticmethod
    def initialise():
        pass

    @staticmethod
    def _get_conn():
        return pymysql.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWD,
            database=MYSQL_DATABASE,
            charset=MYSQL_CHARSET
        )

    @staticmethod
    def query(sql, args=None):
        conn = None
        try:
            conn = OracleAccess._get_conn()
            with conn.cursor() as cursor:
                cursor.execute(sql, args)
                return cursor.fetchall()
        except pymysql.Error as e:
            logger.error(f"MySQL Error: {e}")
            raise
        finally:
            if conn:
                conn.close()

    @staticmethod
    def query_by_offset(sql, offset=0, numrows=20):
        conn = None
        try:
            conn = OracleAccess._get_conn()
            with conn.cursor() as cursor:
                limit_sql = f"{sql} LIMIT {offset}, {numrows}"
                cursor.execute(limit_sql)
                return cursor.fetchall()
        except pymysql.Error as e:
            logger.error(f"MySQL Error: {e}")
            raise
        finally:
            if conn:
                conn.close()

    @staticmethod
    def insert(sql, rows):
        conn = None
        try:
            conn = OracleAccess._get_conn()
            with conn.cursor() as cursor:
                cursor.executemany(sql, rows)
                conn.commit()
        except pymysql.Error as e:
            logger.error(f"MySQL Error: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()

    @staticmethod
    def execute(sql, args=None):
        conn = None
        try:
            conn = OracleAccess._get_conn()
            with conn.cursor() as cursor:
                cursor.execute(sql, args)
                conn.commit()
        except pymysql.Error as e:
            logger.error(f"MySQL Error: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()
