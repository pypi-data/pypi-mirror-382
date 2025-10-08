from datetime import datetime
from typing import Any, Dict, Optional
from sqlalchemy import Engine, MetaData, Table, text, bindparam
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import sqlalchemy.exc
import polars as pl

from yitool.log import logger
from yitool.const import __ENV__
from yitool.enums import DB_TYPE
from yitool.yi_db import YiDB

# 数据库引擎缓存global变量
charset_engine_map: Dict[str, Dict[str, Engine]] = {}
engine_map: Dict[str, Dict[str, Engine]] = {}
meta_table_map: Dict[str, Table] = {}

def get_engine(db_type: str, db_name: str, env_file: str = __ENV__, charset: Optional[str] = None) -> Engine:
    """ 获取数据库引擎 """
    if charset is not None:
        global charset_engine_map
        if db_type not in charset_engine_map:
            charset_engine_map[db_type] = {}
        if db_name not in charset_engine_map[db_type]:
            engine = YiDB.create_engine(db_name, db_type, env_file=env_file, charset=charset)
            charset_engine_map[db_type][db_name] = engine
        return charset_engine_map[db_type][db_name]
    global engine_map
    if db_type not in engine_map:
        engine_map[db_type] = {}
    if db_name not in engine_map[db_type]:
        engine = YiDB.create_engine(db_name, db_type, env_file=env_file)
        engine_map[db_type][db_name] = engine
    return engine_map[db_type][db_name]


class DB:
    def __init__(self, env_path: str = __ENV__, db_type: str = DB_TYPE.MYSQL.value):
        self._env_path = env_path
        self._db_type = db_type
        self._engine: Optional[Engine] = None
        self._db: Optional[YiDB] = None

    def init(self) -> YiDB:
        self._engine = get_engine(self._db_type, self._env_path)
        self._db = YiDB(self._engine)
        return self._db

    @property
    def engine(self) -> Optional[Engine]:
        return self._engine

    @property
    def db(self) -> Optional[YiDB]:
        return self._db

    @property
    def closed(self) -> bool:
        return self._db is None or self._db.closed

    def _ensure_db_initialized(self) -> bool:
        """ 确保数据库连接已初始化 """
        if self.closed:
            self.init()
        return self._db is not None

    def execute(self, sql: str) -> bool:
        if not self._ensure_db_initialized():
            return False
        try:
            with self._engine.connect() as conn:
                conn.execute(text(sql))
            return True
        except SQLAlchemyError as err:
            logger.error(f"Error occurred while executing SQL: {sql}, Error: {err}")
            return False

    def drop_table(self, table_name: str) -> bool:
        if not self._ensure_db_initialized():
            return False
        try:
            with self._engine.connect() as conn:
                conn.execute(text(f'DROP TABLE IF EXISTS {table_name}'))
            return True
        except SQLAlchemyError as err:
            logger.error(f"Error occurred while dropping table: {table_name}, Error: {err}")
            return False

    def exists(self, table_name: str) -> bool:
        if not self._ensure_db_initialized():
            return False
        return self._db.exists(table_name)

    def truncate(self, table_name: str) -> bool:
        if not self._ensure_db_initialized():
            return False
        if not self.exists(table_name):
            return False
        try:
            with self._engine.connect() as conn:
                conn.execute(text(f'TRUNCATE TABLE {table_name}'))
            return True
        except SQLAlchemyError as err:
            logger.error(f"Error occurred while truncating table: {table_name}, Error: {err}")
            return False

    def read(self, sql: str, schema_overrides=None) -> Optional[pl.DataFrame]:
        if not self._ensure_db_initialized():
            return None
        try:
            df = self._db.read(sql, schema_overrides=schema_overrides)
            return df
        except SQLAlchemyError as err:
            logger.error(f"Error occurred while reading data with SQL: {sql}, Error: {err}")
            return pl.DataFrame()  # 统一返回空DataFrame以避免None处理

    def write(self, df: pl.DataFrame, table_name: str, if_table_exists: str = 'append') -> int:
        if not self._ensure_db_initialized():
            return 0
        try:
            num = self._db.write(df, table_name, if_table_exists=if_table_exists)
            return num
        except SQLAlchemyError as err:
            logger.error(f"Error occurred while writing data to table: {table_name}, Error: {err}")
            return 0