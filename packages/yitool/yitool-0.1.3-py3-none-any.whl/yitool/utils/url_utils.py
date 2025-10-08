# -*- coding: utf-8 -*-

from tornado.escape import url_escape

from yitool.enums import DB_TYPE  # escape特殊字符


class UrlUtils(object):
    """ URL工具类 """

    @staticmethod
    def db_mysql_url(
        username: str,
        password: str,
        host: str,
        port: int,
        database: str,
    ) -> str:
        return f'mysql+pymysql://{username}:{url_escape(password)}@{host}:{port}/{database}'

    @staticmethod
    def db_mssql_url(
        username: str,
        password: str,
        host: str,
        port: int,
        database: str,
    ) -> str:
        # return f"mssql+pymssql://{username}:{url_escape(password)}@{host}:{port}/{database}"
        return f'mssql+pymssql://{username}:{url_escape(password)}@{host}:{port}/{database}?charset=utf8'
        
    @staticmethod
    def url_from_db_type(db_type: str):
        url_fn_dict = {
            DB_TYPE.MYSQL.value: UrlUtils.db_mysql_url,
            DB_TYPE.MSSQL.value: UrlUtils.db_mssql_url,
        }
        if not DB_TYPE.has(db_type):
            raise ValueError(f"不支持的数据库类型: {db_type}")
        return url_fn_dict.get(db_type)