from enum import Enum
from typing import Union

class YiEnum(Enum):
    
    @classmethod
    def names(cls) -> list:
        return [item.name for item in cls]

    @classmethod
    def values(cls) -> list:
        return [item.value for item in cls]
    
    @classmethod
    def has(cls, val: Union[str, int]) -> bool:
        for item in cls:
            if item.value == val:
                return True
        return False
    
    @classmethod
    def create(cls, val: Union[str, int]) -> 'YiEnum':
        if isinstance(val, str):
            val = val.strip().lower()
        for item in cls:
            if item.value == val:
                return item
        raise ValueError(f"{val} is not a valid {cls.__name__}")


class DB_TYPE(YiEnum):
    """数据库类型枚举"""
    REDIS = 'redis'
    MYSQL = 'mysql'
    MSSQL = 'mssql' 
    
class YES_NO(YiEnum):
    """是/否 枚举"""
    YES = '1'
    NO = '0'
    
class YES_NO_INT(YiEnum):
    """是/否 枚举，整数值"""
    YES = 1
    NO = 0
    
class TRUE_FALSE(YiEnum):
    """真/假 枚举"""
    TRUE = 'true'
    FALSE = 'false'
    
class DATE_FORMAT(YiEnum):
    """日期时间格式枚举"""
    PRESION = '%Y-%m-%d %H:%M:%S.%f'
    DATETIME = '%Y-%m-%d %H:%M:%S'
    DATE = '%Y-%m-%d'
    TIME = '%H:%M:%S'
    
class REPEAT_TYPE(YiEnum):
    MINUTE = 'minute'
    HOUR = 'hour'
    DAY = 'day'
    MONTH = 'month'
    WEEK = 'week'
    YEAR = 'year'