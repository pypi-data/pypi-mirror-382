# -*- coding: utf-8 -*-
import re
import ipaddress
import datetime
from typing import Union, Optional, List


class ValidatorUtils:
    """验证工具类"""
    
    # 常用正则表达式模式
    # 邮箱正则表达式
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    # 手机号正则表达式（中国）
    PHONE_PATTERN = re.compile(r'^1[3-9]\d{9}$')
    # 身份证号正则表达式（中国）
    ID_CARD_PATTERN = re.compile(r'^[1-9]\d{5}(18|19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[0-9Xx]$')
    # URL正则表达式
    URL_PATTERN = re.compile(r'^https?://(www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\\+.~#?&//=]*)$')
    # 中文字符正则表达式
    CHINESE_CHAR_PATTERN = re.compile(r'[\u4e00-\u9fa5]+')
    # 特殊字符正则表达式
    SPECIAL_CHAR_PATTERN = re.compile(r'[!@#$%^&*(),.?":{}|<>]')
    # 纯数字正则表达式
    DIGIT_PATTERN = re.compile(r'^\d+$')
    # 整数正则表达式
    INTEGER_PATTERN = re.compile(r'^-?\d+$')
    # 浮点数正则表达式
    FLOAT_PATTERN = re.compile(r'^-?\d+\.\d+$')
    
    @staticmethod
    def is_email(value: str) -> bool:
        """验证是否为有效的邮箱地址
        
        Args:
            value: 要验证的字符串
        
        Returns:
            是否为有效邮箱地址
        """
        if not isinstance(value, str):
            return False
        return bool(ValidatorUtils.EMAIL_PATTERN.match(value))
    
    @staticmethod
    def is_phone(value: str) -> bool:
        """验证是否为有效的中国手机号
        
        Args:
            value: 要验证的字符串
        
        Returns:
            是否为有效中国手机号
        """
        if not isinstance(value, str):
            return False
        return bool(ValidatorUtils.PHONE_PATTERN.match(value))
    
    @staticmethod
    def is_id_card(value: str) -> bool:
        """验证是否为有效的中国身份证号
        
        此方法仅验证格式和简单的校验位，不保证身份证号真实存在
        
        Args:
            value: 要验证的字符串
        
        Returns:
            是否为有效中国身份证号
        """
        if not isinstance(value, str):
            return False
        
        # 验证格式
        if not ValidatorUtils.ID_CARD_PATTERN.match(value):
            return False
        
        # 验证校验位（简单实现）
        try:
            # 前17位为数字
            if not value[:17].isdigit():
                return False
            
            # 计算校验位
            factors = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
            check_codes = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']
            
            total = sum(int(value[i]) * factors[i] for i in range(17))
            check_code = check_codes[total % 11]
            
            return check_code == value[-1].upper()
        except Exception:
            return False
    
    @staticmethod
    def is_url(value: str) -> bool:
        """验证是否为有效的URL地址
        
        Args:
            value: 要验证的字符串
        
        Returns:
            是否为有效URL地址
        """
        if not isinstance(value, str):
            return False
        return bool(ValidatorUtils.URL_PATTERN.match(value))
    
    @staticmethod
    def is_ipv4(value: str) -> bool:
        """验证是否为有效的IPv4地址
        
        Args:
            value: 要验证的字符串
        
        Returns:
            是否为有效IPv4地址
        """
        if not isinstance(value, str):
            return False
        
        try:
            ipaddress.IPv4Address(value)
            return True
        except ipaddress.AddressValueError:
            return False
    
    @staticmethod
    def is_ipv6(value: str) -> bool:
        """验证是否为有效的IPv6地址
        
        Args:
            value: 要验证的字符串
        
        Returns:
            是否为有效IPv6地址
        """
        if not isinstance(value, str):
            return False
        
        try:
            ipaddress.IPv6Address(value)
            return True
        except ipaddress.AddressValueError:
            return False
    
    @staticmethod
    def is_ip(value: str) -> bool:
        """验证是否为有效的IP地址（IPv4或IPv6）
        
        Args:
            value: 要验证的字符串
        
        Returns:
            是否为有效IP地址
        """
        return ValidatorUtils.is_ipv4(value) or ValidatorUtils.is_ipv6(value)
    
    @staticmethod
    def is_date(value: str, format_str: str = '%Y-%m-%d') -> bool:
        """验证是否为有效的日期字符串
        
        Args:
            value: 要验证的字符串
            format_str: 日期格式
        
        Returns:
            是否为有效日期字符串
        """
        if not isinstance(value, str):
            return False
        
        try:
            datetime.datetime.strptime(value, format_str)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def is_datetime(value: str, format_str: str = '%Y-%m-%d %H:%M:%S') -> bool:
        """验证是否为有效的日期时间字符串
        
        Args:
            value: 要验证的字符串
            format_str: 日期时间格式
        
        Returns:
            是否为有效日期时间字符串
        """
        return ValidatorUtils.is_date(value, format_str)
    
    @staticmethod
    def is_integer(value: Union[str, int, float]) -> bool:
        """验证是否为整数
        
        Args:
            value: 要验证的值
        
        Returns:
            是否为整数
        """
        if isinstance(value, int):
            return True
        if isinstance(value, float):
            return value.is_integer()
        if isinstance(value, str):
            return bool(ValidatorUtils.INTEGER_PATTERN.match(value))
        return False
    
    @staticmethod
    def is_float(value: Union[str, int, float]) -> bool:
        """验证是否为浮点数
        
        Args:
            value: 要验证的值
        
        Returns:
            是否为浮点数
        """
        if isinstance(value, float):
            return not value.is_integer()
        if isinstance(value, str):
            return bool(ValidatorUtils.FLOAT_PATTERN.match(value))
        return False
    
    @staticmethod
    def is_numeric(value: Union[str, int, float]) -> bool:
        """验证是否为数值（整数或浮点数）
        
        Args:
            value: 要验证的值
        
        Returns:
            是否为数值
        """
        if isinstance(value, (int, float)):
            return True
        if isinstance(value, str):
            return ValidatorUtils.is_integer(value) or ValidatorUtils.is_float(value)
        return False
    
    @staticmethod
    def has_chinese(value: str) -> bool:
        """验证字符串是否包含中文字符
        
        Args:
            value: 要验证的字符串
        
        Returns:
            是否包含中文字符
        """
        if not isinstance(value, str):
            return False
        return bool(ValidatorUtils.CHINESE_CHAR_PATTERN.search(value))
    
    @staticmethod
    def is_all_chinese(value: str) -> bool:
        """验证字符串是否全部由中文字符组成
        
        Args:
            value: 要验证的字符串
        
        Returns:
            是否全部由中文字符组成
        """
        if not isinstance(value, str):
            return False
        # 移除可能的空格
        value = value.strip()
        return len(value) > 0 and all('\u4e00' <= char <= '\u9fa5' for char in value)
    
    @staticmethod
    def has_special_char(value: str) -> bool:
        """验证字符串是否包含特殊字符
        
        Args:
            value: 要验证的字符串
        
        Returns:
            是否包含特殊字符
        """
        if not isinstance(value, str):
            return False
        return bool(ValidatorUtils.SPECIAL_CHAR_PATTERN.search(value))
    
    @staticmethod
    def is_length_between(value: str, min_length: int, max_length: int) -> bool:
        """验证字符串长度是否在指定范围内
        
        Args:
            value: 要验证的字符串
            min_length: 最小长度
            max_length: 最大长度
        
        Returns:
            长度是否在指定范围内
        """
        if not isinstance(value, str):
            return False
        return min_length <= len(value) <= max_length
    
    @staticmethod
    def is_username(value: str, min_length: int = 2, max_length: int = 20) -> bool:
        """验证是否为有效的用户名
        
        用户名规则：只能包含字母、数字、下划线，长度在指定范围内
        
        Args:
            value: 要验证的字符串
            min_length: 最小长度
            max_length: 最大长度
        
        Returns:
            是否为有效用户名
        """
        if not isinstance(value, str):
            return False
        # 检查长度
        if not (min_length <= len(value) <= max_length):
            return False
        # 检查字符
        return bool(re.match(r'^[a-zA-Z0-9_]+$', value))
    
    @staticmethod
    def is_password_strong(value: str, min_length: int = 8, 
                          require_upper: bool = True, 
                          require_lower: bool = True, 
                          require_digit: bool = True, 
                          require_special: bool = False) -> bool:
        """验证密码是否足够强
        
        Args:
            value: 要验证的密码字符串
            min_length: 最小长度
            require_upper: 是否要求包含大写字母
            require_lower: 是否要求包含小写字母
            require_digit: 是否要求包含数字
            require_special: 是否要求包含特殊字符
        
        Returns:
            密码是否足够强
        """
        if not isinstance(value, str):
            return False
        
        # 检查长度
        if len(value) < min_length:
            return False
        
        # 检查是否包含大写字母
        if require_upper and not any(char.isupper() for char in value):
            return False
        
        # 检查是否包含小写字母
        if require_lower and not any(char.islower() for char in value):
            return False
        
        # 检查是否包含数字
        if require_digit and not any(char.isdigit() for char in value):
            return False
        
        # 检查是否包含特殊字符
        if require_special and not ValidatorUtils.has_special_char(value):
            return False
        
        return True
    
    @staticmethod
    def is_in_list(value: str, valid_list: List[str], case_sensitive: bool = True) -> bool:
        """验证值是否在指定的列表中
        
        Args:
            value: 要验证的值
            valid_list: 有效值列表
            case_sensitive: 是否区分大小写
        
        Returns:
            值是否在列表中
        """
        if not isinstance(value, str):
            return False
        
        if case_sensitive:
            return value in valid_list
        else:
            value_lower = value.lower()
            return any(item.lower() == value_lower for item in valid_list)
    
    @staticmethod
    def is_mac_address(value: str) -> bool:
        """验证是否为有效的MAC地址
        
        Args:
            value: 要验证的字符串
        
        Returns:
            是否为有效MAC地址
        """
        if not isinstance(value, str):
            return False
        
        # MAC地址格式：XX:XX:XX:XX:XX:XX 或 XX-XX-XX-XX-XX-XX
        pattern = re.compile(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$')
        return bool(pattern.match(value))
    
    @staticmethod
    def is_postal_code(value: str, country: str = 'CN') -> bool:
        """验证是否为有效的邮政编码
        
        Args:
            value: 要验证的字符串
            country: 国家代码，默认为中国（CN）
        
        Returns:
            是否为有效邮政编码
        """
        if not isinstance(value, str):
            return False
        
        # 中国邮政编码是6位数字
        if country.upper() == 'CN':
            return bool(re.match(r'^\d{6}$', value))
        
        # 可以根据需要添加其他国家的邮政编码验证规则
        return False
    
    @staticmethod
    def is_currency(value: str, currency_symbol: str = '¥') -> bool:
        """验证是否为有效的货币格式
        
        Args:
            value: 要验证的字符串
            currency_symbol: 货币符号
        
        Returns:
            是否为有效货币格式
        """
        if not isinstance(value, str):
            return False
        
        # 支持的格式：¥123, ¥123.45, 123元, 123.45元
        pattern = re.compile(rf'^({re.escape(currency_symbol)}|\d+元?)\d+(\.\d{{1,2}})?$')
        return bool(pattern.match(value))
    
    @staticmethod
    def is_hex_color(value: str) -> bool:
        """验证是否为有效的十六进制颜色代码
        
        Args:
            value: 要验证的字符串
        
        Returns:
            是否为有效十六进制颜色代码
        """
        if not isinstance(value, str):
            return False
        
        # 支持 #RGB, #RGBA, #RRGGBB, #RRGGBBAA 格式
        pattern = re.compile(r'^#([A-Fa-f0-9]{3,4}|[A-Fa-f0-9]{6}|[A-Fa-f0-9]{8})$')
        return bool(pattern.match(value))