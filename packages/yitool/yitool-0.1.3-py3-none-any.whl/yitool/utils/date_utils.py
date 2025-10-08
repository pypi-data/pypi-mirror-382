from datetime import datetime

from yitool.enums import DATE_FORMAT

class DateUtils(object):
    """日期时间工具类"""
    
    @staticmethod
    def is_empty(dt: datetime) -> bool:
        """判断日期时间是否为空"""
        return dt is None
    
    @staticmethod
    def to_timestamp(dt: datetime) -> float:
        """将日期时间转换为时间戳"""
        if DateUtils.is_empty(dt):
            return 0.0
        return dt.timestamp()
    
    @staticmethod
    def from_timestamp(ts: float) -> datetime:
        """将时间戳转换为日期时间"""
        return datetime.fromtimestamp(ts)
    
    @staticmethod
    def format(dt: datetime, fmt: str = DATE_FORMAT.DATETIME.value) -> str:
        """格式化日期时间为字符串"""
        if DateUtils.is_empty(dt):
            return ''
        return dt.strftime(fmt)
        
    @staticmethod
    def parse(date_str: str, fmt: str = DATE_FORMAT.DATETIME.value) -> datetime:
        """将字符串解析为日期时间"""
        if date_str is None or date_str.strip() == '':
            return None
        return datetime.strptime(date_str, fmt)