# -*- coding: utf-8 -*-
from cachetools import cached
import yitool.utils._humps as _humps

class StrUtils(object):
    """字符串工具类"""
    
    @staticmethod
    def is_empty(s: str) -> bool:
        """判断字符串是否为空"""
        return s is None or s.strip() == ''
    
    @staticmethod
    def is_not_empty(s: str) -> bool:
        """判断字符串是否非空"""
        return not StrUtils.is_empty(s)
    
    @staticmethod
    def safe(s: str) -> str:
        """安全获取字符串，避免 None，返回空字符串"""
        return s if s is not None else ''

    # @cached(cache={}, key=lambda str_or_iter: str_or_iter)
    @staticmethod
    def camelize(str_or_iter: str) -> str:
        """Convert string or iterable to camel case."""
        return _humps.camelize(str_or_iter)
    
    @staticmethod
    def decamelize(str_or_iter: str) -> str:
        """Convert string or iterable to snake case."""
        return _humps.decamelize(str_or_iter)
    
    @staticmethod
    def pascalize(str_or_iter: str) -> str:
        """Convert string or iterable to pascal case."""
        return _humps.pascalize(str_or_iter)
    
    @staticmethod
    def kebabize(str_or_iter: str) -> str:
        """Convert string or iterable to kebab case."""
        return _humps.kebabize(str_or_iter)
    
    @staticmethod
    def split(s: str, delimiter: str = ',') -> list:
        """将字符串拆分为数组，使用指定的分隔符"""
        if StrUtils.is_empty(s):
            return []
        return [item.strip() for item in s.split(delimiter) if item.strip()]
    
    @staticmethod
    def camelize_dict_keys(d: dict) -> dict:
        """将字典的键转换为驼峰命名法"""
        if d is None:
            return {}
        return {StrUtils.camelize(k): v for k, v in d.items()}
    
    @staticmethod
    def decamelize_dict_keys(d: dict) -> dict:
        """将字典的键转换为蛇形命名法"""
        if d is None:
            return {}
        return {StrUtils.decamelize(k): v for k, v in d.items()}
    
    @staticmethod
    def camelize_list_of_dicts(lst: list) -> list:
        """将字典列表的键转换为驼峰命名法"""
        if lst is None:
            return []
        return [StrUtils.camelize_dict_keys(item) if isinstance(item, dict) else item for item in lst]
    
    @staticmethod
    def decamelize_list_of_dicts(lst: list) -> list:
        """将字典列表的键转换为蛇形命名法"""
        if lst is None:
            return []
        return [StrUtils.decamelize_dict_keys(item) if isinstance(item, dict) else item for item in lst]
    