# -*- coding: utf-8 -*-
import os
from pathlib import Path
from typing import Dict, Optional, Union, IO, Any
from cachetools import cached
from dotenv import load_dotenv, dotenv_values

from yitool.const import __ENV__
from yitool.utils.path_utils import PathUtils


class EnvUtils(object):
    """系统环境变量和配置管理工具类
    
    提供环境变量的读取、管理和配置文件的加载功能，支持：
    - 从.env文件加载配置
    - 缓存配置结果提高性能
    - 类型转换和默认值处理
    - 环境变量的安全访问
    """

    @cached({})
    @staticmethod
    def dotenv_values(
        dotenv_path: Union[str, os.PathLike, None] = __ENV__,
        stream: Optional[IO[str]] = None,
        verbose: bool = False,
        interpolate: bool = True,
        encoding: Optional[str] = "utf-8",
    ) -> Dict[str, Optional[str]]:
        """获取dotenv文件内容，返回键值对字典
        
        加载.env格式的配置文件，但不将其设置到系统环境变量中。
        结果会被缓存，提高重复调用的性能。
        
        Args:
            dotenv_path: .env文件路径，默认为项目根目录的.env文件
            stream: 文件流对象（可选）
            verbose: 是否打印详细信息
            interpolate: 是否解析变量引用（如 ${VAR}）
            encoding: 文件编码
        
        Returns:
            包含配置项的字典
        
        Raises:
            FileNotFoundError: 如果指定的.env文件不存在
        
        Example:
            >>> config = EnvUtils.dotenv_values()
            >>> db_host = config.get('MYSQL_HOST')
        """
        PathUtils.raise_if_not_exists(dotenv_path)
        return dotenv_values(
            dotenv_path=dotenv_path, stream=stream, verbose=verbose, interpolate=interpolate, encoding=encoding,
        )

    @cached({})
    @staticmethod
    def load_env_file(
        dotenv_path: Union[str, os.PathLike, None] = __ENV__,
        stream: Optional[IO[str]] = None,
        verbose: bool = False,
        override: bool = False,
        interpolate: bool = True,
        encoding: Optional[str] = "utf-8",
    ) -> bool:
        """加载dotenv文件到系统环境变量中
        
        读取.env格式的配置文件，并将其内容设置为系统环境变量。
        结果会被缓存，提高重复调用的性能。
        
        Args:
            dotenv_path: .env文件路径，默认为项目根目录的.env文件
            stream: 文件流对象（可选）
            verbose: 是否打印详细信息
            override: 是否覆盖已存在的环境变量
            interpolate: 是否解析变量引用（如 ${VAR}）
            encoding: 文件编码
        
        Returns:
            操作是否成功
        
        Raises:
            FileNotFoundError: 如果指定的.env文件不存在
        
        Example:
            >>> EnvUtils.load_env_file(override=True)  # 强制覆盖已存在的环境变量
        """
        PathUtils.raise_if_not_exists(dotenv_path)
        return load_dotenv(
            dotenv_path=dotenv_path,
            stream=stream,
            verbose=verbose,
            override=override,
            interpolate=interpolate,
            encoding=encoding,
        )

    @staticmethod
    def get_env(key: str, default: Optional[Any] = None, cast: Optional[type] = None) -> Any:
        """安全获取环境变量，支持类型转换和默认值
        
        Args:
            key: 环境变量名称
            default: 当环境变量不存在时返回的默认值
            cast: 类型转换函数，如int, float, bool等
        
        Returns:
            环境变量的值（可能经过类型转换）或默认值
        
        Example:
            >>> port = EnvUtils.get_env('REDIS_PORT', default=6379, cast=int)
            >>> debug_mode = EnvUtils.get_env('DEBUG', default=False, cast=bool)
        """
        value = os.environ.get(key, default)
        
        # 处理布尔类型的特殊情况
        if cast is bool and isinstance(value, str):
            return value.lower() in ('true', 'yes', '1', 'y', 't')
        
        # 执行类型转换
        if cast and value is not None and not isinstance(value, cast):
            try:
                return cast(value)
            except (ValueError, TypeError):
                return default
        
        return value

    @staticmethod
    def set_env(key: str, value: Any) -> None:
        """设置系统环境变量
        
        Args:
            key: 环境变量名称
            value: 环境变量的值，将被转换为字符串
        
        Example:
            >>> EnvUtils.set_env('APP_NAME', 'yitool')
        """
        os.environ[key] = str(value)

    @staticmethod
    def unset_env(key: str) -> None:
        """删除系统环境变量
        
        Args:
            key: 环境变量名称
        
        Example:
            >>> EnvUtils.unset_env('TEMP_VAR')
        """
        if key in os.environ:
            del os.environ[key]