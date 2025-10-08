# -*- coding: utf-8 -*-
from typing import Any, Union, List, Dict, Optional, Type
import json
import decimal
from datetime import datetime, date, time
from yitool.exceptions import YiToolException


class ConvertUtils:
    """类型转换工具类，提供各种数据类型之间的转换功能"""
    
    @staticmethod
    def to_str(value: Any, default: str = '') -> str:
        """将任意值转换为字符串
        
        Args:
            value: 要转换的值
            default: 转换失败时的默认值
        
        Returns:
            转换后的字符串
        """
        if value is None:
            return default
        try:
            return str(value)
        except Exception:
            return default
    
    @staticmethod
    def to_int(value: Any, default: int = 0) -> int:
        """将任意值转换为整数
        
        Args:
            value: 要转换的值
            default: 转换失败时的默认值
        
        Returns:
            转换后的整数
        """
        if value is None:
            return default
        try:
            if isinstance(value, str):
                # 去除千位分隔符
                value = value.replace(',', '')
            return int(value)
        except Exception:
            return default
    
    @staticmethod
    def to_float(value: Any, default: float = 0.0) -> float:
        """将任意值转换为浮点数
        
        Args:
            value: 要转换的值
            default: 转换失败时的默认值
        
        Returns:
            转换后的浮点数
        """
        if value is None:
            return default
        try:
            if isinstance(value, str):
                # 去除千位分隔符
                value = value.replace(',', '')
            return float(value)
        except Exception:
            return default
    
    @staticmethod
    def to_bool(value: Any, default: bool = False) -> bool:
        """将任意值转换为布尔值
        
        Args:
            value: 要转换的值
            default: 转换失败时的默认值
        
        Returns:
            转换后的布尔值
        
        Note:
            - 对于字符串，将 'true', 'yes', '1', 'y', 't' (不区分大小写) 转换为 True
            - 对于字符串，将 'false', 'no', '0', 'n', 'f' (不区分大小写) 转换为 False
            - 对于数字，0 转换为 False，非 0 转换为 True
        """
        if value is None:
            return default
        
        if isinstance(value, bool):
            return value
        
        if isinstance(value, (int, float)):
            return value != 0
        
        if isinstance(value, str):
            value = value.lower().strip()
            if value in ('true', 'yes', '1', 'y', 't'):
                return True
            if value in ('false', 'no', '0', 'n', 'f'):
                return False
        
        return default
    
    @staticmethod
    def to_list(value: Any, default: List = None) -> List:
        """将任意值转换为列表
        
        Args:
            value: 要转换的值
            default: 转换失败时的默认值
        
        Returns:
            转换后的列表
        """
        if default is None:
            default = []
            
        if value is None:
            return default
        
        if isinstance(value, list):
            return value
        
        if isinstance(value, (str, bytes)):
            # 尝试解析JSON字符串
            try:
                result = json.loads(value)
                if isinstance(result, list):
                    return result
            except (json.JSONDecodeError, TypeError):
                pass
            # 单个字符串转为单元素列表
            return [value]
        
        # 其他类型尝试迭代转换
        try:
            return list(value)
        except Exception:
            # 无法迭代则转为单元素列表
            return [value]
    
    @staticmethod
    def to_dict(value: Any, default: Dict = None) -> Dict:
        """将任意值转换为字典
        
        Args:
            value: 要转换的值
            default: 转换失败时的默认值
        
        Returns:
            转换后的字典
        """
        if default is None:
            default = {}
            
        if value is None:
            return default
        
        if isinstance(value, dict):
            return value
        
        if isinstance(value, (str, bytes)):
            # 尝试解析JSON字符串
            try:
                result = json.loads(value)
                if isinstance(result, dict):
                    return result
            except (json.JSONDecodeError, TypeError):
                pass
        
        # 对于有__dict__属性的对象，转换其属性
        if hasattr(value, '__dict__'):
            return dict(value.__dict__)
        
        # 对于有items()方法的对象，尝试转换
        try:
            if callable(getattr(value, 'items', None)):
                return dict(value)
        except Exception:
            pass
        
        return default
    
    @staticmethod
    def to_datetime(value: Any, format_str: str = None, default: datetime = None) -> Optional[datetime]:
        """将任意值转换为datetime对象
        
        Args:
            value: 要转换的值
            format_str: 日期时间格式字符串，如果为None则尝试自动解析
            default: 转换失败时的默认值
        
        Returns:
            转换后的datetime对象或默认值
        """
        if value is None:
            return default
        
        if isinstance(value, datetime):
            return value
        
        if isinstance(value, (date, time)):
            if isinstance(value, date):
                return datetime.combine(value, time.min)
            else:
                return datetime.combine(date.today(), value)
        
        try:
            if isinstance(value, (int, float)):
                # 时间戳转换
                return datetime.fromtimestamp(value)
            
            str_value = str(value)
            if format_str:
                return datetime.strptime(str_value, format_str)
            
            # 尝试自动解析常见格式
            for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M', 
                        '%Y/%m/%d %H:%M:%S', '%Y/%m/%d', '%Y-%m-%d']:
                try:
                    return datetime.strptime(str_value, fmt)
                except ValueError:
                    continue
            
            # 尝试ISO格式
            return datetime.fromisoformat(str_value.replace('Z', '+00:00'))
        except Exception:
            return default
    
    @staticmethod
    def to_date(value: Any, format_str: str = None, default: date = None) -> Optional[date]:
        """将任意值转换为date对象
        
        Args:
            value: 要转换的值
            format_str: 日期格式字符串，如果为None则尝试自动解析
            default: 转换失败时的默认值
        
        Returns:
            转换后的date对象或默认值
        """
        if value is None:
            return default
        
        if isinstance(value, date):
            if isinstance(value, datetime):
                return value.date()
            return value
        
        try:
            if isinstance(value, (int, float)):
                # 时间戳转换
                return datetime.fromtimestamp(value).date()
            
            str_value = str(value)
            if format_str:
                return datetime.strptime(str_value, format_str).date()
            
            # 尝试自动解析常见格式
            for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%Y%m%d']:
                try:
                    return datetime.strptime(str_value.split(' ')[0].split('T')[0], fmt).date()
                except ValueError:
                    continue
            
            # 尝试ISO格式
            dt = datetime.fromisoformat(str_value.replace('Z', '+00:00'))
            return dt.date()
        except Exception:
            return default
    
    @staticmethod
    def to_decimal(value: Any, precision: int = None, default: decimal.Decimal = None) -> Optional[decimal.Decimal]:
        """将任意值转换为Decimal对象
        
        Args:
            value: 要转换的值
            precision: 保留的小数位数，为None时不做精度处理
            default: 转换失败时的默认值
        
        Returns:
            转换后的Decimal对象或默认值
        """
        if value is None:
            return default
        
        if isinstance(value, decimal.Decimal):
            result = value
        else:
            try:
                if isinstance(value, str):
                    # 去除千位分隔符
                    value = value.replace(',', '')
                result = decimal.Decimal(str(value))
            except Exception:
                return default
        
        # 处理精度
        if precision is not None:
            result = result.quantize(decimal.Decimal(f'0.{"0" * precision}'))
        
        return result
    
    @staticmethod
    def convert_type(value: Any, target_type: Type, default: Any = None) -> Any:
        """将值转换为指定类型
        
        Args:
            value: 要转换的值
            target_type: 目标类型
            default: 转换失败时的默认值
        
        Returns:
            转换后的值或默认值
        
        Raises:
            YiToolException: 当不支持的目标类型时抛出
        """
        if value is None:
            return default
        
        # 如果已经是目标类型，直接返回
        if isinstance(value, target_type):
            return value
        
        # 根据目标类型选择转换方法
        try:
            if target_type == str:
                return ConvertUtils.to_str(value)
            elif target_type == int:
                return ConvertUtils.to_int(value)
            elif target_type == float:
                return ConvertUtils.to_float(value)
            elif target_type == bool:
                return ConvertUtils.to_bool(value)
            elif target_type == list:
                return ConvertUtils.to_list(value)
            elif target_type == dict:
                return ConvertUtils.to_dict(value)
            elif target_type == datetime:
                return ConvertUtils.to_datetime(value)
            elif target_type == date:
                return ConvertUtils.to_date(value)
            elif target_type == decimal.Decimal:
                return ConvertUtils.to_decimal(value)
            else:
                # 尝试直接转换
                return target_type(value)
        except Exception:
            return default