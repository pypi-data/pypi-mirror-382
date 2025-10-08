# -*- coding: utf-8 -*-
import random
import string
import secrets
import uuid
from typing import List, Optional, Union, Any


class RandomUtils:
    """随机工具类，提供各种随机数、随机字符串和随机选择的功能"""
    
    # 定义字符集常量
    LOWERCASE_CHARS = string.ascii_lowercase  # 小写字母
    UPPERCASE_CHARS = string.ascii_uppercase  # 大写字母
    DIGITS = string.digits  # 数字
    SYMBOLS = string.punctuation  # 特殊符号
    ALL_CHARS = LOWERCASE_CHARS + UPPERCASE_CHARS + DIGITS + SYMBOLS  # 所有字符
    
    @staticmethod
    def random_int(min_value: int = 0, max_value: int = 99999999) -> int:
        """生成指定范围内的随机整数
        
        Args:
            min_value: 最小值（包含）
            max_value: 最大值（包含）
        
        Returns:
            随机整数
        
        Raises:
            ValueError: 如果min_value大于max_value
        """
        if min_value > max_value:
            raise ValueError("min_value must be less than or equal to max_value")
        return random.randint(min_value, max_value)
    
    @staticmethod
    def random_float(min_value: float = 0.0, max_value: float = 1.0, precision: int = 2) -> float:
        """生成指定范围内的随机浮点数
        
        Args:
            min_value: 最小值
            max_value: 最大值
            precision: 小数位数
        
        Returns:
            随机浮点数
        
        Raises:
            ValueError: 如果min_value大于max_value或precision小于0
        """
        if min_value > max_value:
            raise ValueError("min_value must be less than or equal to max_value")
        if precision < 0:
            raise ValueError("precision must be non-negative")
        
        random_value = random.uniform(min_value, max_value)
        # 四舍五入到指定精度
        return round(random_value, precision)
    
    @staticmethod
    def random_str(length: int = 10, use_lowercase: bool = True, use_uppercase: bool = True,
                  use_digits: bool = True, use_symbols: bool = False, custom_chars: str = None) -> str:
        """生成随机字符串
        
        Args:
            length: 字符串长度
            use_lowercase: 是否使用小写字母
            use_uppercase: 是否使用大写字母
            use_digits: 是否使用数字
            use_symbols: 是否使用特殊符号
            custom_chars: 自定义字符集，如果提供则忽略其他字符集选项
        
        Returns:
            随机字符串
        
        Raises:
            ValueError: 如果length小于1或没有选择任何字符集
        """
        if length < 1:
            raise ValueError("length must be at least 1")
        
        # 确定字符集
        if custom_chars:
            chars = custom_chars
        else:
            chars = ''
            if use_lowercase:
                chars += RandomUtils.LOWERCASE_CHARS
            if use_uppercase:
                chars += RandomUtils.UPPERCASE_CHARS
            if use_digits:
                chars += RandomUtils.DIGITS
            if use_symbols:
                chars += RandomUtils.SYMBOLS
        
        if not chars:
            raise ValueError("No character set selected. Please enable at least one character type or provide custom_chars.")
        
        # 生成随机字符串
        return ''.join(random.choice(chars) for _ in range(length))
    
    @staticmethod
    def random_secure_str(length: int = 10, use_lowercase: bool = True, use_uppercase: bool = True,
                         use_digits: bool = True, use_symbols: bool = False, custom_chars: str = None) -> str:
        """生成加密安全的随机字符串
        
        Args:
            length: 字符串长度
            use_lowercase: 是否使用小写字母
            use_uppercase: 是否使用大写字母
            use_digits: 是否使用数字
            use_symbols: 是否使用特殊符号
            custom_chars: 自定义字符集，如果提供则忽略其他字符集选项
        
        Returns:
            加密安全的随机字符串
        
        Raises:
            ValueError: 如果length小于1或没有选择任何字符集
        """
        if length < 1:
            raise ValueError("length must be at least 1")
        
        # 确定字符集
        if custom_chars:
            chars = custom_chars
        else:
            chars = ''
            if use_lowercase:
                chars += RandomUtils.LOWERCASE_CHARS
            if use_uppercase:
                chars += RandomUtils.UPPERCASE_CHARS
            if use_digits:
                chars += RandomUtils.DIGITS
            if use_symbols:
                chars += RandomUtils.SYMBOLS
        
        if not chars:
            raise ValueError("No character set selected. Please enable at least one character type or provide custom_chars.")
        
        # 使用secrets模块生成加密安全的随机字符串
        return ''.join(secrets.choice(chars) for _ in range(length))
    
    @staticmethod
    def random_choice(sequence: Union[List, tuple, str]) -> Any:
        """从序列中随机选择一个元素
        
        Args:
            sequence: 序列（列表、元组或字符串）
        
        Returns:
            随机选择的元素
        
        Raises:
            ValueError: 如果sequence为空
        """
        if not sequence:
            raise ValueError("sequence cannot be empty")
        return random.choice(sequence)
    
    @staticmethod
    def random_sample(population: Union[List, tuple, str], k: int) -> list:
        """从总体中随机选择k个不重复的元素
        
        Args:
            population: 总体（列表、元组或字符串）
            k: 要选择的元素数量
        
        Returns:
            包含k个随机不重复元素的列表
        
        Raises:
            ValueError: 如果population为空或k大于population的长度
        """
        if not population:
            raise ValueError("population cannot be empty")
        if k > len(population):
            raise ValueError(f"k cannot be greater than population length. Got k={k}, population length={len(population)}")
        if k < 0:
            raise ValueError("k cannot be negative")
        return random.sample(population, k)
    
    @staticmethod
    def shuffle(sequence: Union[List, tuple, str]) -> Union[List, tuple, str]:
        """打乱序列的顺序
        
        Args:
            sequence: 序列（列表、元组或字符串）
        
        Returns:
            打乱后的序列
        
        Note:
            - 对于列表，会在原列表上进行修改并返回修改后的列表
            - 对于元组和字符串，会返回一个新的打乱后的列表
        """
        if isinstance(sequence, list):
            # 列表原地打乱
            random.shuffle(sequence)
            return sequence
        else:
            # 对于其他类型，转换为列表后打乱
            shuffled_list = list(sequence)
            random.shuffle(shuffled_list)
            # 如果是字符串，重新连接
            if isinstance(sequence, str):
                return ''.join(shuffled_list)
            # 如果是元组，转换回元组
            elif isinstance(sequence, tuple):
                return tuple(shuffled_list)
            return shuffled_list
    
    @staticmethod
    def random_uuid(version: int = 4) -> str:
        """生成随机UUID
        
        Args:
            version: UUID版本（1, 3, 4, 5）
        
        Returns:
            UUID字符串
        
        Raises:
            ValueError: 如果version不是支持的UUID版本
        """
        if version == 1:
            # 基于时间的UUID
            return str(uuid.uuid1())
        elif version == 3:
            # 基于名称和MD5哈希的UUID
            namespace = uuid.NAMESPACE_DNS
            name = RandomUtils.random_str(20)
            return str(uuid.uuid3(namespace, name))
        elif version == 4:
            # 随机UUID
            return str(uuid.uuid4())
        elif version == 5:
            # 基于名称和SHA-1哈希的UUID
            namespace = uuid.NAMESPACE_DNS
            name = RandomUtils.random_str(20)
            return str(uuid.uuid5(namespace, name))
        else:
            raise ValueError(f"Unsupported UUID version: {version}. Supported versions are 1, 3, 4, 5.")
    
    @staticmethod
    def random_hex(length: int = 32) -> str:
        """生成随机十六进制字符串
        
        Args:
            length: 字符串长度（十六进制字符的数量）
        
        Returns:
            随机十六进制字符串
        
        Raises:
            ValueError: 如果length小于1
        """
        if length < 1:
            raise ValueError("length must be at least 1")
        # 计算需要多少字节
        num_bytes = (length + 1) // 2  # 向上取整
        # 生成随机字节并转换为十六进制
        return secrets.token_hex(num_bytes)[:length]
    
    @staticmethod
    def random_bool(weight_true: float = 0.5) -> bool:
        """随机生成布尔值
        
        Args:
            weight_true: True的概率权重（0-1之间）
        
        Returns:
            随机布尔值
        
        Raises:
            ValueError: 如果weight_true不在0-1范围内
        """
        if not 0 <= weight_true <= 1:
            raise ValueError("weight_true must be between 0 and 1")
        return random.random() < weight_true
    
    @staticmethod
    def random_phone(prefix: str = '13', length: int = 11) -> str:
        """生成随机手机号
        
        Args:
            prefix: 手机号前缀
            length: 手机号总长度
        
        Returns:
            随机手机号字符串
        
        Raises:
            ValueError: 如果prefix不是数字或length小于len(prefix)或总长度不符合手机号标准
        """
        if not prefix.isdigit():
            raise ValueError("prefix must consist of digits")
        if length < len(prefix):
            raise ValueError(f"length must be at least the length of prefix. Got length={length}, prefix length={len(prefix)}")
        if length < 10 or length > 12:
            raise ValueError(f"Invalid phone number length: {length}. Valid length is between 10 and 12.")
        
        # 生成剩余位数的随机数字
        remaining_length = length - len(prefix)
        remaining_digits = ''.join(random.choice(RandomUtils.DIGITS) for _ in range(remaining_length))
        
        return prefix + remaining_digits
    
    @staticmethod
    def random_email(domain: str = None) -> str:
        """生成随机邮箱地址
        
        Args:
            domain: 自定义邮箱域名，如果为None则随机生成
        
        Returns:
            随机邮箱地址
        """
        # 生成随机用户名
        username_length = RandomUtils.random_int(5, 15)
        username = RandomUtils.random_str(username_length, use_lowercase=True, use_uppercase=False, 
                                         use_digits=True, use_symbols=False)
        
        # 生成或使用提供的域名
        if not domain:
            domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'icloud.com', 'example.com']
            domain = RandomUtils.random_choice(domains)
        
        return f"{username}@{domain}"
    
    @staticmethod
    def random_ip() -> str:
        """生成随机IP地址（IPv4）
        
        Returns:
            随机IPv4地址字符串
        """
        # 生成4个0-255之间的随机数
        return '.'.join(str(RandomUtils.random_int(0, 255)) for _ in range(4))