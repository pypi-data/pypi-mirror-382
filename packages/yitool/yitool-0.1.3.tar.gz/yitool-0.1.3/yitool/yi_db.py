import polars as pl
from polars import DataFrame
from time import sleep
from datetime import datetime
from typing import Dict, Optional
from pymysql import OperationalError
from sqlalchemy import Engine, Connection, MetaData, Table, create_engine, inspect, text
from sqlalchemy.engine.reflection import Inspector
from yitool.const import __ENV__
from yitool.enums import DB_TYPE
from yitool.log import logger
from yitool.utils.dict_utils import DictUtils
from yitool.utils.env_utils import EnvUtils
from yitool.utils.url_utils import UrlUtils

DB_CHARSET_GBK = 'cp936'

class YiDB:
    """ 数据库工具，engine 为 sqlalchemy 的 Engine """
    _connection: Connection = None
    _engine: Engine = None

    def __init__(self, engine: Engine):
        self._engine = engine
        self._connection = None
        
    @property
    def engine(self) -> Engine:
        return self._engine
    
    @property
    def connection(self) -> Connection:
        return self._connection
        
    @property
    def closed(self) -> bool:
        return self._connection is None or self._connection.closed

    def connect(self):
        """ 连接数据库 """
        if self.closed:
            self._connection = self._engine.connect()
        return self._connection

    def close(self):
        """ 关闭数据库连接 """
        try:
            if self._connection and not self._connection.closed:
                self._connection.close()
        except Exception as err:
            logger.error(f"close db connection error: {err}")
            
    @property
    def inspector(self) -> Inspector:
        """ 获取数据库检查器 """
        return inspect(self._engine)

    @property
    def metadata(self) -> MetaData:
        """ 获取数据库元数据 """
        return MetaData(bind=self._engine)
    
    @property
    def tables(self) -> Dict[str, Table]:
        """ 获取数据库所有表 """
        meta = self.metadata
        meta.reflect(bind=self._engine)
        return meta.tables
    
    def exists(self, table_name: str) -> bool:
        inspector = inspect(self._engine)
        return table_name in inspector.get_table_names()

    def columns(self, table_name: str) -> Optional[list]:
        """ 获取表的所有列名 """
        if not self.exists(table_name):
            return None
        inspector = inspect(self._engine)
        return inspector.get_columns(table_name)
    
    def column_names(self, table_name: str) -> Optional[list[str]]:
        """ 获取表的所有列名 """
        columns = self.columns(table_name)
        if columns is None:
            return None
        return [col['name'] for col in columns]
    
    def primary_key(self, table_name: str) -> Optional[list[str]]:
        """ 获取表的主键列名 """
        if not self.exists(table_name):
            return None
        pk = self.inspector.get_pk_constraint(table_name)
        return pk.get('constrained_columns', []) if pk else []

    def read(self, query: str, schema_overrides = None, retry_times: int = 3) -> DataFrame:
        """ 从数据库读取数据 """ 
        try:
            df = None
            with self._engine.connect() as conn:
                df = pl.read_database(query, conn, schema_overrides=schema_overrides, infer_schema_length=10000000)
            return df
        except Exception as err:
            logger.error(f"read from db error (query: {query}): {err}")
            self._engine.dispose()
            sleep(3)
            if retry_times <= 0:
                return None
            return self.read(query, schema_overrides, retry_times=retry_times-1)

    def write(self, df: DataFrame, table_name: str, if_table_exists: str = 'append', retry_times: int = 3) -> int:
        """ 写入数据库表 """
        num = 0
        try:
            with self._engine.connect() as conn:
                num = df.write_database(table_name, conn, if_table_exists=if_table_exists)
        except OperationalError as db_error:
            logger.error(f"write to db error (table: {table_name}): {db_error}")
            self._engine.dispose()
            sleep(3)
            if retry_times <= 0:
                return 0
            return self.write(df, table_name, if_table_exists=if_table_exists, retry_times=retry_times-1)
        except Exception as err:
            logger.error(f"write to db error (table: {table_name}): {err}")
            self._engine.dispose()
            sleep(3)
            if retry_times <= 0:
                return 0
            return self.write(df, table_name, if_table_exists=if_table_exists, retry_times=retry_times-1)
        return num

    @staticmethod
    def load_env_values(values: Dict[str, str], db_type: str = DB_TYPE.MYSQL.value) -> Dict[str, str]:
        db_prefix = db_type.upper()
        return {
            'username': DictUtils.get_value_or_raise(values, f'{db_prefix}_USERNAME'),
            'password': DictUtils.get_value_or_raise(values, f'{db_prefix}_PASSWORD'),
            'host': DictUtils.get_value_or_raise(values, f'{db_prefix}_HOST'),
            'port': DictUtils.get_value_or_raise(values, f'{db_prefix}_PORT'),
        }

    @staticmethod
    def create_engine(database: str, db_type_value: str = DB_TYPE.MYSQL.value, env_path: str = __ENV__, charset: Optional[str] = None) -> Engine:
        if not DB_TYPE.has(db_type_value):
            raise ValueError(f"不支持的数据库类型: {db_type_value}")

        values = EnvUtils.dotenv_values(env_path)
        db_values = YiDB.load_env_values(values, db_type_value)
        db_url = UrlUtils.url_from_db_type(db_type_value)(**db_values, database=database)
        logger.debug(f"Connecting to database with URL: {db_url}")
        if db_type_value == DB_TYPE.MSSQL.value:
            if charset is not None:
                return create_engine(db_url, connect_args={ "charset": charset })
            return create_engine(db_url, connect_args={ "charset": 'utf8' })
        else:
            return create_engine(db_url)
    
    @classmethod
    def from_env(cls, database: str, db_type_value: str = DB_TYPE.MYSQL.value, env_path: str = __ENV__, charset: Optional[str] = None) -> 'YiDB':
        engine = cls.create_engine(database, db_type_value, env_path, charset)
        return cls(engine)