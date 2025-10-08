# -*- coding: utf-8 -*-
import uuid
import time
import random
import hashlib
import base64
from typing import Optional, Union, Tuple
from datetime import datetime
from yitool.exceptions import YiToolException


class IdUtils:
    """ID工具类，提供各种ID生成和处理的功能"""
    
    # 雪花ID相关常量
    _WORKER_ID_BITS = 5
    _DATACENTER_ID_BITS = 5
    _SEQUENCE_BITS = 12
    
    _MAX_WORKER_ID = -1 ^ (-1 << _WORKER_ID_BITS)  # 31
    _MAX_DATACENTER_ID = -1 ^ (-1 << _DATACENTER_ID_BITS)  # 31
    _MAX_SEQUENCE = -1 ^ (-1 << _SEQUENCE_BITS)  # 4095
    
    _WORKER_ID_SHIFT = _SEQUENCE_BITS
    _DATACENTER_ID_SHIFT = _SEQUENCE_BITS + _WORKER_ID_BITS
    _TIMESTAMP_LEFT_SHIFT = _SEQUENCE_BITS + _WORKER_ID_BITS + _DATACENTER_ID_BITS
    
    _EPOCH = 1609459200000  # 2021-01-01 00:00:00
    
    # 类变量，用于存储雪花ID生成器的状态
    _worker_id = 0
    _datacenter_id = 0
    _sequence = 0
    _last_timestamp = -1
    
    @staticmethod
    def init_snowflake(worker_id: int = 0, datacenter_id: int = 0) -> None:
        """初始化雪花ID生成器
        
        Args:
            worker_id: 工作机器ID（0-31）
            datacenter_id: 数据中心ID（0-31）
        
        Raises:
            ValueError: 如果worker_id或datacenter_id超出范围
        """
        if not (0 <= worker_id <= IdUtils._MAX_WORKER_ID):
            raise ValueError(f"worker_id must be between 0 and {IdUtils._MAX_WORKER_ID}")
        if not (0 <= datacenter_id <= IdUtils._MAX_DATACENTER_ID):
            raise ValueError(f"datacenter_id must be between 0 and {IdUtils._MAX_DATACENTER_ID}")
        
        IdUtils._worker_id = worker_id
        IdUtils._datacenter_id = datacenter_id
        IdUtils._sequence = 0
        IdUtils._last_timestamp = -1
    
    @staticmethod
    def _til_next_millis(last_timestamp: int) -> int:
        """等待直到下一个毫秒时间戳
        
        Args:
            last_timestamp: 上一个时间戳
        
        Returns:
            新的时间戳
        """
        timestamp = int(time.time() * 1000)
        while timestamp <= last_timestamp:
            timestamp = int(time.time() * 1000)
        return timestamp
    
    @staticmethod
    def snowflake_id() -> int:
        """生成雪花ID
        
        Returns:
            64位雪花ID
        
        Raises:
            YiToolException: 如果时钟回拨或生成失败
        """
        # 使用类变量来跟踪状态
        worker_id = IdUtils._worker_id
        datacenter_id = IdUtils._datacenter_id
        sequence = IdUtils._sequence
        last_timestamp = IdUtils._last_timestamp
        
        timestamp = int(time.time() * 1000)
        
        # 处理时钟回拨
        if timestamp < last_timestamp:
            raise YiToolException(f"Clock moved backwards. Refusing to generate id for {last_timestamp - timestamp} milliseconds")
        
        # 如果是同一时间戳，则递增序列号
        if timestamp == last_timestamp:
            sequence = (sequence + 1) & IdUtils._MAX_SEQUENCE
            # 如果序列号溢出，则等待下一个毫秒
            if sequence == 0:
                timestamp = IdUtils._til_next_millis(last_timestamp)
        else:
            # 重置序列号
            sequence = 0
        
        # 更新状态
        IdUtils._last_timestamp = timestamp
        IdUtils._sequence = sequence
        
        # 组合ID：时间戳 << 22 | 数据中心ID << 17 | 工作ID << 12 | 序列号
        return ((timestamp - IdUtils._EPOCH) << IdUtils._TIMESTAMP_LEFT_SHIFT) | \
               (datacenter_id << IdUtils._DATACENTER_ID_SHIFT) | \
               (worker_id << IdUtils._WORKER_ID_SHIFT) | \
               sequence
    
    @staticmethod
    def parse_snowflake_id(snowflake_id: int) -> dict:
        """解析雪花ID，提取其中的时间戳、数据中心ID、工作ID和序列号
        
        Args:
            snowflake_id: 雪花ID
        
        Returns:
            包含解析信息的字典
        
        Raises:
            ValueError: 如果snowflake_id不是有效的整数
        """
        if not isinstance(snowflake_id, int):
            raise ValueError("snowflake_id must be an integer")
        
        timestamp = (snowflake_id >> IdUtils._TIMESTAMP_LEFT_SHIFT) + IdUtils._EPOCH
        datacenter_id = (snowflake_id >> IdUtils._DATACENTER_ID_SHIFT) & IdUtils._MAX_DATACENTER_ID
        worker_id = (snowflake_id >> IdUtils._WORKER_ID_SHIFT) & IdUtils._MAX_WORKER_ID
        sequence = snowflake_id & IdUtils._MAX_SEQUENCE
        
        return {
            'timestamp': timestamp,
            'datetime': datetime.fromtimestamp(timestamp / 1000),
            'datacenter_id': datacenter_id,
            'worker_id': worker_id,
            'sequence': sequence
        }
    
    @staticmethod
    def uuid() -> str:
        """生成标准UUID（版本4）
        
        Returns:
            UUID字符串（如"123e4567-e89b-12d3-a456-426614174000"）
        """
        return str(uuid.uuid4())
    
    @staticmethod
    def uuid_no_dash() -> str:
        """生成无连字符的UUID
        
        Returns:
            无连字符的UUID字符串（如"123e4567e89b12d3a456426614174000"）
        """
        return uuid.uuid4().hex
    
    @staticmethod
    def short_uuid(length: int = 8) -> str:
        """生成短UUID
        
        Args:
            length: 短UUID的长度
        
        Returns:
            短UUID字符串
        
        Raises:
            ValueError: 如果length小于1或大于22
        """
        if length < 1:
            raise ValueError("length must be at least 1")
        if length > 22:
            raise ValueError("length cannot exceed 22")
        
        # 生成UUID并转换为base64，去除特殊字符
        uuid_bytes = uuid.uuid4().bytes
        # 使用urlsafe版本，去掉padding
        short_uuid = base64.urlsafe_b64encode(uuid_bytes)[:length].decode('utf-8')
        return short_uuid
    
    @staticmethod
    def md5_id(data: Union[str, bytes]) -> str:
        """基于MD5生成ID
        
        Args:
            data: 用于生成ID的数据
        
        Returns:
            MD5哈希值（32位十六进制字符串）
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        return hashlib.md5(data).hexdigest()
    
    @staticmethod
    def sha1_id(data: Union[str, bytes]) -> str:
        """基于SHA1生成ID
        
        Args:
            data: 用于生成ID的数据
        
        Returns:
            SHA1哈希值（40位十六进制字符串）
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        return hashlib.sha1(data).hexdigest()
    
    @staticmethod
    def sha256_id(data: Union[str, bytes]) -> str:
        """基于SHA256生成ID
        
        Args:
            data: 用于生成ID的数据
        
        Returns:
            SHA256哈希值（64位十六进制字符串）
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        return hashlib.sha256(data).hexdigest()
    
    @staticmethod
    def timestamp_id() -> str:
        """基于时间戳生成ID
        
        Returns:
            当前时间戳的字符串表示（毫秒级）
        """
        return str(int(time.time() * 1000))
    
    @staticmethod
    def nano_id(length: int = 21) -> str:
        """生成类似nanoid的随机ID
        
        Args:
            length: ID长度
        
        Returns:
            随机ID字符串
        
        Raises:
            ValueError: 如果length小于1
        """
        if length < 1:
            raise ValueError("length must be at least 1")
        
        # 定义字符集（排除了一些容易混淆的字符）
        alphabet = '_-0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        alphabet_length = len(alphabet)
        
        # 生成随机ID
        id_chars = []
        for _ in range(length):
            id_chars.append(random.choice(alphabet))
        
        return ''.join(id_chars)
    
    @staticmethod
    def is_valid_uuid(uuid_str: str) -> bool:
        """验证字符串是否为有效的UUID
        
        Args:
            uuid_str: 要验证的字符串
        
        Returns:
            是否为有效UUID
        """
        if not isinstance(uuid_str, str):
            return False
        
        # 支持带连字符和不带连字符的UUID
        try:
            # 尝试解析UUID
            if len(uuid_str) == 32:
                # 不带连字符的UUID
                uuid_obj = uuid.UUID(hex=uuid_str)
            else:
                # 带连字符的UUID
                uuid_obj = uuid.UUID(uuid_str)
            # 验证解析结果是否与输入匹配
            return str(uuid_obj) == uuid_str or uuid_obj.hex == uuid_str
        except ValueError:
            return False
    
    @staticmethod
    def is_valid_snowflake_id(snowflake_id: int) -> bool:
        """验证整数是否为有效的雪花ID
        
        Args:
            snowflake_id: 要验证的整数
        
        Returns:
            是否为有效雪花ID
        """
        if not isinstance(snowflake_id, int) or snowflake_id <= 0:
            return False
        
        try:
            # 尝试解析雪花ID
            parsed = IdUtils.parse_snowflake_id(snowflake_id)
            # 检查时间戳是否合理（不早于2021年，不晚于未来5年）
            current_time = int(time.time() * 1000)
            five_years_later = current_time + 5 * 365 * 24 * 60 * 60 * 1000
            return IdUtils._EPOCH <= parsed['timestamp'] <= five_years_later
        except Exception:
            return False
    
    @staticmethod
    def combine_ids(*ids: str, separator: str = '-') -> str:
        """合并多个ID
        
        Args:
            *ids: 要合并的ID列表
            separator: 分隔符
        
        Returns:
            合并后的ID字符串
        
        Raises:
            ValueError: 如果没有提供ID
        """
        if not ids:
            raise ValueError("At least one ID must be provided")
        
        return separator.join(str(id_) for id_ in ids)
    
    @staticmethod
    def split_id(combined_id: str, separator: str = '-') -> Tuple[str, ...]:
        """分割合并的ID
        
        Args:
            combined_id: 合并的ID字符串
            separator: 分隔符
        
        Returns:
            分割后的ID元组
        """
        if not isinstance(combined_id, str):
            raise ValueError("combined_id must be a string")
        
        return tuple(combined_id.split(separator))
    
    @staticmethod
    def format_id(prefix: str, id_value: str, suffix: str = '', separator: str = '_') -> str:
        """格式化ID，添加前缀和后缀
        
        Args:
            prefix: ID前缀
            id_value: 核心ID值
            suffix: ID后缀
            separator: 分隔符
        
        Returns:
            格式化后的ID字符串
        """
        parts = []
        if prefix:
            parts.append(str(prefix))
        parts.append(str(id_value))
        if suffix:
            parts.append(str(suffix))
        
        return separator.join(parts)
    
    @staticmethod
    def hash_id(id_value: str, hash_length: int = 8) -> str:
        """生成ID的哈希值，用于短链接或隐私保护
        
        Args:
            id_value: 原始ID
            hash_length: 哈希值长度
        
        Returns:
            哈希后的ID字符串
        
        Raises:
            ValueError: 如果hash_length小于1或大于16
        """
        if hash_length < 1:
            raise ValueError("hash_length must be at least 1")
        if hash_length > 16:
            raise ValueError("hash_length cannot exceed 16")
        
        # 使用SHA256生成哈希，然后截取指定长度
        hash_bytes = hashlib.sha256(str(id_value).encode('utf-8')).digest()
        # 转换为base64并删除特殊字符
        hash_str = base64.urlsafe_b64encode(hash_bytes)[:hash_length].decode('utf-8')
        return hash_str